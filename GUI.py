from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QProcess




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


