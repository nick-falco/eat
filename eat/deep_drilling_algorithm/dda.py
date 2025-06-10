from eat.core.components import ValidTermGenerator
from eat.core.utilities import combine_postfix, get_logger, log_search_summary
from random import choice, shuffle
import time


LOG = get_logger('dda_logger')


class Node():

    def __init__(self, term, array, parent, term_operation,
                 left_child=None, right_child=None, label=None):
        self.term = term
        self.to = term_operation
        self.array = array
        self.parent_node = parent
        self.left_child = left_child
        self.right_child = right_child
        self.label = label


class DeepDrillingAlgorithm():

    def __init__(self, groupoid, term_operation, m=1):
        self.grp = groupoid
        self.to = term_operation
        self.vtg = ValidTermGenerator(self.to.term_variables)
        self._test_terms = self.generate_test_terms(m=m)

    @property
    def test_terms(self):
        shuffled_list = self._test_terms[:]
        shuffle(shuffled_list)
        return shuffled_list

    def generate_test_terms(self, m=4):
        """
        Generate the test terms.
        """
        def generate_up_to_height(test_terms, m=4):
            m = m - 1
            if m > 0:
                new_terms = []
                for a in test_terms:
                    for b in test_terms:
                        new_term = a + b + '*'
                        new_terms.append(new_term)
                return generate_up_to_height(test_terms + new_terms, m)
            else:
                return list(set(test_terms))

        test_terms = generate_up_to_height(self.to.term_variables, m)
        return test_terms

    def get_solution_term(self, curr_node):
        """
        Check if the current node has a solution.

        Returns:
            Term: The solution term if a solution is found, else None
        """
        for term in self.test_terms:
            term_sol = self.to.compute(term)
            if (self.to.is_solution(term_sol, curr_node.array)):
                return term
        return None

    def determine_branching_direction(self, node):
        """
        Determine the direction to take when branching.
        """
        direction = None
        if not node.left_child and not node.right_child:
            direction = choice(["L", "R"])
        elif not node.left_child:
            direction = "L"
        elif not node.right_child:
            direction = "R"
        return direction

    def get_l_or_r(self, node, verbose=False):
        """
        Randomly take the left (L) or right (R) branch.

        Returns:
            Node: The next node to explore, L or R
        """
        direction = self.determine_branching_direction(node)
        if not direction:
            return
        elif direction == "L":
            if node.right_child:
                female_term = "F" + node.right_child.term + "*"
                is_valid, new_array = self.to.compute_validity_array(
                    female_term, node.array)
                new_label = "{}({})".format(
                    direction, node.right_child.label)
                if not is_valid:
                    raise ValueError("Validity array is not valid")
            else:
                new_array = self.to.l_array(node.array)
                new_label = "{}{}".format(direction, node.label)
        elif direction == "R":
            if node.left_child:
                female_term = node.left_child.term + "F*"
                is_valid, new_array = self.to.compute_validity_array(
                    female_term, node.array)
                new_label = "{}({})".format(
                    direction, node.left_child.label)
                if not is_valid:
                    raise ValueError("Validity array is not valid")
            else:
                new_array = self.to.r_array(node.array)
                new_label = "{}{}".format(direction, node.label)
        if verbose:
            LOG.info("Current Node: {}, Next Node: {}".format(
                node.label, new_label))
        # create a new node and attach it to the parent node
        new_node = Node("", new_array, node, self.to, label=new_label)
        if direction == "L":
            node.left_child = new_node
        elif direction == "R":
            node.right_child = new_node
        return new_node

    def build_term_tree(self, node, verbose=False):
        """
        Add a child node to the parent node.

        Args:
            node (Node): The starting node
            direction (str): The direction to take, left or right
        """
        # Check if any of the test terms are a solution, if so return the term
        solution_term = self.get_solution_term(node)
        if solution_term:
            node.term = solution_term
            if verbose:
                LOG.info("Found {} as a solution to {}".format(
                    solution_term, node.label))
            return node

        # Start exploring the tree
        current_node = node
        while True:
            # Get the next node to explore
            child_node = self.get_l_or_r(current_node, verbose=verbose)
            if not child_node:
                # No new node to explore. Backtrack to the parent node,
                # or return the root node.
                current_node.term = combine_postfix(
                    current_node.left_child.term,
                    current_node.right_child.term)
                current_node.array = self.to.compute(current_node.term)
                if current_node.parent_node:
                    current_node = current_node.parent_node
                else:
                    # We're at the root, return the root node
                    return current_node
            else:
                # We have a new node to explore
                solution_term = self.get_solution_term(child_node)
                if solution_term:
                    # If a solution is found, set the term and continue
                    child_node.term = solution_term
                    child_node.array = self.to.compute(solution_term)
                    if verbose:
                        LOG.info("Found {} as a solution to {}".format(
                            child_node.term, child_node.label))
                        LOG.info("Term array = {}".format(child_node.array))
                else:
                    # Otherwise continue to search in a random direction
                    # higher up the tree
                    current_node = child_node

    def run(self, verbose=False, print_summary=False):
        """
        Run the deep drilling algorithm.
        """
        start = time.perf_counter()
        if verbose:
            LOG.info("Current Node: Root (T)")
        root_node = Node("", self.to.target, None, self.to, label="T")
        sol_node = self.build_term_tree(root_node, verbose=verbose)
        end = time.perf_counter()
        if (print_summary or verbose):
            log_search_summary(sol_node, None, self.to, self.grp, start, end,
                               LOG, show_creation_history=False)
        else:
            if verbose:
                LOG.info(sol_node.term)
        return sol_node, end - start
