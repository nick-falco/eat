from eat.core.components import ValidTermGenerator
from eat.core.utilities import get_all_one_and_two_variable_terms, \
    print_search_summary, split_male_term
import queue
import multiprocessing as mp
import logging
import time


class Node():

    def __init__(self, term, array, parent, male_terms):
        self.term = term
        self.array = array
        self.parent_node = parent
        self.male_terms = male_terms

    def check_if_has_male_term_solution(self, to):
        male_terms = self.male_terms + to.term_variables
        for mt in male_terms:
            male_term_sol = to.compute(mt)
            sol = to.is_solution(male_term_sol, self.array)
            if(sol):
                # found a solution
                return Node(mt, male_term_sol, self, self.male_terms)

class BeamEnumerationAlgorithm():

    def __init__(self, groupoid, term_operation, min_male_term_length=2,
                 max_male_term_length=None,
                 term_expansion_probability=0.3,
                 male_term_generation_method="GRA", beam_width=3,
                 beam_timeout=None,
                 number_candidate_terms=300,
                 number_initial_candidate_terms=2500,
                 ignore_valid_term_count=False,
                 sort_candidates_by_fitness=False):
        self.grp = groupoid
        self.to = term_operation
        self.vtg = ValidTermGenerator(self.to.term_variables)
        self.validity_terms = \
            get_all_one_and_two_variable_terms(self.to.term_variables)
        self.min_male_term_length = min_male_term_length
        self.max_male_term_length = max_male_term_length
        self.term_expansion_probability = term_expansion_probability
        self.male_term_generation_method = male_term_generation_method
        self.beam_width = beam_width
        self.beam_timeout = beam_timeout
        self.number_candidate_terms = number_candidate_terms
        self.number_initial_candidate_terms = number_initial_candidate_terms
        self.ignore_valid_term_count = ignore_valid_term_count
        self.sort_candidates_by_fitness = sort_candidates_by_fitness
        self.beam_nodes = []
        try:
            mp.set_start_method('fork', force=True)
        except RuntimeError:
            pass
        except AttributeError:
            logging.warning("Unable to configure how subprocesses are initialized. "
                            "This could cause slower performance on some systems. "
                            "It is recommended that you use python3.")
            pass

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

    def try_to_create_valid_female_node(self, candidate_term, curr_fnode):
        """
        
        """
        direction_order = ["right", "left"]
        for direction in direction_order:
            new_female_term = self.create_female_term(candidate_term,
                                                      direction)
            has_validity_array, validity_array = \
                self.to.compute_validity_array(new_female_term,
                                               curr_fnode.array)
            if has_validity_array:
                candidate_terms = self.generate_candidate_terms(
                    validity_array,
                    self.number_candidate_terms)
                return Node(new_female_term, validity_array, curr_fnode,
                            candidate_terms)
        else:
            # we couldn't find a valid female term
            return None

    def search_for_valid_female_node(self, mp_queue, curr_fnode, curr_height):
        """
        Continuously searches for a valid female node
        """
        # if no validity terms produce valid female term, we continue
        # to try random terms
        nct = self.number_initial_candidate_terms if curr_height == 0 \
            else self.number_candidate_terms
        candidate_terms = self.generate_candidate_terms(
            curr_fnode.array,
            nct)
        for ct in candidate_terms:
            ct_parts = split_male_term(ct)
            for ctp in ct_parts:
                fnode = self.try_to_create_valid_female_node(ctp,
                                                             curr_fnode)
                if (fnode and fnode.term not in
                        [fnode.term for fnode in self.beam_nodes[-1]]):
                    
                    mp_queue.put_nowait(fnode)
                    continue

    def generate_candidate_terms(self, target_array, num_candidates):
        candidate_terms = self.vtg.generate_list(num_candidates,
            algorithm=self.male_term_generation_method,
            min_term_length=self.min_male_term_length,
            max_term_length=self.max_male_term_length,
            prob=self.term_expansion_probability)
        if self.sort_candidates_by_fitness:
            candidate_terms = sorted(
                candidate_terms,
                key=(lambda mterm:
                    self.to.calculate_term_fitness(mterm, target_array)),
                reverse=True
            )
        return candidate_terms
        

    def run(self, verbose=False, print_summary=False,
            include_validity_array=False):
        sol_node = None
        height = 0
        # initialize beam at height 0
        f_node = Node("F", self.to.target, None,
                      self.generate_candidate_terms(
                          self.to.target, self.number_candidate_terms))
        self.beam_nodes = [[f_node for _ in range(0, self.beam_width)]]

        start = time.time()
        while(True):
            mp_queue = mp.Queue()
            if verbose:
                if include_validity_array:
                    print(str(height),
                          [(fnode.term, fnode.array)
                           for fnode in self.beam_nodes[height]],
                          str(time.time() - start))
                else:
                    print(str(height),
                          [(fnode.term)
                           for fnode in self.beam_nodes[height]],
                          str(time.time() - start))
            
            for f_node in self.beam_nodes[height]:
                sol_node = f_node.check_if_has_male_term_solution(self.to)
                if sol_node:
                    break
            else:
                # add a height to the beam (height+1)
                self.beam_nodes.append([])
                procs = []
                for f_node in self.beam_nodes[height]:
                    # start a process for each of the nodes at the current
                    # beam height
                    proc = mp.Process(
                        target=
                        self.search_for_valid_female_node,
                        args=(mp_queue, f_node, height))
                    proc.start()
                    procs.append(proc)
                start_beam_search = time.time()
                alive = True
                while len(self.beam_nodes[height+1]) < self.beam_width:
                    if (self.beam_timeout and self.beam_nodes[height+1] and 
                        (time.time() - start_beam_search) >=
                         self.beam_timeout):
                        # lets give up and try to keep moving up the beam
                        break
                    try:
                        f_node_sol = mp_queue.get_nowait()
                        if f_node_sol:
                            if f_node_sol.term not in \
                                    [t.term for t in self.beam_nodes[height+1]]:
                                self.beam_nodes[height+1].append(f_node_sol)
                            if len(self.beam_nodes[height+1]) < self.beam_width:
                                proc = mp.Process(
                                    target=
                                    self.search_for_valid_female_node, #noqa
                                    args=(mp_queue, f_node_sol.parent_node,
                                          height))
                                proc.start()
                                procs.append(proc)
                    except queue.Empty:
                        pass
                    # break if no more processes are running
                    alive = False
                    for proc in procs:
                        if proc.is_alive():
                            alive = True
                            break
                    else:
                        # no more processes are running
                        break
                    if alive is False:
                        break
                # kill any remaining processes
                for proc in procs:
                    proc.terminate()
                next_beam_level = [t.term for t in self.beam_nodes[height+1]]
                if (len(next_beam_level) == 0 or
                    (len(next_beam_level) < self.beam_width and
                     self.ignore_valid_term_count is False)):
                    print("------ Solution Not Found! ------")
                    print("Unable to find valid female terms at height {}"
                          .format(height))
                    print("Beam at height {} = {}"
                           .format(height+1, next_beam_level))
                    print("Insuffient valid female terms were found for "
                            "beam height {}. Found {} valid female terms "
                            "but required a beam width of {} to advance to "
                            "height {}."
                            .format(height+1, len(next_beam_level),
                                    self.beam_width, height+1))
                    print("---------------------------------")
                    return
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


