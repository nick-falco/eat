from eat.core import utilities
from eat.core.components import Groupoid, TermOperation, ValidTermGenerator
import time


class DDA_Row():

    def __init__(self, N=None, n=None, label=None, output=None, m=None):
        self.N = N  # keep track of number of rows in array
        self.n = n
        self.label = label  # label for type of row T, B, L, or Term
        self.output = output  # term output data
        self.m = m  # keep track of highest value n introduced so far

    def __str__(self):
        return ("%s\t%s\t%10s\t%60s...\t%5s" % (self.N, self.n, self.label,
                                                self.output[:3], self.m))


class DDA_Array():

    def __init__(self):
        self.array = []
    
    def __str__(self):
        s = []
        s.append("%s\t%s\t%10s\t%60s\t%5s" % ("N", "n", "Label", "Array", "m"))
        s.append("-" * (len(s[0]) + 30))
        for row in self.array:
            s.append(str(row))
        return "\n".join(s)

    def get_m_eq_n(self, n):
        for idx, row in enumerate(self.array):
            if n == row.m:
                return row

    def get_n_eq_k(self, k):
        # find row numbered k that has some term u(x,y,z) as its label
        count = 1
        first_n_eq_k = None
        for idx, row in enumerate(self.array):
            if row.n == k:
                if count == 1:
                    first_n_eq_k = row
                elif count == 2:
                    second_n_eq_k = row
                    break
                count = count + 1
        return first_n_eq_k, second_n_eq_k


class DeepDrillingAlgorithm():

    def get_k_from_label(self, rowlabel):
        # Get label K from row M labeled Bk or Lk
        parts = rowlabel.split("B")
        k = int(parts[-1])
        return k

    def run(self):
        pds = []  # push down stack containing number of terms
        pds.append(1)

        # create groupoid table
        grp = Groupoid(3)
        grp.data = grp.list_to_groupoid_data([1, 1, 2,
                                              0, 2, 0,
                                              0, 2, 1])

        # setup term operation
        to = TermOperation(grp,
                           standard_target="ternary_descriminator",
                           term_variables=["x", "y", "z"])
        # initilize a valid term generator
        vtg = ValidTermGenerator(to.term_variables)

        # initialize DDA array
        dda = DDA_Array()
        dda.array.append(DDA_Row(0, 1, "T", to.solution, 1))

        # algorithm variables
        N = 1  # we start at the second row
        m = 1  # keep track of highest value n introduced so far
        n = 1  # get the initial value of n

        while(True):
            new_row = DDA_Row()
            last_row = dda.array[-1]
            n = last_row.n
            m = last_row.m
            label = last_row.label
            # check to see if rowtype is the first term, left array, or B array
            if label == "T" or label.startswith("B") or label.startswith("L"):
                random_term = vtg.generate()
                random_term_sol = to.solve(random_term)
                # check to see if there was a variable solution to the term
                if(to.is_solution(random_term_sol, last_row.output)):
                    print("STEP 1 A")
                    new_row.label = random_term
                    new_row.output = random_term_sol
                    new_row.N = N
                    new_row.n = n
                    new_row.m = m
                    # pop n off the top of stack to indicate that a solution
                    # to the array numbered n has been found
                    pds.pop()
                else:  # term is not a variable solution
                    print("STEP 1 B")
                    new_row.N = N
                    new_row.n = m + 1
                    new_row.label = f"L{n}"
                    l_array = to.l_array(last_row.output)
                    new_row.output = l_array
                    new_row.m = m + 1
                    pds.append(m + 1)  # push m+1 onto stack
            else:
                # do this if the label of row N is a term
                meqln_row = dda.get_m_eq_n(n)
                if meqln_row.label.startswith("T"):
                    print("STEP 2 A")
                    # found solution
                    break
                elif meqln_row.label.startswith("L"):
                    print("STEP 2 B")
                    # row is labeled Ln
                    print("ROW M - 1 = %s" % dda.array[meqln_row.N - 1])
                    print("ROW M = %s" % meqln_row)
                    print("ROW N = %s" % last_row)
                    new_row.N = N
                    new_row.n = m + 1
                    new_row.label = f"B{n}"
                    r_array = to.r_array(last_row.output,
                                         dda.array[meqln_row.N - 1].output)
                    new_row.output = r_array
                    new_row.m = m + 1
                    pds.append(m + 1)  # push m+1 onto stack
                elif meqln_row.label.startswith("B"):
                    print("STEP 2 C")
                    # row is labeled Bk
                    k = self.get_k_from_label(meqln_row.label)
                    firstk, secondk = dda.get_n_eq_k(k)
                    print(firstk)
                    print(secondk)
                    new_row.N = N
                    new_row.n = pds.pop()
                    secondk_term = utilities.combine_postfix(secondk.label,
                                                             last_row.label)
                    new_row.label = secondk_term
                    new_row.output = to.solve(secondk_term)
                    new_row.m = m

            # increment number of rows. N = N + 1
            dda.array.append(new_row)
            N = N + 1
            if N == 40:
                break
            print(new_row)
            print(pds)                          
        print(dda)
        s = dda.array.pop()
        print(s.label)
        print(to.solve(s.label))
        print("solution = %s" % to.solution)
