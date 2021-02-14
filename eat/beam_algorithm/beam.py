from eat.core.components import ValidTermGenerator
from eat.core.utilities import get_all_one_and_two_variable_terms
from random import choice
import logging


class BeamRow():

    def __init__(self, term, array):
        self.term = term
        self.array = array


class Beam():

    def __init__(self):
        self.table = []


class BeamEnumerationAlgorithm():

    def __init__(self, groupoid, term_operation):
        self.grp = groupoid
        self.to = term_operation
        self.vtg = ValidTermGenerator(self.to.term_variables)
        self.logger = logging.getLogger(__name__)

    def run(self):
        beam = Beam()
        beam.table.append(BeamRow("F", self.to.target))

        male_terms = self.to.term_variables
        validity_terms = \
            get_all_one_and_two_variable_terms(self.to.term_variables)

        solution = None
        while(True):
            last_row = beam.table[-1]
            female_term = last_row.term
            print("STEP 1")
            print("female_term = %s" % female_term)
            for mt in validity_terms:
                male_term = female_term.replace("F", mt)
                male_term_sol = self.to.compute(mt)
                if(self.to.is_solution(male_term_sol, last_row.array)):
                    # found a solution
                    print("FOUND A SOLUTION!!!!!!!!!!!!!!!!!")
                    solution = male_term
                    print(solution)
                    return
                    break
            else:
                print("STEP 2")
                has_var_sol = False
                var_sol = []
                new_female_term = ""

                # randomly choose to go right or left first
                direction_order = choice([["left", "right"],
                                          ["right", "left"]])
                for direction in direction_order:
                    print(direction)
                    # we need to check for new valid female terms with respect
                    # to the last female term
                    for validity_term in validity_terms:
                        # first check left then check right
                        test_term = ""
                        if direction == "left":
                            test_term = "F{}".format(validity_term)
                        elif direction == "right":
                            test_term = "{}F".format(validity_term)
                        has_var_sol, var_sol = \
                            self.to.compute_variable_solution(test_term,
                                                              last_row.array)
                        if has_var_sol:
                            if direction == "left":
                                new_female_term = female_term.replace(
                                    "F", "{}*".format(test_term))
                            elif direction == "right":
                                new_female_term = female_term.replace(
                                    "F", "{}*".format(test_term))
                else:
                    print("STEP 2 B")
                    # try a random term
                    while(True):
                        direction_order = choice([["left", "right"],
                                                  ["right", "left"]])
                        random_term = self.vtg.generate(prob=0.3)
                        for direction in direction_order:
                            test_term = ""
                            if direction == "left":
                                test_term = "F{}".format(random_term)
                            elif direction == "right":
                                test_term = "{}F".format(random_term)
                            has_var_sol, var_sol = \
                                self.to.compute_variable_solution(
                                    test_term, last_row.array)
                            if has_var_sol:
                                if direction == "left":
                                    new_female_term = female_term.replace(
                                        "F", "{}*".format(test_term))
                                elif direction == "right":
                                    new_female_term = female_term.replace(
                                        "F", "{}*".format(test_term))
                                break
                        if has_var_sol:
                            break
                print("var_sol = %s" % var_sol)
                new_beam = BeamRow(new_female_term, var_sol)
                beam.table.append(new_beam)
                    
            if (solution):
                print("solution = %s" % solution)
                break
        print("Found solution {}".format(solution))
