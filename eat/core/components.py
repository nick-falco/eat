import itertools
import math
from random import choice, uniform
from collections import OrderedDict, deque
from eat.core.utilities import subset_sums, get_term_variables


class Groupoid():

    def __init__(self, data=None):
        """
        Construtor for a groupoid. If data is not supplied, a randomly
        filled 3 element groupoid is created.
        """
        if data:
            self.size = self.get_groupoid_size(data)
            self.data = self.list_to_groupoid_data(data)
        else:
            self.data = self.get_random_primal_groupoid_data(size=3)
            self.size = self.get_groupoid_size(
                self.groupoid_data_to_list(self.data))

    def __str__(self):
        return "\n".join([" ".join(
                         [str(cell) for cell in row])
                         for row in self.data])

    def set_value(self, x, y, value):
        """
        Set groupoid value at index (x, y)

        :type x: int
        :param x: groupoid x index
        :type y: int
        :param y: groupoid y index
        :type value: int
        :param value: value of groupoid at index (x, y)
        """
        self.data[x][y] = value

    def get_value(self, x, y):
        """
        Get groupoid value at index (x, y)

        :type x: int
        :param x: groupoid x index
        :type y: int
        :param y: groupoid y index

        :rtype: int
        :return: value of groupoid at index (x, y)
        """
        return self.data[x][y]

    def get_groupoid_size(self, data):
        size = int(math.sqrt(len(data)))
        if int(size + 0.5) ** 2 != len(data):
            raise ValueError("Groupoid data must be a perfect square.")
        return size

    def groupoid_data_to_list(self, groupoid_data):
        """
        Converts groupoid data to a flat list

        [[0,0,0],[0,0,0],[0,0,0]] -> [0,0,0,0,0,0,0,0,0]

        :type groupoid_data: list
        :param groupoid_data: groupoid data as a list of lists

        :rtype: list
        :return: groupoid values flattened to a single list
        """
        return [cell for row in groupoid_data for cell in row]

    def list_to_groupoid_data(self, groupoid_values, size=None):
        """
        Converts flat list to groupoid data

        [0,0,0,0,0,0,0,0,0] -> [[0,0,0],[0,0,0],[0,0,0]]

        :type groupoid_values: list
        :param groupoid_values: flat list of groupoid values
        :type size: int
        :param size: number of groupoid cells per row

        :rtype: list
        :return: groupoid data as a list of lists
        """
        if size is None:
            size = self.size
        return [groupoid_values[i:i+size]
                for i in range(0, len(groupoid_values), size)]

    def get_random_groupoid_data(self, size=None):
        """
        Generate randomly filled groupoid data

        :type size: int
        :param size: number of groupoid cells per row

        :rtype: list
        :return: groupoid data as a list of lists
        """
        if size is None:
            size = self.size

        assigned_indexes = []  # keep track of assigned indexes
        groupoid_cell_count = pow(size, 2)
        groupoid_values = [None] * groupoid_cell_count

        for _ in range(0, size**2):
            # choose a random input value
            possible_inputs = [i for i in range(0, size)]
            input_value = choice(possible_inputs)
            # choose random groupoid cell [0, groupoid_cell_count-1]
            cell = choice([i for i in range(0, groupoid_cell_count)
                           if i not in assigned_indexes])
            assigned_indexes.append(cell)
            # assign random input value to a random groupoid cell
            groupoid_values[cell] = input_value
        return self.list_to_groupoid_data(groupoid_values, size)

    def get_random_primal_groupoid_data(self, size=None):
        """
        Generate randomly filled primal groupoid data

        :type size: int
        :param size: number of groupoid cells per row

        :rtype: list
        :return: groupoid data as a list of lists
        """
        if size is None:
            size = self.size

        groupoid_cell_count = pow(size, 2)
        groupoid_values = [None] * groupoid_cell_count

        # find subset sum resulting in the total number of groupoid cells
        subset_sum = choice(subset_sums(range(1, groupoid_cell_count-1),
                                        groupoid_cell_count,
                                        size))

        assigned_indexes = []  # keep track of assigned indexes
        assigned_inputs = []  # keep track of assigned input values
        index_by_input = {}  # keep track of indexes for a given input
        for num_inputs in subset_sum:
            # choose a random input value
            possible_inputs = [i for i in range(0, size)
                               if i not in assigned_inputs]
            input_value = choice(possible_inputs)
            assigned_inputs.append(input_value)
            index_by_input[input_value] = []
            # for each subset sum value, assign input value to randomly
            # selected groupoid cells
            for _ in range(0, num_inputs):
                # choose random groupoid cell [0, groupoid_cell_count-1]
                cell = choice([i for i in range(0, groupoid_cell_count)
                               if i not in assigned_indexes])
                assigned_indexes.append(cell)
                index_by_input[input_value].append(cell)
                # assign random input value to a random groupoid cell
                groupoid_values[cell] = input_value

        # swap diagional values if they match inputs
        curr_diag_idx = 0
        input_value = 0
        step = size
        while curr_diag_idx < len(groupoid_values):
            curr_diagonal = groupoid_values[curr_diag_idx]
            if curr_diagonal == input_value:
                # swap diagonal with another value
                if input_value < size-1:
                    # swap with larger input value
                    swap_index = index_by_input[input_value+1][0]
                else:
                    # swap with smaller input value
                    swap_index = index_by_input[input_value-1][0]
                # swap the diagonal with a different value
                groupoid_values[curr_diag_idx], groupoid_values[swap_index] = \
                    groupoid_values[swap_index], groupoid_values[curr_diag_idx]
            input_value += 1
            curr_diag_idx += step + 1
        return self.list_to_groupoid_data(groupoid_values, size)


