import itertools
from random import choice, uniform
from core.utilities import subset_sums, get_term_variables


class Groupoid():

    def __init__(self, row_size, fill=None, random=False):
        """
        :type row_size: int
        :param row_size: number of groupoid cells per row
        :type fill: int
        :param fill: default fill value for all cells of groupoid
        :type random: bool
        :param random: if true randomly fill the groupoid and ignore fill value
        """
        if row_size < 3:
            raise ValueError("Groupoid must contain 3 or more elments.")
        self.row_size = row_size
        if random:
            self.data = self.get_random_primal_groupoid_data()
        else:
            self.data = self.list_to_groupoid_data([fill] * pow(row_size, 2))

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

    def list_to_groupoid_data(self, groupoid_values, row_size=None):
        """
        Converts flat list to groupoid data

        [0,0,0,0,0,0,0,0,0] -> [[0,0,0],[0,0,0],[0,0,0]]

        :type groupoid_values: list
        :param groupoid_values: flat list of groupoid values
        :type row_size: int
        :param row_size: number of groupoid cells per row

        :rtype: list
        :return: groupoid data as a list of lists
        """
        if row_size is None:
            row_size = self.row_size
        return [groupoid_values[i:i+row_size]
                for i in range(0, len(groupoid_values), row_size)]

    def get_random_primal_groupoid_data(self, row_size=None):
        """
        Generate randomly filled primal groupoid data

        :type row_size: int
        :param row_size: number of groupoid cells per row

        :rtype: list
        :return: groupoid data as a list of lists
        """
        if row_size is None:
            row_size = self.row_size

        groupoid_cell_count = pow(row_size, 2)
        groupoid_values = [None] * groupoid_cell_count

        # find subset sum resulting in the total number of groupoid cells
        subset_sum = choice(subset_sums(range(1, groupoid_cell_count-1),
                                        groupoid_cell_count,
                                        row_size))

        assigned_indexes = []  # keep track of assigned indexes
        assigned_inputs = []  # keep track of assigned input values
        index_by_input = {}  # keep track of indexes for a given input
        for num_inputs in subset_sum:
            # choose a random input value
            possible_inputs = [i for i in range(0, row_size)
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
        step = row_size
        while curr_diag_idx < len(groupoid_values):
            curr_diagonal = groupoid_values[curr_diag_idx]
            if curr_diagonal == input_value:
                # swap diagonal with another value
                if input_value < row_size-1:
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
        return self.list_to_groupoid_data(groupoid_values, row_size)


class TermOperation():

    def __init__(self, groupoid, random_target=False, term_variables=None):
        """
        :type groupoid: :class: Groupoid
        :param groupoid: groupoid to apply term operation on
        :type random_target: bool
        :param random_target: if true randomly fill the output
        :type term_variables: list
        :param term_variables: list of possible variables in a term
        """
        self.groupoid = groupoid
        if term_variables:
            self.term_variables = term_variables
        else:
            self.term_variables = get_term_variables(self.groupoid.row_size)
        self.input = self.get_input_array(row_size=len(self.term_variables))
        if random_target:
            self.solution = self.get_random_target_array()
        else:
            self.solution = [0] * pow(self.groupoid.row_size, len(term_variables))

    def __str__(self):
        value = []
        value.append("{} |  ".format(" ".join(self.term_variables)))
        value.append("-" * (2 * len(self.term_variables) + 4))
        for idx in range(0, len(self.input)):
            value.append("{} | {}".format(
                " ".join([str(i) for i in self.input[idx]]),
                " ".join([str(o) for o in self.solution[idx]]))
            )
        return "\n".join(value)

    def get_input_array(self, row_size=None):
        """
        Returns a list of inputs to the term operation. Each input is a list
        of input values for each term element.

        e.g. [[0,0,0], [0,0,1], [0,0,2], [0,1,0], [0,1,1] ... etc.]

        :type row_size: int
        :param row_size: number of possible term elements

        :rtype: list
        :return: list of term operation inputs
        """
        if row_size is None:
            row_size = self.groupoid.row_size
        return [list(p) for p in itertools.product(
                range(self.groupoid.row_size),
                repeat=row_size)]

    def get_random_target_array(self):
        """
        Returns a random list of outputs to the term operation. Each element
        is a one element list.

        e.g. [[0], [2], [1], [0], [1] ... etc.]

        :type row_size: int
        :param row_size: number of possible term elements

        :rtype: list
        :return: list of random term operation outputs
        """
        return [[choice(range(0, self.groupoid.row_size))]
                for _ in range(0, pow(self.groupoid.row_size,
                                      len(self.term_variables)))]

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
        :return: dictionary mapping term element to input value
        """
        variable_mapping = {}
        for idx, var in enumerate(self.term_variables):
            variable_mapping[var] = input_row[idx]
        return variable_mapping

    def solve(self, term, operator="*"):
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
        for input_row in self.input:
            char_term = term
            term_variables = self.get_term_variable_mapping(input_row)
            for var, val in term_variables.items():
                char_term = char_term.replace(var, str(val))
            term_list = [int(i) if i.isdigit() else i
                         for i in list(char_term)]
            result = []
            for i in term_list:
                if type(i) is int:
                    result.insert(0, i)
                else:
                    val1 = result.pop(0)
                    val2 = result.pop(0)
                    result.insert(0, self.groupoid.get_value(val1, val2))
            output.append(result.pop())
        return output


class ValidTermGenerator():

    def __init__(self, term_variables):
        self.term_variables = term_variables

    def gamblers_ruin_algorithm(self, prob=0.20):
        """
        Generate a random term using the gamblers ruin algorithm

        :type prop: float
        :param prob: Probability of growing the size of a random term
        """
        substitutions = ["EE*", "I"]
        term = "E"
        # randomly build an arbitrarily long term
        while("E" in term):
            rand = uniform(0, 1)
            if rand < prob:
                index = 0
            else:
                index = 1
            term = term.replace("E", substitutions[index], 1)
        # randomly replace operands
        while("I" in term):
            rand = (0 + (int)(uniform(0, 1)*len(self.term_variables)))
            term = term.replace("I", self.term_variables[rand], 1)
        return term

    def generate(self, algorithm="GRA"):
        if algorithm == "GRA":
            return self.gamblers_ruin_algorithm()
        else:
            raise ValueError("Unkown algorithm {}.")


class Term():

    def __init__(self):
        pass


if __name__ == '__main__':

    grp = Groupoid(3, random=True)
    print("")
    print(grp)
    print("")
    to = TermOperation(grp, random=True)
    print(to)
    solution = to.solve("ab*cc**")
    print("")
    print("solution = %s" % solution)
    print("")
    vtg = ValidTermGenerator(to.term_variables)
    print(vtg.generate())
