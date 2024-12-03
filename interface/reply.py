# import sys
# import os
# from PyQt5.QtWidgets import (
#     QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QSlider, QMessageBox, QGridLayout, QGroupBox, QFormLayout, QScrollArea
# )
# from PyQt5.QtCore import Qt
# from PyQt5.QtGui import QFont

# class DatasetMergerApp(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()

#     def initUI(self):
#         self.setWindowTitle('Dataset Merger Tool')

#         layout = QVBoxLayout()

#         self.scroll = QScrollArea()
#         self.scroll.setWidgetResizable(True)
#         self.scroll_content = QWidget()
#         self.scroll_layout = QVBoxLayout(self.scroll_content)

#         self.datasets_layout = QVBoxLayout()

#         # Add initial source dataset
#         self.add_source_dataset()

#         self.add_dataset_button = QPushButton('Add Source Dataset', self)
#         self.add_dataset_button.clicked.connect(self.add_source_dataset)

#         self.scroll_layout.addLayout(self.datasets_layout)
#         self.scroll.setWidget(self.scroll_content)
#         layout.addWidget(self.scroll)
#         layout.addWidget(self.add_dataset_button)

#         # Target dataset
#         self.target_label = QLabel('Target Dataset:')
#         self.target_input = QLineEdit(self)
#         self.target_button = QPushButton('Browse', self)
#         self.target_button.clicked.connect(lambda: self.browse_directory(self.target_input))

#         layout.addWidget(self.target_label)
#         layout.addWidget(self.target_input)
#         layout.addWidget(self.target_button)

#         # Merge button
#         self.merge_button = QPushButton('Merge Datasets', self)
#         self.merge_button.clicked.connect(self.merge_datasets)

#         layout.addWidget(self.merge_button)

#         self.setLayout(layout)

#         self.setFont(QFont('Arial', 12))
#         self.setStyleSheet("""
#             QWidget {
#                 background-color: #f0f0f0;
#             }
#             QLabel {
#                 font-size: 14px;
#             }
#             QLineEdit {
#                 padding: 5px;
#                 font-size: 14px;
#             }
#             QPushButton {
#                 font-size: 14px;
#                 background-color: #007BFF;
#                 color: white;
#                 padding: 5px;
#                 border-radius: 5px;
#             }
#             QPushButton:hover {
#                 background-color: #0056b3;
#             }
#             QSlider {
#                 background-color: #ffffff;
#             }
#         """)

#     def add_source_dataset(self):
#         group_box = QGroupBox("Source Dataset")
#         form_layout = QFormLayout()

#         src_label = QLabel('Source Dataset:')
#         src_input = QLineEdit(self)
#         src_button = QPushButton('Browse', self)
#         src_button.clicked.connect(lambda: self.browse_directory(src_input))

#         form_layout.addRow(src_label, src_input)
#         form_layout.addRow('', src_button)

#         slider_label = QLabel('Percentage:')
#         slider = QSlider(Qt.Horizontal, self)
#         slider.setMinimum(0)
#         slider.setMaximum(100)
#         slider.setValue(50)
#         slider.setTickInterval(10)
#         slider.setTickPosition(QSlider.TicksBelow)
#         percentage_label = QLabel('50%', self)
#         slider.valueChanged.connect(lambda: self.update_percentage_label(slider, percentage_label))

#         form_layout.addRow(slider_label, slider)
#         form_layout.addRow('', percentage_label)

#         group_box.setLayout(form_layout)
#         self.datasets_layout.addWidget(group_box)

#     def browse_directory(self, line_edit):
#         dir = QFileDialog.getExistingDirectory(self, 'Select Directory')
#         if dir:
#             line_edit.setText(dir)

#     def update_percentage_label(self, slider, label):
#         label.setText(f'{slider.value()}%')

#     def merge_files(self, src_file, target_file, percentage):
#         if not os.path.exists(src_file):
#             QMessageBox.warning(self, 'File Error', f'File does not exist: {src_file}')
#             return

#         with open(src_file, 'r') as file:
#             lines = file.readlines()

#         num_lines = len(lines)
#         num_to_copy = int(num_lines * (percentage / 100))
#         selected_lines = lines[:num_to_copy]

#         with open(target_file, 'a') as file:
#             file.writelines(selected_lines)

#     def backup_and_create_new_file(self, file_path):
#         if os.path.exists(file_path):
#             base_name, ext = os.path.splitext(file_path)
#             backup_file = base_name + '_backup' + ext
#             os.rename(file_path, backup_file)
#         open(file_path, 'w').close()

#     def merge_datasets(self):
#         target_dir = self.target_input.text()

#         if not os.path.exists(target_dir):
#             os.makedirs(target_dir)

#         target_train_file = os.path.join(target_dir, 'train.txt')
#         target_valid_file = os.path.join(target_dir, 'valid.txt')

#         # Backup and create new target files
#         self.backup_and_create_new_file(target_train_file)
#         self.backup_and_create_new_file(target_valid_file)