class TermOperation():

    def __init__(self, groupoid, target=None,
                 term_variables=None):
        """
        :type groupoid: :class: Groupoid
        :param groupoid: groupoid to apply term operation on
        :type target: list
        :param target: the target array to find a term solution for. If a
          target is not specified, a random target will be used.
        :type term_variables: list
        :param term_variables: list of possible variables in a term. If
          term variables are not specified, they will be created to match
          the size of the groupoid.
        """
        self.groupoid = groupoid
        if term_variables:
            self.term_variables = term_variables
        else:
            self.term_variables = get_term_variables(self.groupoid.size)
        self.input = self.get_input_array(size=len(self.term_variables))
        self.mapped_input = self.get_mapped_input_array(
            size=len(self.term_variables))
        if target:
            self.target = target
        else:
            self.target = self.get_random_target_array()

    def __str__(self):
        value = []
        value.append("{} |  ".format(" ".join(self.term_variables)))
        value.append("-" * (2 * len(self.term_variables) + 4))
        for idx in range(0, len(self.input)):
            value.append("{} | {}".format(
                " ".join([str(i) for i in self.input[idx]]),
                " ".join([str(o) for o in self.target[idx]]))
            )
        return "\n".join(value)

    def get_mapped_input(self, input_row):
        """
        Given a input tuple return its variable mapping
        """
        return self.mapped_input[hash(input_row)]

    def get_mapped_input_array(self, size=None):
        """
        Returns a dictionary where the key is the has of the input tuple
        and the value is the variabled mapping dictionary for that input tuple.

        e.g. {<hash>(0,0,0): {"x": 0, "y": 0, "z": 0},
              <hash>(0,0,1): {"x": 0, "y": 0, "z": 1},
              <hash>(0,0,2): {"x": 0, "y": 0, "z": 2},
              <hash>(0,1,0): {"x": 0, "y": 1, "z": 0},
              etc.}
        """
        if size is None:
            size = self.groupoid.size
        input_array = self.get_input_array(size)
        mapped_input = OrderedDict()
        for input_row in input_array:
            mapped_input[hash(input_row)] = \
                self.get_term_variable_mapping(input_row)
        return mapped_input

    def get_input_array(self, size=None):
        """
        Returns a list of inputs to the term operation. Each input is a tuple
        of input values for each term variable.

        e.g. [(0,0,0), (0,0,1), (0,0,2), (0,1,0), (0,1,1) ... etc.]

        :type size: int
        :param size: number of possible term elements

        :rtype: list
        :return: list of term operation inputs
        """
        if size is None:
            size = self.groupoid.size
        return [tuple(p) for p in itertools.product(
                range(self.groupoid.size),
                repeat=size)]

    def get_random_target_array(self):
        """
        Returns a random list of outputs to the term operation. Each list
        element is a one element list.

        e.g. [[0], [2], [1], [0], [1] ... etc.]

        :type size: int
        :param size: number of possible term elements

        :rtype: list
        :return: list of random term operation outputs
        """
        return [[choice(range(0, self.groupoid.size))]
                for _ in range(0, pow(self.groupoid.size,
                                      len(self.term_variables)))]

    def get_ternary_descriminator_target_array(self):
        """
        Returns target solution, representing the ternary
        descriminator:

        d(a, b, c) := {c if a == b; a if a != b}
        """
        if len(self.term_variables) > 3:
            raise ValueError("Ternary descriminator output only applies to "
                             "term operations with 3 term variables")
        target_array = []
        for row in self.input:
            a = row[0]
            b = row[1]
            c = row[2]
            if a == b:
                target_array.append([c])
            else:
                target_array.append([a])
        return target_array

    def get_filled_target_array(self, target, target_free_count):
        """
        Returns a target solution with output values filled to accept any
        possible input value (specified by target_free_count). This is designed
        to make it possible to specify easier targets for groupoids with very
        large search spaces.
        """
        if target_free_count > len(target):
            raise ValueError("Specified a target free count ({}) greater than "
                             "the length of the target array ({})."
                             .format(target_free_count, len(target)))
        for idx, _ in enumerate(target):
            if idx < target_free_count:
                target[idx] = list(range(0, self.groupoid.size))
        return target

    def get_term_variable_mapping(self, input_row, term_variables=None):
        """
        Returns a mapping of input values to term variables

        e.g. for input_row=[0, 1, 2] and term_variables=[a,b,c]
             returns {"a": 0, "b": 1, "c": 2}

        :type input_row: list
        :param input_row: list of input values
        :type term_variables: list
        :param term_variables: list of term elements

        :rtype: dict
        :return: dictionary mapping term variable to input value
        """
        variable_mapping = {}
        for idx, var in enumerate(self.term_variables):
            variable_mapping[var] = input_row[idx]
        return variable_mapping

    def l_array(self, term_output):
        """
        Returns an array containing the rows indexes of the groupoid that
        contain a value matching the target output at a given index.

        LA(x, y, z) = {d E G | d * g E A(x, y, z) forsome g E G}:

        e.g.

         * 0 1 2
         0 2 1 2
         1 1 0 0
         2 0 0 1

         l_array([[0], [1], [0], [2]])
         >>> [[1, 2], [0, 1, 2], [1, 2], [0]]

         Because
         [0] is found at gropuoid rows [1] and [2]
         [1] is found at groupoid rows [0], [1] and [2]
         [2] is found at groupoid rows [0]
        """
        l_array = [[] for _ in range(0, len(term_output))]
        for row_idx, term_row in enumerate(term_output):
            for grp_row in range(0, self.groupoid.size):
                for grp_col in range(0, self.groupoid.size):
                    if self.groupoid.get_value(grp_row, grp_col) in term_row:
                        l_array[row_idx].append(grp_row)
                        break  # continue to check next row of groupoid
        return l_array

    def r_array(self, term_output):
        """
        Returns an array containing the column indexes of the groupoid that
        contain a value matching the target output at a given index.

        RA(x, y, z) = {d E G | g * d E A(x, y, z) forsome g E G}:

        e.g.

         * 0 1 2
         0 2 1 2
         1 1 0 0
         2 0 0 1

         l_array([[0], [1], [0], [2]])
         >>> [[0, 1, 2], [0, 1, 2], [0, 1, 2], [0, 2]]

         Because
         [0] is found at gropuoid rows [0], [1] and [2]
         [1] is found at groupoid rows [0], [1] and [2]
         [2] is found at groupoid rows [0] and [2]
        """
        r_array = [[] for _ in range(0, len(term_output))]
        for row_idx, term_row in enumerate(term_output):
            for grp_row in range(0, self.groupoid.size):
                for grp_col in range(0, self.groupoid.size):
                    if self.groupoid.get_value(grp_row, grp_col) in term_row:
                        if grp_col not in r_array[row_idx]:
                            r_array[row_idx].append(grp_col)
            r_array[row_idx] = sorted(r_array[row_idx])
        return r_array

    def r_of_l_array(self, term_output, sol_output):
        """
        Given a term's output array and a left array returns a new right array,
        where for each value in the term's output array "term_val" the
        right array contains the groupoid column value at the groupoid row
        equal to "term_val".
        """
        r_array = [[] for _ in range(0, len(term_output))]
        for row_idx, term_row in enumerate(term_output):
            for term_val in term_row:
                for grp_col in range(0, self.groupoid.size):
                    if self.groupoid.get_value(term_val, grp_col) in \
                            sol_output[row_idx]:
                        r_array[row_idx].append(grp_col)
        return r_array

    def calucate_number_pos_sol(self, target_array):
        count = 1
        for idx, input_row in enumerate(self.input):
            if len(set(input_row)) == 1:
                # check if idempontent
                val = input_row[0]
                if self.groupoid.get_value(val, val) == val:
                    continue  # skip idempontent
            count *= len(target_array[idx])
        return count

    def calculate_array_solution_count(self, input_array, target_array):
        """
        Returns count of input_array rows that are correct in the target_array
        """
        count = sum(1 for idx, val_array in enumerate(input_array)
                    if set(val_array).intersection(set(target_array[idx])))
        return count

    def is_solution(self, input_array, target_array):
        """
        Checks if input_array is a solution to the target_array.

        :type input_array: list
        :param input_array: array to check against target array
        :type target_array: list
        :param target_array: target solution array
        """
        count = self.calculate_array_solution_count(input_array,
                                                    target_array)
        if count == len(target_array):
            return True
        else:
            return False

    def solve(self, term):
        """
        Solves the value of a term containing ony numbers and operator values
        """
        pds = deque()
        for i in term:
            if i.isdigit():
                pds.append(int(i))
            else:
                val2 = pds.pop()
                val1 = pds.pop()
                pds.append(self.groupoid.get_value(val1,
                                                   val2))
        return pds.pop()

    def compute(self, term):
        """
        Computes output array for the given term

        :type term: string
        :param term: postfix notation term
        :type operator: string
        :param operator: operator character

        :rtype: list
        :return: computed output array for term
        """
        output = []
        for term_variables in self.mapped_input.values():
            char_term = term
            for var, val in term_variables.items():
                char_term = char_term.replace(var, str(val))
            out = self.solve(char_term)
            output.append([out])
        return output

    def compute_validity_array(self, female_term, solution_array):
        """
        Check if female term is valid. Meaning that there is a value such that
        the female term produces the correct solution.
        """

        def is_target_full(target):
            return len(target) == self.groupoid.size

        def split_female_term(f_term):
            """
            Splits a female term and returns the side that the "F" was on and
            the male subterm. Returns True for Left and False for Right.
            """
            if f_term[-1] == "*":
                f_term = f_term[:-1]
            parts = f_term.split("F")
            if parts[0] == "":
                return True, parts[1]
            else:
                return False, parts[0]

        is_valid = True
        validity_array = [[] for _ in range(0, len(solution_array))]
        is_left_side, subterm = split_female_term(female_term)
        for idx, term_variables_mapping in \
                enumerate(self.mapped_input.values()):
            if is_target_full(solution_array[idx]):
                validity_array[idx] = solution_array[idx]
            else:
                term = subterm
                for var, val in term_variables_mapping.items():
                    term = term.replace(var, str(val))
                # solve the right or left of the term first only one time
                subterm_sol = self.solve(term)
                # see if one of the input values provides a solution
                for input_val in range(0, self.groupoid.size):
                    if is_left_side:
                        sol = self.groupoid.get_value(input_val, subterm_sol)
                    else:
                        sol = self.groupoid.get_value(subterm_sol, input_val)
                    if sol in solution_array[idx]:
                        validity_array[idx].append(input_val)
                if len(validity_array[idx]) == 0:
                    is_valid = False
                    break
        return is_valid, validity_array


