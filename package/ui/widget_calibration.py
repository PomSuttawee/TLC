from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QListWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QLineEdit, QTreeWidget, QTreeWidgetItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from package.image_processing.image_processing import read_image
from package.tlc_class.calibration import Calibration

from PIL.ImageQt import ImageQt
from PIL import Image
import numpy as np
import cv2
import matplotlib
matplotlib.use('Qt5Agg')

class WidgetCalibration(QWidget):
    data_sent = Signal(dict)

    def __init__(self):
        super().__init__()
        self.dict_input_path = {}
        self.dict_calibration_object = {}
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
        button_calibrate = QPushButton("Calibrate")
        button_calibrate.clicked.connect(self.calibrate_image)
        h_layout_button.addWidget(button_upload)
        h_layout_button.addWidget(button_delete)
        h_layout_button.addWidget(button_calibrate)
        # Concentration Input
        h_layout_concentration = QHBoxLayout()
        label_concentration = QLabel("Concentration: ")
        self.line_edit_concentration = QLineEdit()
        self.line_edit_concentration.setText("5 8.33 16.67 33.33 50 66.67 83.33 100")
        h_layout_concentration.addWidget(label_concentration)
        h_layout_concentration.addWidget(self.line_edit_concentration)
        # Input Path
        self.list_widget_input_path = QListWidget()
        # Calibration Data
        self.tree_widget_calibration_data = QTreeWidget()
        self.tree_widget_calibration_data.setColumnCount(1)
        self.tree_widget_calibration_data.setHeaderLabel("Calibration Data")
        self.tree_widget_calibration_data.itemClicked.connect(self.show_calibration_data)
        self.v_layout_left.addLayout(h_layout_button)
        self.v_layout_left.addLayout(h_layout_concentration)
        self.v_layout_left.addWidget(self.list_widget_input_path, 1)
        self.v_layout_left.addWidget(self.tree_widget_calibration_data, 4)
        
    def init_middle_layout(self):
        self.v_layout_middle = QVBoxLayout()
        # Original Image
        self.label_image_original = QLabel()
        self.label_image_original.setAlignment(Qt.AlignTop)
        # Processed Image
        self.label_image_processed = QLabel()
        self.label_image_processed .setAlignment(Qt.AlignTop)
        # Peak Image
        self.label_image_peak = QLabel()
        self.label_image_peak.setAlignment(Qt.AlignTop)
        # Peak Data Label
        self.label_peak_data = QLabel()
        self.v_layout_middle.addWidget(self.label_image_original, 1)
        self.v_layout_middle.addWidget(self.label_image_processed, 1)
        self.v_layout_middle.addWidget(self.label_image_peak, 1)
        self.v_layout_middle.addWidget(self.label_peak_data, 1)
    
    def upload_image(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Open file", "C:\\Users\\Suttawee\\Desktop\\TLC\\Input", "Image files (*.png *.jpg *.gif *.svg)")
        for path in files:
            image_name = path.split('/')[-1]
            self.dict_input_path[image_name] = path
            self.list_widget_input_path.addItem(image_name)
            self.dict_calibration_object[image_name] = None

    def delete_image(self):
        image_name = self.list_widget_input_path.currentItem().text()
        self.dict_calibration_object.pop(image_name)
        self.dict_input_path.pop(image_name)
        self.list_widget_input_path.takeItem(self.list_widget_input_path.currentRow())

    def calibrate_image(self):
        self.tree_widget_calibration_data.clear()
        concentration = [float(c) for c in self.line_edit_concentration.text().split(' ')]

        items = []
        for name, path in self.dict_input_path.items():
            image = read_image(path)
            calibration_object = Calibration(name, image, concentration)
            self.dict_calibration_object[name] = calibration_object

            item = QTreeWidgetItem([name])
            for peak in range(len(calibration_object.peaks)):
                child = QTreeWidgetItem([f"Peak {peak+1}"])
                item.addChild(child)
            items.append(item)
            self.tree_widget_calibration_data.addTopLevelItems(items)

        # Send Signal
        self.data_sent.emit(self.dict_calibration_object)
        
    def show_calibration_data(self, item, column):
        name = item.parent().text(column)
        peak_index = int(item.text(column).split(' ')[1]) - 1
        calibration_object = self.dict_calibration_object[name]
        
        pix = self.__convert_cv2_to_qpixmap(calibration_object.image)
        self.label_image_original.setPixmap(pix)

        pix = self.__convert_cv2_to_qpixmap(calibration_object.processed_image_result)
        self.label_image_processed.setPixmap(pix)

        pix = self.__convert_cv2_to_qpixmap(calibration_object.peaks[peak_index].image)
        self.label_image_peak.setPixmap(pix)
        
        data_peak_area = calibration_object.peaks[peak_index].peak_area
        data_best_fit_line = calibration_object.peaks[peak_index].best_fit_line
        data_calibration = f"Calibration: {name}\nPeak: {peak_index+1}\nPeak Area:\n\tR: {data_peak_area['R']}\n\tG: {data_peak_area['G']}\n\tB: {data_peak_area['B']}\nBest Fit Line:\n\tR: {data_best_fit_line['R']}\n\tG: {data_best_fit_line['G']}\n\tB: {data_best_fit_line['B']}"
        self.label_peak_data.setText(data_calibration)
        
        plot = calibration_object.peaks[peak_index].plot_fit_line
        if self.v_layout_right.count() != 0:
            canvas = self.v_layout_right.takeAt(0)
            canvas.widget().deleteLater()
        canvas_best_fit_line = FigureCanvasQTAgg(plot)
        self.v_layout_right.addWidget(canvas_best_fit_line)

    def __convert_cv2_to_qpixmap(self, cv_image: np.ndarray):
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        PIL_image = Image.fromarray(rgb_image).convert('RGB')
        pix = QPixmap.fromImage(ImageQt(PIL_image))
        return pix.scaledToWidth(500)