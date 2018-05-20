from sympy import *
from sympy.parsing.sympy_parser import parse_expr
from sympy import Symbol
import numpy as np
import time


"""
(Run on a Macbook Air 2016)
Trials: 5000
Sympy solve(): 0.013043633413314819
Sympy nonlinsolve(): 0.06551389598846435
Sympy LUsolve(): 0.0007110137939453125
Numpy linalg.solve(): 2.0845413208007813e-05
"""


if __name__ == '__main__':
    trials = 5000
    print("Trials: " + str(trials))


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
