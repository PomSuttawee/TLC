from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QListWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QAbstractItemView, QDoubleSpinBox
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
        self.mixture_hack_object = None
        self.init_main_layout()
    
    def init_main_layout(self):
        main_layout = QHBoxLayout()
        self.init_left_layout()
        self.init_middle_layout()
        self.init_right_layout()
        main_layout.addLayout(self.v_layout_left, 1)
        main_layout.addLayout(self.v_layout_middle, 1)
        main_layout.addLayout(self.v_layout_right, 3)
        self.setLayout(main_layout)
    
    def init_left_layout(self):
        self.v_layout_left = QVBoxLayout()
        ## Button
        button_hack = QPushButton("Calculate Concentration")
        button_hack.clicked.connect(self.calculate_concentration)
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
        self.layout_canvas = QVBoxLayout()
        self.layout_spinbox = QHBoxLayout()
        self.v_layout_right.addLayout(self.layout_canvas, 5)
        self.v_layout_right.addLayout(self.layout_spinbox, 1)
    
    def calculate_concentration(self):
        selected_mixture_name = self.list_widget_mixture_object.currentItem().text()
        selected_calibration_name = [item.text() for item in self.list_widget_calibration_object.selectedItems()]
        
        selected_mixture_object = self.dict_mixture_object[selected_mixture_name]
        list_selected_calibration_object = [self.dict_calibration_object[name] for name in selected_calibration_name]
        
        self.mixture_hack_object = MixtureHack(selected_mixture_object, list_selected_calibration_object)
        log = ''
        for color in 'RGB':
            log += f'============ {color} Channel ============\n'
            log += self.mixture_hack_object.solve_equation(color=color)
        self.label_hack_data.setText(log)
        
        self.mixture_hack_object.plot_answer()
        plot = self.mixture_hack_object.plot_mixture
        if self.layout_canvas.count() != 0:
            canvas = self.layout_canvas.takeAt(0)
            canvas.widget().deleteLater()
        canvas_mixture = FigureCanvasQTAgg(plot)
        self.layout_canvas.addWidget(canvas_mixture)
        
        self.list_spinbox = []
        for calibration in self.dict_calibration_object.keys():
            label_spinbox_name = QLabel(calibration)
            spinbox = QDoubleSpinBox(self)
            spinbox.setRange(0, 100)
            spinbox.setValue(self.mixture_hack_object.solution['R'][calibration])
            self.layout_spinbox.addWidget(label_spinbox_name)
            self.layout_spinbox.addWidget(spinbox)
    
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