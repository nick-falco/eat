from eat.core.components import ValidTermGenerator
from eat.core.utilities import combine_postfix, print_search_summary
import logging
import time


class DDA_Row():

    def __init__(self, N=None, n=None, label=None, array=None, m=None):
        self.N = N  # keep track of number of rows in array
        self.n = n
        self.label = label  # label for type of row T, B, L, or Term
        self.array = array
        self.m = m  # keep track of highest value n introduced so far

    @property
    def term(self):
        """
        Shim to return the term for the print_search_summary method.
        """
        return self.label

    def __str__(self):
        return ("%s\t%s\t%10s\t%60s...\t%5s" % (self.N, self.n, self.label,
                                                self.array[:3], self.m))


class DDA_Table():

    def __init__(self):
        self.table = []

    def __str__(self):
        s = []
        s.append("%s\t%s\t%10s\t%60s\t%5s" % ("N", "n", "Label", "Array", "m"))
        s.append("-" * (len(s[0]) + 30))
        for row in self.table:
            s.append(str(row))
        return "\n".join(s)

    def get_m_eq_n(self, n):
        for row in self.table:
            if n == row.m:
                return row

    def get_n_eq_k(self, k):
        # find row numbered k that has some term u(x,y,z) as its label
        count = 1
        first_n_eq_k = None
        for idx, row in enumerate(self.table):
            if row.n == k:
                if count == 1:
                    first_n_eq_k = row
                elif count == 2:
                    second_n_eq_k = row
                    break
                count = count + 1
        return first_n_eq_k, second_n_eq_k


class DeepDrillingAlgorithm():

    def __init__(self, groupoid, term_operation,
                 term_expansion_probability=0.3,
                 male_term_generation_method="random"):
        self.grp = groupoid
        self.to = term_operation
        self.vtg = ValidTermGenerator(self.to.term_variables)
        self.term_expansion_probability = term_expansion_probability
        self.male_term_generation_method = male_term_generation_method
        self.logger = logging.getLogger(__name__)

    def get_k_from_label(self, rowlabel):
        # Get label K from row M labeled Bk or Lk
        parts = rowlabel.split("B")
        k = int(parts[-1])
        return k

    def get_male_term(self, generation_method="GRA"):
        if generation_method == "GRA":
            return self.vtg.generate(algorithm="GRA",
                                     prob=self.term_expansion_probability)
        elif generation_method == "random-term-generation":
            return self.vtg.generate(algorithm=generation_method,
                                     prob=self.term_expansion_probability)

    def run(self, verbose=False, print_summary=False):
        pds = []  # push down stack containing number of terms
        pds.append(1)

        # initialize DDA table
        dda = DDA_Table()
        dda.table.append(DDA_Row(0, 1, "T", self.to.target, 1))

        # algorithm variables
        N = 1  # we start at the second row
        m = 1  # keep track of highest value n introduced so far
        n = 1  # get the initial value of n

        start = time.time()
        while (True):
            new_row = DDA_Row()
            last_row = dda.table[-1]
            n = last_row.n
            m = last_row.m
            label = last_row.label
            # check to see if rowtype is the first term, left array, or B array
            if label == "T" or label.startswith("B") or label.startswith("L"):
                male_term = self.get_male_term(
                    generation_method=self.male_term_generation_method)
                male_term_sol = self.to.compute(male_term)
                # check to see if there was a variable solution to the term
                if (self.to.is_solution(male_term_sol, last_row.array)):
                    self.logger.debug("STEP 1 A")
                    new_row.label = male_term
                    new_row.array = male_term_sol
                    new_row.N = N
                    new_row.n = n
                    new_row.m = m
                    # pop n off the top of stack to indicate that a solution
                    # to the array numbered n has been found
                    pds.pop()
                else:  # term is not a variable solution
                    self.logger.debug("STEP 1 B")
                    new_row.N = N
                    new_row.n = m + 1
                    new_row.label = "L{}".format(m+1)
                    l_array = self.to.l_array(last_row.array)
                    new_row.array = l_array
                    new_row.m = m + 1
                    pds.append(m + 1)  # push m+1 onto stack
            else:
                # do this if the label of row N is a term
                meqln_row = dda.get_m_eq_n(n)
                if meqln_row.label.startswith("T"):
                    self.logger.debug("STEP 2 A")
                    # found solution
                    break
                elif meqln_row.label.startswith("L"):  # row is labeled Ln
                    self.logger.debug("STEP 2 B")
                    A = dda.get_m_eq_n(n-1)
                    new_row.N = N
                    new_row.n = m + 1
                    new_row.label = "B{}".format(n)
                    r_array = self.to.r_of_l_array(last_row.array,
                                                   A.array)
                    new_row.array = r_array
                    new_row.m = m + 1
                    pds.append(m + 1)  # push m+1 onto stack
                elif meqln_row.label.startswith("B"):
                    self.logger.debug("STEP 2 C")
                    k = self.get_k_from_label(meqln_row.label)
                    first, second = dda.get_n_eq_k(k)
                    new_row.N = N
                    new_row.n = pds.pop()
                    combined_term = combine_postfix(second.label,
                                                    last_row.label)
                    new_row.label = combined_term
                    new_row.array = self.to.compute(combined_term)
                    new_row.m = m
            dda.table.append(new_row)
            N = N + 1
        sol = dda.table.pop()
        end = time.time()

        if (verbose):
            print(dda)
            print("")
        if (print_summary or verbose):
            print_search_summary(sol, sol, self.to, self.grp, start, end)
        return sol
