import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QFileDialog,
                             QMessageBox, QTextEdit, QTabWidget, QVBoxLayout, QCheckBox, QPlainTextEdit, QComboBox)
from PyQt5.QtCore import QProcess, Qt
from PyQt5.QtGui import QPixmap, QFont
import shutil

class YOLOv9Interface(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('YOLOv9 Interface')
        self.setGeometry(100, 100, 1200, 700)

        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Training tab
        self.train_tab = QWidget()
        self.train_tab_layout = QGridLayout()

        # Adding title
        self.train_title = QLabel('YOLOv9 Training Interface')
        self.train_title.setFont(QFont("Arial", 18, QFont.Bold))
        self.train_tab_layout.addWidget(self.train_title, 0, 0, 1, 3, Qt.AlignCenter)

        # Weights file input
        weights_label = QLabel('Weights Path:')
        self.train_tab_layout.addWidget(weights_label, 1, 0)
        self.weights_input = QLineEdit(self)
        self.train_tab_layout.addWidget(self.weights_input, 1, 1)
        weights_button = QPushButton('Select')
        weights_button.clicked.connect(self.select_weights_file)
        self.train_tab_layout.addWidget(weights_button, 1, 2)

        # Data file input
        data_label = QLabel('Data File Path:')
        self.train_tab_layout.addWidget(data_label, 2, 0)
        self.data_input = QLineEdit(self)
        self.train_tab_layout.addWidget(self.data_input, 2, 1)
        data_button = QPushButton('Select')
        data_button.clicked.connect(self.select_data_file)
        self.train_tab_layout.addWidget(data_button, 2, 2)

        # Hyp file input
        hyp_label = QLabel('Hyp File Path:')
        self.train_tab_layout.addWidget(hyp_label, 3, 0)
        self.hyp_input = QLineEdit(self)
        self.train_tab_layout.addWidget(self.hyp_input, 3, 1)
        hyp_button = QPushButton('Select')
        hyp_button.clicked.connect(self.select_hyp_file)
        self.train_tab_layout.addWidget(hyp_button, 3, 2)

        # Epochs input
        epochs_label = QLabel('Epochs:')
        self.train_tab_layout.addWidget(epochs_label, 4, 0)
        self.epochs_input = QLineEdit(self)
        self.epochs_input.setText('15')
        self.train_tab_layout.addWidget(self.epochs_input, 4, 1)

        # Batch size input
        batch_size_label = QLabel('Batch Size:')
        self.train_tab_layout.addWidget(batch_size_label, 5, 0)
        self.batch_size_input = QLineEdit(self)
        self.batch_size_input.setText('3')
        self.train_tab_layout.addWidget(self.batch_size_input, 5, 1)
        
        # 在 Train 标签页中创建训练模式选择框
        self.mode_selector = QComboBox(self)
        self.mode_selector.addItems(["目标识别", "实例分割"])
        self.mode_selector.setFont(QFont("Arial", 12))  # 设置字体

        # 在界面上添加 QComboBox 控件用于选择模式
        self.train_tab_layout.addWidget(QLabel("选择训练模式:", self), 6, 0)  # 添加标签说明
        self.train_tab_layout.addWidget(self.mode_selector, 6, 1, 1, 2)     # 添加选择框

        # Train button
        train_button = QPushButton('Start Training')
        train_button.setFont(QFont("Arial", 14, QFont.Bold))
        train_button.clicked.connect(self.start_training)

        # 将 Train 按钮添加到布局中
        self.train_tab_layout.addWidget(train_button, 7, 0, 1, 3)

        # # Train button
        # train_button = QPushButton('Start Training')
        # train_button.setFont(QFont("Arial", 14, QFont.Bold))
        # train_button.clicked.connect(self.start_training)
        # self.train_tab_layout.addWidget(train_button, 6, 0, 1, 3)

        # Output display
        self.output_display = QPlainTextEdit(self)
        self.output_display.setReadOnly(True)
        self.train_tab_layout.addWidget(self.output_display, 8, 0, 1, 3)

        self.train_tab.setLayout(self.train_tab_layout)

        # Detecting tab
        self.detect_tab = QWidget()
        self.detect_tab_layout = QVBoxLayout()

        # Adding title
        self.detect_title = QLabel('YOLOv9 Detecting Interface')
        self.detect_title.setFont(QFont("Arial", 18, QFont.Bold))
        self.detect_tab_layout.addWidget(self.detect_title)

        self.detect_tabs = QTabWidget()
        self.detect_tab_layout.addWidget(self.detect_tabs)

        # Single image detection tab
        self.single_image_tab = QWidget()
        self.single_image_layout = QGridLayout()

        # Image input
        image_label = QLabel('Image Path:')
        self.single_image_layout.addWidget(image_label, 1, 0)
        self.image_input = QLineEdit(self)
        self.single_image_layout.addWidget(self.image_input, 1, 1)
        image_button = QPushButton('Select')
        image_button.clicked.connect(self.select_image_file)
        self.single_image_layout.addWidget(image_button, 1, 2)

        # Weights file input for detection
        detect_weights_label = QLabel('Weights Path:')
        self.single_image_layout.addWidget(detect_weights_label, 2, 0)
        self.detect_weights_input = QLineEdit(self)
        self.single_image_layout.addWidget(self.detect_weights_input, 2, 1)
        detect_weights_button = QPushButton('Select')
        detect_weights_button.clicked.connect(self.select_detect_weights_file)
        self.single_image_layout.addWidget(detect_weights_button, 2, 2)

        # Confidence threshold input
        conf_thres_label = QLabel('Confidence Threshold:')
        self.single_image_layout.addWidget(conf_thres_label, 3, 0)
        self.conf_thres_input = QLineEdit(self)
        self.conf_thres_input.setText('0.3')  # 设置默认值为0.3
        self.single_image_layout.addWidget(self.conf_thres_input, 3, 1)

        # Hide labels and confidences checkboxes
        self.hide_labels_checkbox = QCheckBox('Hide Labels')
        self.single_image_layout.addWidget(self.hide_labels_checkbox, 4, 0)

        self.hide_conf_checkbox = QCheckBox('Hide Confidences')
        self.single_image_layout.addWidget(self.hide_conf_checkbox, 4, 1)

        # Detect button
        detect_button = QPushButton('Start Detecting')
        detect_button.setFont(QFont("Arial", 14, QFont.Bold))
        detect_button.clicked.connect(self.start_detecting)
        self.single_image_layout.addWidget(detect_button, 5, 0, 1, 3)

        # Save button
        save_button = QPushButton('Save Detection')
        save_button.setFont(QFont("Arial", 14, QFont.Bold))
        save_button.clicked.connect(self.save_detection)
        self.single_image_layout.addWidget(save_button, 6, 2)

        # Original image display
        self.image_display = QLabel(self)
        self.image_display.setFixedSize(400, 300)
        self.image_display.setStyleSheet("border: 1px solid black;")
        self.image_display.setAlignment(Qt.AlignCenter)
        self.single_image_layout.addWidget(self.image_display, 6, 0, 1, 1)

        # Result image display
        self.result_image_display = QLabel(self)
        self.result_image_display.setFixedSize(400, 300)
        self.result_image_display.setStyleSheet("border: 1px solid black;")
        self.result_image_display.setAlignment(Qt.AlignCenter)
        self.single_image_layout.addWidget(self.result_image_display, 6, 1, 1, 1)

        # Output display for detecting
        self.detect_output_display = QPlainTextEdit(self)
        self.detect_output_display.setReadOnly(True)
        self.single_image_layout.addWidget(self.detect_output_display, 7, 0, 1, 2)

        self.single_image_tab.setLayout(self.single_image_layout)
        self.detect_tabs.addTab(self.single_image_tab, "Single Image Detection")

        # Directory detection tab
        self.directory_tab = QWidget()
        self.directory_layout = QGridLayout()

        # Directory input
        directory_label = QLabel('Directory Path:')
        self.directory_layout.addWidget(directory_label, 1, 0)
        self.directory_input = QLineEdit(self)
        self.directory_layout.addWidget(self.directory_input, 1, 1)
        directory_button = QPushButton('Select')
        directory_button.clicked.connect(self.select_directory)
        self.directory_layout.addWidget(directory_button, 1, 2)

        # Weights file input for detection
        detect_weights_label = QLabel('Weights Path:')
        self.directory_layout.addWidget(detect_weights_label, 2, 0)
        self.detect_weights_input_dir = QLineEdit(self)
        self.directory_layout.addWidget(self.detect_weights_input_dir, 2, 1)
        detect_weights_button_dir = QPushButton('Select')
        detect_weights_button_dir.clicked.connect(self.select_detect_weights_file_dir)
        self.directory_layout.addWidget(detect_weights_button_dir, 2, 2)

        # Confidence threshold input
        conf_thres_label_dir = QLabel('Confidence Threshold:')
        self.directory_layout.addWidget(conf_thres_label_dir, 3, 0)
        self.conf_thres_input_dir = QLineEdit(self)
        self.conf_thres_input_dir.setText('0.3')  # 设置默认值为0.3
        self.directory_layout.addWidget(self.conf_thres_input_dir, 3, 1)

        # Hide labels and confidences checkboxes
        self.hide_labels_checkbox_dir = QCheckBox('Hide Labels')
        self.directory_layout.addWidget(self.hide_labels_checkbox_dir, 4, 0)

        self.hide_conf_checkbox_dir = QCheckBox('Hide Confidences')
        self.directory_layout.addWidget(self.hide_conf_checkbox_dir, 4, 1)

        # Detect button
        detect_button_dir = QPushButton('Start Detecting')
        detect_button_dir.setFont(QFont("Arial", 14, QFont.Bold))
        detect_button_dir.clicked.connect(self.start_detecting_dir)
        self.directory_layout.addWidget(detect_button_dir, 5, 0, 1, 3)

        # Save button for directory
        save_button_dir = QPushButton('Save All Detections')
        save_button_dir.setFont(QFont("Arial", 14, QFont.Bold))
        save_button_dir.clicked.connect(self.save_all_detections)
        self.directory_layout.addWidget(save_button_dir, 6, 0, 1, 3)

        # Output display for detecting
        self.detect_output_display_dir = QPlainTextEdit(self)
        self.detect_output_display_dir.setReadOnly(True)
        self.directory_layout.addWidget(self.detect_output_display_dir, 7, 0, 1, 3)

        self.directory_tab.setLayout(self.directory_layout)
        self.detect_tabs.addTab(self.directory_tab, "Directory Detection")

        self.detect_tab.setLayout(self.detect_tab_layout)
        self.tabs.addTab(self.train_tab, "Training")
        self.tabs.addTab(self.detect_tab, "Detecting")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

        # Initialize loading_message attribute
        self.loading_message = QMessageBox(self)
        self.loading_message.setWindowTitle("Loading")
        self.loading_message.setText("Processing... Please wait.")
        self.loading_message.setStandardButtons(QMessageBox.NoButton)
        
        # Apply styles
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                font-size: 14px;
                background-color: #f0f0f0;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #fff;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPlainTextEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
                font-family: Consolas, "Courier New", monospace;
                background-color: #fff;
            }
            QLabel {
                font-weight: bold;
                color: #333;
            }
            QCheckBox {
                font-size: 14px;
            }
        """)

    def select_weights_file(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, "Select Weights File", "", "All Files (*);;Python Files (*.pt)", options=options)
        if file:
            self.weights_input.setText(file)

    def select_data_file(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, "Select Data File", "", "All Files (*);;YAML Files (*.yaml)", options=options)
        if file:
            self.data_input.setText(file)

    def select_hyp_file(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, "Select Hyp File", "", "All Files (*);;YAML Files (*.yaml)", options=options)
        if file:
            self.hyp_input.setText(file)

    def select_image_file(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, "Select Image File", "", "All Files (*);;Image Files (*.jpg; *.jpeg; *.png)", options=options)
        if file:
            self.image_input.setText(file)
            self.display_image(file)

    def select_directory(self):
        options = QFileDialog.Options()
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", options=options)
        if directory:
            self.directory_input.setText(directory)

    def select_detect_weights_file(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, "Select Weights File", "", "All Files (*);;Python Files (*.pt)", options=options)
        if file:
            self.detect_weights_input.setText(file)

    def select_detect_weights_file_dir(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, "Select Weights File", "", "All Files (*);;Python Files (*.pt)", options=options)
        if file:
            self.detect_weights_input_dir.setText(file)

    def start_training(self):
        weights = self.weights_input.text()
        data = self.data_input.text()
        hyp = self.hyp_input.text()
        epochs = self.epochs_input.text()
        batch_size = self.batch_size_input.text()
        mode = self.mode_selector.currentText()  # 获取选择的模式

        if not all([weights, data, hyp, epochs, batch_size]):
            QMessageBox.warning(self, "Input Error", "All fields are required")
            return

        # 显示训练开始的提示框
        # self.loading_message.setText("Training has started...")
        # self.loading_message.show()

        # 根据模式生成不同的命令
        if mode == "目标识别":
            command = f"python train.py --weights {weights} --data {data} --hyp {hyp} --epochs {epochs} --batch-size {batch_size}"
        elif mode == "实例分割":
            command = f"python segment/train.py --weights {weights} --data {data} --hyp {hyp} --epochs {epochs} --batch-size {batch_size}"
        self.run_command(command, self.output_display)

    def start_detecting(self):
        image = self.image_input.text()
        weights = self.detect_weights_input.text()
        conf_thres = self.conf_thres_input.text()
        hide_labels = self.hide_labels_checkbox.isChecked()
        hide_conf = self.hide_conf_checkbox.isChecked()

        if not all([image, weights, conf_thres]):
            QMessageBox.warning(self, "Input Error", "All fields are required")
            return

        # 显示加载中的提示框
        self.loading_message.setText("Detecting... Please wait.")
        self.loading_message.show()

        command = f"python detect.py --source {image} --weights {weights} --conf-thres {conf_thres}"
        command += f" --hide-labels {'True' if hide_labels else 'False'}"
        command += f" --hide-conf {'True' if hide_conf else 'False'}"
        
        self.run_command(command, self.detect_output_display, image)

    def start_detecting_dir(self):
        directory = self.directory_input.text()
        weights = self.detect_weights_input_dir.text()
        conf_thres = self.conf_thres_input_dir.text()
        hide_labels = self.hide_labels_checkbox_dir.isChecked()
        hide_conf = self.hide_conf_checkbox_dir.isChecked()

        if not all([directory, weights, conf_thres]):
            QMessageBox.warning(self, "Input Error", "All fields are required")
            return

        # 显示加载中的提示框
        self.loading_message.setText("Detecting... Please wait.")
        self.loading_message.show()

        command = f"python detect.py --source {directory} --weights {weights} --conf-thres {conf_thres}"
        command += f" --hide-labels {'True' if hide_labels else 'False'}"
        command += f" --hide-conf {'True' if hide_conf else 'False'}"

        
        self.run_command(command, self.detect_output_display_dir, directory)

    def run_command(self, command, output_display, image_path=None):
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(lambda: self.on_ready_read_standard_output(output_display))
        if image_path:
            self.process.finished.connect(lambda: self.on_detection_finished(image_path))
        self.process.finished.connect(self.loading_message.hide)  # 检测完成后关闭加载提示框
        self.process.start(command)

    def save_detection(self):
        if hasattr(self, 'result_image_path'):
            options = QFileDialog.Options()
            default_file_name = os.path.basename(self.result_image_path)
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Detection", default_file_name, "Images (*.png *.xpm *.jpg);;All Files (*)", options=options)
            if save_path:
                try:
                    # Save the image
                    shutil.copy(self.result_image_path, save_path)
                    
                    # Create labels directory
                    labels_src_dir = os.path.join(os.path.dirname(self.result_image_path), 'labels')
                    if os.path.exists(labels_src_dir) and os.path.isdir(labels_src_dir):
                        labels_dst_dir = os.path.join(os.path.dirname(save_path), 'labels')
                        os.makedirs(labels_dst_dir, exist_ok=True)
                        
                        # Save the corresponding labels file
                        label_file_name = os.path.basename(self.result_image_path).replace('.jpg', '.txt').replace('.png', '.txt').replace('.xpm', '.txt')
                        src_label_path = os.path.join(labels_src_dir, label_file_name)
                        if os.path.exists(src_label_path):
                            shutil.copy(src_label_path, os.path.join(labels_dst_dir, label_file_name))
                    
                    QMessageBox.information(self, "Save Successful", f"Image and labels saved to {save_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Save Failed", f"Failed to save image and labels: {str(e)}")
        else:
            QMessageBox.warning(self, "No Image", "No detected image to save.")

    def save_all_detections(self):
        if hasattr(self, 'result_directory_path'):
            options = QFileDialog.Options()
            save_dir = QFileDialog.getExistingDirectory(self, "Save All Detections", options=options)
            if save_dir:
                try:
                    for file_name in os.listdir(self.result_directory_path):
                        full_file_name = os.path.join(self.result_directory_path, file_name)
                        if os.path.isfile(full_file_name):
                            shutil.copy(full_file_name, save_dir)
                    
                    # Save the labels directory
                    labels_src_dir = os.path.join(self.result_directory_path, 'labels')
                    if os.path.exists(labels_src_dir) and os.path.isdir(labels_src_dir):
                        labels_dst_dir = os.path.join(save_dir, 'labels')
                        shutil.copytree(labels_src_dir, labels_dst_dir)
                    
                    QMessageBox.information(self, "Save Successful", f"All images and labels saved to {save_dir}")
                except Exception as e:
                    QMessageBox.critical(self, "Save Failed", f"Failed to save images and labels: {str(e)}")
            else:
                QMessageBox.warning(self, "Save Cancelled", "Save operation was cancelled.")
        else:
            QMessageBox.warning(self, "No Directory", "No detected images to save.")

    def on_ready_read_standard_output(self, output_display):
        try:
            output = self.process.readAllStandardOutput().data().decode('utf-8')
        except UnicodeDecodeError:
            output = self.process.readAllStandardOutput().data().decode('latin-1')
        output_display.appendPlainText(output)

    def on_detection_finished(self, image_path):
        result_dir = self.get_latest_result_dir()
        if result_dir:
            if os.path.isdir(image_path):  # Directory detection
                self.result_directory_path = result_dir
                self.display_detection_results(result_dir)
            else:  # Single image detection
                self.result_image_path = os.path.join(result_dir, os.path.basename(image_path))
                self.display_image(self.result_image_path, True)
                self.display_detection_results(result_dir)
        else:
            QMessageBox.warning(self, "Result Error", "No result directory found.")

    def get_latest_result_dir(self):
        runs_dir = os.path.join('runs', 'detect')
        exp_dirs = [d for d in os.listdir(runs_dir) if os.path.isdir(os.path.join(runs_dir, d)) and d.startswith('exp') and d[3:].isdigit()]
        exp_dirs.sort(key=lambda x: int(x[3:]), reverse=True)
        latest_dir = os.path.join(runs_dir, exp_dirs[0]) if exp_dirs else None
        return latest_dir
    

    def get_latest_result_dir_seg(self):
        runs_dir = os.path.join('runs', 'predict-seg')
        exp_dirs = [d for d in os.listdir(runs_dir) if os.path.isdir(os.path.join(runs_dir, d)) and d.startswith('exp') and d[3:].isdigit()]
        exp_dirs.sort(key=lambda x: int(x[3:]), reverse=True)
        latest_dir_seg = os.path.join(runs_dir, exp_dirs[0]) if exp_dirs else None
        return latest_dir_seg
    


    def display_image(self, image_path, is_result=False):
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if is_result:
                self.result_image_display.setPixmap(pixmap.scaled(self.result_image_display.size(), Qt.KeepAspectRatio))
            else:
                self.image_display.setPixmap(pixmap.scaled(self.image_display.size(), Qt.KeepAspectRatio))
        else:
            QMessageBox.warning(self, "Image Error", f"Image file {image_path} not found.")

    def display_detection_results(self, result_dir):
        labels_dir = os.path.join(result_dir, 'labels')
        if os.path.exists(labels_dir):
            result_files = [f for f in os.listdir(labels_dir) if f.endswith('.txt')]

            counts = {}
            for result_file in result_files:
                with open(os.path.join(labels_dir, result_file), 'r') as f:
                    results = f.readlines()
                for line in results:
                    cls = line.split()[0]
                    if cls in counts:
                        counts[cls] += 1
                    else:
                        counts[cls] = 1

            result_text = "Detection Results:\n"
            for cls, count in counts.items():
                result_text += f"Class {cls}: {count}\n"

            self.detect_output_display.appendPlainText(result_text)
        else:
            self.detect_output_display.appendPlainText("No labels directory found in result directory.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = YOLOv9Interface()
    window.show()
    sys.exit(app.exec_())
