from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QListWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem, QAbstractItemView

from PIL.ImageQt import ImageQt
from PIL import Image
import cv2

from package.mixhack.image_processing import read_image
from package.mixhack.mixture import Mixture
from package.mixhack import mixture_hack

class WidgetMixture(QWidget):
    def __init__(self):
        super().__init__()
        self.list_image_path = []
        self.list_calibration_object = []

        # Top Horizontal Layout
        h_layout_1 = QHBoxLayout()
        ## Button Layout
        v_layout_1 = QVBoxLayout()
        h_layout_button = QHBoxLayout()
        button_upload = QPushButton("Upload")
        button_upload.clicked.connect(self.upload_image)
        button_delete = QPushButton("Delete")
        button_delete.clicked.connect(self.delete_image)
        button_process = QPushButton("Process")
        button_process.clicked.connect(self.process_image)
        h_layout_button.addWidget(button_upload)
        h_layout_button.addWidget(button_delete)
        h_layout_button.addWidget(button_process)
        ## Image Path List Widget
        self.list_widget_image_path = QListWidget()
        self.list_widget_image_path.currentItemChanged.connect(self.show_image)
        v_layout_1.addLayout(h_layout_button)
        v_layout_1.addWidget(self.list_widget_image_path)
        ## Image Label
        self.label_image = QLabel()
        self.label_image.setAlignment(Qt.AlignCenter)
        
        h_layout_1.addLayout(v_layout_1, 1)
        h_layout_1.addWidget(self.label_image, 3)

        # Bottom Horizontal Layout
        h_layout_2 = QHBoxLayout()
        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(1)
        self.tree_widget.setHeaderLabel("Name")
        self.tree_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        
        self.label_image_mixture = QLabel()
        # self.label_result = QLabel()
        h_layout_2.addWidget(self.tree_widget)
        # h_layout_2.addWidget(self.label_image_mixture)
        # h_layout_2.addWidget(self.label_result)

        # Main Vertical Layout
        main_v_layout = QVBoxLayout()
        main_v_layout.addLayout(h_layout_1, 1)
        main_v_layout.addLayout(h_layout_2, 2)
        self.setLayout(main_v_layout)

    def upload_image(self):
        file_name = QFileDialog.getOpenFileName(self, "Open file", "C:\\Users\\User\\Desktop\\TLC\\Project\\Input", "Image files (*.png *.jpg *.gif *.svg)")
        self.list_image_path.append(file_name[0])
        self.list_widget_image_path.addItem(file_name[0])

    def delete_image(self):
        self.list_image_path.remove(self.list_widget_image_path.currentItem().text())
        self.list_widget_image_path.takeItem(self.list_widget_image_path.currentRow())
    
    def process_image(self):
        self.tree_widget.clear()
        path = self.list_widget_image_path.currentItem().text()
        image = read_image(path)
        self.mixture_object = Mixture(image)
        self.label_image_mixture.setPixmap(self._convert_cv2_to_qpixmap(self.mixture_object.processed_image))

        items = []
        item = QTreeWidgetItem([f"Mixture"])
        for peak in range(len(self.mixture_object.peak_area['R'])):
            child = QTreeWidgetItem([f"Peak {peak+1}"])
            item.addChild(child)
        items.append(item)
        self.tree_widget.addTopLevelItems(items)

        for i, calibration_object in enumerate(self.list_calibration_object):
            item = QTreeWidgetItem([f"Calibration {i+1}"])
            for j, peak in enumerate(calibration_object.peaks):
                    child = QTreeWidgetItem([f"Peak {j+1}"])
                    item.addChild(child)
            items.append(item)
            self.tree_widget.addTopLevelItems(items)
    
    def show_image(self, item):
        pix = QPixmap(item.text())
        pix = pix.scaledToHeight(250)
        self.label_image.setPixmap(pix)
    
    def on_signal_from_calibration(self, list_calibration_object):
        self.list_calibration_object = list_calibration_object
    
    def _convert_cv2_to_qpixmap(self, cv_image):
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        PIL_image = Image.fromarray(rgb_image).convert('RGB')
        pix = QPixmap.fromImage(ImageQt(PIL_image))
        return pix.scaledToWidth(600)