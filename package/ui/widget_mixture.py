from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from package.image_processing.image_processing import read_image
from package.tlc_class.mixture import Mixture

from PIL.ImageQt import ImageQt
from PIL import Image
import numpy as np
import cv2
import matplotlib
matplotlib.use('Qt5Agg')

class WidgetMixture(QWidget):
    data_sent = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.dict_input_path = {}
        self.dict_mixture_object = {}
        self.init_main_layout()
        
    def init_main_layout(self):
        self.main_layout = QHBoxLayout()
        self.init_left_layout()
        self.init_middle_layout()
        self.v_layout_right = QVBoxLayout()
        self.main_layout.addLayout(self.v_layout_left, 1)
        self.main_layout.addLayout(self.v_layout_middle, 2)
        self.main_layout.addLayout(self.v_layout_right, 2)
        self.setLayout(self.main_layout)
    
    def init_left_layout(self):
        self.v_layout_left = QVBoxLayout()
        # Button
        h_layout_button = QHBoxLayout()
        button_upload = QPushButton("Upload")
        button_upload.clicked.connect(self.upload_image)
        button_delete = QPushButton("Delete")
        button_delete.clicked.connect(self.delete_image)
        button_calibrate = QPushButton("Process")
        button_calibrate.clicked.connect(self.process_image)
        h_layout_button.addWidget(button_upload)
        h_layout_button.addWidget(button_delete)
        h_layout_button.addWidget(button_calibrate)
        # Input Path
        self.list_widget_input_path = QListWidget()
        # Mixture Data
        self.list_widget_mixture_data = QListWidget()
        self.list_widget_mixture_data.currentItemChanged.connect(self.show_mixture_data)
        self.v_layout_left.addLayout(h_layout_button)
        self.v_layout_left.addWidget(self.list_widget_input_path, 1)
        self.v_layout_left.addWidget(self.list_widget_mixture_data, 4)
        
    def init_middle_layout(self):
        self.v_layout_middle = QVBoxLayout()
        # Original Image
        self.label_image_original = QLabel()
        self.label_image_original.setAlignment(Qt.AlignTop)
        # Processed Image
        self.label_image_processed = QLabel()
        self.label_image_processed.setAlignment(Qt.AlignTop)
        # Mixture Data Label
        self.label_mixture_data = QLabel()
        self.v_layout_middle.addWidget(self.label_image_original, 1)
        self.v_layout_middle.addWidget(self.label_image_processed, 1)
        self.v_layout_middle.addWidget(self.label_mixture_data, 1)
    
    def upload_image(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Open file", "C:\\Users\\Suttawee\\Desktop\\TLC\\Input", "Image files (*.png *.jpg *.gif *.svg)")
        for path in files:
            image_name = path.split('/')[-1]
            self.dict_input_path[image_name] = path
            self.list_widget_input_path.addItem(image_name)
            self.dict_mixture_object[image_name] = None

    def delete_image(self):
        image_name = self.list_widget_input_path.currentItem().text()
        self.dict_mixture_object.pop(image_name)
        self.dict_input_path.pop(image_name)
        self.list_widget_input_path.takeItem(self.list_widget_input_path.currentRow())

    def process_image(self):
        self.list_widget_mixture_data.clear()
        for name, path in self.dict_input_path.items():
            image = read_image(path)
            mixture_object = Mixture(name, image)
            self.dict_mixture_object[name] = mixture_object
            self.list_widget_mixture_data.addItem(name)
        
        # Send Signal
        self.data_sent.emit(self.dict_mixture_object)
    
    def show_mixture_data(self, item: QListWidgetItem):
        name = item.text()
        mixture_object = self.dict_mixture_object[name]
        
        pix = self.__convert_cv2_to_qpixmap(mixture_object.image)
        self.label_image_original.setPixmap(pix)
        
        pix = self.__convert_cv2_to_qpixmap(mixture_object.processed_image)
        self.label_image_processed.setPixmap(pix)
        
        data_mixture = f"Mixture: {name}\nPeak Count: {len(mixture_object.peak_area['R'])}\nPeak Area:\n\tR: {mixture_object.peak_area['R']}\n\tG: {mixture_object.peak_area['G']}\n\tB: {mixture_object.peak_area['B']}"
        self.label_mixture_data.setText(data_mixture)

        plot = mixture_object.plot_intensity
        if self.v_layout_right.count() != 0:
            canvas = self.v_layout_right.takeAt(0)
            canvas.widget().deleteLater()
        canvas_intensity = FigureCanvasQTAgg(plot)
        self.v_layout_right.addWidget(canvas_intensity)
    
    def __convert_cv2_to_qpixmap(self, cv_image: np.ndarray):
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        PIL_image = Image.fromarray(rgb_image).convert('RGB')
        pix = QPixmap.fromImage(ImageQt(PIL_image))
        return pix.scaledToWidth(500)