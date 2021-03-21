from eat.core.components import ValidTermGenerator
from eat.core.utilities import get_all_one_and_two_variable_terms, \
    print_search_summary
import queue
import multiprocessing as mp
import logging
import time
import uuid


class Node():

    def __init__(self, term, array, parent, height):
        self.term = term
        self.array = array
        self.parent_node = parent
        self.height = height
        self.proc_hash = None


class BeamProccess():

    def __init__(self):
        self.proc = None
        self.hash = uuid.uuid4()
        self.child_nodes = []
    
    def run(self, target, args=None):
        if args is None:
            args = ()
        self.proc = mp.Process(target=target, args=args)
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
        beam_nodes = [[f_node for _ in range(0, self.beam_width)]]

        start = time.time()
        while(True):
            mp_queue = mp.Queue()
            if verbose:
                if include_validity_array:
                    print(str(height),
                          [(fnode.term, fnode.array)
                           for fnode in beam_nodes[height]],
                          str(time.time() - start))
                else:
                    print(str(height),
                          [(fnode.term)
                           for fnode in beam_nodes[height]],
                          str(time.time() - start))
            
            for f_node in beam_nodes[height]:
                sol_node = self.check_if_has_male_term_solution(f_node)
                if sol_node:
                    break
            else:
                beam_nodes.append([]) # add a height to the beam (height+1)
                proc_map = {}
                for f_node in beam_nodes[height]:
                    # start a process for each of the nodes at the current
                    # beam height
                    bp = BeamProccess()
                    f_node.proc_hash = bp.hash
                    bp.run(target=self.search_for_valid_female_node,
                           args=(mp_queue,
                                 bp.hash,
                                 f_node))
                    proc_map[bp.hash] = bp
                start_beam_search = time.time()
                while len(beam_nodes[height+1]) < self.beam_width:
                    if (self.beam_timeout and beam_nodes[height+1] and 
                        (time.time() - start_beam_search) >=
                         self.beam_timeout):
                        # lets give up and try to keep moving up the beam
                        break
                    try:
                        f_node_sol = mp_queue.get_nowait()
                        if f_node_sol:
                            if f_node_sol.term not in \
                                    [t.term for t in beam_nodes[height+1]]:
                                beam_nodes[height+1].append(f_node_sol)
                                bp = proc_map[f_node_sol.parent_node.proc_hash]
                                bp.child_nodes.append(f_node_sol)
                            procs_to_promote = \
                                [proc for proc in proc_map.values()
                                 if len(proc.child_nodes) == 2]
                            if procs_to_promote:
                                # Terminate productive solution nodes parent
                                # process and dedicate to a node a level H+1
                                promote_proc = procs_to_promote[0]
                                print("PROMOTE = %s" % promote_proc.hash)
                                promote_proc.terminate()
                                child_nodes = promote_proc.child_nodes
                                promote_proc.restart()
                                child_nodes[0].proc_hash = promote_proc.hash
                                promote_proc.run(
                                    target=
                                    self.search_for_valid_female_node,
                                    args=(mp_queue,
                                          promote_proc.hash,
                                          child_nodes[0]))
                                # Terminate an unproductive process and 
                                # dedicate to a node at level H+1 
                                slow_process = \
                                    [proc for proc in proc_map.values() 
                                     if not proc.child_nodes][0]
                                slow_process.terminate()
                                slow_process.restart()
                                child_nodes[1].proc_hash = slow_process.hash
                                slow_process.run(
                                    target=
                                    self.search_for_valid_female_node,
                                    args=(mp_queue,
                                          slow_process.hash,
                                          child_nodes[1]))
                                proc_map[slow_process.hash] = slow_process
                            else:
                                # Create a new process dedicated to the
                                # solution node's parent
                                if len(beam_nodes[height+1]) < self.beam_width:
                                    bp = proc_map[
                                        f_node_sol.parent_node.proc_hash]
                                    bp.run(
                                        target=
                                        self.search_for_valid_female_node,
                                        args=(mp_queue,
                                              bp.hash,
                                              f_node_sol.parent_node))
                                    f_node_sol.parent_node.proc = bp
                    except queue.Empty:
                        pass
                # kill any remaining processes
                for proc in proc_map.values():
                    proc.terminate()
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


