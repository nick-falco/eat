from eat.core.components import ValidTermGenerator
from eat.core.utilities import get_all_one_and_two_variable_terms
import logging


class Node():

    def __init__(self, term, array, parent):
        self.term = term
        self.array = array
        self.parent_node = parent


class BeamEnumerationAlgorithm():

    def __init__(self, groupoid, term_operation,
                 term_expansion_probability=0.3):
        self.grp = groupoid
        self.to = term_operation
        self.vtg = ValidTermGenerator(self.to.term_variables)
        self.validity_terms = \
            get_all_one_and_two_variable_terms(self.to.term_variables)
        self.male_terms = self.to.term_variables
        self.term_expansion_probability = term_expansion_probability
        self.logger = logging.getLogger(__name__)

    def create_female_term(self, male_term, direction):
        """
        Given a male term and a direction (left or right) returns a new female
        term string
        """
        female_term = ""
        if direction == "left":
            female_term = "F{}".format(male_term)
        elif direction == "right":
            female_term = "{}F".format(male_term)
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
            random_term = self.vtg.generate(
                prob=self.term_expansion_probability)
            fnode = self.try_to_create_valid_female_node(random_term,
                                                         curr_fnode)
            if fnode:
                return fnode

    def check_if_has_male_term_solution(self, curr_fnode):
        for mt in self.male_terms:
            male_term = curr_fnode.term.replace("F", mt)
            male_term_sol = self.to.compute(mt)
            if(self.to.is_solution(male_term_sol, curr_fnode.array)):
                # found a solution
                return Node(male_term, male_term_sol, curr_fnode)

    def run(self):
        sol_node = None
        curr_fnode = Node("F", self.to.target, None)
        level = 1
        print("Printing (Recursion level, valid female term, validity array)")
        while(True):
            print(level, curr_fnode.term, curr_fnode.array)
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
                node.parent_node.term.replace("F", "{}*".format(node.term))
            node = node.parent_node
        print("Final solution term  = {}".format(node.term))
        print("Soution term array   = {}"
              .format(self.to.compute(node.term)))
        print("Target array         = {}".format(self.to.target))


