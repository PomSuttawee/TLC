from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from package.ui.widget_mixture import WidgetMixture
from package.ui.widget_calibration import WidgetCalibration
from package.ui.widget_mixture_hack import WidgetMixtureHack

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mixture Hack")
        self.showMaximized()

        tab_widget = QTabWidget()
        widget_calibration = WidgetCalibration()
        widget_mixture = WidgetMixture()
        widget_mixture_hack = WidgetMixtureHack()
        
        widget_calibration.data_sent.connect(widget_mixture_hack.on_signal_from_calibration)
        widget_mixture.data_sent.connect(widget_mixture_hack.on_signal_from_mixture)
        
        # Add tabs to widget
        tab_widget.addTab(widget_calibration, "Calibration")
        tab_widget.addTab(widget_mixture, "Mixture")
        tab_widget.addTab(widget_mixture_hack, "Mixture Hack")

        layout = QVBoxLayout()
        layout.addWidget(tab_widget)
        self.setLayout(layout)