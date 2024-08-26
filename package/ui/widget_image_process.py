from PySide6.QtWidgets import QWidget, QListWidget, QHBoxLayout, QVBoxLayout

class WidgetImageProcess(QWidget):
    def __init__(self):
        super().__init__()

        v_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.currentItemChanged.connect(self.show_image)

        main_h_layout = QHBoxLayout()
        main_h_layout.addLayout(v_layout, 1)

        self.image_path = []

        self.setLayout(main_h_layout)

    def show_image(self):
        pass

    def recieve_image_path(self, image_path):
        self.image_path = image_path
        self.list_widget.addItem(self.image_path)
        print("Recieve image path:\n", self.image_path)