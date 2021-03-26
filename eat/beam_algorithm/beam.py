from eat.core.components import ValidTermGenerator
from eat.core.utilities import get_all_one_and_two_variable_terms, \
    print_search_summary, condensed_array
from operator import attrgetter
import queue
import multiprocessing as mp
import logging
import time
import uuid


class Beam():

    def __init__(self, width):
        self.width = width
        self.levels = []

    def add_node(self, node):
        self.levels[node.level].append(node)
    
    def add_level(self, nodes_list=None):
        if not nodes_list:
            nodes_list = []
        self.levels.append(nodes_list)

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

    def __init__(self, term, array, parent, level):
        self.term = term
        self.array = array
        self.parent_node = parent
        self.level = level
        self.proc_hash = None


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

class BeamProcess():

    def __init__(self, process_hash):
        self.proc = None
        self.hash = process_hash
        self.child_nodes = []
        self.node = None
    
    def run(self, target, queue, node):
        self.node = node
        self.proc = mp.Process(target=target,
                               args=(queue, node))
        self.proc.start()

    def terminate(self):
        self.proc.terminate()

    def reset(self):
        if self.proc:
            self.proc.terminate()
        self.child_nodes = []

    def is_alive(self):
        return self.proc.is_alive()


class BeamEnumerationAlgorithm():

    def __init__(self, groupoid, term_operation, min_term_length=None,
                 max_term_length=None, term_expansion_probability=0.5,
                 male_term_generation_method="random", beam_width=3,
                 promotion_child_count=2):
        self.grp = groupoid
        self.to = term_operation
        self.beam = Beam(beam_width)
        self.vtg = ValidTermGenerator(self.to.term_variables)
        self.validity_terms = \
            get_all_one_and_two_variable_terms(self.to.term_variables)
        self.male_terms = self.to.term_variables
        self.term_expansion_probability = term_expansion_probability
        self.min_term_length = min_term_length
        self.max_term_length = max_term_length
        self.male_term_generation_method = male_term_generation_method
        self.beam_width = beam_width
        self.promotion_child_count = promotion_child_count
        try:
            mp.set_start_method('fork', force=True)
        except RuntimeError:
            pass
        except AttributeError:
            logging.warning("Unable to configure how subprocesses are initialized. "
                            "This could cause slower performance on some systems. "
                            "It is recommended that you use python3.")
            pass

    def get_male_term(self, generation_method="GRA", **kwargs):
        if generation_method == "GRA":
            return self.vtg.generate(
                algorithm="GRA",
                min_term_length=self.min_term_length,
                max_term_length=self.max_term_length,
                prob=self.term_expansion_probability,
                **kwargs)
        elif generation_method == "random-12-terms":
            return self.vtg.generate(algorithm="random-12-terms", **kwargs)

    def create_female_term(self, male_term, direction):
        """
        Given a male term and a direction (left or right) returns a new female
        term string
        """
        female_term = ""
        if direction == "left":
            female_term = "F{}*".format(male_term)
        elif direction == "right":
            female_term = "{}F*".format(male_term)
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
            has_validity_array, validity_array = \
                self.to.compute_validity_array(new_female_term,
                                               curr_fnode.array)
            if has_validity_array:
                return Node(new_female_term, validity_array, curr_fnode,
                            curr_fnode.level+1)
        else:
            # we couldn't find a valid female term
            return None

    def search_for_valid_female_node(self, mp_queue, curr_fnode):
        """
        Continuously searches for a valid female node
        """
        # Exclude solutions that we know have already been found when we start
        # a new search process
        exclude = {}
        next_level = self.beam.get_level(curr_fnode.level+1)
        if next_level:
            exclude = {f_node.term for f_node in next_level}
        
        random_terms = set()
        # Continuously search for a new solution
        while(True):
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

    def check_if_has_male_term_solution(self, curr_fnode):
        for mt in self.male_terms:
            male_term_sol = self.to.compute(mt)
            if(self.to.is_solution(male_term_sol, curr_fnode.array)):
                # found a solution
                return Node(mt, male_term_sol, curr_fnode, curr_fnode.level+1)

    def run(self, verbose=False, print_summary=False,
            include_validity_array=False):
        sol_node = None
        # initialize beam at level 0
        f_node = Node("F", self.to.target, None, 0)
        self.beam.add_level([f_node for _ in range(0, self.beam_width)])

        start = time.time()
        mp_queue = mp.Queue()

        bpm = BeamProcessManager()
        for idx, f_node in enumerate(self.beam.get_level(0)):
            # start a process for each of the initial nodes at level 0
            bp = BeamProcess("P{}".format(idx))
            bpm.add_process(bp)
            f_node.proc_hash = bp.hash
            bp.run(self.search_for_valid_female_node,
                   mp_queue,
                   f_node)

        while(True):
            try:
                f_node_sol = mp_queue.get_nowait()

                # If we reach here we found a valid female term
                if not self.beam.get_level(f_node_sol.level):
                    # Grow the beam
                    self.beam.add_level()

                if (verbose):
                    if self.beam_width > 1:
                        f_node_sol_level = [bn.term for bn in 
                            self.beam.get_level(f_node_sol.level)]
                        print("{} found {}valid term {} at level {} {}"
                              .format(
                                f_node_sol.parent_node.proc_hash,
                                ("DUPLICATE "
                                 if f_node_sol.term in f_node_sol_level
                                 else ""),
                                f_node_sol.term,
                                f_node_sol.level,
                                ("with array {}"
                                 .format(condensed_array(f_node_sol.array,
                                                         self.grp.size))
                                 if include_validity_array else "")
                              ))
                    else:
                        print("{} found valid term {} at level {} {}"
                              .format(
                                f_node_sol.parent_node.proc_hash,
                                f_node_sol.term,
                                f_node_sol.level,
                                ("with array {}"
                                 .format(condensed_array(f_node_sol.array,
                                                         self.grp.size))
                                 if include_validity_array else "")
                              ))
                        print(f_node_sol.level,
                              [f_node_sol.term],
                              condensed_array(f_node_sol.array,
                                              self.grp.size)
                              if include_validity_array else "")

                sol_node = self.check_if_has_male_term_solution(f_node_sol)
                if sol_node:
                    break
                else:
                    f_node_sol_proc = \
                        bpm.get_process(f_node_sol.parent_node.proc_hash)
                    if f_node_sol.term not in \
                            [t.term for t in
                             self.beam.get_level(f_node_sol.level)]:
                        self.beam.add_node(f_node_sol)
                        f_node_sol_proc.child_nodes.append(f_node_sol)

                    highest_full_level_num = \
                        self.beam.get_highest_full_level_number()
                    # Check if the valid female terms parent has
                    # produced sufficient children for promotion
                    if (len(f_node_sol_proc.child_nodes) ==
                            self.promotion_child_count):
                        # Terminate productive solution nodes parent
                        # process and dedicate to a node a level H+1
                        child_nodes = f_node_sol_proc.child_nodes
                        child_nodes[0].proc_hash = \
                            f_node_sol_proc.hash
                        f_node_sol_proc.reset()
                        f_node_sol_proc.run(
                            self.search_for_valid_female_node,
                            mp_queue,
                            child_nodes[0])
                        # Terminate an unproductive process and 
                        # dedicate to a node at level H+1
                        least_productive_processes = []
                        if len(child_nodes) > 1:
                            least_productive_processes = \
                                bpm.get_process_below_level(f_node_sol.level)
                            reassigned_proc_count = 0
                            if least_productive_processes:
                                for unproductive_process in \
                                        least_productive_processes:
                                    next_child = child_nodes[
                                        reassigned_proc_count+1]
                                    next_child.proc_hash = \
                                            unproductive_process.hash
                                    unproductive_process.reset()
                                    unproductive_process.run(
                                        self.search_for_valid_female_node,
                                        mp_queue,
                                        next_child)
                                    reassigned_proc_count += 1
                                    if reassigned_proc_count == \
                                            self.promotion_child_count - 1:
                                        break
                        if verbose:
                            promoted_procs = [f_node_sol_proc] + \
                                least_productive_processes
                            print("{}-CHILDREN - Promoted {} since {} found "
                                  "{} children"
                                  .format(self.promotion_child_count,
                                          ["{}_{}"
                                           .format(bp.hash, bp.node.level)
                                           for bp in promoted_procs],
                                          f_node_sol_proc.hash,
                                          self.promotion_child_count))
                    elif (bpm.get_lowest_process_level() <
                            highest_full_level_num):
                        # Check if the beam is full at a level above
                        # the lowest working process
                        lowest_processes = bpm.get_process_below_level(
                            highest_full_level_num)
                        full_level_f_nodes = self.beam.get_level(
                            highest_full_level_num)
                        # kill all lower level processes and move to the
                        # highest full level
                        for bp in lowest_processes:
                            for f_node in full_level_f_nodes:
                                f_node.proc_hash = bp.hash
                                bp.reset()
                                bp.run(
                                    self.search_for_valid_female_node,
                                    mp_queue,
                                    f_node)
                        if verbose:
                            print("FULL-ROW-{} - Promoted {} to level {} since "
                                  "beam level {} was filled"
                                  .format(highest_full_level_num,
                                          [bp.hash for bp in lowest_processes],
                                          highest_full_level_num,
                                          highest_full_level_num))
                    else:
                        # Create a new process dedicated to the
                        # solution node's parent
                        f_node_sol_proc.run(
                            self.search_for_valid_female_node,
                            mp_queue,
                            f_node_sol.parent_node)
                        f_node_sol.parent_node.proc = bp
                        if verbose:
                            print("CONTINUE - Continue searching with {} for "
                                  "another child at {}"
                                  .format(bp.hash, f_node_sol.level))

                if verbose:
                    print("(pid,lvl,chldn): {}".format(
                          [(bp.hash, bp.node.level,
                            len(bp.child_nodes))
                           for bp in bpm.get_processes()]))
            except queue.Empty:
                pass
        # kill any remaining processes
        bpm.terminate_all()
        mp_queue.close()
        node = sol_node

        while(node.parent_node is not None):
            # recursively construct the term
            node.parent_node.term = \
                node.parent_node.term.replace("F", node.term)
            node = node.parent_node
        end = time.time()

        if (print_summary or verbose):
            print_search_summary(node.term, self.to, self.grp, end - start)
        else:
            print(node.term)


