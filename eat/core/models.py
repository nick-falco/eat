import itertools
from random import choice
from utilities import subset_sums


class Groupoid():

    def __init__(self, size, fill=None, random=False):
        self.size = size
        if random:
            self.data = self.get_random_primal_groupoid_data()
        else:
            self.data = self.list_to_groupoid_data([fill] * pow(size, 2))

    def __str__(self):
        return "\n".join([" ".join(
                         [str(cell) for cell in row])
                         for row in self.data])

    def set_value(self, x, y, value):
        self.data[x][y] = value

    def get_value(self, x, y):
        return self.data[x][y]

    def groupoid_data_to_list(self, groupoid_data):
        return [cell for row in groupoid_data for cell in row]

    def list_to_groupoid_data(self, groupoid_values, size=None):
        if size is None:
            size = self.size
        return [groupoid_values[i:i+size]
                for i in range(0, len(groupoid_values), size)]

    def get_random_primal_groupoid_data(self, size=None):
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

    def __init__(self, groupoid, random=False):
        self.groupoid = groupoid
        self.input = self.get_input_array(groupoid.size)
        if random:
            self.output = self.get_random_output_array(groupoid.size)
        else:
            self.output = [0] * pow(groupoid.size, 3)
        self.element_values = None

    def get_input_array(self, size):
        return [list(p) for p in itertools.product(range(size), repeat=size)]

    def get_random_output_array(self, size):
        return [[choice(range(0, size))] for _ in range(0, pow(size, 3))]

    def imply_element_mapping(self, term, operator="*"):
        elements = sorted(list(set(term)))
        elements.remove(operator)
        possible_values = range(0, self.groupoid.size)
        if len(possible_values) < len(elements):
            raise ValueError("The number of term elements is greater than "
                             "the number of possible values")
        element_values = {}
        for idx, element in enumerate(elements):
            element_values[element] = possible_values[idx]
        return element_values

    def solve(self, term, operator="*"):
        if self.element_values is None:
            element_values = self.imply_element_mapping(term, operator)
        else:
            element_values = self.element_values
        for element, val in element_values.items():
            term = term.replace(element, str(val))

        term_list = [int(i) if i.isdigit() else i for i in list(term)]
        result = []
        for i in term_list:
            if type(i) is int:
                result.insert(0, i)
            else:
                val1 = result.pop(0)
                val2 = result.pop(0)
                result.insert(0, self.groupoid.get_value(val1, val2))
        return result.pop()


class Term():

    def __init__(self):
        pass


class FemaleTerm(Term):

    def __init__(self):
        pass


class MaleTerm(Term):

    def __init__(self):
        pass


if __name__ == '__main__':

    grp = Groupoid(3, random=True)
    print("------")
    print(grp)
    print("------")
    to = TermOperation(grp, random=True)
    print(len(to.input))
    print(to.input)
    print(len(to.output))
    print(to.output)
    solution = to.solve("xy*zz**")
    print("solution = %s" % solution)
