import cv2
import numpy as np
import matplotlib.pyplot as plt
from package.image_processing import image_processing

class PeakInfo:
    def __init__(self, image):
        self.image = image
        self.intensity = {}
        self.minima = []
        self.peak_area = {}
        self.best_fit_line = {}
        self.r2 = {}
        self.plot_intensity = None
        self.plot_best_fit_line = None
    
class Calibration:
    def __init__(self, name: str, image: np.ndarray, concentration: list[float]):
        """
        Initialize the Calibration object.
        """
        self.name = name
        self.image = image
        self.concentration = concentration
        processed_image_by_peak, self.processed_image_result = image_processing.preprocessing_calibration(image)
        self.peaks = [PeakInfo(image) for image in processed_image_by_peak]
        
        self.__calculate_intensity()
        self.__calculate_minima()
        self.__calculate_peak_area()
        self.__calculate_fit_line()
        self.__plot_intensity()
        self.__plot_best_fit_line()
    
    def set_name(self, name):
        self.name = name
    
    def __calculate_intensity(self):
        """
        Calculate the intensity for each color channel in the preprocessed images.
        """
        for peak in self.peaks:
            intensity = {}
            image_rgb = cv2.split(cv2.cvtColor(peak.image, cv2.COLOR_BGR2RGB))
            for j, color in enumerate(['R', 'G', 'B']):
                total_intensity = np.sum(image_rgb[j], axis=0)
                count_color_pixel = np.sum(np.where(image_rgb[j] > 0, 1, 0), axis=0)
                safe_count_color_pixel = np.where(count_color_pixel == 0, 1, count_color_pixel)
                average_intensity = (255 - (total_intensity / safe_count_color_pixel)).astype(int)
                average_intensity[count_color_pixel == 0] = 0
                intensity[color] = average_intensity
            peak.intensity = intensity

    def __calculate_minima(self):
        """
        Calculate the minima points for intensity curves to determine peak boundaries.
        """
        for i, peak in enumerate(self.peaks):
            intensity = peak.intensity
            intensity_grayscale = 0.299*intensity['R'] + 0.587*intensity['G'] + 0.114*intensity['B']
            threshold_intensity = np.where(intensity_grayscale > 0, 1, 0)
            zero_to_non_zero = np.where((threshold_intensity[:-1] == 0) & (threshold_intensity[1:] != 0))[0]
            non_zero_to_zero = np.where((threshold_intensity[:-1] != 0) & (threshold_intensity[1:] == 0))[0] + 1
            minima_index = np.sort(np.concatenate((zero_to_non_zero, non_zero_to_zero)))
            self.peaks[i].minima = minima_index

    def __refine_minima(self, minima):
        """
        Refine the minima points to determine accurate peak boundaries.
        """
        new_minima = [(minima[i] + minima[i + 1]) // 2 for i in range(1, len(minima) - 1, 2)]
        new_minima.insert(0, 0)
        new_minima.append(self.image.shape[1] - 1)
        return new_minima

    def __calculate_peak_area(self):
        """
        Calculate the area under the intensity curve for each peak and color channel.
        """
        for peak in self.peaks:
            peak_area = {}
            for color in 'RGB':
                each_color_area = []
                intensity = peak.intensity[color]
                for index_minima in range(0, len(peak.minima)-1, 2):
                    each_color_area.append(np.trapz(intensity[peak.minima[index_minima]: peak.minima[index_minima+1]+1]))
                peak_area[color] = np.array(each_color_area)
            peak.peak_area = peak_area
    
    def __calculate_fit_line(self):
        """
        Calculate the best fit line for the peak areas vs. concentrations.
        """
        for peak in self.peaks:
            best_fit_line = {}
            r2 = {}
            for color in 'RGB':
                # Best fite line
                concentration = self.concentration[-len(peak.peak_area[color]):]
                best_fit_line[color] = tuple(np.polyfit(concentration, peak.peak_area[color], 1).astype(int))
                
                # R2
                actual = np.array(peak.peak_area[color])
                coef, const = best_fit_line[color]
                predict = np.array([coef*cont + const for cont in concentration])
                mean = np.mean(actual)
                ssr = sum(np.power(actual-predict, 2))
                sst = sum(np.power(actual-mean, 2))
                r2[color] = round(1 - ssr/sst, 3)
            peak.best_fit_line = best_fit_line
            peak.r2 = r2

    def __plot_intensity(self):
        x = np.arange(0, len(self.peaks[0].intensity['R']))
        for j, peak in enumerate(self.peaks):
            figure, axis = plt.subplots(nrows=3, ncols=1, figsize=(4, 12))
            rgb = ['Red', 'Green', 'Blue']
            for i, color in enumerate(['R', 'G', 'B']):
                intensity = peak.intensity[color]
                axis[i].plot(x, intensity, color=rgb[i])
                axis[i].scatter(peak.minima, np.take(intensity, peak.minima))
                axis[i].set_title(f'Peak {j+1}: {rgb[i]} Intensity')
                axis[i].set_xlabel('Pixel')
                axis[i].set_ylabel('Intensity')
                axis[i].set_ylim((0, 255))
                axis[i].grid()
            figure.tight_layout()
            peak.plot_intensity = figure
            plt.close()

    def __plot_best_fit_line(self):
        max_peak_area_count = max([len(peak.peak_area['R']) for peak in self.peaks])
        for j, peak in enumerate(self.peaks):
            figure, axis = plt.subplots(nrows=3, ncols=1, figsize=(3, 9))
            rgb = ['Red', 'Green', 'Blue']
            for i, color in enumerate(['R', 'G', 'B']):
                peak_area = peak.peak_area[color]
                while len(peak_area) < max_peak_area_count:
                    peak_area = np.insert(peak_area, 0, 0, axis=0)
                a, b = peak.best_fit_line[color]
                x = np.linspace(self.concentration[0], self.concentration[-1], 100)
                y = a*x + b
                r2 = round(peak.r2[color], 3)
                axis[i].scatter(self.concentration, peak_area, color=rgb[i])
                axis[i].plot(x, y, color=rgb[i], label=f'{a}c + {b}\nR2: {r2}') 
                axis[i].set_title(f'Peak {j+1}: {rgb[i]} Peak Area')
                axis[i].set_xlabel('Concentration')
                axis[i].set_ylabel('Peak Area')
                axis[i].grid()
                axis[i].legend()
            figure.tight_layout()
            peak.plot_best_fit_line = figure
            plt.close()