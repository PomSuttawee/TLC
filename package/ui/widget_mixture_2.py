from PIL.ImageQt import ImageQt
from PIL import Image 
import cv2
import matplotlib
matplotlib.use('Qt5Agg')

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QListWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem, QAbstractItemView
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from package.image_processing.image_processing import read_image
from package.tlc_class.mixture import Mixture

class WidgetMixture(QWidget):
    def __init__(self):
        super().__init__()
        self.list_input_path = []
        self.dict_mixture_object = {}
        self.list_calibration_object = []
        
        main_layout = QHBoxLayout()
        
        # Left Vertical Box
        v_layout_left = QVBoxLayout()
        
        ## Button
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
        
        ## Input Path
        self.list_widget_input_path = QListWidget()
        self.list_widget_input_path.currentItemChanged.connect(self.show_image)
        
        ## Calibration Object
        self.tree_widget_calibration_object = QTreeWidget()
        self.tree_widget_calibration_object.setColumnCount(1)
        self.tree_widget_calibration_object.setHeaderLabel("Calibration")
        self.tree_widget_calibration_object.setSelectionMode(QAbstractItemView.MultiSelection)
        
        v_layout_left.addLayout(h_layout_button)
        v_layout_left.addWidget(self.list_widget_input_path, 1)
        v_layout_left.addWidget(self.tree_widget_calibration_object, 4)
        
        # Middle Vertical Box
        v_layout_middle = QVBoxLayout()
        
        ## Original Image
        self.label_image_original = QLabel()
        self.label_image_original.setAlignment(Qt.AlignTop)
        
        v_layout_middle.addWidget(self.label_image_original)
        
        main_layout.addLayout(v_layout_left, 1)
        main_layout.addLayout(v_layout_middle, 1)
        self.setLayout(main_layout)
        
    
    def upload_image(self):
        file_name = QFileDialog.getOpenFileName(self, "Open file", "C:\\Users\\Suttawee\\Desktop\\Mixture-Hack-main\\Project\\Input", "Image files (*.png *.jpg *.gif *.svg)")
        self.list_input_path.append(file_name[0])
        self.list_widget_input_path.addItem(file_name[0])
        self.dict_mixture_object[file_name[0]] = None

    def delete_image(self):
        path = self.list_widget_input_path.currentItem().text()
        self.dict_mixture_object.pop(path)
        self.list_input_path.remove(path)
        self.list_widget_input_path.takeItem(self.list_widget_input_path.currentRow())

    def process_image(self):
        for calibration_object in self.list_calibration_object:
            best_peak = -1
            max_r2 = -1
            for j, peak in enumerate(calibration_object.peaks):
                average_r2 = (peak.r2["R"] + peak.r2["G"] + peak.r2["B"]) / 3
                if average_r2 > max_r2:
                    best_peak = j

    
    def show_image(self, item):
        pix = QPixmap(item.text())
        pix = pix.scaledToWidth(400)
        self.label_image_original.setPixmap(pix)
        
    def on_signal_from_calibration(self, list_calibration_object):
        self.list_calibration_object = list_calibration_object
        self.tree_widget_calibration_object.clear()
        
        items = []
        for i, calibration_object in enumerate(self.list_calibration_object):
            item = QTreeWidgetItem([f"Calibration {i+1}"])
            for j, peak in enumerate(calibration_object.peaks):
                    child = QTreeWidgetItem([f"Peak {j+1}"])
                    item.addChild(child)
            items.append(item)
            self.tree_widget_calibration_object.addTopLevelItems(items)