from PIL.ImageQt import ImageQt
from PIL import Image 
import cv2
import matplotlib
matplotlib.use('Qt5Agg')

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QListWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QLineEdit, QTreeWidget, QTreeWidgetItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from package.mixhack.image_processing import read_image
from package.mixhack.calibration import Calibration

class WidgetCalibration(QWidget):
    data_sent = Signal(list)

    def __init__(self):
        super().__init__()
        self.list_input_path = []
        self.dict_calibration_object = {}

        main_layout = QHBoxLayout()
        
        # Left Vertical Box
        v_layout_left = QVBoxLayout()
        
        ## Button
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
        
        ## Concentration Input
        h_layout_concentration = QHBoxLayout()
        label_concentration = QLabel("Concentration: ")
        self.line_edit_concentration = QLineEdit()
        self.line_edit_concentration.setText("1 2 3 4 5 6 7 8")
        h_layout_concentration.addWidget(label_concentration)
        h_layout_concentration.addWidget(self.line_edit_concentration)
        
        ## Input Path
        self.list_widget_input_path = QListWidget()
        self.list_widget_input_path.currentItemChanged.connect(self.show_image)

        ## Calibration Information
        self.tree_widget_calibration_image = QTreeWidget()
        self.tree_widget_calibration_image.setColumnCount(1)
        self.tree_widget_calibration_image.setHeaderLabel("Calibration Information")
        self.tree_widget_calibration_image.itemClicked.connect(self.show_calibration_info)
        
        v_layout_left.addLayout(h_layout_button)
        v_layout_left.addLayout(h_layout_concentration)
        v_layout_left.addWidget(self.list_widget_input_path, 1)
        v_layout_left.addWidget(self.tree_widget_calibration_image, 4)
        
        # Middle Vertical Box
        v_layout_middle = QVBoxLayout()
        
        ## Original Image
        self.label_image_original = QLabel()
        self.label_image_original.setAlignment(Qt.AlignTop)
        
        ## Peak Image
        self.label_image_peak = QLabel()
        self.label_image_peak.setAlignment(Qt.AlignTop)
        
        v_layout_middle.addWidget(self.label_image_original)
        v_layout_middle.addWidget(self.label_image_peak)
        
        # Right Vertical Box
        self.v_layout_right = QVBoxLayout()
        
        ## Best fit line Plot
        self.canvas_best_fit_line = FigureCanvasQTAgg(Figure(figsize=(4, 12)))
        
        main_layout.addLayout(v_layout_left, 1)
        main_layout.addLayout(v_layout_middle, 1)
        main_layout.addLayout(self.v_layout_right, 1)
        self.setLayout(main_layout)

    def upload_image(self):
        file_name = QFileDialog.getOpenFileName(self, "Open file", "C:\\Users\\Suttawee\\Desktop\\Mixture-Hack-main\\Project\\Input", "Image files (*.png *.jpg *.gif *.svg)")
        self.list_input_path.append(file_name[0])
        self.list_widget_input_path.addItem(file_name[0])
        self.dict_calibration_object[file_name[0]] = None

    def delete_image(self):
        path = self.list_widget_input_path.currentItem().text()
        self.dict_calibration_object.pop(path)
        self.list_input_path.remove(path)
        self.list_widget_input_path.takeItem(self.list_widget_input_path.currentRow())

    def calibrate_image(self):
        self.tree_widget_calibration_image.clear()
        concentration = [float(c) for c in self.line_edit_concentration.text().split(' ')]

        items = []
        for path in self.list_input_path:
            image = read_image(path)
            calibration_object = Calibration(image, concentration)
            self.dict_calibration_object[path] = calibration_object
            
            # UI
            item = QTreeWidgetItem([path])
            for peak in range(len(calibration_object.peaks)):
                child = QTreeWidgetItem([f"Peak {peak+1}"])
                item.addChild(child)
            items.append(item)
            self.tree_widget_calibration_image.addTopLevelItems(items)
        
        list_calibration_object = [value for value in self.dict_calibration_object.values()]
        self.data_sent.emit(list_calibration_object)
    
    def show_image(self, item):
        pix = QPixmap(item.text())
        pix = pix.scaledToWidth(500)
        self.label_image_original.setPixmap(pix)
    
    def show_calibration_info(self, item, column):
        path = item.parent().text(column)
        peak_index = int(item.text(column).split(' ')[1]) - 1
        
        pix = self._convert_cv2_to_qpixmap(self.dict_calibration_object[path].image)
        self.label_image_original.setPixmap(pix)

        pix = self._convert_cv2_to_qpixmap(self.dict_calibration_object[path].peaks[peak_index].image)
        self.label_image_peak.setPixmap(pix)
        
        plot = self.dict_calibration_object[path].peaks[peak_index].plot_best_fit_line
                
        self.v_layout_right.takeAt(0)
        self.canvas_best_fit_line = FigureCanvasQTAgg(plot)
        self.v_layout_right.addWidget(self.canvas_best_fit_line)
        
        # info_peak_area = self.dict_calibration_object[path].peaks[peak_index].peak_area
        # info_best_fit_line = self.dict_calibration_object[path].peaks[peak_index].best_fit_line
        # calibration_info = f"{path}\nPeak {peak_index+1}\nPeak Area:\n\tR: {info_peak_area['R']}\n\tG: {info_peak_area['G']}\n\tB: {info_peak_area['B']}\nBest Fit Line:\n\tR: {info_best_fit_line['R']}\n\tG: {info_best_fit_line['G']}\n\tB: {info_best_fit_line['B']}"
        # self.label_calibration_info.setText(calibration_info)

    def _convert_cv2_to_qpixmap(self, cv_image):
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        PIL_image = Image.fromarray(rgb_image).convert('RGB')
        pix = QPixmap.fromImage(ImageQt(PIL_image))
        return pix.scaledToWidth(500)