from eat.core.components import ValidTermGenerator
from eat.core.utilities import get_all_one_and_two_variable_terms, \
    print_search_summary
import logging
import time


class Node():

    def __init__(self, term, array, parent):
        self.term = term
        self.array = array
        self.parent_node = parent


class BeamEnumerationAlgorithm():

    def __init__(self, groupoid, term_operation, max_male_term_length=None,
                 term_expansion_probability=0.3,
                 male_term_generation_method="random"):
        self.grp = groupoid
        self.to = term_operation
        self.vtg = ValidTermGenerator(self.to.term_variables)
        self.validity_terms = \
            get_all_one_and_two_variable_terms(self.to.term_variables)
        self.male_terms = self.to.term_variables
        self.term_expansion_probability = term_expansion_probability
        self.max_male_term_length = max_male_term_length
        self.male_term_generation_method = male_term_generation_method
        self.logger = logging.getLogger(__name__)

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
                return Node(new_female_term, var_sol, curr_fnode)
        else:
            # we couldn't find a valid female term
            return None

    def continuously_search_for_valid_female_node(self, curr_fnode):
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
                return fnode

    def check_if_has_male_term_solution(self, curr_fnode):
        for mt in self.male_terms:
            male_term_sol = self.to.compute(mt)
            if(self.to.is_solution(male_term_sol, curr_fnode.array)):
                # found a solution
                return Node(mt, male_term_sol, curr_fnode)

    def run(self, verbose=False, print_summary=False,
            include_validity_array=False):
        sol_node = None
        curr_fnode = Node("F", self.to.target, None)
        level = 1

        start = time.time()
        while(True):
            if verbose:
                if include_validity_array:
                    print(str(level), str(curr_fnode.term),
                          str(curr_fnode.array), str(time.time() - start))
                else:
                    print(str(level), str(curr_fnode.term),
                          str(time.time() - start))
            sol_node = self.check_if_has_male_term_solution(curr_fnode)
            if sol_node:
                break
            else:
                fnode = \
                    self.continuously_search_for_valid_female_node(curr_fnode)
                curr_fnode = fnode
            level = level + 1
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


