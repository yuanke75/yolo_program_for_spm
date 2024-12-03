import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QGroupBox, QWidget, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QProgressBar, QDialog, QFormLayout, QDialogButtonBox, QMessageBox,QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class ClassDialog(QDialog):
    def __init__(self, class_labels, parent=None):
        super(ClassDialog, self).__init__(parent)
        self.class_labels = class_labels
        self.class_info = []
        self.setWindowTitle('Class Information Input')

        layout = QVBoxLayout()
        self.form_layout = QFormLayout()
        self.class_id_inputs = []

        for i, label in enumerate(class_labels):
            class_id_input = QLineEdit(self)
            self.form_layout.addRow(f'Class "{label}" ID:', class_id_input)
            self.class_id_inputs.append(class_id_input)

        layout.addLayout(self.form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def accept(self):
        for class_id_input, label in zip(self.class_id_inputs, self.class_labels):
            class_id = class_id_input.text().strip()
            if class_id:
                self.class_info.append((label, int(class_id)))
        super(ClassDialog, self).accept()


class ConversionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('JSON to TXT Conversion Tool')
        layout = QVBoxLayout()

        # JSON Folder Group
        json_folder_group = QGroupBox("JSON Folder Path")
        json_folder_layout = QHBoxLayout()
        self.json_folder_input = QLineEdit(self)
        self.json_folder_button = QPushButton('Browse', self)
        self.json_folder_button.clicked.connect(self.browse_json_folder)
        json_folder_layout.addWidget(self.json_folder_input)
        json_folder_layout.addWidget(self.json_folder_button)
        json_folder_group.setLayout(json_folder_layout)
        
        # Output Folder Group
        output_folder_group = QGroupBox("Output Folder Path")
        output_folder_layout = QHBoxLayout()
        self.output_folder_input = QLineEdit(self)
        self.output_folder_button = QPushButton('Browse', self)
        self.output_folder_button.clicked.connect(self.browse_output_folder)
        output_folder_layout.addWidget(self.output_folder_input)
        output_folder_layout.addWidget(self.output_folder_button)
        output_folder_group.setLayout(output_folder_layout)
        
        # Progress Bar and Start Button
        self.class_info_button = QPushButton('Enter Class Information', self)
        self.class_info_button.clicked.connect(self.enter_class_info)
        self.start_button = QPushButton('Start Conversion', self)
        self.start_button.clicked.connect(self.start_conversion)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        
        # Adding Widgets to Main Layout
        layout.addWidget(json_folder_group)
        layout.addWidget(output_folder_group)
        layout.addWidget(self.class_info_button)
        layout.addWidget(self.start_button)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        self.class_info = []
        self.json_folder_path = ""

        # Apply Styles
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
    
    def browse_json_folder(self):
        options = QFileDialog.Options()
        folder_path = QFileDialog.getExistingDirectory(self, 'Select JSON Folder', options=options)
        if folder_path:
            self.json_folder_input.setText(folder_path)
            self.json_folder_path = folder_path

    def browse_output_folder(self):
        options = QFileDialog.Options()
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Output Folder', options=options)
        if folder_path:
            self.output_folder_input.setText(folder_path)

    def enter_class_info(self):
        if not self.json_folder_path:
            QMessageBox.warning(self, 'Input Error', 'Please select a JSON folder path first.')
            return
        
        class_labels = set()
        for filename in os.listdir(self.json_folder_path):
            if filename.endswith('.json'):
                json_path = os.path.join(self.json_folder_path, filename)
                with open(json_path) as f:
                    data = json.load(f)
                    for shape in data['shapes']:
                        class_labels.add(shape['label'])
        
        if class_labels:
            dialog = ClassDialog(class_labels)
            if dialog.exec_():
                self.class_info = dialog.class_info

    def start_conversion(self):
        json_folder_path = self.json_folder_input.text()
        output_folder_path = self.output_folder_input.text()

        if not json_folder_path or not output_folder_path or not self.class_info:
            QMessageBox.warning(self, 'Input Error', 'Please provide all the required inputs and class information.')
            return

        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        json_files = [f for f in os.listdir(json_folder_path) if f.endswith('.json')]
        total_files = len(json_files)
        self.progress_bar.setValue(0)

        for idx, filename in enumerate(json_files):
            json_path = os.path.join(json_folder_path, filename)
            output_txt_name = filename.replace('.json', '.txt')
            output_txt_path = os.path.join(output_folder_path, output_txt_name)
            
            with open(json_path) as f:
                data = json.load(f)
            
            image_width = data['imageWidth']
            image_height = data['imageHeight']

            with open(output_txt_path, 'w') as txt_file:
                for shape in data['shapes']:
                    bbox = shape['points']
                    x1, y1 = bbox[0]
                    x2, y2 = bbox[1]
                    x, y, w, h = self.bbox_to_xywh(x1, y1, x2, y2, image_width, image_height)

                    label = shape['label']
                    class_id = next((class_id for lbl, class_id in self.class_info if lbl == label), None)
                    if class_id is not None:
                        txt_file.write(f"{class_id} {x} {y} {w} {h}\n")

            self.progress_bar.setValue(int((idx + 1) / total_files * 100))

        QMessageBox.information(self, 'Success', 'All JSON files have been successfully converted to TXT files.')

    def bbox_to_xywh(self, x1, y1, x2, y2, img_w, img_h):
        w = x2 - x1
        h = y2 - y1
        x = x1 + w / 2
        y = y1 + h / 2
        return x / img_w, y / img_h, w / img_w, h / img_h


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ConversionApp()
    ex.show()
    sys.exit(app.exec_())
