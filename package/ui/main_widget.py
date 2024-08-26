from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from package.ui.widget_mixture_2 import WidgetMixture
from package.ui.widget_calibration import WidgetCalibration

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mixture Hack")
        self.showMaximized()

        tab_widget = QTabWidget()
        # widget_upload = WidgetUpload()
        widget_calibration = WidgetCalibration()
        widget_mixture = WidgetMixture()
        
        widget_calibration.data_sent.connect(widget_mixture.on_signal_from_calibration)
        # widget_upload.data_sent.connect(widget_image_process.recieve_image_path)

        # Add tabs to widget
        # tab_widget.addTab(widget_upload, "Upload")
        tab_widget.addTab(widget_calibration, "Calibration")
        tab_widget.addTab(widget_mixture, "Mixture")

        layout = QVBoxLayout()
        layout.addWidget(tab_widget)

        self.setLayout(layout)