class ValidTermGenerator():

    terms = ['E', 'EE*', 'EE*E*', 'EEE**', 'EE*EE**', 'EEE*E**', 'EEEE***',
             'EEE**E*', 'EE*E*E*']

    def __init__(self, term_variables):
        self.term_variables = term_variables

    def random_term_generation(self, prob=0.1):
        term = choice(ValidTermGenerator.terms)
        if len(term) > 5:
            substitutions = ("EE*", "I")
            while ("E" in term):
                rand = uniform(0, 1)
                term = term.replace("E",
                                    substitutions[0 if rand < prob else 1], 1)
        else:
            term = term.replace("E", "I")
        # randomly replace operands
        while ("I" in term):
            term = term.replace("I", choice(self.term_variables), 1)
        return term

    def gamblers_ruin_algorithm(self, prob=0.1):
        """
        Generate a random term using the gamblers ruin algorithm

        :type prop: float
        :param prob: Probability of growing the size of a random term
        """
        substitutions = ("EE*", "I")
        term = "E"
        # randomly build a term
        while ("E" in term):
            rand = uniform(0, 1)
            term = term.replace("E",
                                substitutions[0 if rand < prob else 1], 1)
        # randomly replace operands
        while ("I" in term):
            term = term.replace("I", choice(self.term_variables), 1)
        return term

    def generate(self, algorithm="GRA", **kwargs):
        if kwargs is None:
            kwargs = {}
        if algorithm == "GRA":
            return self.gamblers_ruin_algorithm(**kwargs)
        elif algorithm == "random-term-generation":
            return self.random_term_generation(**kwargs)
        else:
            raise ValueError("Unkown algorithm {}.")

    def generate_list(self, number_male_terms, algorithm="GRA", **kwargs):
        male_terms = {}
        count = 0
        while count < number_male_terms:
            random_term = self.generate(algorithm=algorithm, **kwargs)
            if not male_terms.get(random_term):
                male_terms[random_term] = random_term
                count += 1
            else:
                # we already found this term
                continue
        return list(male_terms.values())
