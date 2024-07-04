from eat.core.components import ValidTermGenerator, TermOperation
from eat.core.utilities import print_search_summary, condensed_array, \
    combine_postfix
from collections import deque
from copy import deepcopy
from decimal import Decimal
from operator import attrgetter
from random import choice
import multiprocessing as mp
import logging
import time
import signal
import sys


def exit_gracefully(func):
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            return
    return func_wrapper


class Beam():

    __slots__ = ['width', 'levels']

    def __init__(self, width):
        self.width = width
        self.levels = []

    def add_node(self, node):
        self.levels[node.level].append(node)

    def add_level(self, nodes_list=None):
        self.levels.append(nodes_list if nodes_list else [])

    def get_level(self, level):
        if level < self.get_height():
            return self.levels[level]
        else:
            return None

    def get_level_size(self, level):
        return len(self.get_level(level))

    def get_height(self):
        return len(self.levels)

    def get_highest_full_level_number(self):
        for idx, level in enumerate(reversed(self.levels)):
            if len(level) == self.width:
                return self.get_height() - idx - 1

    def get_highest_full_level(self):
        return self.levels[self.get_highest_full_level_number()]


class Node():

    def __init__(self, term, array, parent, level, term_operation):
        self.term = term
        self.to = term_operation
        self.array = array
        self.parent_node = parent
        self.level = level
        self.proc_hash = None
        self.fitness = self.to.calucate_number_pos_sol(self.array)
        self.creation_time = time.perf_counter()

    def elapsed_time(self, reference_time):
        return self.creation_time - reference_time if self.parent_node else 0

    def time_since_parent_creation(self):
        return time.perf_counter() - self.parent_node.creation_time \
            if self.parent_node else 0

    def recurse(self):
        node = deepcopy(self)
        while (node.parent_node is not None):
            # recursively construct the term
            node.parent_node.term = \
                node.parent_node.term.replace("F", node.term)
            node = deepcopy(node.parent_node)
        return node


class BeamProcessManager():

    def __init__(self):
        self.proc_map = {}

    def add_process(self, bp):
        self.proc_map[bp.hash] = bp

    def get_process(self, proc_hash):
        proc = self.proc_map.get(proc_hash, None)
        return proc

    def get_processes(self):
        return self.proc_map.values()

    def get_processes_by_decr_fitness(self, level):
        processes = self.get_process_below_level(level)
        processes = sorted(processes,
                           key=lambda bp: bp.node.fitness,
                           reverse=True)
        return processes

    def get_process_below_level(self, level):
        processes_below_h = []
        for bp in self.get_processes():
            if bp.node.level < level:
                processes_below_h.append(bp)
        processes_below_h = sorted(processes_below_h,
                                   key=lambda bp:
                                   (bp.node.level, len(bp.child_nodes)))
        return processes_below_h

    def get_lowest_process_level(self):
        return min(self.get_processes(),
                   key=attrgetter('node.level')).node.level

    def terminate_all(self):
        for bp in self.get_processes():
            bp.terminate()

    def deactivate_all(self):
        for bp in self.get_processes():
            bp.deactivate()


class BeamProcess():

    def __init__(self, process_hash):
        self.proc = None
        self.hash = process_hash
        self.child_nodes = deque()
        self.node = None

    def run(self, target, queue, node, **kwargs):
        node.proc_hash = self.hash
        self.node = node
        self.terminate()
        self.proc = mp.Process(target=target,
                               args=(queue, node),
                               kwargs=kwargs)
        self.proc.start()

    def terminate(self):
        if self.proc:
            try:
                self.proc.terminate()
            except AttributeError:
                # process already terminated by parent
                return

    def deactivate(self):
        self.terminate()
        self.child_nodes = deque()

    def is_alive(self):
        return self.proc.is_alive()

    def __eq__(self, obj):
        return obj.hash == self.hash


