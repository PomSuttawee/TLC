import cv2
import numpy as np
import matplotlib.pyplot as plt
import image_processing

class Calibration:
    def __init__(self, image, concentration):
        """
        Initialize the Calibration object.

        Parameters:
        - image: The input image for calibration.
        - concentration: List of concentrations corresponding to the peaks.
        """
        self.image = image
        self.concentration = np.array(concentration)
        self.preprocessed_image = image_processing.preprocessing_calibration(image, remove_background=True)
        self.peak_info = {f'Peak {i+1}': {} for i in range(len(self.preprocessed_image))}
        self.plot = {}
        
        self._calculate_intensity()
        best_minima = self.peak_info[self._calculate_minima()]['Minima']
        new_best_minima = [(best_minima[i] + best_minima[i+1]) // 2 for i in range(1, len(best_minima)-1, 2)]
        new_best_minima.insert(0, 0)
        new_best_minima.insert(len(new_best_minima), self.image.shape[1]-1)
        self.best_minima = np.array(new_best_minima)
        
        self._calculate_peak_area()
        self._calculate_fit_line()

    def plot_intensity(self):
        intensity_plot = {}
        x = np.arange(0, len(self.peak_info['Peak 1']['Intensity']['R']))
        for peak, info in self.peak_info.items():
            figure, axis = plt.subplots(nrows=3, ncols=1, figsize=(5, 12))
            rgb = ['Red', 'Green', 'Blue']
            for i, color in enumerate(['R', 'G', 'B']):
                intensity = info['Intensity'][color]
                axis[i].plot(x, intensity, color=rgb[i])
                axis[i].set_title(f'{peak}: {rgb[i]} Intensity')
                axis[i].set_xlabel('Pixel')
                axis[i].set_ylabel('Intensity')
                axis[i].set_ylim((0, 255))
                axis[i].grid()
            figure.tight_layout()
            intensity_plot[peak] = figure
        self.plot['Intensity'] = intensity_plot
    
    def plot_peak_area(self):
        peak_area_plot = {}
        for peak, info in self.peak_info.items():
            figure, axis = plt.subplots(nrows=3, ncols=1, figsize=(5, 12))
            rgb = ['Red', 'Green', 'Blue']
            for i, color in enumerate(['R', 'G', 'B']):
                peak_area = info['Peak_area'][color]
                a = self.peak_info[peak]['Best_fit_line'][color][0]
                b = self.peak_info[peak]['Best_fit_line'][color][1]
                x = np.linspace(self.concentration[0], self.concentration[-1], 100)
                y = a*x + b
                axis[i].scatter(self.concentration, peak_area, color=rgb[i])
                axis[i].plot(x, y, color=rgb[i], label=f'{a}x + {b}') 
                axis[i].set_title(f'{peak}: {rgb[i]} Peak Area')
                axis[i].set_xlabel('Concentration')
                axis[i].set_ylabel('Peak Area')
                axis[i].grid()
                axis[i].legend()
            figure.tight_layout()
            peak_area_plot[peak] = figure
        self.plot['Peak_area'] = peak_area_plot

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
            self.peak_info[f'Peak {i+1}']['Intensity'] = intensity

    def _calculate_minima(self):
        """
        Calculate the minima points for intensity curves to determine peak boundaries.
        """
        max_minima_count = -1
        max_minima_peak = ''
        for peak, info in self.peak_info.items():
            intensity = info['Intensity']
            intensity_grayscale = 0.299*intensity['R'] + 0.587*intensity['G'] + 0.114*intensity['B']
            threshold_intensity = np.where(intensity_grayscale > 0, 1, 0)
            zero_to_non_zero = np.where((threshold_intensity[:-1] == 0) & (threshold_intensity[1:] != 0))[0]
            non_zero_to_zero = np.where((threshold_intensity[:-1] != 0) & (threshold_intensity[1:] == 0))[0] + 1
            minima_index = np.sort(np.concatenate((zero_to_non_zero, non_zero_to_zero)))
            self.peak_info[peak]['Minima'] = minima_index
            if max_minima_count < len(minima_index):
                max_minima_peak = peak
                max_minima_count = len(minima_index)
        return max_minima_peak

    def _calculate_peak_area(self):
        """
        Calculate the area under the intensity curve for each peak and color channel.
        """
        for peak in self.peak_info:
            peak_area = {}
            for color in 'RGB':
                each_color_area = []
                intensity = self.peak_info[peak]['Intensity'][color]
                for index_minima in range(0, len(self.best_minima)-1, 1):
                    each_color_area.append(np.trapz(intensity[self.best_minima[index_minima]: self.best_minima[index_minima+1]+1]))
                peak_area[color] = np.array(each_color_area)
            self.peak_info[peak]['Peak_area'] = peak_area
    
    def _calculate_fit_line(self):
        """
        Calculate the best fit line for the peak areas vs. concentrations.
        """
        for peak in self.peak_info:
            best_fit_line = {}
            for color in 'RGB':
                peak_index = np.nonzero(self.peak_info[peak]['Peak_area'][color])
                best_fit_line[color] = tuple(np.polyfit(self.concentration[peak_index], self.peak_info[peak]['Peak_area'][color][peak_index], 1).astype(int))
            self.peak_info[peak]['Best_fit_line'] = best_fit_line