import cv2
import numpy as np
import matplotlib.pyplot as plt
from package.image_processing import image_processing
import time

class PeakInfo:
    def __init__(self, image: np.ndarray, concentration: list[float]):
        self.image = image
        self.concentration = concentration
        self.intensity = {}
        self.minima = []
        self.peak_area = {}
        self.best_fit_line = {}
        self.r2 = {}
        self.plot_intensity = None
        self.plot_fit_line = None
        self.__process_peak()
        
    def __process_peak(self):
        self.__calculate_intensity()
        self.__calculate_minima()
        self.__calculate_peak_area()
        self.__calculate_fit_line(self.concentration)
        self.__create_plot_intensity()
        self.__create_plot_fit_line(self.concentration)
    
    def __calculate_intensity(self):
        intensity = {}
        image_rgb = cv2.split(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB))
        for j, color in enumerate(['R', 'G', 'B']):
            sum_intensity = np.sum(image_rgb[j], axis=0)
            count_color_pixel = np.sum(np.where(image_rgb[j] > 0, 1, 0), axis=0)
            safe_count_color_pixel = np.where(count_color_pixel == 0, 1, count_color_pixel)
            average_intensity = (255 - (sum_intensity / safe_count_color_pixel)).astype(int)
            average_intensity[count_color_pixel == 0] = 0
            intensity[color] = average_intensity
        self.intensity = intensity
    
    def __calculate_minima(self):
        """ Calculate the minima points for intensity curves to determine peak boundaries. """
        intensity_grayscale = 0.299*self.intensity['R'] + 0.587*self.intensity['G'] + 0.114*self.intensity['B']
        threshold_intensity = np.where(intensity_grayscale > 0, 1, 0)
        zero_to_non_zero = np.where((threshold_intensity[:-1] == 0) & (threshold_intensity[1:] != 0))[0]
        non_zero_to_zero = np.where((threshold_intensity[:-1] != 0) & (threshold_intensity[1:] == 0))[0] + 1
        minima_index = np.sort(np.concatenate((zero_to_non_zero, non_zero_to_zero)))
        self.minima = minima_index
    
    def __calculate_peak_area(self):
        """ Calculate the area under the intensity curve for each peak and color channel. """
        peak_area = {}
        for color in 'RGB':
            each_color_area = []
            intensity = self.intensity[color]
            for index_minima in range(0, len(self.minima)-1, 2):
                each_color_area.append(np.trapz(intensity[self.minima[index_minima]: self.minima[index_minima + 1] + 1]))
            peak_area[color] = np.array(each_color_area)
        self.peak_area = peak_area
    
    def __calculate_fit_line(self, concentration):
        """ Calculate the best fit line for the peak areas vs. concentrations. """
        best_fit_line = {}
        r2 = {}
        for color in 'RGB':
            # Best fite line
            new_concentration = concentration[-len(self.peak_area[color]):]
            best_fit_line[color] = tuple(np.polyfit(new_concentration, self.peak_area[color], 1).astype(int))
            
            # R2
            actual = np.array(self.peak_area[color])
            coef, const = best_fit_line[color]
            predict = np.array([coef*cont + const for cont in new_concentration])
            mean = np.mean(actual)
            ssr = sum(np.power(actual-predict, 2))
            sst = sum(np.power(actual-mean, 2))
            r2[color] = round(1 - ssr/sst, 3)
        self.best_fit_line = best_fit_line
        self.r2 = r2
    
    def __create_plot_intensity(self):
        x = np.arange(0, len(self.intensity['R']))
        figure, axis = plt.subplots(nrows=3, ncols=1, figsize=(4, 12))
        rgb = ['Red', 'Green', 'Blue']
        for i, color in enumerate(['R', 'G', 'B']):
            intensity = self.intensity[color]
            axis[i].plot(x, intensity, color=rgb[i])
            axis[i].scatter(self.minima, np.take(intensity, self.minima))
            axis[i].set_title(f'{rgb[i]} Intensity')
            axis[i].set_xlabel('Pixel')
            axis[i].set_ylabel('Intensity')
            axis[i].set_ylim((0, 255))
            axis[i].grid()
        figure.tight_layout()
        self.plot_intensity = figure
        plt.close()
    
    def __create_plot_fit_line(self, concentration):
        figure, axis = plt.subplots(nrows=3, ncols=1, figsize=(3, 9))
        rgb_color = {'R':'Red', 'G':'Green', 'B':'Blue'}
        for i, color in enumerate('RGB'):
            peak_area = self.peak_area[color]
            while len(peak_area) < len(concentration):
                peak_area = np.insert(peak_area, 0, 0, axis=0)
            a, b = self.best_fit_line[color]
            x = np.linspace(concentration[0], concentration[-1], 100)
            y = a * x + b
            r2 = round(self.r2[color], 3)
            axis[i].scatter(concentration, peak_area, color=rgb_color[color])
            axis[i].plot(x, y, color=rgb_color[color], label=f'{a}c + {b}\nR2: {r2}')
            axis[i].set_title(f'Peak: {rgb_color[color]} Peak Area')
            axis[i].set_xlabel('Concentration')
            axis[i].set_ylabel('Peak Area')
            axis[i].grid()
            axis[i].legend()
        figure.tight_layout()
        self.plot_fit_line = figure
        plt.close()
    
class Calibration:
    def __init__(self, name: str, image: np.ndarray, concentration: list[float]):
        """ Initialize the Calibration object. """
        self.name = name
        self.image = image
        self.concentration = concentration
        self.processed_image_peak, self.processed_image_full = image_processing.preprocessing_calibration(image)
        self.peaks = [PeakInfo(image, self.concentration) for image in self.processed_image_peak]
    
    def set_name(self, name):
        self.name = name