import cv2
import numpy as np
import matplotlib.pyplot as plt
import image_processing
import ui_1

class PeakInfo:
    def __init__(self):
        self.intensity = {}
        self.minima = []
        self.peak_area = {}
        self.concentration = []
        self.best_fit_line = {}
        
class Calibration:
    def __init__(self, image):
        """
        Initialize the Calibration object.

        Parameters:
        - image: The input image for calibration.
        - concentration: List of concentrations corresponding to the peaks.
        """
        self.image = image
        self.preprocessed_image = image_processing.preprocessing_calibration(image)
        self.peaks = [PeakInfo() for _ in range(len(self.preprocessed_image))]
        self.plot = {}
        
        self._calculate_intensity()
        print('\n\n### Intensity')
        for i, peak in enumerate(self.peaks):
            print(f'\tPeak {i+1}: {peak.intensity}')
        
        self._calculate_minima()
        print('\n### Minima')
        for i, peak in enumerate(self.peaks):
            print(f'\tPeak {i+1}: {peak.minima}')
        # refined_best_minima = self._refine_minima(best_minima)
        
        self._calculate_peak_area()
        print('\n### Peak Area')
        for i, peak in enumerate(self.peaks):
            print(f'\tPeak {i+1}:')
            for color in 'RGB':
                print(f'\t\t{color}: {peak.peak_area[color]}')
        

    def _calculate_intensity(self):
        """
        Calculate the intensity for each color channel in the preprocessed images.
        """
        for i, image in enumerate(self.preprocessed_image):
            intensity = {}
            image_rgb = cv2.split(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            for j, color in enumerate(['R', 'G', 'B']):
                total_intensity = np.sum(image_rgb[j], axis=0)
                count_color_pixel = np.sum(np.where(image_rgb[j] > 0, 1, 0), axis=0)
                average_intensity = np.where(count_color_pixel > 0, (255 - (total_intensity / count_color_pixel)).astype(int), 0)
                intensity[color] = average_intensity
            self.peaks[i].intensity = intensity

    def _calculate_minima(self):
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

    def _refine_minima(self, minima):
        """
        Refine the minima points to determine accurate peak boundaries.

        Parameters:
        - minima: Initial minima points.

        Returns:
        - new_minima: Refined minima points.
        """
        new_minima = [(minima[i] + minima[i + 1]) // 2 for i in range(1, len(minima) - 1, 2)]
        new_minima.insert(0, 0)
        new_minima.append(self.image.shape[1] - 1)
        return new_minima

    def _calculate_peak_area(self):
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
    
    def calculate_fit_line(self):
        """
        Calculate the best fit line for the peak areas vs. concentrations.
        """
        for peak in self.peaks:
            best_fit_line = {}
            for color in 'RGB':
                best_fit_line[color] = tuple(np.polyfit(peak.concentration, peak.peak_area[color], 1).astype(int))
            peak.best_fit_line = best_fit_line
        
        print('\n### Best Fit Line')
        for i, peak in enumerate(self.peaks):
            print(f'\tPeak {i+1}:')
            for color in 'RGB':
                print(f'\t\t{color}: {peak.best_fit_line[color]}')

    def plot_intensity(self):
        intensity_plot = {}
        x = np.arange(0, len(self.peaks[0].intensity['R']))
        for j, peak in enumerate(self.peaks):
            figure, axis = plt.subplots(nrows=3, ncols=1, figsize=(5, 12))
            rgb = ['Red', 'Green', 'Blue']
            for i, color in enumerate(['R', 'G', 'B']):
                intensity = peak.intensity[color]
                axis[i].plot(x, intensity, color=rgb[i])
                axis[i].scatter(self.best_minima, np.take(intensity, self.best_minima))
                axis[i].set_title(f'Peak {j}: {rgb[i]} Intensity')
                axis[i].set_xlabel('Pixel')
                axis[i].set_ylabel('Intensity')
                axis[i].set_ylim((0, 255))
                axis[i].grid()
            figure.tight_layout()
            intensity_plot[peak] = figure
        self.plot['Intensity'] = intensity_plot
    
    def plot_peak_area(self):
        peak_area_plot = {}
        for j, peak in enumerate(self.peaks):
            figure, axis = plt.subplots(nrows=3, ncols=1, figsize=(5, 12))
            rgb = ['Red', 'Green', 'Blue']
            for i, color in enumerate(['R', 'G', 'B']):
                peak_area = peak.peak_area[color]
                a, b = peak.best_fit_line[color]
                x = np.linspace(self.concentration[0], self.concentration[-1], 100)
                y = a*x + b
                axis[i].scatter(self.concentration, peak_area, color=rgb[i])
                axis[i].plot(x, y, color=rgb[i], label=f'{a}x + {b}') 
                axis[i].set_title(f'Peak {j}: {rgb[i]} Peak Area')
                axis[i].set_xlabel('Concentration')
                axis[i].set_ylabel('Peak Area')
                axis[i].grid()
                axis[i].legend()
            figure.tight_layout()
            peak_area_plot[peak] = figure
        self.plot['Peak_area'] = peak_area_plot
