import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget
from yolo_uiV3 import YOLOv9Interface
from label_duobianxing import LabelingTool
from makedatasetV11 import CombinedApp
from analysisv2 import LabelAnalyzer
from replayv3 import IncrementalLearningTool
from yolo_ui_seg import YOLOv9Interface_seg
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('YOLOv9 and Labeling Tool Interface')
        self.setGeometry(100, 100, 1200, 700)

        self.tabs = QTabWidget()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # YOLOv9 Interface
        self.yolo_interface = YOLOv9Interface()
        self.tabs.addTab(self.yolo_interface, "YOLOv9 Interface")

        # YOLOv9 Interface
        self.yolo_interface = YOLOv9Interface_seg()
        self.tabs.addTab(self.yolo_interface, "YOLOv9-segment Interface")

        # Labeling Tool Interface
        self.labeling_tool_interface = LabelingTool()
        self.tabs.addTab(self.labeling_tool_interface, "Labeling Tool")

        # Add original application tabs
        self.tabs.addTab(CombinedApp(), "Make Dataset")

        self.tabs.addTab(LabelAnalyzer(), "LabelAnalyzer")

        self.tabs.addTab(IncrementalLearningTool(), "replay")
        layout.addWidget(self.tabs)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())
