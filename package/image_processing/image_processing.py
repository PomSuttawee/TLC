from package.image_processing.util import *
import numpy as np
import cv2
from package.image_processing import parameter

def read_image(image_path: str) -> np.ndarray:
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found at {image_path}")
    return image

def resize_image(image: np.ndarray, scale: float) -> np.ndarray:
    if scale <= 0:
        raise ValueError("Scale must be a positive number")
    return cv2.resize(image, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

def select_area_from_image(image: np.ndarray) -> np.ndarray:
    x, y, width, height = cv2.selectROI(image, False)
    new_image = np.zeros((height, width))
    new_image = image[y:y+height, x:x+width]
    cv2.destroyAllWindows()
    return new_image

def preprocessing_mixture(image: np.ndarray) -> np.ndarray:
    image_original = image.copy()
    image = __to_grayscale(image)
    image = __apply_gaussian_blur(image)
    image = __apply_clahe(image)
    image = __apply_adaptive_thresholding(image, mode='Mixture')
    threshold_mask = __apply_morph(image)
    image_remove_background = __apply_mask(image_original, threshold_mask, 'and')
    return image_remove_background

def preprocessing_calibration(image: np.ndarray) -> list[np.ndarray]:
    image_original = image.copy()
    image_gray = __to_grayscale(image_original)
    image_blur = __apply_gaussian_blur(image_gray)
    image_clahe = __apply_clahe(image_blur)
    mask = __apply_adaptive_thresholding(image_clahe)
    mask_morph = __apply_morph(mask)
    image_remove_background = __apply_mask(image_original, mask_morph, operator='and')
    list_contour = __get_contour(mask_morph, min_area=500)
    list_box_horizontal = __get_bounding_box_horizontal(list_contour, image_original.shape[1])
    list_cropped_by_box_horizontal = __crop_by_bounding_box(image_remove_background, list_box_horizontal)
    image_with_contour = draw_contour(image_original, list_contour)
    image_with_bounding_box = draw_bounding_box(image_with_contour, list_box_horizontal)
    return list_cropped_by_box_horizontal, image_with_bounding_box

def draw_contour(image: np.ndarray, list_contour: list) -> np.ndarray:
    index = -1
    color = (0, 255, 255)
    thickness = 4
    line_type = cv2.LINE_AA
    new_image = image.copy()
    cv2.drawContours(new_image, list_contour, index, color, thickness, line_type)
    return new_image

def draw_bounding_box(image: np.ndarray, list_box: list) -> np.ndarray:
    new_image = image.copy()
    for i, box in enumerate(list_box):
        x, y, w, h = box
        top_left_point = (x, y)
        bottom_right_point = (x+w, y+h)
        color = (255, 0, 255)
        thickness = 4
        new_image = cv2.rectangle(new_image, top_left_point, bottom_right_point, color, thickness)
        
        new_image = cv2.putText(new_image, f"Peak {i+1}", (10, y+h-10), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0), 6)
    return new_image

def __to_grayscale(image_rgb: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image_rgb, cv2.COLOR_BGR2GRAY)

def __apply_gaussian_blur(image: np.ndarray) -> np.ndarray:
    kernel_size = parameter.GAUSSIAN_BLUR_KERNEL_SIZE
    return cv2.GaussianBlur(image, kernel_size, 3)

def __apply_clahe(image: np.ndarray) -> np.ndarray:
    clip_limit = parameter.CLAHE_CLIP_LIMIT
    tile_grid_size = parameter.CLAHE_GRID_SIZE
    clahe_object = cv2.createCLAHE(clip_limit, tile_grid_size)
    return clahe_object.apply(image)

def __apply_adaptive_thresholding(image: np.ndarray, mode='Calibration') -> np.ndarray:
    max_value = 255
    adaptive_method = cv2.ADAPTIVE_THRESH_MEAN_C
    threshold_type = cv2.THRESH_BINARY_INV
    block_cnt = 11 if mode == 'Calibration' else 1
    block_size = image.shape[0] // block_cnt  if (image.shape[0] // block_cnt) % 2 == 1 else image.shape[0] // block_cnt + 1
    constant = parameter.ADAPTIVE_THRESHOLDING_CONSTANT
    return cv2.adaptiveThreshold(image, max_value, adaptive_method, threshold_type, block_size, constant)

def __apply_morph(image: np.ndarray) -> np.ndarray:
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, parameter.MORPH_KERNEL_SIZE))

def __apply_mask(image: np.ndarray, mask: np.ndarray, operator: str) -> np.ndarray:
    mask_rgb = cv2.merge([mask, mask, mask])
    if operator == 'and':
        return cv2.bitwise_and(image, mask_rgb)
    elif operator == 'or':
        return cv2.bitwise_or(image, mask_rgb)
    return KeyError

def __get_contour(image: np.ndarray, min_area: int) -> list:
    mode = cv2.RETR_EXTERNAL
    method = cv2.CHAIN_APPROX_NONE
    list_contour, _ = cv2.findContours(image, mode, method)
    if min_area < 0:
        return list_contour
    return __remove_contour(list_contour, min_area)

def __remove_contour(list_contour: list, min_area: int) -> list:
    new_list_contour = []
    for contour in list_contour:
        if cv2.contourArea(contour) > min_area:
            new_list_contour.append(contour)
    return new_list_contour

def __get_bounding_box_vertical(list_contour: list, h_max: int) -> list:
    list_box = []
    for contour in list_contour:
        x, y, w ,h = cv2.boundingRect(contour)
        list_box.append((x, 0, w, h_max))
    return groupBoundingBox(list_box)

def __get_bounding_box_horizontal(list_contour: list, w_max: int) -> list:
    list_box = []
    for contour in list_contour:
        x, y, w ,h = cv2.boundingRect(contour)
        list_box.append((0, y, w_max, h))
    grouped_list_box = sorted(groupBoundingBox(list_box), key=lambda x: x[1], reverse=True)
    return grouped_list_box

def __crop_by_bounding_box(image: np.ndarray, list_bounding_box: list) -> list:
    list_cropped_by_bounding_box = []
    for box in list_bounding_box:
        x, y, w, h = box
        list_cropped_by_bounding_box.append(image[y:y+h, x:x+w])
    return list_cropped_by_bounding_box