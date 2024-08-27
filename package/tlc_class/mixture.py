import cv2
import numpy as np
import matplotlib.pyplot as plt
from package.image_processing import image_processing

class Mixture:
    """
    Initialize the Mixture object.
    """
    def __init__(self, image: np.ndarray):
        self.image = image
        self.processed_image = self._preprocess_image(image)
        self.intensity = {}
        self.peak_area = {}
        
        self._calculate_intensity()
        minima = self._calculate_minima()
        new_minima = self._refine_minima(minima)
        self._calculate_peak_area(new_minima)

    def _preprocess_image(self, image):
        """
        Preprocess the image for analysis.
        """
        preprocessed_image = image_processing.preprocessing_mixture(image)
        return preprocessed_image

    def _calculate_intensity(self):
        """
        Calculate the intensity for each color channel in the preprocessed images.
        """
        intensity = {}
        image_rgb = cv2.split(cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB))
        for i, color in enumerate(['R', 'G', 'B']):
            total_intensity = np.sum(image_rgb[i], axis=0)
            count_color_pixel = np.sum(np.where(image_rgb[i] > 0, 1, 0), axis=0)
            average_intensity = np.where(count_color_pixel > 0, (255 - (total_intensity / count_color_pixel)).astype(int), 0)
            intensity[color] = average_intensity
        self.intensity = intensity

    def _calculate_minima(self):
        """
        Calculate the minima points for intensity curves to determine peak boundaries.
        """
        intensity_grayscale = 0.299*self.intensity['R'] + 0.587*self.intensity['G'] + 0.114*self.intensity['B']
        threshold_intensity = np.where(intensity_grayscale > 0, 1, 0)
        zero_to_non_zero = np.where((threshold_intensity[:-1] == 0) & (threshold_intensity[1:] != 0))[0]
        non_zero_to_zero = np.where((threshold_intensity[:-1] != 0) & (threshold_intensity[1:] == 0))[0] + 1
        minima_index = np.sort(np.concatenate((zero_to_non_zero, non_zero_to_zero)))
        return minima_index

    def _refine_minima(self, minima):
        """
        Refine the minima points to determine accurate peak boundaries.
        """
        new_minima = [(minima[i] + minima[i + 1]) // 2 for i in range(1, len(minima) - 1, 2)]
        new_minima.insert(0, 0)
        new_minima.append(self.image.shape[1] - 1)
        return new_minima

    def _calculate_peak_area(self, minima):
        """
        Calculate the area under the intensity curve for each peak and color channel.
        """
        peak_area = {}
        for color in 'RGB':
            each_color_area = []
            intensity = self.intensity[color]
            for index_minima in range(0, len(minima)-1, 1):
                each_color_area.append(np.trapz(intensity[minima[index_minima]: minima[index_minima + 1] + 1]))
            peak_area[color] = np.array(each_color_area)
        self.peak_area = peak_area