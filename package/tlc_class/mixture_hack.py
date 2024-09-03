from package.tlc_class.mixture import Mixture
from package.tlc_class.calibration import Calibration
import sympy as sp

class MixtureHack:
    def __init__(self, mixture: Mixture, list_calibration: list[Calibration]):
        self.mixture = mixture
        self.list_calibration = list_calibration
        self.list_variable = []
        self.expression = {}
        self.equation = {}
        
        self.__create_variable()
        self.__create_expression()
        self.__create_equation()
    
    def solve_equation(self, list_peak_index: list[int], color: str):
        print("\nSolving equation system...")
        list_equation = [self.equation[peak_index][color] for peak_index in list_peak_index]
        text = f"Equation: {list_equation}\nSolution: {sp.solve(list_equation, self.list_variable)}\n\n"
        print(text)
        return text
    
    # TODO
    def plot_answer(self):
        pass
    
    def __create_variable(self):
        print("\nCreating variable...")
        self.list_variable = [sp.symbols(f'c{i+1}') for i in range(len(self.list_calibration))]
        print(f'Calibration Count: {len(self.list_calibration)}\nVariables: {self.list_variable}')
    
    def __create_expression(self):
        print("\nCreating expression...")
        for peak_index in range(len(self.mixture.peak_area['R'])):
            expression = {}
            for color in 'RGB':
                coef = [calibration.peaks[peak_index].best_fit_line[color][0] for calibration in self.list_calibration]
                constant = sum([calibration.peaks[peak_index].best_fit_line[color][1] for calibration in self.list_calibration])
                expression[color] = sum(a*v for a,v in zip(coef, self.list_variable)) + constant
            self.expression[peak_index+1] = expression
            print(f'Expression {peak_index+1}: {self.expression[peak_index+1]}')
    
    def __create_equation(self):
        print("\nCreating equation...")
        for peak_index in range(len(self.mixture.peak_area['R'])):
            equation = {}
            for color in 'RGB':
                peak_area = self.mixture.peak_area[color][peak_index]
                equation[color] = sp.Eq(peak_area, self.expression[peak_index+1][color])
            self.equation[peak_index+1] = equation
            print(f'Equation {peak_index+1}: {self.equation[peak_index+1]}')