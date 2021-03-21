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
    
    def add_level(self, nodes_list):
        self.levels.append(nodes_list)

    def add_to_level(self, level, node):
        self.levels[level].append(node)

    def get_level(self, level):
        return self.levels[level]
    
    def get_level_size(self, level):
        return len(self.get_level(level))

    def get_height(self):
        return len(self.levels)

    def get_highest_full_level(self):
        for idx, level in enumerate(reversed(self.levels)):
            if len(level) == self.width:
                return self.get_height() - idx - 1

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

    def set_process(self, proc_hash, proc):
        self.proc_map[proc_hash] = proc

    def get_process(self, proc_hash):
        return self.proc_map[proc_hash]

    def get_processes(self):
        return self.proc_map.values()

    def get_processes_to_promote(self):
        return [proc for proc in self.get_processes()
                if len(proc.child_nodes) == 2]

    def get_processes_without_children(self):
        return [proc for proc in self.get_processes()
                if not proc.child_nodes]

    def get_lowest_level_processes(self):
        min_hight = self.get_lowest_process_level()
        return [proc for proc in self.get_processes()
                if proc.height == min_hight]

    def get_lowest_process_level(self):
        return min(self.get_processes(), key=attrgetter('height')).height

    def terminate_all(self):
        for proc in self.get_processes():
            proc.terminate()

class BeamProcess():

    def __init__(self):
        self.proc = None
        self.hash = uuid.uuid4()
        self.child_nodes = []
        self.height = None
    
    def run(self, target, queue, beam_hash, node):
        self.height = node.height
        self.proc = mp.Process(target=target,
                               args=(queue, beam_hash, node))
        self.proc.start()

    def terminate(self):
        self.proc.terminate()

    def restart(self):
       self.hash = uuid.uuid4()
       self.child_nodes = []


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

    def search_for_valid_female_node(self, mp_queue, proc_hash, curr_fnode):
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
                fnode.proc_hash = proc_hash
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
        while(True):
            mp_queue = mp.Queue()
            if verbose:
                if include_validity_array:
                    print(str(height),
                          [(fnode.term, fnode.array)
                           for fnode in beam.get_level(height)],
                          str(time.time() - start))
                else:
                    print(str(height),
                          [(fnode.term)
                           for fnode in beam.get_level(height)],
                          str(time.time() - start))
            
            for f_node in beam.get_level(height):
                sol_node = self.check_if_has_male_term_solution(f_node)
                if sol_node:
                    break
            else:
                beam.add_level([]) # add a height to the beam (height+1)
                bpm = BeamProcessManager()
                for f_node in beam.get_level(height):
                    # start a process for each of the nodes at the current
                    # beam height
                    bp = BeamProcess()
                    f_node.proc_hash = bp.hash
                    bp.run(self.search_for_valid_female_node,
                           mp_queue,
                           bp.hash,
                           f_node)
                    bpm.set_process(bp.hash, bp)
                start_beam_search = time.time()
                while beam.get_level_size(height+1) < self.beam_width:
                    if (self.beam_timeout and beam.get_level(height+1) and 
                        (time.time() - start_beam_search) >=
                         self.beam_timeout):
                        # lets give up and try to keep moving up the beam
                        break
                    try:
                        f_node_sol = mp_queue.get_nowait()
                        if f_node_sol:
                            if f_node_sol.term not in \
                                    [t.term for t in beam.get_level(height+1)]:
                                beam.add_to_level(height+1, f_node_sol)
                                bp = bpm.get_process(
                                    f_node_sol.parent_node.proc_hash)
                                bp.child_nodes.append(f_node_sol)
                            procs_to_promote = bpm.get_processes_to_promote()
                            if procs_to_promote:
                                # Terminate productive solution nodes parent
                                # process and dedicate to a node a level H+1
                                promote_proc = procs_to_promote[0]
                                promote_proc.terminate()
                                child_nodes = promote_proc.child_nodes
                                promote_proc.restart()
                                child_nodes[0].proc_hash = promote_proc.hash
                                promote_proc.run(
                                    self.search_for_valid_female_node,
                                    mp_queue,
                                    promote_proc.hash,
                                    child_nodes[0])
                                # Terminate an unproductive process and 
                                # dedicate to a node at level H+1 
                                slow_process = \
                                    bpm.get_processes_without_children()[0]
                                slow_process.terminate()
                                slow_process.restart()
                                child_nodes[1].proc_hash = slow_process.hash
                                slow_process.run(
                                    self.search_for_valid_female_node,
                                    mp_queue,
                                    slow_process.hash,
                                    child_nodes[1])
                                bpm.set_process(slow_process.hash,
                                                slow_process)
                            else:
                                # Create a new process dedicated to the
                                # solution node's parent
                                if (beam.get_level_size(height+1) <
                                        self.beam_width):
                                    bp = bpm.get_process(
                                        f_node_sol.parent_node.proc_hash)
                                    bp.run(
                                        self.search_for_valid_female_node,
                                        mp_queue,
                                        bp.hash,
                                        f_node_sol.parent_node)
                                    f_node_sol.parent_node.proc = bp
                    except queue.Empty:
                        pass
                # kill any remaining processes
                bpm.terminate_all()
            mp_queue.close()
            if sol_node:
                break
            height = height + 1
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


