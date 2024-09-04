import cv2
import numpy as np
import matplotlib.pyplot as plt
from package.image_processing import image_processing
from scipy.signal import find_peaks

class Mixture:
    """
    Initialize the Mixture object.
    """
    def __init__(self, name: str, image: np.ndarray):
        self.name = name
        self.image = image
        self.processed_image = None
        self.intensity = {}
        self.peak_area = {}
        self.plot_intensity = None
        
        self.__preprocess_image()
        self.__calculate_intensity_rgb()
        minima = self.__calculate_minima()
        self.minima_refined = self.__refine_minima(minima)
        self.__calculate_peak_area_rgb()
        self.__plot_intensity()

    def set_name(self, name: str):
        self.name = name
    
    def __preprocess_image(self):
        """ Preprocess the image for analysis. """
        self.processed_image = image_processing.preprocessing_mixture(self.image)

    def __calculate_intensity_rgb(self):
        image_rgb = cv2.split(cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB))
        self.intensity = {color: self.__calculate_intensity_single_channel(image_rgb[i]) for i, color in enumerate('RGB')}
    
    def __calculate_intensity_single_channel(self, image):
        total_intensity = np.sum(image, axis=0)
        count_color_pixel = np.sum(np.where(image > 0, 1, 0), axis=0)
        safe_count_color_pixel = np.where(count_color_pixel == 0, 1, count_color_pixel)
        average_intensity = (255 - (total_intensity / safe_count_color_pixel)).astype(int)
        average_intensity[count_color_pixel == 0] = 0
        return average_intensity

    def __calculate_minima(self):
        """ Calculate the minima points for intensity curves to determine peak boundaries. """
        intensity_grayscale = 255 - (0.299*self.intensity['R'] + 0.587*self.intensity['G'] + 0.114*self.intensity['B'])
        minima_index, _ = find_peaks(intensity_grayscale, prominence=2)
        return minima_index

    def __refine_minima(self, minima: list):
        """ Refine the minima points to determine accurate peak boundaries. """
        new_minima = list(minima.copy())
        new_minima.insert(0, 0)
        new_minima.append(self.image.shape[1] - 1)
        return new_minima

    def __calculate_peak_area_rgb(self):
        """ Calculate the area under the intensity curve for each peak and color channel. """
        self.peak_area = {color: self.__calculate_peak_area_single_channel(self.intensity[color]) for color in 'RGB'}
    
    def __calculate_peak_area_single_channel(self, intensity):
        peak_area = []
        for index_minima in range(0, len(self.minima_refined)-1, 1):
            peak_area.append(np.trapz(intensity[self.minima_refined[index_minima]: self.minima_refined[index_minima + 1] + 1]))
        return np.array(peak_area)
    
    def __plot_intensity(self):
        x = np.arange(0, len(self.intensity['R']))
        figure, axis = plt.subplots(nrows=3, ncols=1, figsize=(4, 12))
        rgb = ['Red', 'Green', 'Blue']
        for i, color in enumerate(['R', 'G', 'B']):
            intensity = self.intensity[color]
            axis[i].plot(x, intensity, color=rgb[i])
            axis[i].scatter(self.minima_refined, np.take(intensity, self.minima_refined))
            axis[i].set_title(f'{rgb[i]} Intensity')
            axis[i].set_xlabel('Pixel')
            axis[i].set_ylabel('Intensity')
            # axis[i].set_ylim((0, 255))
            axis[i].grid()
        figure.tight_layout()
        self.plot_intensity = figure
        plt.close()