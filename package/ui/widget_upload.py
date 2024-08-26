from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QListWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog


class WidgetUpload(QWidget):
    data_sent = Signal(list)

    def __init__(self):
        super().__init__()
        self.list_image_path = []

        # Button Layout
        h_button_layout = QHBoxLayout()
        button_upload = QPushButton("Upload")
        button_upload.clicked.connect(self.upload_image)
        button_delete = QPushButton("Delete")
        button_delete.clicked.connect(self.delete_image)
        button_process = QPushButton("Process")
        button_process.clicked.connect(self.process_image)
        h_button_layout.addWidget(button_upload)
        h_button_layout.addWidget(button_delete)
        h_button_layout.addWidget(button_process)

        # Image Path & Image Label Layout
        v_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.currentItemChanged.connect(self.show_image)
        self.label_image = QLabel()
        self.label_image.setAlignment(Qt.AlignCenter)
        v_layout.addLayout(h_button_layout)
        v_layout.addWidget(self.list_widget)

        # Main Layout
        main_h_layout = QHBoxLayout()
        main_h_layout.addLayout(v_layout, 1)
        main_h_layout.addWidget(self.label_image, 5)

        self.setLayout(main_h_layout)

    def upload_image(self):
        file_name = QFileDialog.getOpenFileName(self, "Open file", "c:\\", "Image files (*.png *.jpg *.gif *.svg)")
        self.list_image_path.append(file_name[0])
        self.list_widget.addItem(file_name[0])

    def delete_image(self):
        print("Delete image path:\n", self.list_widget.currentItem().text())
        self.list_image_path.remove(self.list_widget.currentItem().text())
        self.list_widget.takeItem(self.list_widget.currentRow())

    def process_image(self):
        print("Emit list of image path:\n", self.list_image_path)
        self.data_sent.emit(self.list_image_path)
    
    def show_image(self, item):
        print("Show image :\n", item.text())
        pix = QPixmap(item.text())
        pix = pix.scaledToHeight(600)
        self.label_image.setPixmap(pix)