#         for i in range(self.datasets_layout.count()):
#             group_box = self.datasets_layout.itemAt(i).widget()
#             src_input = group_box.findChild(QLineEdit)
#             slider = group_box.findChild(QSlider)

#             src_dir = src_input.text()
#             percentage = slider.value()

#             src_train_file = os.path.join(src_dir, 'train.txt')
#             src_valid_file = os.path.join(src_dir, 'valid.txt')

#             self.merge_files(src_train_file, target_train_file, percentage)
#             self.merge_files(src_valid_file, target_valid_file, percentage)

#         QMessageBox.information(self, 'Success', 'Datasets merged successfully.')

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     merger = DatasetMergerApp()
#     merger.show()
#     sys.exit(app.exec_())
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QSlider, QMessageBox, QGroupBox, QFormLayout, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class DatasetMergerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('数据集合并工具')

        layout = QVBoxLayout()

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        self.datasets_layout = QVBoxLayout()

        # 添加初始源数据集
        self.add_source_dataset()

        self.add_dataset_button = QPushButton('添加源数据集', self)
        self.add_dataset_button.clicked.connect(self.add_source_dataset)

        self.scroll_layout.addLayout(self.datasets_layout)
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)
        layout.addWidget(self.add_dataset_button)

        # 目标数据集
        self.target_label = QLabel('目标数据集:')
        self.target_input = QLineEdit(self)
        self.target_button = QPushButton('浏览', self)
        self.target_button.clicked.connect(lambda: self.browse_directory(self.target_input))

        layout.addWidget(self.target_label)
        layout.addWidget(self.target_input)
        layout.addWidget(self.target_button)

        # 合并按钮
        self.merge_button = QPushButton('合并数据集', self)
        self.merge_button.clicked.connect(self.merge_datasets)

        layout.addWidget(self.merge_button)

        self.setLayout(layout)

        self.setFont(QFont('Arial', 12))
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit {
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                font-size: 14px;
                background-color: #007BFF;
                color: white;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QSlider {
                background-color: #ffffff;
            }
        """)

    def add_source_dataset(self):
        group_box = QGroupBox("源数据集")
        form_layout = QFormLayout()

        src_label = QLabel('源数据集:')
        src_input = QLineEdit(self)
        src_button = QPushButton('浏览', self)
        src_button.clicked.connect(lambda: self.browse_file(src_input))

        form_layout.addRow(src_label, src_input)
        form_layout.addRow('', src_button)

        slider_label = QLabel('百分比:')
        slider = QSlider(Qt.Horizontal, self)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(50)
        slider.setTickInterval(10)
        slider.setTickPosition(QSlider.TicksBelow)
        percentage_label = QLabel('50%', self)
        slider.valueChanged.connect(lambda: self.update_percentage_label(slider, percentage_label))

        form_layout.addRow(slider_label, slider)
        form_layout.addRow('', percentage_label)

        group_box.setLayout(form_layout)
        self.datasets_layout.addWidget(group_box)

    def browse_directory(self, line_edit):
        dir = QFileDialog.getExistingDirectory(self, '选择目录')
        if dir:
            line_edit.setText(dir)

    def browse_file(self, line_edit):
        file, _ = QFileDialog.getOpenFileName(self, '选择文件', '', '文本文件 (*.txt)')
        if file:
            line_edit.setText(file)

    def update_percentage_label(self, slider, label):
        label.setText(f'{slider.value()}%')

    def merge_files(self, src_file, target_file, percentage):
        if not os.path.exists(src_file):
            QMessageBox.warning(self, '文件错误', f'文件不存在: {src_file}')
            return

        with open(src_file, 'r') as file:
            lines = file.readlines()

        num_lines = len(lines)
        num_to_copy = int(num_lines * (percentage / 100))
        selected_lines = lines[:num_to_copy]

        with open(target_file, 'a') as file:
            file.writelines(selected_lines)

    def merge_datasets(self):
        target_dir = self.target_input.text()

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        target_train_file = os.path.join(target_dir, 'train.txt')
        target_valid_file = os.path.join(target_dir, 'valid.txt')

        # 备份并创建新目标文件
        self.backup_and_create_new_file(target_train_file)
        self.backup_and_create_new_file(target_valid_file)

        for i in range(self.datasets_layout.count()):
            group_box = self.datasets_layout.itemAt(i).widget()
            src_input = group_box.findChild(QLineEdit)
            slider = group_box.findChild(QSlider)

            src_file = src_input.text()
            percentage = slider.value()

            if 'train' in src_file:
                self.merge_files(src_file, target_train_file, percentage)
            elif 'valid' in src_file:
                self.merge_files(src_file, target_valid_file, percentage)

        QMessageBox.information(self, '成功', '数据集合并成功。')

    def backup_and_create_new_file(self, file_path):
        if os.path.exists(file_path):
            base_name, ext = os.path.splitext(file_path)
            backup_file = base_name + '_backup' + ext
            os.rename(file_path, backup_file)
        open(file_path, 'w').close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    merger = DatasetMergerApp()
    merger.show()
    sys.exit(app.exec_())
