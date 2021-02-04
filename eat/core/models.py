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

    def __init__(self, groupoid):
        self.groupoid = groupoid
        self.input = self.generate_all_inputs(groupoid.size)
        self.output = [0] * groupoid.size

    def generate_all_inputs(self, size):
        return [list(p) for p in itertools.product(range(size), repeat=size)]


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
    grp = Groupoid(4, random=True)
    print("------")
    print(grp)
    print("------")
    grp = Groupoid(5, random=True)
    print("------")
    print(grp)
    print("------")
    grp = Groupoid(6, random=True)
    print("------")
    print(grp)
    print("------")

