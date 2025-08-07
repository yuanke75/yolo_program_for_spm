from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QProcess
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsScene
import argparse
import os
import platform
import sys
from pathlib import Path
import argparse
import os
import platform
import sys
from pathlib import Path
from collections import Counter
import torch
import time
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLO root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative


from utils.general import increment_path




project=ROOT / 'runs/detect'
name='exp'
exist_ok=False
save_dir = increment_path(Path(project) / name, exist_ok=exist_ok)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1500, 1200)  # 增加主窗口的大小以容纳更大的视图
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # 放大 graphicsView 和 graphicsView_2
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(20, 20, 600, 600))
        self.graphicsView.setObjectName("graphicsView")

        self.graphicsView_2 = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView_2.setGeometry(QtCore.QRect(640, 20, 600, 600))  # 调整位置以放下另一个1000x1000的视图
        self.graphicsView_2.setObjectName("graphicsView_2")
        
        # 调整按钮和文本浏览器的位置和尺寸
        self.uploadButton = QtWidgets.QPushButton(self.centralwidget)
        self.uploadButton.setGeometry(QtCore.QRect(20, 640, 200, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.uploadButton.setFont(font)
        self.uploadButton.setObjectName("uploadButton")
        
        self.detectButton = QtWidgets.QPushButton(self.centralwidget)
        self.detectButton.setGeometry(QtCore.QRect(240, 640, 200, 50))
        self.detectButton.setFont(font)
        self.detectButton.setObjectName("detectButton")

        self.resetButton = QtWidgets.QPushButton(self.centralwidget)
        self.resetButton.setGeometry(QtCore.QRect(460, 640, 200, 50))
        self.resetButton.setFont(font)
        self.resetButton.setObjectName("resetButton")
        
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(20, 710, 400, 200))
        self.textBrowser.setObjectName("textBrowser")
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1500, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)        
        # Connect buttons to their respective slot functions
        self.uploadButton.clicked.connect(self.open_image)
        self.detectButton.clicked.connect(self.run_detect_script)
        self.resetButton.clicked.connect(self.reset_interface)


        self.imagePath = ""  # Variable to store the image path
        # self.outputImagePath = os.path.join(save_dir, filename)  # Path to the output image from detect.py
        self.process = QProcess()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Image Detection"))
        self.uploadButton.setText(_translate("MainWindow", "Upload Image"))
        self.detectButton.setText(_translate("MainWindow", "Detect"))
        self.resetButton.setText(_translate("MainWindow", "Reset"))
    def __init__(self):
        self.project = ROOT / 'runs/detect'
        self.name = 'exp'
        self.exist_ok = False
        self.update_save_dir()  # 初始化 save_dir

    def update_save_dir(self):
        self.save_dir = increment_path(Path(self.project) / self.name, exist_ok=self.exist_ok)
    # def open_image(self):
    #     # Open file dialog to select an image
    #     self.imagePath, _ = QFileDialog.getOpenFileName()
    #     if self.imagePath:
    #         filename = os.path.basename(self.imagePath)
    #         print("Loaded file:", filename)  # 输出文件名，或进行其他操作
    #         self.outputImagePath = os.path.join(save_dir, filename)
    #         # Display image in the graphicsView
    #         pixmap = QPixmap(self.imagePath)
    #         scene = QGraphicsScene()
    #         scene.addPixmap(pixmap.scaled(self.graphicsView.size(), QtCore.Qt.KeepAspectRatio))
    #         self.graphicsView.setScene(scene)

    def open_image(self):
        # Open file dialog to select an image
        self.imagePath, _ = QFileDialog.getOpenFileName()
        if self.imagePath:
            # 更新 save_dir 路径
            # self.save_dir = increment_path(Path(self.project) / self.name, exist_ok=self.exist_ok)
            filename = os.path.basename(self.imagePath)
            self.outputImagePath = os.path.join(save_dir, filename)
            
            print("Loaded file:", filename)  # 输出文件名，或进行其他操作
            
            # Display image in the graphicsView
            pixmap = QPixmap(self.imagePath)
            if not pixmap.isNull():
                scene = QGraphicsScene()
                scene.addPixmap(pixmap.scaled(self.graphicsView.size(), QtCore.Qt.KeepAspectRatio))
                self.graphicsView.setScene(scene)
            else:
                print("Failed to load image.")


    # def run_detect_script(self):
    #     if self.imagePath:
    #         self.process = QProcess()  # Reinitialize the QProcess to ensure clean state
    #         self.process.finished.connect(self.display_output_image)
    #         self.process.finished.connect(self.display_category_counts)
    #         self.process.start("python", ["detect.py", "--source", self.imagePath])

    def run_detect_script(self):
        if self.imagePath:
            # 更新 save_dir 路径
            self.project=ROOT / 'runs/detect'
            self.name='exp'
            self.exist_ok=False
            self.save_dir = increment_path(Path(self.project) / self.name, exist_ok=self.exist_ok)
            self.outputImagePath = os.path.join(self.save_dir, os.path.basename(self.imagePath))

            self.process = QProcess()  # Reinitialize the QProcess to ensure clean state
            self.process.finished.connect(self.display_output_image)
            # self.process.finished.connect(self.display_category_counts)
            # 确保传递正确的 save_dir 到检测脚本
            self.process.start("python", ["detect.py", "--source", self.imagePath, "--project", str(self.project), "--name", self.name])
            

            # Initialize path to label files
            time.sleep(10)
            label_dir = os.path.join(self.save_dir, "labels")
            categories = Counter()
            
            # Read all .txt files in the label directory
            for label_file in os.listdir(label_dir):
                if label_file.endswith(".txt"):
                    with open(os.path.join(label_dir, label_file), 'r') as file:
                        for line in file:
                            category = line.split()[0]  # Assuming the category is the first item in each line
                            categories[category] += 1
            
            # Display results in the textBrowser
            display_text = "Detected Categories and Counts:\n"
            for category, count in categories.items():
                display_text += f"Category {category}: {count} items\n"
            
            self.textBrowser.setText(display_text)

    
    
    def display_output_image(self):
        # Load and display the output image in graphicsView_2
        pixmap = QPixmap(self.outputImagePath)
        scene = QGraphicsScene()
        scene.addPixmap(pixmap.scaled(self.graphicsView_2.size(), QtCore.Qt.KeepAspectRatio))
        self.graphicsView_2.setScene(scene)


    # def display_category_counts(self):
    #     # Initialize path to label files

    #     label_dir = os.path.join(save_dir, "labels")
    #     categories = Counter()
        
    #     # Read all .txt files in the label directory
    #     for label_file in os.listdir(label_dir):
    #         if label_file.endswith(".txt"):
    #             with open(os.path.join(label_dir, label_file), 'r') as file:
    #                 for line in file:
    #                     category = line.split()[0]  # Assuming the category is the first item in each line
    #                     categories[category] += 1
        
    #     # Display results in the textBrowser
    #     display_text = "Detected Categories and Counts:\n"
    #     for category, count in categories.items():
    #         display_text += f"Category {category}: {count} items\n"
        
    #     self.textBrowser.setText(display_text)
    



    # def reset_interface(self):
    #     # Clear graphics views and reset scenes
    #     self.graphicsView.setScene(QGraphicsScene(self.centralwidget))
    #     self.graphicsView_2.setScene(QGraphicsScene(self.centralwidget))

    #     # Clear text browser
    #     self.textBrowser.clear()

    #     # Reset the image paths
    #     self.imagePath = ""
    #     self.outputImagePath = ""

    #     # Reset save_dir
    #     self.project = ROOT / 'runs/detect'
    #     self.name = 'exp'
    #     self.exist_ok = False
    #     self.save_dir = increment_path(Path(self.project) / self.name, exist_ok=self.exist_ok)

    #     # Terminate and reset the process if running
    #     if self.process.state() == QProcess.Running:
    #         self.process.terminate()
    #         self.process.waitForFinished()

    #     # Disconnect any signals that might be connected to old process slots
    #     try:
    #         self.process.finished.disconnect()
    #     except TypeError:
    #         print("No connections to disconnect.")
    #     finally:
    #         self.process = QProcess()  # Reinitialize the QProcess object

    def reset_interface(self):
        # Clear graphics views and reset scenes
        self.graphicsView.setScene(QGraphicsScene(self.centralwidget))
        self.graphicsView_2.setScene(QGraphicsScene(self.centralwidget))

        # Clear text browser
        self.textBrowser.clear()

        # Reset the image paths
        self.imagePath = ""
        self.outputImagePath = ""

        # 更新 save_dir 以便于下一次运行使用
        self.save_dir = increment_path(Path(self.project) / self.name, exist_ok=self.exist_ok)

        # Terminate and reset the process if running
        if self.process.state() == QProcess.Running:
            self.process.terminate()
            self.process.waitForFinished()

        # Disconnect any signals that might be connected to old process slots
        try:
            self.process.finished.disconnect()
        except TypeError:
            print("No connections to disconnect.")
        finally:
            self.process = QProcess()  # Reinitialize the QProcess object



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