class BeamEnumerationAlgorithm():

    def __init__(self, groupoid, term_operation, algorithm,
                 term_expansion_probability=0.1,
                 male_term_generation_method="GRA", beam_width=3,
                 sub_beam_width=3):
        self.grp = groupoid
        self.to = term_operation
        self.algorithm = algorithm
        self.is_subbeam = (algorithm == "FBA")
        self.beam = Beam(beam_width)
        self.vtg = ValidTermGenerator(self.to.term_variables)
        self.male_terms = self.to.term_variables
        self.term_expansion_probability = term_expansion_probability
        self.male_term_generation_method = male_term_generation_method
        self.beam_width = beam_width
        self.sub_beam_width = sub_beam_width
        try:
            mp.set_start_method('fork', force=True)
        except RuntimeError:
            pass
        except AttributeError:
            logging.warning("Unable to configure how subprocesses are "
                            "initialized. This could cause slower performance "
                            "on some systems. It is recommended that you use "
                            "python3.")
            pass

    def get_male_term(self, generation_method="GRA", **kwargs):
        if generation_method == "GRA":
            return self.vtg.generate(
                algorithm=generation_method,
                prob=self.term_expansion_probability,
                **kwargs)
        elif generation_method == "random-term-generation":
            return self.vtg.generate(algorithm=generation_method,
                                     prob=self.term_expansion_probability,
                                     **kwargs)

    def create_female_term(self, male_term, direction):
        """
        Given a male term and a direction (left or right) returns a new female
        term string
        """
        female_term = ""
        if direction == "left":
            female_term = combine_postfix("F", male_term)
        elif direction == "right":
            female_term = combine_postfix(male_term, "F")
        return female_term

    def try_to_create_valid_female_node(self, male_term, curr_fnode):
        """
        Using the male_term, try to create a female term that is valid
        with respect to the curr_fnodes validity array.
        """
        direction_order = ["right", "left"]
        for direction in direction_order:
            new_female_term = self.create_female_term(male_term,
                                                      direction)
            is_valid, validity_array = \
                self.to.compute_validity_array(new_female_term,
                                               curr_fnode.array)
            if is_valid:
                return Node(new_female_term, validity_array, curr_fnode,
                            curr_fnode.level+1, curr_fnode.to)
        else:
            # we couldn't find a valid female term
            return None

    @exit_gracefully
    def search_for_valid_female_node(self, mp_queue, curr_fnode):
        """
        Continuously searches for a valid female node and put result in the
        multiprocessing queue
        """
        # Exclude solutions that we know have already been found when we start
        # a new search process
        exclude = set()
        next_level = self.beam.get_level(curr_fnode.level+1)
        if next_level:
            exclude = {f_node.term for f_node in next_level}

        random_terms = set()
        # Continuously search for a new solution
        while (True):
            random_term = self.get_male_term(
                generation_method=self.male_term_generation_method
            )
            if random_term not in random_terms:
                f_node = self.try_to_create_valid_female_node(random_term,
                                                              curr_fnode)
                if f_node:
                    if f_node.term not in exclude:
                        mp_queue.put_nowait(f_node)
                        return
            random_terms.add(random_term)

    @exit_gracefully
    def search_for_valid_female_node_using_lr_array(
                                self, mp_queue, curr_fnode,
                                direction="left"):
        """
        Continuously searches for a valid female node by finding a solution to
        the left or right array
        """
        # Exclude solutions that we know have already been found when we start
        # a new search process
        exclude = set()
        next_level = self.beam.get_level(curr_fnode.level+1)
        if next_level:
            exclude = {f_node.term for f_node in next_level}

        target_array = []
        if direction == "left":
            target_array = self.to.l_array(curr_fnode.array)
        elif direction == "right":
            target_array = self.to.r_array(curr_fnode.array)
        else:
            raise ValueError("Unknown direction. Choose from 'left' or "
                             "'right'.")
        target_to = TermOperation(self.grp,
                                  target=target_array,
                                  term_variables=self.to.term_variables)
        ba = BeamEnumerationAlgorithm(
                 self.grp, target_to, "FBA",
                 term_expansion_probability=self.term_expansion_probability,
                 male_term_generation_method=self.male_term_generation_method,
                 beam_width=self.sub_beam_width)
        # Continuously search for a new solution
        while (True):
            sol_node = ba.run()
            if direction == "left":
                new_female_term = combine_postfix(sol_node.term, "F")
            else:
                new_female_term = combine_postfix("F", sol_node.term)
            is_valid, validity_array = \
                self.to.compute_validity_array(new_female_term,
                                               curr_fnode.array)
            if is_valid is False:
                raise RuntimeError("A {} array solution was found that is not "
                                   "valid! Something went wrong!"
                                   .format(direction))
            f_node = Node(new_female_term,
                          validity_array,
                          curr_fnode,
                          curr_fnode.level+1,
                          curr_fnode.to)
            if f_node.term not in exclude:
                mp_queue.put_nowait(f_node)
                return

    def check_if_has_male_term_solution(self, curr_fnode):
        for mt in self.male_terms:
            male_term_sol = self.to.compute(mt)
            if (self.to.is_solution(male_term_sol, curr_fnode.array)):
                # found a solution
                return Node(mt, male_term_sol, curr_fnode, curr_fnode.level+1,
                            curr_fnode.to)

    def _print_verbose_valid_term_log(self, f_node_sol,
                                      include_validity_array):
        if self.beam_width > 1:
            f_node_sol_level = [bn.term for bn in
                                self.beam.get_level(f_node_sol.level)]
            print("{}: Found {}valid term {} of fitness {:.2e} at level {} {}"
                  .format(
                    f_node_sol.parent_node.proc_hash if
                    f_node_sol.parent_node.proc_hash else "Main",
                    ("DUPLICATE "
                        if f_node_sol.term in f_node_sol_level
                        else ""),
                    f_node_sol.term,
                    Decimal(f_node_sol.fitness),
                    f_node_sol.level,
                    ("with array {}"
                        .format(condensed_array(f_node_sol.array,
                                                self.grp.size))
                        if include_validity_array else "")
                    ))
        else:
            print("{}: Found valid term {} of fitness {:.2e} at level {} {}"
                  .format(
                    f_node_sol.parent_node.proc_hash if
                    f_node_sol.parent_node.proc_hash else "Main",
                    f_node_sol.term,
                    f_node_sol.fitness,
                    f_node_sol.level,
                    ("with array {}"
                        .format(condensed_array(f_node_sol.array,
                                                self.grp.size))
                        if include_validity_array else "")
                  ))

    def run(self, verbose=False, print_summary=False,
            include_validity_array=False):
        sol_node = None
        # initialize beam at level 0
        f_node = Node("F", self.to.target, None, 0, self.to)
        self.beam.add_level([f_node for _ in range(0, self.beam_width)])

        start = time.perf_counter()

        mp_mngr = mp.Manager()
        mp_queue = mp_mngr.Queue()

        bpm = BeamProcessManager()

        def terminate_signal_handler(signum, frame):
            # this closure gets the objects in scope of the process actively
            # being terminated
            mp_mngr.shutdown()

        def interupt_signal_handler(signum, frame):
            bpm.terminate_all()
            sys.exit()

        # Use signal handler to throw exception which can be caught to allow
        # graceful exit.
        signal.signal(signal.SIGINT, interupt_signal_handler)
        signal.signal(signal.SIGTERM, terminate_signal_handler)

        for idx, f_node in enumerate(
                self.beam.get_level(self.beam.get_height()-1)):
            # start a process for each of the initial nodes at level 0
            bp = BeamProcess("P{}".format(idx))
            bpm.add_process(bp)
            f_node.proc_hash = bp.hash
            if self.algorithm == "MFBA":
                bp.run(self.search_for_valid_female_node_using_lr_array,
                       mp_queue,
                       f_node,
                       direction=choice(["left", "right"]))
            else:
                bp.run(self.search_for_valid_female_node,
                       mp_queue,
                       f_node)

        while (True):
            f_node_sol = mp_queue.get()
            f_node_sol_parent_proc = \
                bpm.get_process(f_node_sol.parent_node.proc_hash)

            # If we reach here we found a valid female term of
            # sufficient fitness
            if not self.beam.get_level(f_node_sol.level):
                # Grow the beam
                self.beam.add_level()

            if verbose:
                self._print_verbose_valid_term_log(f_node_sol,
                                                   include_validity_array)

            sol_node = self.check_if_has_male_term_solution(f_node_sol)
            if sol_node:
                break

            procs_by_fitness = bpm.get_processes_by_decr_fitness(
                f_node_sol.level)
            if not procs_by_fitness:
                if verbose:
                    print(f"!!Skipping {f_node_sol.term}. No processes "
                          f"running at a level below {f_node_sol.level}!!")
                continue
            least_fit_bp = procs_by_fitness[-1]

            if (f_node_sol.fitness < least_fit_bp.node.fitness):
                # Rerun process for solution node's parent
                # and discard f_node_sol
                if verbose:
                    print(
                        f"{f_node_sol_parent_proc.hash}: Discard lower "
                        f"fitness term {f_node_sol.term} and rerun "
                        f"{f_node_sol_parent_proc.hash} to search for "
                        f"a new term. "
                        f"{f_node_sol.fitness} < {least_fit_bp.node.fitness}")
                if self.algorithm == "MFBA":
                    f_node_sol_parent_proc.run(
                        self.search_for_valid_female_node_using_lr_array,  # noqa
                        mp_queue,
                        f_node_sol.parent_node,
                        direction=choice(["left", "right"]))
                else:
                    f_node_sol_parent_proc.run(
                        self.search_for_valid_female_node,
                        mp_queue,
                        f_node_sol.parent_node)
            elif self.algorithm == "SBA" and f_node_sol.term not in \
                    [t.term for t in self.beam.get_level(f_node_sol.level)]:
                # add node to beam and parent process child nodes
                self.beam.add_node(f_node_sol)
                f_node_sol_parent_proc.child_nodes.append(f_node_sol)
                # check if we need to run the next full level or continue
                # searching
                if self.beam.get_highest_full_level_number() == \
                        f_node_sol.level:
                    # beam is full, start the next level
                    nodes = self.beam.get_level(f_node_sol.level)
                    for i, proc in enumerate(bpm.get_processes()):
                        proc.run(
                            self.search_for_valid_female_node,
                            mp_queue,
                            nodes[i])
                else:
                    # continue searching until the next level is full
                    f_node_sol_parent_proc.run(
                        self.search_for_valid_female_node,
                        mp_queue,
                        f_node_sol.parent_node)
            elif self.algorithm in ["FBA", "MFBA"] and f_node_sol.term not in \
                    [t.term for t in self.beam.get_level(f_node_sol.level)]:
                # add node to beam and parent process child nodes
                self.beam.add_node(f_node_sol)
                f_node_sol_parent_proc.child_nodes.append(f_node_sol)

                # deactivate the process since it's being reassigned
                least_fit_bp.deactivate()
                # reassign least fit beam process to work on newly found
                # female term
                if verbose:
                    print(f"{least_fit_bp.hash}: Reassigned "
                          f"{least_fit_bp.hash} to work on the newly "
                          f"found female term {f_node_sol.term}")
                if self.algorithm == "MFBA":
                    least_fit_bp.run(
                        self.search_for_valid_female_node_using_lr_array,  # noqa
                        mp_queue,
                        f_node_sol,
                        direction=choice(["left", "right"]))
                else:
                    least_fit_bp.run(
                        self.search_for_valid_female_node,
                        mp_queue,
                        f_node_sol)
                if f_node_sol_parent_proc.hash != least_fit_bp.hash:
                    if verbose:
                        print(f"{f_node_sol_parent_proc.hash}: Rerun "
                              f"{f_node_sol_parent_proc.hash} to "
                              f"search for a new child female term "
                              f"different than {f_node_sol.term}")
                    if self.algorithm == "MFBA":
                        f_node_sol_parent_proc.run(
                            self.search_for_valid_female_node_using_lr_array,
                            mp_queue,
                            f_node_sol.parent_node,
                            direction=choice(["left", "right"]))
                    else:
                        f_node_sol_parent_proc.run(
                            self.search_for_valid_female_node,
                            mp_queue,
                            f_node_sol.parent_node)
            else:
                if verbose:
                    print(f"{f_node_sol_parent_proc.hash}: Duplicate term."
                          f"Rerun {f_node_sol_parent_proc.hash} to "
                          f"search for a new child female term "
                          f"different than {f_node_sol.term}")
                if self.algorithm == "MFBA":
                    f_node_sol_parent_proc.run(
                        self.search_for_valid_female_node_using_lr_array,
                        mp_queue,
                        f_node_sol.parent_node,
                        direction=choice(["left", "right"]))
                else:
                    f_node_sol_parent_proc.run(
                        self.search_for_valid_female_node,
                        mp_queue,
                        f_node_sol.parent_node)
            if verbose:
                print("(pid,lvl,chldn,fitness,is_alive): {}".format(
                    [(bp.hash,
                      bp.node.level,
                      len(bp.child_nodes),
                      f"{Decimal(bp.node.fitness):.2e}",
                      bp.is_alive())
                     for bp in bpm.get_processes()]))

        # kill any remaining processes
        bpm.deactivate_all()

        node = sol_node.recurse()

        end = time.perf_counter()

        if (print_summary or verbose):
            print_search_summary(node, sol_node, self.to, self.grp, start, end,
                                 show_creation_history=verbose)
        else:
            if verbose:
                print(node.term)
        return node
