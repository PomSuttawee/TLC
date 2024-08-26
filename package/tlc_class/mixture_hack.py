from package.tlc_class.mixture import Mixture
from package.tlc_class.calibration import Calibration
import sympy as sp

def calculate_concentration(mixture: Mixture, calibration: list[Calibration]):
    # Define symbolic variables
    log = ""
    variables = [sp.symbols(f'c{i+1}') for i in range(len(calibration))]
    log += f"There are {len(calibration)} calibration object --> variables are {variables}\n"

    equations = []
    coef = []
    expression = []
    good_peak_index = []
    for i in range(len(mixture.peak_area['R'])):
        for calib in calibration:
            if calib.peaks[i].best_fit_line['R'] is None:
                continue
            else:
                good_peak_index.append(i)
                coef.append(calib.peaks[i].best_fit_line['R'][0])
                const = sum([calib.peaks[i].best_fit_line['R'][1]])
        log += f"Equation {i+1}:\n\tcoef: {coef}\n\tconstant: {const}\n"
        expression.append(sum(a*v for a,v in zip(coef, variables)) + const)
    
    for peak_index in good_peak_index:
        equations.append(sp.Eq(mixture.peak_area['R'][peak_index], expression))
        log += f'\t{equations[i]}'
    
    solution = sp.solve(equations, variables)
    log += f"Solution is {solution}"
    return log