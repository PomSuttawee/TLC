from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QListWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QLineEdit, QTreeWidget, QTreeWidgetItem, QAbstractItemView
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from package.image_processing.image_processing import read_image
from package.tlc_class.calibration import Calibration
from package.tlc_class.mixture import Mixture
from package.tlc_class.mixture_hack import MixtureHack

from PIL.ImageQt import ImageQt
from PIL import Image 
import cv2
import matplotlib
matplotlib.use('Qt5Agg')

class WidgetMixtureHack(QWidget):
    def __init__(self):
        super().__init__()
        self.dict_calibration_object = {}
        self.dict_mixture_object = {}
        self.init_main_layout()
    
    def init_main_layout(self):
        main_layout = QHBoxLayout()
        self.init_left_layout()
        self.init_middle_layout()
        self.init_right_layout()
        main_layout.addLayout(self.v_layout_left, 1)
        main_layout.addLayout(self.v_layout_middle, 2)
        main_layout.addLayout(self.v_layout_right, 2)
        self.setLayout(main_layout)
    
    def init_left_layout(self):
        self.v_layout_left = QVBoxLayout()
        ## Button
        button_hack = QPushButton("Calculate Concentration")
        button_hack.clicked.connect(self.hack)
        ## Mixture List Widget
        self.list_widget_mixture_object = QListWidget()
        ## Calibration List Widget
        self.list_widget_calibration_object = QListWidget()
        self.list_widget_calibration_object.setSelectionMode(QAbstractItemView.MultiSelection)
        self.v_layout_left.addWidget(button_hack)
        self.v_layout_left.addWidget(self.list_widget_mixture_object, 1)
        self.v_layout_left.addWidget(self.list_widget_calibration_object, 1)
    
    def init_middle_layout(self):
        self.v_layout_middle = QVBoxLayout()
        self.label_hack_data = QLabel()
        self.v_layout_middle.addWidget(self.label_hack_data)
        
    def init_right_layout(self):
        self.v_layout_right = QVBoxLayout()
        self.label_answer = QLabel()
        self.v_layout_right.addWidget(self.label_answer)
    
    def hack(self):
        selected_mixture_name = self.list_widget_mixture_object.currentItem().text()
        selected_calibration_name = [item.text() for item in self.list_widget_calibration_object.selectedItems()]
        
        selected_mixture_object = self.dict_mixture_object[selected_mixture_name]
        list_selected_calibration_object = [self.dict_calibration_object[name] for name in selected_calibration_name]
        
        mh = MixtureHack(selected_mixture_object, list_selected_calibration_object)
        text_answer = ''
        for i, color in enumerate('RGB'):
            text_answer += mh.solve_equation(list_peak_index=[1], color=color)

        self.label_answer.setText(text_answer)
        # mh.solve_equation([1, 2], 'R')
        # mh.solve_equation([1, 2], 'G')
        # mh.solve_equation([1, 2], 'B')
        # mh.solve_equation([1, 2, 3], 'R')
        # mh.solve_equation([1, 2, 3], 'G')
        # mh.solve_equation([1, 2, 3], 'B')
        
        text_data = f'Mixture: {selected_mixture_name}\n\tPeak Area: {selected_mixture_object.peak_area}'
        for calibration_object in list_selected_calibration_object:
            text_data += f'\n\nCalibration: {calibration_object.name}'
            for i, peak in enumerate(calibration_object.peaks):
                text_data += f'\n\tPeak {i+1}:\n\t\tBest fit line: {peak.best_fit_line}\n\t\tR2: {peak.r2}'
            
        self.label_hack_data.setText(text_data)
    
    # SIGNAL
    def on_signal_from_calibration(self, dict_calibration_object: dict[str, Calibration]):
        self.label_hack_data.clear()
        self.dict_calibration_object = dict_calibration_object
        self.list_widget_calibration_object.clear()
        for name in self.dict_calibration_object.keys():
            self.list_widget_calibration_object.addItem(name)
    
    def on_signal_from_mixture(self, dict_mixture_object: dict[str, Mixture]):
        self.label_hack_data.clear()
        self.dict_mixture_object = dict_mixture_object
        self.list_widget_mixture_object.clear()
        for name in self.dict_mixture_object.keys():
            self.list_widget_mixture_object.addItem(name)