import sys
import os
import json
import shutil
import random
from PyQt5.QtWidgets import (QApplication, QGroupBox, QWidget, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QProgressBar, QCheckBox, QHBoxLayout, QMessageBox, QSpinBox, QDialog, QFormLayout, QDialogButtonBox, QLabel, QStackedWidget)
from PyQt5.QtCore import Qt
import imageio.v2 as imageio
import imgaug as ia
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
from imgaug import augmenters as iaa
from PIL import Image
import io
import base64
import copy
import numpy as np
import yaml
from PyQt5.QtGui import QFont
from imgaug.augmentables.polys import Polygon, PolygonsOnImage
from labelv7 import LabelingTool  # Ensure you import LabelingTool from the correct module

# Define a recursive function to handle and convert all float32 values
def convert_float32(obj):
    if isinstance(obj, list):
        return [convert_float32(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_float32(v) for k, v in obj.items()}
    elif isinstance(obj, np.float32):
        return float(obj)
    return obj

def bbox_to_xywh(x1, y1, x2, y2, img_w, img_h):
    w = x2 - x1
    h = y2 - y1
    x = x1 + w / 2
    y = y1 + h / 2
    return x / img_w, y / img_h, w / img_w, h / img_h

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

        # 连接信号
        self.labeling_tool = LabelingTool()
        self.labeling_tool.label_index_updated.connect(self.reload_label_index)

    def reload_label_index(self):
        self.expert_app.load_label_index()

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

class ExpertApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # Augmentation section
        aug_layout = QHBoxLayout()
        aug_left_layout = QVBoxLayout()
        aug_right_layout = QVBoxLayout()

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
        aug_times_layout.addWidget(self.aug_times_input)
        aug_times_group.setLayout(aug_times_layout)

        # Add groups to left layout
        aug_left_layout.addWidget(json_group)
        aug_left_layout.addWidget(output_group)
        aug_left_layout.addWidget(aug_times_group)

        # Augmentation options
        self.dropout_checkbox = QCheckBox("Dropout")
        self.elastic_transform_checkbox = QCheckBox("Elastic Transformation")
        self.gaussian_blur_checkbox = QCheckBox("Gaussian Blur")
        self.multiply_brightness_checkbox = QCheckBox("Multiply Brightness")
        self.multiply_hue_saturation_checkbox = QCheckBox("Multiply Hue and Saturation")
        self.add_hue_checkbox = QCheckBox("Add Hue")
        self.add_saturation_checkbox = QCheckBox("Add Saturation")
        self.horizontal_jitter_checkbox = QCheckBox("horizontal Jitter")

        aug_right_layout.addWidget(self.dropout_checkbox)
        aug_right_layout.addWidget(self.elastic_transform_checkbox)
        aug_right_layout.addWidget(self.gaussian_blur_checkbox)
        aug_right_layout.addWidget(self.multiply_brightness_checkbox)
        aug_right_layout.addWidget(self.multiply_hue_saturation_checkbox)
        aug_right_layout.addWidget(self.add_hue_checkbox)
        aug_right_layout.addWidget(self.add_saturation_checkbox)
        aug_right_layout.addWidget(self.horizontal_jitter_checkbox)

        # Progress Bar and Start Button
        self.start_button = QPushButton('Start Augmentation', self)
        self.start_button.clicked.connect(self.start_augmentation)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)

        aug_right_layout.addWidget(self.start_button)
        aug_right_layout.addWidget(self.progress_bar)

        # Add left and right layouts to main layout
        aug_layout.addLayout(aug_left_layout)
        aug_layout.addLayout(aug_right_layout)

        main_layout.addLayout(aug_layout)

        # Conversion section
        conversion_group = QGroupBox("Conversion Section")
        conversion_layout = QVBoxLayout()

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
        self.convert_button = QPushButton('Start Conversion', self)
        self.convert_button.clicked.connect(self.start_conversion)
        self.convert_progress_bar = QProgressBar(self)
        self.convert_progress_bar.setAlignment(Qt.AlignCenter)
        self.convert_progress_bar.setMinimum(0)
        self.convert_progress_bar.setMaximum(100)

        # Adding Widgets to Conversion Layout
        conversion_layout.addWidget(json_folder_group)
        conversion_layout.addWidget(output_folder_group)
        conversion_layout.addWidget(self.class_info_button)
        conversion_layout.addWidget(self.convert_button)
        conversion_layout.addWidget(self.convert_progress_bar)

        conversion_group.setLayout(conversion_layout)

        main_layout.addWidget(conversion_group)

        # Splitter section
        splitter_group = QGroupBox("Dataset Splitter")
        splitter_layout = QVBoxLayout()

        # Root Path Group
        root_path_group = QGroupBox("Root Path")
        root_path_layout = QHBoxLayout()
        self.root_path_input = QLineEdit()
        self.root_path_button = QPushButton('Browse')
        self.root_path_button.clicked.connect(self.browse_root_path)
        root_path_layout.addWidget(self.root_path_input)
        root_path_layout.addWidget(self.root_path_button)
        root_path_group.setLayout(root_path_layout)
        
        # Train/Test/Validation Percentages Group
        percent_group = QGroupBox("Train/Test/Validation Percentages")
        percent_layout = QVBoxLayout()
        
        self.train_test_percent_label = QLabel('Train/Test Percent (0-100):')
        self.train_test_percent_input = QSpinBox()
        self.train_test_percent_input.setRange(0, 100)
        self.train_test_percent_input.setValue(90)

        self.train_valid_percent_label = QLabel('Train/Valid Percent (0-100):')
        self.train_valid_percent_input = QSpinBox()
        self.train_valid_percent_input.setRange(0, 100)
        self.train_valid_percent_input.setValue(90)

        percent_layout.addWidget(self.train_test_percent_label)
        percent_layout.addWidget(self.train_test_percent_input)
        percent_layout.addWidget(self.train_valid_percent_label)
        percent_layout.addWidget(self.train_valid_percent_input)
        percent_group.setLayout(percent_layout)

        # Split Button
        self.split_button = QPushButton('Split and Organize Dataset')
        self.split_button.clicked.connect(self.split_dataset)

        # Adding Widgets to Splitter Layout
        splitter_layout.addWidget(root_path_group)
        splitter_layout.addWidget(percent_group)
        splitter_layout.addWidget(self.split_button)

        splitter_group.setLayout(splitter_layout)
        main_layout.addWidget(splitter_group)

        self.setLayout(main_layout)
        self.class_info = []
        self.json_folder_path = ""
        self.label_index_path = os.path.join(os.path.dirname(__file__), '..', 'label_indices', 'label_index.json')
        self.load_label_index()

    def load_label_index(self):
        with open(self.label_index_path, 'r', encoding='utf-8') as f:
            self.label_index = json.load(f)

    def browse_filename(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, 'Select JSON File', '', 'JSON Files (*.json)', options=options)
        if filename:
            self.filename_input.setText(filename)

    def browse_outputpath(self):
        options = QFileDialog.Options()
        outputpath = QFileDialog.getExistingDirectory(self, 'Select Output Directory', options=options)
        if outputpath:
            self.outputpath_input.setText(outputpath)


    def start_augmentation(self):
        filename = self.filename_input.text()
        output_path = self.outputpath_input.text()
        aug_times = self.aug_times_input.value()

        if not filename or not output_path:
            QMessageBox.warning(self, 'Input Error', 'Please provide all the required inputs.')
            return

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        with open(filename, 'r', encoding='utf-8') as f:
            original_squad_box = json.load(f)

        image_data = base64.b64decode(original_squad_box['imageData'])
        image = Image.open(io.BytesIO(image_data))
        image = np.array(image)

        rotation_list = list(range(15, 360, 15))

        ia.seed(42)

        sometimes = lambda aug: iaa.Sometimes(1, aug)
        augments = []

        # Add augmentations
        if self.dropout_checkbox.isChecked():
            augments.append(sometimes(iaa.Dropout((0.01, 0.1), per_channel=0.5)))
        if self.elastic_transform_checkbox.isChecked():
            augments.append(sometimes(iaa.ElasticTransformation(alpha=(0.5, 3.5), sigma=0.25)))
        if self.gaussian_blur_checkbox.isChecked():
            augments.append(sometimes(iaa.GaussianBlur(sigma=(0.0, 3.0))))
        if self.multiply_brightness_checkbox.isChecked():
            augments.append(sometimes(iaa.MultiplyBrightness(mul=(0.7, 1.3))))
        if self.multiply_hue_saturation_checkbox.isChecked():
            augments.append(sometimes(iaa.MultiplyHueAndSaturation(mul_hue=(0.8, 1.2), mul_saturation=(0.8, 1.2))))
        if self.add_hue_checkbox.isChecked():
            augments.append(sometimes(iaa.AddToHue(value=(-10, 10))))
        if self.add_saturation_checkbox.isChecked():
            augments.append(sometimes(iaa.AddToSaturation(value=(-10, 10))))
        if self.horizontal_jitter_checkbox.isChecked():
            augments.append(sometimes(iaa.Affine(translate_percent={"x": (-0.05, 0.05)})))  # 水平方向随机平移 -5% 到 5%


        # Combine rotation and other augmentations
        seq = iaa.Sequential([iaa.Affine(rotate=rotation_list,fit_output=True)] + augments, random_order=True)

        total_operations = len(rotation_list) * (aug_times if seq else 1)
        progress = 0

        self.progress_bar.setValue(0)
        jpegimages_path = os.path.join(output_path, 'dataset/voc/JPEGImages')
        worktxt_path = os.path.join(output_path, 'dataset/voc/worktxt')

        if not os.path.exists(jpegimages_path):
            os.makedirs(jpegimages_path)
        if not os.path.exists(worktxt_path):
            os.makedirs(worktxt_path)

        # Process image and annotations
        for theta in rotation_list:
            squad_box = copy.deepcopy(original_squad_box)

            file_prefix = os.path.splitext(os.path.basename(filename))[0]
            new_image_name = f"{file_prefix}_{theta}.jpg"
            new_image_path = os.path.join(output_path, new_image_name)

            # Separate bounding boxes and polygons
            bbs_list = []
            polygons_list = []
            for shape in squad_box['shapes']:
                if shape['shape_type'] == 'rectangle':
                    bbox = shape['points']
                    x1, y1 = bbox[0]
                    x2, y2 = bbox[1]
                    bbs_list.append(BoundingBox(x1=x1, x2=x2, y1=y1, y2=y2))
                elif shape['shape_type'] == 'polygon':
                    polygon_points = shape['points']
                    polygons_list.append(Polygon(polygon_points))

            # Create bounding boxes and polygons objects
            bbs = BoundingBoxesOnImage(bbs_list, shape=image.shape)
            polys = PolygonsOnImage(polygons_list, shape=image.shape)

            # Apply augmentations consistently to both image and annotations
            for i in range(aug_times):
                aug_image_name = f"{file_prefix}_{theta}_aug_{i}.jpg"
                aug_image_path = os.path.join(output_path, aug_image_name)

                # Apply augmentations to both image, bounding boxes, and polygons
                image_aug, bbs_aug, polys_aug = seq(image=image, bounding_boxes=bbs, polygons=polys)

                # Save the augmented image and annotations
                self.save_augmented_image(image_aug, bbs_aug, polys_aug, squad_box, aug_image_name, aug_image_path, jpegimages_path, worktxt_path)

                progress += 1
                self.progress_bar.setValue(int((progress / total_operations) * 100))

        QMessageBox.information(self, 'Success', 'Augmentation completed successfully.')

    def save_augmented_image(self, image_aug, bbs_aug, polys_aug, squad_box, image_name, image_path, jpegimages_path, worktxt_path):
        # Save the augmented image
        imageio.imwrite(image_path, image_aug)
        
        # Copy the image to JPEGImages folder
        shutil.copy(image_path, jpegimages_path)
        
        # Convert the augmented image to JPEG and save as base64
        pil_img = Image.fromarray(image_aug)
        buff = io.BytesIO()
        pil_img.save(buff, format="JPEG")
        base64_string = base64.b64encode(buff.getvalue()).decode("utf-8")

        # Update annotations with new bounding boxes and polygons
        new_shapes = []
        for i, shape in enumerate(squad_box['shapes']):
            if shape['shape_type'] == 'rectangle':
                bb_aug = bbs_aug.bounding_boxes[i]
                x1_new, y1_new = bb_aug.x1, bb_aug.y1
                x2_new, y2_new = bb_aug.x2, bb_aug.y2
                new_shapes.append({
                    'label': shape['label'],
                    'points': [[x1_new, y1_new], [x2_new, y2_new]],
                    'group_id': shape.get('group_id'),
                    'shape_type': 'rectangle',
                    'flags': shape.get('flags', {})
                })
            elif shape['shape_type'] == 'polygon':
                poly_aug = polys_aug.polygons[i]
                augmented_polygon_points = poly_aug.exterior.tolist()
                new_shapes.append({
                    'label': shape['label'],
                    'points': augmented_polygon_points,
                    'group_id': shape.get('group_id'),
                    'shape_type': 'polygon',
                    'flags': shape.get('flags', {})
                })

        # Update the JSON with the new image and annotations
        squad_box['imagePath'] = image_name
        squad_box['imageData'] = base64_string
        squad_box['imageHeight'], squad_box['imageWidth'] = image_aug.shape[0:2]
        squad_box['shapes'] = new_shapes
        
        # Ensure conversion of np.float32 to standard float
        squad_box = convert_float32(squad_box)

        # Save the new JSON file
        json_name = os.path.splitext(image_name)[0] + '.json'
        json_path = os.path.join(worktxt_path, json_name)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(squad_box, f, indent=4, ensure_ascii=False)





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
                print(f"Processing file: {json_path}")
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for shape in data['shapes']:
                        label = shape['label']
                        class_labels.add(label)
                        print(f"Found label: {label}")

        if class_labels:
            print(f"Class labels found: {class_labels}")
            class_info = []
            for label in class_labels:
                matched = False
                for class_id, class_name in self.label_index.items():
                    print(class_id, class_name)
                    # 分割 class_name 以获取标签
                    class_name_parts = class_name.split(':')
                    if len(class_name_parts) > 1 and class_name_parts[1] == label:
                        class_info.append((label, class_id))
                        matched = True
                        print(f"Matched label: {label} with class ID: {class_id}")
                        break
                if not matched:
                    print(f"Label '{label}' not found in the index")
                    QMessageBox.warning(self, 'Class Info Error', f'Label "{label}" not found in the index.')
                    return
            self.class_info = class_info
            print(f"Class info: {self.class_info}")

    def start_conversion(self):
        json_folder_path = self.json_folder_input.text()
        output_folder_path = self.output_folder_input.text()

        # 确保输出文件夹存在
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        # 函数：将多边形点集转换为归一化的格式
        def normalize_polygon(polygon, img_w, img_h):
            return [(x / img_w, y / img_h) for x, y in polygon]

        # 遍历文件夹中的所有JSON文件
        for filename in os.listdir(json_folder_path):
            if filename.endswith(".json"):
                json_path = os.path.join(json_folder_path, filename)
                output_txt_name = filename.replace('.json', '.txt')
                output_txt_path = os.path.join(output_folder_path, output_txt_name)

                # 读取JSON文件
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                image_width = data['imageWidth']
                image_height = data['imageHeight']

                # 处理每个标注，写入TXT文件
                with open(output_txt_path, 'w', encoding='utf-8') as txt_file:
                    for shape in data['shapes']:
                        if shape['shape_type'] == 'rectangle':
                            # 处理矩形，转换为YOLO格式
                            bbox = shape['points']
                            x1, y1 = bbox[0]
                            x2, y2 = bbox[1]
                            x_center, y_center, bbox_w, bbox_h = self.bbox_to_xywh(x1, y1, x2, y2, image_width, image_height)

                            # 假设您已经有一个class_info列表
                            label = shape['label']
                            class_id = next((class_id for lbl, class_id in self.class_info if lbl == label), None)
                            if class_id is not None:
                                txt_file.write(f"{class_id} {x_center} {y_center} {bbox_w} {bbox_h}\n")

                        elif shape['shape_type'] == 'polygon':
                            # 处理多边形，归一化并转换为YOLO格式
                            polygon = shape['points']
                            normalized_polygon = normalize_polygon(polygon, image_width, image_height)

                            # 根据标注名称分配类别ID
                            label = shape['label']
                            class_id = next((class_id for lbl, class_id in self.class_info if lbl == label), None)
                            if class_id is not None:
                                # 将多边形点集写入TXT文件
                                polygon_str = ' '.join(f"{x} {y}" for x, y in normalized_polygon)
                                txt_file.write(f"{class_id} {polygon_str}\n")

        QMessageBox.information(self, 'Success', 'All JSON files have been successfully converted to TXT files.')


    def bbox_to_xywh(self, x1, y1, x2, y2, img_w, img_h):
        w = x2 - x1
        h = y2 - y1
        x = x1 + w / 2
        y = y1 + h / 2
        return x / img_w, y / img_h, w / img_w, h / img_h

    def browse_root_path(self):
        dir = QFileDialog.getExistingDirectory(self, 'Select Root Directory')
        if dir:
            self.root_path_input.setText(dir)

    def split_dataset(self):
        root_path = self.root_path_input.text().replace('\\', '/')
        train_test_percent = self.train_test_percent_input.value() / 100
        train_valid_percent = self.train_valid_percent_input.value() / 100

        jpegimages_path = os.path.join(root_path, 'dataset/voc/JPEGImages').replace('\\', '/')
        txtsavepath = os.path.join(root_path, 'dataset/voc/worktxt').replace('\\', '/')
        ImageSetspath = os.path.join(root_path,'dataset/voc/ImageSets').replace('\\', '/')
        
        if not os.path.exists(ImageSetspath):
            os.makedirs(ImageSetspath)
        if not os.path.exists(jpegimages_path) or not os.path.exists(txtsavepath):
            QMessageBox.warning(self, 'Error', 'Required directories not found. Ensure augmentation and conversion are completed.')
            return

        total_images = [f for f in os.listdir(jpegimages_path) if f.endswith('.jpg')]
        total_txts = [f for f in os.listdir(txtsavepath) if f.endswith('.txt')]

        num = len(total_images)
        if num == 0:
            QMessageBox.warning(self, 'Error', 'No files found in the specified directory.')
            return

        list_indices = list(range(num))
        tv = int(num * train_test_percent)
        tr = int(tv * train_valid_percent)
        trainval = random.sample(list_indices, tv)
        train = random.sample(trainval, tr)

        train_txt = open(os.path.join(ImageSetspath, 'train.txt'), 'w', encoding='utf-8')
        valid_txt = open(os.path.join(ImageSetspath, 'valid.txt'), 'w', encoding='utf-8')
        test_txt = open(os.path.join(ImageSetspath, 'test.txt'), 'w', encoding='utf-8')

        train_img_txt = open(os.path.join(ImageSetspath, 'img_train.txt'), 'w', encoding='utf-8')
        valid_img_txt = open(os.path.join(ImageSetspath, 'img_valid.txt'), 'w', encoding='utf-8')
        test_img_txt = open(os.path.join(ImageSetspath, 'img_test.txt'), 'w', encoding='utf-8')

        for i in list_indices:
            txt_name = total_txts[i][:-4] + '.txt' + '\n'
            img_name = total_images[i][:-4] + '.jpg' + '\n'
            if i in trainval:
                if i in train:
                    train_txt.write(txt_name)
                    train_img_txt.write(img_name)
                else:
                    valid_txt.write(txt_name)
                    valid_img_txt.write(img_name)
            else:
                test_txt.write(txt_name)
                test_img_txt.write(img_name)

        train_txt.close()
        valid_txt.close()
        test_txt.close()
        train_img_txt.close()
        valid_img_txt.close()
        test_img_txt.close()

        self.organize_dataset(root_path, txtsavepath, ImageSetspath)

    def organize_dataset(self, root_path, txtsavepath, ImageSetspath):
        img_txt_cg_train = []
        img_txt_cg_test = []
        img_txt_cg_valid = []
        label_txt_cg_train = []
        label_txt_cg_test = []
        label_txt_cg_valid = []

        for line in open(os.path.join(ImageSetspath, "img_train.txt"), 'r', encoding='utf-8'):
            img_txt_cg_train.append(line.strip('\n'))
        for line in open(os.path.join(ImageSetspath, "img_test.txt"), 'r', encoding='utf-8'):
            img_txt_cg_test.append(line.strip('\n'))
        for line in open(os.path.join(ImageSetspath, "img_valid.txt"), 'r', encoding='utf-8'):
            img_txt_cg_valid.append(line.strip('\n'))

        for line in open(os.path.join(ImageSetspath, "train.txt"), 'r', encoding='utf-8'):
            label_txt_cg_train.append(line.strip('\n'))
        for line in open(os.path.join(ImageSetspath, "test.txt"), 'r', encoding='utf-8'):
            label_txt_cg_test.append(line.strip('\n'))
        for line in open(os.path.join(ImageSetspath, "valid.txt"), 'r', encoding='utf-8'):
            label_txt_cg_valid.append(line.strip('\n'))

        new_dataset_train = os.path.join(root_path, 'dataset/voc/data/train/images').replace('\\', '/')
        new_dataset_test = os.path.join(root_path, 'dataset/voc/data/test/images').replace('\\', '/')
        new_dataset_valid = os.path.join(root_path, 'dataset/voc/data/valid/images').replace('\\', '/')

        new_dataset_trainl = os.path.join(root_path, 'dataset/voc/data/train/labels').replace('\\', '/')
        new_dataset_testl = os.path.join(root_path, 'dataset/voc/data/test/labels').replace('\\', '/')
        new_dataset_validl = os.path.join(root_path, 'dataset/voc/data/valid/labels').replace('\\', '/')

        if not os.path.exists(new_dataset_train):
            os.makedirs(new_dataset_train)
        if not os.path.exists(new_dataset_test):
            os.makedirs(new_dataset_test)
        if not os.path.exists(new_dataset_valid):
            os.makedirs(new_dataset_valid)
        if not os.path.exists(new_dataset_trainl):
            os.makedirs(new_dataset_trainl)
        if not os.path.exists(new_dataset_testl):
            os.makedirs(new_dataset_testl)
        if not os.path.exists(new_dataset_validl):
            os.makedirs(new_dataset_validl)

        fimg = os.path.join(root_path, 'dataset/voc/JPEGImages').replace('\\', '/')
        flabel = os.path.join(root_path, 'dataset/voc/worktxt').replace('\\', '/')

        for i in img_txt_cg_train:
            shutil.copy(os.path.join(fimg, i), new_dataset_train)
        for i in label_txt_cg_train:
            shutil.copy(os.path.join(flabel, i), new_dataset_trainl)
        for i in img_txt_cg_test:
            shutil.copy(os.path.join(fimg, i), new_dataset_test)
        for i in label_txt_cg_test:
            shutil.copy(os.path.join(flabel, i), new_dataset_testl)
        for i in img_txt_cg_valid:
            shutil.copy(os.path.join(fimg, i), new_dataset_valid)
        for i in label_txt_cg_valid:
            shutil.copy(os.path.join(flabel, i), new_dataset_validl)

        QMessageBox.information(self, 'Success', 'Dataset organized successfully.')

        # Reopen and rewrite the img_train.txt, img_valid.txt, and img_test.txt files
        with open(os.path.join(ImageSetspath, 'img_train.txt'), 'w', encoding='utf-8') as train_img_txt:
            for img_name in img_txt_cg_train:
                train_img_txt.write(os.path.join(root_path, 'dataset/voc/data/train/images/', img_name) + '\n')

        with open(os.path.join(ImageSetspath, 'img_valid.txt'), 'w', encoding='utf-8') as valid_img_txt:
            for img_name in img_txt_cg_valid:
                valid_img_txt.write(os.path.join(root_path, 'dataset/voc/data/valid/images/', img_name) + '\n')

        with open(os.path.join(ImageSetspath, 'img_test.txt'), 'w', encoding='utf-8') as test_img_txt:
            for img_name in img_txt_cg_test:
                test_img_txt.write(os.path.join(root_path, 'dataset/voc/data/test/images/', img_name) + '\n')
        self.generate_yaml(root_path, ImageSetspath)

    def generate_yaml(self, root_path, ImageSetspath):
        data = {
            'path': os.path.join(root_path, 'dataset').replace('\\', '/'),
            'train': os.path.join(ImageSetspath, 'img_train.txt').replace('\\', '/'),
            'val': os.path.join(ImageSetspath, 'img_valid.txt').replace('\\', '/'),
            'test': os.path.join(ImageSetspath, 'img_test.txt').replace('\\', '/'),
            'names': {i: f'M{i+1}' for i in range(80)}
        }

        options = QFileDialog.Options()
        yaml_path, _ = QFileDialog.getSaveFileName(self, 'Save YAML File', '', 'YAML Files (*.yaml)', options=options)
        if yaml_path:
            with open(yaml_path, 'w', encoding='utf-8') as yaml_file:
                yaml.dump(data, yaml_file, allow_unicode=True)

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
        output_layout = QVBoxLayout()  # 使用垂直布局，以便将备注放在按钮下方

        # 创建水平布局用于 QLineEdit 和 Browse 按钮
        hbox_layout = QHBoxLayout()
        self.outputpath_input = QLineEdit(self)
        self.outputpath_button = QPushButton('Browse', self)
        self.outputpath_button.clicked.connect(self.browse_outputpath)

        # 添加 QLineEdit 和 Browse 按钮到水平布局
        hbox_layout.addWidget(self.outputpath_input)
        hbox_layout.addWidget(self.outputpath_button)

        # 创建备注标签
        self.outputpath_remark = QLabel("要求json文件在outputpath中<br>例如<br>jsonpath：D:\code\dbba\interfacetest\dbba.json<br>output path：D:\code\dbba\interfacetest", self)

        # 添加水平布局和备注到垂直布局
        output_layout.addLayout(hbox_layout)  # 先添加输入框和按钮
        output_layout.addWidget(self.outputpath_remark)  # 然后添加备注

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

            # Automatically enter class info by calling the ExpertApp method
            json_file = self.filename_input.text()
            if json_file and os.path.exists(json_file):
                self.expert_app.json_folder_path = os.path.dirname(json_file)  # Set the json_folder_path in ExpertApp
                self.expert_app.enter_class_info()  # Call the method to ensure labels are consistent with the index
                
                if not self.expert_app.class_info:
                    QMessageBox.warning(self, 'Error', 'No class information was found or matched.')
                    return

            # Select all augmentation checkboxes
            self.expert_app.dropout_checkbox.setChecked(True)
            self.expert_app.elastic_transform_checkbox.setChecked(True)
            self.expert_app.gaussian_blur_checkbox.setChecked(True)
            self.expert_app.multiply_brightness_checkbox.setChecked(True)
            self.expert_app.multiply_hue_saturation_checkbox.setChecked(True)
            self.expert_app.add_hue_checkbox.setChecked(True)
            self.expert_app.add_saturation_checkbox.setChecked(True)
            self.expert_app.horizontal_jitter_checkbox.setChecked(True)
            
            # Start the augmentation, conversion, and splitting process
            self.expert_app.start_augmentation()
            self.expert_app.start_conversion()
            self.expert_app.split_dataset()
            
            QMessageBox.information(self, 'Success', 'Dataset created successfully.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CombinedApp()
    window.show()
    sys.exit(app.exec_())
