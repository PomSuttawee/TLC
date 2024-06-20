import mixture as mt
import calibration as cb
import sympy as sp

def calculate_concentration(mixture: mt.Mixture, calibration: list):
    # Define symbolic variables
    variables = [sp.symbols(f'c{i+1}') for i in range(len(calibration))]
    print(f'There are {len(calibration)} calibration object --> variables are {variables}')

    equations = []
    for i in range(len(mixture.peak_area['R'])):
        coef = [calib.peak_info[f'Peak {i+1}']['Best_fit_line']['R'][0] for calib in calibration]
        const = sum([calib.peak_info[f'Peak {i+1}']['Best_fit_line']['R'][1] for calib in calibration])
        print(f'Equation {i+1}:\n\tcoef: {coef}\n\tconstant: {const}')
        expression = sum(a*v for a,v in zip(coef, variables)) + const
     
        equations.append(sp.Eq(mixture.peak_area['R'][i], expression))
        print(f'\t{equations[i]}')
    
    solution = sp.solve(equations, variables)
    print(f'Solution is {solution}')
    return 