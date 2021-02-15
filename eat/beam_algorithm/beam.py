from eat.core.components import ValidTermGenerator
from eat.core.utilities import get_all_one_and_two_variable_terms
from random import choice
import logging


class FemaleNode():

    def __init__(self, term, array, parent):
        self.term = term
        self.array = array
        self.parent_node = parent


class Beam():

    def __init__(self):
        self.table = []


class BeamEnumerationAlgorithm():

    def __init__(self, groupoid, term_operation):
        self.grp = groupoid
        self.to = term_operation
        self.vtg = ValidTermGenerator(self.to.term_variables)
        self.validity_terms = \
            get_all_one_and_two_variable_terms(self.to.term_variables)
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
        direction_order = choice([["left", "right"],
                                  ["right", "left"]])
        for direction in direction_order:
            new_female_term = self.create_female_term(male_term,
                                                      direction)
            has_var_sol, var_sol = \
                self.to.compute_variable_solution(new_female_term,
                                                  curr_fnode.array)
            if has_var_sol:
                return FemaleNode(new_female_term, var_sol, curr_fnode)
        else:
            # we couldn't find a valid female term
            return None

    def continuously_search_for_valid_female_node(self, curr_fnode):
        """
        Continuously searches for a valid female node
        """
        # first we check for new valid female terms using the standard
        # set of validity terms
        for validity_term in self.validity_terms:
            fnode = self.try_to_create_valid_female_node(validity_term,
                                                         curr_fnode)
            if fnode:
                return fnode
        # if no validity terms produce valid female term, we continue
        # to try random terms
        while(True):
            random_term = self.vtg.generate(prob=0.3)
            fnode = self.try_to_create_valid_female_node(random_term,
                                                         curr_fnode)
            if fnode:
                return fnode

    def check_if_has_validity_solution(self, curr_fnode):
        for mt in self.validity_terms:
            male_term = curr_fnode.term.replace("F", mt)
            male_term_sol = self.to.compute(mt)
            if(self.to.is_solution(male_term_sol, curr_fnode.array)):
                # found a solution
                return male_term

    def run(self):
        solution = None
        curr_fnode = FemaleNode("F", self.to.target, None)
        while(True):
            print(curr_fnode)
            solution = self.check_if_has_validity_solution(curr_fnode)
            if solution:
                break
            else:
                fnode = \
                    self.continuously_search_for_valid_female_node(curr_fnode)
                curr_fnode = fnode
        print("Found solution {}".format(solution))
