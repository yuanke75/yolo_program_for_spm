import os
import json
from PyQt5.QtWidgets import (QWidget, QGroupBox, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QSpinBox, QFileDialog, QMessageBox)
from expert_app import ExpertApp

class BasicApp(QWidget):
    def __init__(self, expert_app):
        super().__init__()
        self.expert_app = expert_app
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # JSON File Group
        json_group = QGroupBox("JSON File")
        json_layout = QHBoxLayout()
        self.filename_input = QLineEdit(self)
        self.filename_button = QPushButton('Browse', self)
        self.filename_button.clicked.connect(self.browse_filename)
        json_layout.addWidget(self.filename_input)
        json_layout.addWidget(self.filename_button)
        json_group.setLayout(json_layout)
        
        # Output Path Group
        output_group = QGroupBox("Output Path")
        output_layout = QHBoxLayout()
        self.outputpath_input = QLineEdit(self)
        self.outputpath_button = QPushButton('Browse', self)
        self.outputpath_button.clicked.connect(self.browse_outputpath)
        output_layout.addWidget(self.outputpath_input)
        output_layout.addWidget(self.outputpath_button)
        output_group.setLayout(output_layout)
        
        # Number of Augmentations Group
        aug_times_group = QGroupBox("Number of Augmentations")
        aug_times_layout = QHBoxLayout()
        self.aug_times_input = QSpinBox(self)
        self.aug_times_input.setMinimum(1)
        self.aug_times_input.setValue(15)
        aug_times_layout.addWidget(self.aug_times_input)
        aug_times_group.setLayout(aug_times_layout)
        
        # Make Dataset Button
        self.make_dataset_button = QPushButton('Make Dataset', self)
        self.make_dataset_button.clicked.connect(self.make_dataset)
        
        layout.addWidget(json_group)
        layout.addWidget(output_group)
        layout.addWidget(aug_times_group)
        layout.addWidget(self.make_dataset_button)
        
        self.setLayout(layout)
        
    def browse_filename(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, 'Select JSON File', '', 'JSON Files (*.json)', options=options)
        if filename:
            self.filename_input.setText(filename)
            self.expert_app.filename_input.setText(filename)

    def browse_outputpath(self):
        options = QFileDialog.Options()
        outputpath = QFileDialog.getExistingDirectory(self, 'Select Output Directory', options=options)
        if outputpath:
            self.outputpath_input.setText(outputpath)
            self.expert_app.outputpath_input.setText(outputpath)

    def make_dataset(self):
        QMessageBox.information(self, 'Please Wait', 'Please wait, creating the dataset...')
        self.expert_app.aug_times_input.setValue(self.aug_times_input.value())

        # Set default paths and values
        output_path = self.outputpath_input.text()
        if output_path:
            self.expert_app.json_folder_input.setText(os.path.join(output_path, 'dataset/voc/worktxt'))
            self.expert_app.output_folder_input.setText(os.path.join(output_path, 'dataset/voc/worktxt'))
            self.expert_app.root_path_input.setText(output_path)
            self.expert_app.train_test_percent_input.setValue(80)
            self.expert_app.train_valid_percent_input.setValue(80)
            
            # Automatically enter class info as 0, 1, 2, ...
            class_labels = set()
            json_file = self.filename_input.text()
            if json_file and os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for shape in data['shapes']:
                        class_labels.add(shape['label'])
            
            class_info = [(label, idx) for idx, label in enumerate(class_labels)]
            self.expert_app.class_info = class_info
            
            # Select all augmentation checkboxes
            self.expert_app.dropout_checkbox.setChecked(True)
            self.expert_app.elastic_transform_checkbox.setChecked(True)
            self.expert_app.gaussian_blur_checkbox.setChecked(True)
            self.expert_app.multiply_brightness_checkbox.setChecked(True)
            self.expert_app.multiply_hue_saturation_checkbox.setChecked(True)
            self.expert_app.add_hue_checkbox.setChecked(True)
            self.expert_app.add_saturation_checkbox.setChecked(True)
            
            # Start the augmentation, conversion, and splitting process
            self.expert_app.start_augmentation()
            self.expert_app.start_conversion()
            self.expert_app.split_dataset()
            
            QMessageBox.information(self, 'Success', 'Dataset created successfully.')
