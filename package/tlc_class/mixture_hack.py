from package.tlc_class.mixture import Mixture
from package.tlc_class.calibration import Calibration
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

class MixtureHack:
    def __init__(self, mixture: Mixture, list_calibration: list[Calibration], r2_threshold=0.9):
        self.mixture = mixture
        self.list_calibration = list_calibration
        self.list_variable = []
        self.expression = {}
        self.equation = {}
        self.r2_threshold = r2_threshold
        
        self.__create_variable()
        self.__create_expression_rgb()
        self.__create_equation()
    
    def solve_equation(self, color: str):
        log = ''
        # print("\nSelecting peaks based on r² values...")
        # list_peak_index = self.__select_peaks_based_on_r2(color)
        
        # if not list_peak_index:
        #     print(f"\tNo peaks with r² above the threshold {self.r2_threshold} for color {color}.")
        #     return
        # else:
        #     print(f"\t{len(list_peak_index)} peaks with r² above the threshold {self.r2_threshold} for color {color}.\n\tSelected peaks: {list_peak_index}")
        
        log += "Selecting top peaks based on r² values..."
        print("\nSelecting top peaks based on r² values...")
        list_peak_index = self.__select_top_peaks_by_r2(color)

        if not list_peak_index:
            print(f"No peaks with r² above the threshold {self.r2_threshold} for color {color}.")
            return f"No peaks with r² above the threshold {self.r2_threshold} for color {color}."
        else:
            log += f'\n\tSelected peaks: {list_peak_index}'
            print(f'Selected peaks: {list_peak_index}')
        
        log += "\n\nSolving equation system for selected peaks..."
        print("Solving equation system for selected peaks...")
        list_equation = [self.equation[peak_index][color] for peak_index in list_peak_index]
        solutions = sp.solve(list_equation, self.list_variable)
        
        if not solutions:
            print("\tNo solution found for the given system of equations.")
            return log + "\n\tNo solution found for the given system of equations."

        formatted_solution = {str(var): sol for var, sol in solutions.items()}
        log += f"\n\tSelected Peak Indices: {list_peak_index}\n\tEquation: {list_equation}\n\tSolution: {formatted_solution}\n\n\n\n"
        print(f"\tSelected Peak Indices: {list_peak_index}\n\tEquation: {list_equation}\n\tSolution: {formatted_solution}\n\n")
        return log
        
    # TODO
    def plot_answer(self):
        pass
    
    def __create_variable(self):
        print("\nCreating variable...")
        self.list_variable = [sp.symbols(f'c{i+1}') for i in range(len(self.list_calibration))]
        print(f'Calibration Count: {len(self.list_calibration)}\nVariables: {self.list_variable}')
    
    def __create_expression_rgb(self):
        print("\nCreating expression...")
        for peak_index in range(len(self.mixture.peak_area['R'])):
            
            self.expression[peak_index+1] = {color: self.__create_expression_single_channel(color, peak_index) for color in 'RGB'}
            print(f'Expression {peak_index+1}: {self.expression[peak_index+1]}')
    
    def __create_expression_single_channel(self, color: str, peak_index: int):
        coef = [calibration.peaks[peak_index].best_fit_line[color][0] for calibration in self.list_calibration]
        constant = sum([calibration.peaks[peak_index].best_fit_line[color][1] for calibration in self.list_calibration])
        return sum(a*v for a,v in zip(coef, self.list_variable)) + constant
    
    def __create_equation(self):
        print("\nCreating equation...")
        for peak_index in range(len(self.mixture.peak_area['R'])):
            equation = {}
            for color in 'RGB':
                peak_area = self.mixture.peak_area[color][peak_index]
                equation[color] = sp.Eq(peak_area, self.expression[peak_index+1][color])
            self.equation[peak_index+1] = equation
            print(f'Equation {peak_index+1}: {self.equation[peak_index+1]}')
            
    def __select_peaks_based_on_r2(self, color: str):
        """ Automatically select peak indices based on r² values. """
        selected_peak_indices = []
        for peak_index in range(len(self.list_calibration[0].peaks)):
            r2_values = [calibration.peaks[peak_index].r2[color] for calibration in self.list_calibration]
            avg_r2 = np.mean(r2_values)  # Take the average r² across all calibrations for the peak
            if avg_r2 >= self.r2_threshold:
                selected_peak_indices.append(peak_index + 1)
        return selected_peak_indices
    
    def __select_top_peaks_by_r2(self, color: str):
        """ Select enough peaks to solve the equation system based on the highest r² values. """
        peak_r2_values = []
        
        # Collect r² values for each peak
        for peak_index in range(len(self.list_calibration[0].peaks)):
            r2_values = [calibration.peaks[peak_index].r2[color] for calibration in self.list_calibration]
            avg_r2 = np.mean(r2_values)  # Average r² for the peak across calibrations
            peak_r2_values.append((peak_index + 1, avg_r2))  # (peak_index, avg_r2)
        
        # Sort the peaks by the highest average r² values
        sorted_peaks = sorted(peak_r2_values, key=lambda x: x[1], reverse=True)
        
        # Select the top N peaks (where N = number of variables/calibration objects)
        top_peaks = [peak[0] for peak in sorted_peaks[:len(self.list_variable)]]
        return top_peaks