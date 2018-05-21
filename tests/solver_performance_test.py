from sympy import *
from sympy.parsing.sympy_parser import parse_expr
from sympy import Symbol
import numpy as np
import time


"""
(Run on a Macbook Air 2016)
Trials: 5000
Polygon: 0.0768296766281128
Sympy 8eq solve(): 0.0430738639831543
Sympy solve(): 0.014581542015075683
Sympy nonlinsolve(): 0.07651357650756836
Sympy LUsolve(): 0.005532379150390625
Numpy linalg.solve(): 2.669811248779297e-05
"""


if __name__ == '__main__':
    trials = 50
    print("Trials: " + str(trials))
    
    start = time.time()
    for i in range(0, int(trials)):
        poly = Polygon("poly" + str(i), ["a", "b", "c", "d"], ["ab", "bc", "cd", "da"])
        poly.set_constraints(["2", "a", "a", "a"], ["pi/2", "ab", "ab", "ab"])
        if poly.solve_geometry():
            if poly.generate_vertices():
                poly.generate_bmesh()
                poly.link_mesh()
                poly.clean_up()
    elapsed_time = (time.time() - start) / (trials)
    print("Polygon: " + str(elapsed_time))
    
    start = time.time()
    for i in range(0,trials):
        constraints =   [parse_expr("52-a"),
                         parse_expr("a-b"),
                         parse_expr("a-c"),
                         parse_expr("a-d"),
                         parse_expr("pi/2-ab"),
                         parse_expr("ab-bc"),
                         parse_expr("ab-cd"),
                         parse_expr("ab-da"),]
        variables = [Symbol("a"), Symbol("b"), Symbol("c"), Symbol("d"),
                    Symbol("ab"), Symbol("bc"), Symbol("cd"), Symbol("da")]
        solve(constraints, variables, dict=True)
    elapsed_time = (time.time() - start) / trials
    print("Sympy 8eq solve(): " + str(elapsed_time))


    start = time.time()
    for i in range(0,trials):
        constraints =   [parse_expr("52-2*a-3*b-5*c"),
                         parse_expr("61-3*a-6*b-2*c"),
                         parse_expr("75-8*a-3*b-6*c")]
        variables = [Symbol("a"), Symbol("b"), Symbol("c")]
        solve(constraints, variables, dict=True)
    elapsed_time = (time.time() - start) / trials
    print("Sympy solve(): " + str(elapsed_time))


    start = time.time()
    for i in range(0,trials):
        constraints =   [parse_expr("52-2*a-3*b-5*c"),
                         parse_expr("61-3*a-6*b-2*c"),
                         parse_expr("75-8*a-3*b-6*c")]
        variables = [Symbol("a"), Symbol("b"), Symbol("c")]
        nonlinsolve(constraints, variables)
    elapsed_time = (time.time() - start) / trials
    print("Sympy nonlinsolve(): " + str(elapsed_time))


    start = time.time()
    for i in range(0,trials):    
        A = Matrix([ [2, 3, 5], [3, 6, 2], [8, 3, 6] ])
        b = Matrix([52,61,75])
        A.LUsolve(b)
    elapsed_time = (time.time() - start) / trials
    print("Sympy LUsolve(): " + str(elapsed_time))


    start = time.time()
    for i in range(0,trials):
        a = np.array([[2,3,5], [3,6,2], [8,3,6]])
        b = np.array([52,61,75])
        x = np.linalg.solve(a, b)
    elapsed_time = (time.time() - start) / trials
    print("Numpy linalg.solve(): " + str(elapsed_time))            
