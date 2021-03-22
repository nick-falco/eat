from eat.core.components import ValidTermGenerator
from eat.core.utilities import get_all_one_and_two_variable_terms, \
    print_search_summary
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
        self.levels[node.height].append(node)
    
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

    def __init__(self, term, array, parent, height):
        self.term = term
        self.array = array
        self.parent_node = parent
        self.height = height
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

    def get_processes_to_promote(self):
        return [bp for bp in self.get_processes()
                if len(bp.child_nodes) == 2]

    def get_process_below_height(self, height):
        processes_below_h = []
        for bp in self.get_processes():
            if bp.node.height < height:
                processes_below_h.append(bp)
        processes_below_h = sorted(processes_below_h,
                                   key=lambda bp: 
                                   (bp.node.height, len(bp.child_nodes)))
        return processes_below_h

    def get_lowest_level_processes(self):
        min_hight = self.get_lowest_process_level_number()
        return [bp for bp in self.get_processes()
                if bp.node.height == min_hight]

    def get_lowest_process_level_number(self):
        return min(self.get_processes(),
                   key=attrgetter('node.height')).node.height

    def terminate_all(self):
        for bp in self.get_processes():
            bp.terminate()

class BeamProcess():

    def __init__(self):
        self.proc = None
        self.hash = uuid.uuid4()
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

    def __init__(self, groupoid, term_operation, max_male_term_length=None,
                 term_expansion_probability=0.5,
                 male_term_generation_method="random", beam_width=3,
                 beam_timeout=None):
        self.grp = groupoid
        self.to = term_operation
        self.vtg = ValidTermGenerator(self.to.term_variables)
        self.validity_terms = \
            get_all_one_and_two_variable_terms(self.to.term_variables)
        self.male_terms = self.to.term_variables
        self.term_expansion_probability = term_expansion_probability
        self.max_male_term_length = max_male_term_length
        self.male_term_generation_method = male_term_generation_method
        self.beam_width = beam_width
        self.beam_timeout = beam_timeout
        try:
            mp.set_start_method('fork', force=True)
        except RuntimeError:
            pass
        except AttributeError:
            logging.warning("Unable to configure how subprocesses are initialized. "
                            "This could cause slower performance on some systems. "
                            "It is recommended that you use python3.")
            pass

    def get_male_term(self, generation_method="random"):
        if generation_method == "random":
            return self.vtg.generate(
                algorithm="GRA",
                max_male_term_length=self.max_male_term_length,
                prob=self.term_expansion_probability)
        elif generation_method == "random-12-terms":
            return self.vtg.generate(algorithm="random-12-terms")

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
        
        """
        direction_order = ["right", "left"]
        for direction in direction_order:
            new_female_term = self.create_female_term(male_term,
                                                      direction)
            has_var_sol, var_sol = \
                self.to.compute_validity_array(new_female_term,
                                               curr_fnode.array)
            if has_var_sol:
                return Node(new_female_term, var_sol, curr_fnode,
                            curr_fnode.height+1)
        else:
            # we couldn't find a valid female term
            return None

    def search_for_valid_female_node(self, mp_queue, curr_fnode):
        """
        Continuously searches for a valid female node
        """
        # first we check for new valid female terms using the standard
        # set of validity terms
        '''for validity_term in self.validity_terms:
            fnode = self.try_to_create_valid_female_node(validity_term,
                                                         curr_fnode)
            if fnode:
                return fnode'''
        # if no validity terms produce valid female term, we continue
        # to try random terms
        while(True):
            random_term = self.get_male_term(
                generation_method=self.male_term_generation_method
            )
            fnode = self.try_to_create_valid_female_node(random_term,
                                                         curr_fnode)
            if fnode:
                mp_queue.put_nowait(fnode)
                return

    def check_if_has_male_term_solution(self, curr_fnode):
        for mt in self.male_terms:
            male_term_sol = self.to.compute(mt)
            if(self.to.is_solution(male_term_sol, curr_fnode.array)):
                # found a solution
                return Node(mt, male_term_sol, curr_fnode, curr_fnode.height+1)

    def run(self, verbose=False, print_summary=False,
            include_validity_array=False):
        sol_node = None
        height = 0
        # initialize beam at height 0
        f_node = Node("F", self.to.target, None, height)
        beam = Beam(self.beam_width)
        beam.add_level([f_node for _ in range(0, self.beam_width)])

        start = time.time()
        mp_queue = mp.Queue()

        bpm = BeamProcessManager()
        for f_node in beam.get_level(height):
            # start a process for each of the nodes at the current
            # beam height
            bp = BeamProcess()
            bpm.add_process(bp)
            f_node.proc_hash = bp.hash
            bp.run(self.search_for_valid_female_node,
                   mp_queue,
                   f_node)

        while(True):
            try:
                f_node_sol = mp_queue.get_nowait()

                # If we reach here we found a valid female term
                if not beam.get_level(f_node_sol.height):
                    # Grow the beam
                    beam.add_level()

                if (verbose):
                    #### PRINT HIGHEST BEAM LEVEL
                    if self.beam_width > 1:
                        highest_level = \
                            [bn.term for bn in 
                             beam.get_level(beam.get_height()-1)]
                        if highest_level:
                            print(beam.get_height()-1,
                                  f_node_sol.term,
                                  highest_level,
                                  "DUPLICATE SOLUTION!"
                                  if f_node_sol.term in highest_level
                                  else "",
                                  f_node_sol.array if include_validity_array
                                  else ""
                            )
                    else:
                        print(beam.get_height()-1,
                              [f_node_sol.term],
                              f_node_sol.array if include_validity_array
                              else "")

                sol_node = self.check_if_has_male_term_solution(f_node_sol)
                if sol_node:
                    break
                else:
                    f_node_sol_proc = \
                        bpm.get_process(f_node_sol.parent_node.proc_hash)
                    if f_node_sol.term not in \
                            [t.term for t in beam.get_level(f_node_sol.height)]:
                        beam.add_node(f_node_sol)
                        f_node_sol_proc.child_nodes.append(f_node_sol)
                    # Check if the valid female terms parent has
                    # produced sufficient children for promotion
                    if len(f_node_sol_proc.child_nodes) == 2:
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
                        least_productive_processes = \
                            bpm.get_process_below_height(f_node_sol.height)
                        if least_productive_processes:
                            unproductive_process = least_productive_processes[0]
                            child_nodes[1].proc_hash = unproductive_process.hash
                            unproductive_process.reset()
                            unproductive_process.run(
                                self.search_for_valid_female_node,
                                mp_queue,
                                child_nodes[1])
                    elif (bpm.get_lowest_process_level_number() <
                            beam.get_highest_full_level_number()):
                        # Check if the beam is full at a level above
                        # the lowest working process
                        lowest_processes = bpm.get_lowest_level_processes()
                        full_level_f_nodes = beam.get_highest_full_level()
                        for bp in lowest_processes:
                            for f_node in full_level_f_nodes:
                                if bpm.get_process(f_node.proc_hash) is None or \
                                   not bpm.get_process(f_node.proc_hash).is_alive():
                                    f_node.proc_hash = bp.hash
                                    bp.reset()
                                    bp.run(
                                        self.search_for_valid_female_node,
                                        mp_queue,
                                        f_node)
                    else:
                        # Create a new process dedicated to the
                        # solution node's parent
                        f_node_sol_proc.run(
                            self.search_for_valid_female_node,
                            mp_queue,
                            f_node_sol.parent_node)
                        f_node_sol.parent_node.proc = bp
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

        if (print_summary):
            print_search_summary(node.term, self.to, self.grp, end - start)
        else:
            print(node.term)


