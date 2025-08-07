from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QStackedWidget
from expert_app import ExpertApp
from basic_app import BasicApp

class CombinedApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Augmentation, JSON to TXT Conversion, and Dataset Splitter')
        self.stacked_widget = QStackedWidget()
        self.expert_app = ExpertApp()
        self.basic_app = BasicApp(self.expert_app)
        
        self.stacked_widget.addWidget(self.basic_app)
        self.stacked_widget.addWidget(self.expert_app)
        
        self.switch_button = QPushButton('Switch to Expert Mode', self)
        self.switch_button.clicked.connect(self.switch_mode)
        self.update_switch_button_text()
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.switch_button)
        main_layout.addWidget(self.stacked_widget)
        
        self.setLayout(main_layout)
        self.setStyleSheet("""
            QWidget {
                font-size: 14px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid gray;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QProgressBar {
                height: 20px;
                text-align: center;
            }
        """)

    def update_switch_button_text(self):
        if self.stacked_widget.currentIndex() == 0:
            self.switch_button.setText('Switch to Expert Mode')
        else:
            self.switch_button.setText('Switch to Basic Mode')

    def switch_mode(self):
        if self.stacked_widget.currentIndex() == 0:
            self.stacked_widget.setCurrentIndex(1)
        else:
            self.stacked_widget.setCurrentIndex(0)
        self.update_switch_button_text()
