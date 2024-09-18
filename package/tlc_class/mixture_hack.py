from package.tlc_class.mixture import Mixture
from package.tlc_class.calibration import Calibration
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class MixtureHack:
    def __init__(self, mixture: Mixture, list_calibration: list[Calibration], r2_threshold=0.9):
        self.mixture_object = mixture
        self.list_calibration_object = list_calibration
        self.list_variable = []
        self.expression = {}
        self.equation = {}
        self.r2_threshold = r2_threshold
        self.list_selected_peak_index = []
        self.solution = {}
        self.plot_mixture = None
        
        self.__create_variable()
        self.__create_expression_rgb()
        self.__create_equation()
    
    def solve_equation(self, color: str):
        log = ''
        # print("\nSelecting peaks based on r² values...")
        # self.list_selected_peak_index = self.__select_peaks_based_on_r2(color)
        
        # if not self.list_selected_peak_index:
        #     print(f"\tNo peaks with r² above the threshold {self.r2_threshold} for color {color}.")
        #     return
        # else:
        #     print(f"\t{len(self.list_selected_peak_index)} peaks with r² above the threshold {self.r2_threshold} for color {color}.\n\tSelected peaks: {self.list_selected_peak_index}")
        
        log += "Selecting top peaks based on r² values..."
        self.__select_top_peaks_by_r2(color)

        if len(self.list_selected_peak_index) == 0:
            return f"No peaks with r² above the threshold {self.r2_threshold} for color {color}."
        else:
            log += f'\n\tSelected peaks: {self.list_selected_peak_index}'
        
        log += "\n\nSolving equation system for selected peaks..."
        list_equation = [self.equation[peak_index][color] for peak_index in self.list_selected_peak_index]
        solutions = {str(var): con for var, con in sp.solve(list_equation, self.list_variable).items()}
        
        if not solutions:
            return log + "\n\tNo solution found for the given system of equations."
        self.solution[color] = solutions

        formatted_solution = {str(var): sol for var, sol in solutions.items()}
        log += f"\n\tSelected Peak Indices: {self.list_selected_peak_index}\n\tEquation: {list_equation}\n\tSolution: {formatted_solution}\n\n\n\n"
        return log
    
    def plot_answer(self):
        intensity_rgb = self.mixture_object.intensity
        minima = self.mixture_object.minima
        x = np.arange(0, len(intensity_rgb['R']))
        figure, axis = plt.subplots(nrows=3, ncols=1, figsize=(4, 12))
        rgb = ['Red', 'Green', 'Blue']
        for i, color in enumerate('RGB'):
            intensity = intensity_rgb[color]
            axis[i].plot(x, intensity, color=rgb[i])
            axis[i].scatter(minima, np.take(intensity, minima))
            
            for peak_index in self.list_selected_peak_index:
                x_start = minima[peak_index-1]
                y_start = 0
                width = minima[peak_index] - minima[peak_index-1]
                for calibration_object in self.list_calibration_object:
                    concentration = self.solution[color][calibration_object.name]
                    coef, const = calibration_object.peaks[peak_index-1].best_fit_line[color]
                    height = (coef*concentration + const) // width
                    rect = patches.Rectangle((x_start, y_start), width=width, height=height)
                    axis[i].add_patch(rect)
                    y_start += height
            axis[i].set_title(f'{rgb[i]} Intensity')
            axis[i].set_xlabel('Pixel')
            axis[i].set_ylabel('Intensity')
            axis[i].set_ylim((0, 255))
        figure.tight_layout()
        self.plot_mixture = figure
        plt.close()
    
    def __create_variable(self):
        self.list_variable = [sp.symbols(calibration_object.name) for calibration_object in self.list_calibration_object]
    
    def __create_expression_rgb(self):
        for peak_index in range(len(self.mixture_object.peak_area['R'])):
            self.expression[peak_index+1] = {color: self.__create_expression_single_channel(color, peak_index) for color in 'RGB'}
    
    def __create_expression_single_channel(self, color: str, peak_index: int):
        coef = [calibration.peaks[peak_index].best_fit_line[color][0] for calibration in self.list_calibration_object]
        constant = sum([calibration.peaks[peak_index].best_fit_line[color][1] for calibration in self.list_calibration_object])
        return sum(a*v for a,v in zip(coef, self.list_variable)) + constant
    
    def __create_equation(self):
        for peak_index in range(len(self.mixture_object.peak_area['R'])):
            equation = {}
            for color in 'RGB':
                peak_area = self.mixture_object.peak_area[color][peak_index]
                equation[color] = sp.Eq(peak_area, self.expression[peak_index+1][color])
            self.equation[peak_index+1] = equation
    
    def __select_top_peaks_by_r2(self, color: str):
        """ Select enough peaks to solve the equation system based on the highest r² values. """
        peak_r2_values = []
        
        # Collect r² values for each peak
        for peak_index in range(len(self.list_calibration_object[0].peaks)):
            r2_values = [calibration.peaks[peak_index].r2[color] for calibration in self.list_calibration_object]
            avg_r2 = np.mean(r2_values)  # Average r² for the peak across calibrations
            peak_r2_values.append((peak_index + 1, avg_r2))  # (peak_index, avg_r2)
        
        # Sort the peaks by the highest average r² values
        sorted_peaks = sorted(peak_r2_values, key=lambda x: x[1], reverse=True)
        
        # Select the top N peaks (where N = number of variables/calibration objects)
        self.list_selected_peak_index = [peak[0] for peak in sorted_peaks[:len(self.list_variable)]]
        