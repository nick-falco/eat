from eat.deep_drilling_agorithm.dda import DeepDrillingAlgorithm
from eat.core.components import Groupoid, TermOperation, ValidTermGenerator


if __name__ == '__main__':
    dda = DeepDrillingAlgorithm()
    dda.run()

    '''
    grp = Groupoid(3)
    grp.data = grp.list_to_groupoid_data([2, 1, 2,
                                          1, 0, 0,
                                          0, 0, 1])
    print("")
    print(grp)
    print("")
    to = TermOperation(grp, random_target=True)
    print(to)
    term = "ab*ca**"
    solution = to.solve(term)
    print("")
    print("solution = %s" % solution)
    print("")
    vtg = ValidTermGenerator(to.term_variables)
    print(vtg.generate())
    print("")
    has_var_sol, var_sol = to.solve_variable_solution(term_solution=solution,
                                                      side="left")
    print(has_var_sol, var_sol)
    has_var_sol, var_sol = to.solve_variable_solution(term_solution=solution,
                                                      side="right")
    print(has_var_sol, var_sol)'''
