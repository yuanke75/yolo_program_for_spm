# # import sys
# # import os
# # import json
# # from PyQt5.QtWidgets import (QApplication, QGroupBox, QWidget, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QProgressBar, QRadioButton, QHBoxLayout, QMessageBox, QButtonGroup, QSpinBox, QDialog, QFormLayout, QDialogButtonBox)
# # from PyQt5.QtCore import Qt
# # import imageio.v2 as imageio
# # import imgaug as ia
# # from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
# # from imgaug import augmenters as iaa
# # from PIL import Image
# # import io
# # import base64
# # import copy
# # import numpy as np
# # from PyQt5.QtGui import QFont

# # # Define a recursive function to handle and convert all float32 values
# # def convert_float32(obj):
# #     if isinstance(obj, list):
# #         return [convert_float32(item) for item in obj]
# #     elif isinstance(obj, dict):
# #         return {k: convert_float32(v) for k, v in obj.items()}
# #     elif isinstance(obj, np.float32):
# #         return float(obj)
# #     return obj

# # def bbox_to_xywh(x1, y1, x2, y2, img_w, img_h):
# #     w = x2 - x1
# #     h = y2 - y1
# #     x = x1 + w / 2
# #     y = y1 + h / 2
# #     return x / img_w, y / img_h, w / img_w, h / img_h

# # class ClassDialog(QDialog):
# #     def __init__(self, class_labels, parent=None):
# #         super(ClassDialog, self).__init__(parent)
# #         self.class_labels = class_labels
# #         self.class_info = []
# #         self.setWindowTitle('Class Information Input')

# #         layout = QVBoxLayout()
# #         self.form_layout = QFormLayout()
# #         self.class_id_inputs = []

# #         for i, label in enumerate(class_labels):
# #             class_id_input = QLineEdit(self)
# #             self.form_layout.addRow(f'Class "{label}" ID:', class_id_input)
# #             self.class_id_inputs.append(class_id_input)

# #         layout.addLayout(self.form_layout)

# #         self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
# #         self.button_box.accepted.connect(self.accept)
# #         self.button_box.rejected.connect(self.reject)

# #         layout.addWidget(self.button_box)
# #         self.setLayout(layout)

# #     def accept(self):
# #         for class_id_input, label in zip(self.class_id_inputs, self.class_labels):
# #             class_id = class_id_input.text().strip()
# #             if class_id:
# #                 self.class_info.append((label, int(class_id)))
# #         super(ClassDialog, self).accept()

# # class CombinedApp(QWidget):
# #     def __init__(self):
# #         super().__init__()
# #         self.initUI()

# #     def initUI(self):
# #         self.setWindowTitle('Image Augmentation and JSON to TXT Conversion Tool')
# #         main_layout = QVBoxLayout()

# #         # Augmentation section
# #         aug_layout = QHBoxLayout()
# #         aug_left_layout = QVBoxLayout()
# #         aug_right_layout = QVBoxLayout()

# #         # JSON File Group
# #         json_group = QGroupBox("JSON File")
# #         json_layout = QHBoxLayout()
# #         self.filename_input = QLineEdit(self)
# #         self.filename_button = QPushButton('Browse', self)
# #         self.filename_button.clicked.connect(self.browse_filename)
# #         json_layout.addWidget(self.filename_input)
# #         json_layout.addWidget(self.filename_button)
# #         json_group.setLayout(json_layout)

# #         # Image File Group
# #         image_group = QGroupBox("Image File")
# #         image_layout = QHBoxLayout()
# #         self.imagepath_input = QLineEdit(self)
# #         self.imagepath_button = QPushButton('Browse', self)
# #         self.imagepath_button.clicked.connect(self.browse_imagepath)
# #         image_layout.addWidget(self.imagepath_input)
# #         image_layout.addWidget(self.imagepath_button)
# #         image_group.setLayout(image_layout)

# #         # Output Path Group
# #         output_group = QGroupBox("Output Path")
# #         output_layout = QHBoxLayout()
# #         self.outputpath_input = QLineEdit(self)
# #         self.outputpath_button = QPushButton('Browse', self)
# #         self.outputpath_button.clicked.connect(self.browse_outputpath)
# #         output_layout.addWidget(self.outputpath_input)
# #         output_layout.addWidget(self.outputpath_button)
# #         output_group.setLayout(output_layout)

# #         # Number of Augmentations Group
# #         aug_times_group = QGroupBox("Number of Augmentations")
# #         aug_times_layout = QHBoxLayout()
# #         self.aug_times_input = QSpinBox(self)
# #         self.aug_times_input.setMinimum(1)
# #         aug_times_layout.addWidget(self.aug_times_input)
# #         aug_times_group.setLayout(aug_times_layout)

# #         # Add groups to left layout
# #         aug_left_layout.addWidget(json_group)
# #         aug_left_layout.addWidget(image_group)
# #         aug_left_layout.addWidget(output_group)
# #         aug_left_layout.addWidget(aug_times_group)

# #         # Radio Buttons for Augmentation Levels
# #         self.rotation_only_radio = QRadioButton("Rotation Only")
# #         self.rotation_dropout_radio = QRadioButton("Rotation + Dropout")
# #         self.full_augmentation_radio = QRadioButton("Full Augmentation")

# #         self.radio_group = QButtonGroup()
# #         self.radio_group.addButton(self.rotation_only_radio)
# #         self.radio_group.addButton(self.rotation_dropout_radio)
# #         self.radio_group.addButton(self.full_augmentation_radio)
        
# #         self.rotation_only_radio.setChecked(True)

# #         aug_right_layout.addWidget(self.rotation_only_radio)
# #         aug_right_layout.addWidget(self.rotation_dropout_radio)
# #         aug_right_layout.addWidget(self.full_augmentation_radio)

# #         # Progress Bar and Start Button
# #         self.start_button = QPushButton('Start Augmentation', self)
# #         self.start_button.clicked.connect(self.start_augmentation)
# #         self.progress_bar = QProgressBar(self)
# #         self.progress_bar.setAlignment(Qt.AlignCenter)
# #         self.progress_bar.setMinimum(0)
# #         self.progress_bar.setMaximum(100)

# #         aug_right_layout.addWidget(self.start_button)
# #         aug_right_layout.addWidget(self.progress_bar)

# #         # Add left and right layouts to main layout
# #         aug_layout.addLayout(aug_left_layout)
# #         aug_layout.addLayout(aug_right_layout)

# #         main_layout.addLayout(aug_layout)

# #         # Conversion section
# #         conversion_group = QGroupBox("Conversion Section")
# #         conversion_layout = QVBoxLayout()

# #         # JSON Folder Group
# #         json_folder_group = QGroupBox("JSON Folder Path")
# #         json_folder_layout = QHBoxLayout()
# #         self.json_folder_input = QLineEdit(self)
# #         self.json_folder_button = QPushButton('Browse', self)
# #         self.json_folder_button.clicked.connect(self.browse_json_folder)
# #         json_folder_layout.addWidget(self.json_folder_input)
# #         json_folder_layout.addWidget(self.json_folder_button)
# #         json_folder_group.setLayout(json_folder_layout)
        
# #         # Output Folder Group
# #         output_folder_group = QGroupBox("Output Folder Path")
# #         output_folder_layout = QHBoxLayout()
# #         self.output_folder_input = QLineEdit(self)
# #         self.output_folder_button = QPushButton('Browse', self)
# #         self.output_folder_button.clicked.connect(self.browse_output_folder)
# #         output_folder_layout.addWidget(self.output_folder_input)
# #         output_folder_layout.addWidget(self.output_folder_button)
# #         output_folder_group.setLayout(output_folder_layout)
        
# #         # Progress Bar and Start Button
# #         self.class_info_button = QPushButton('Enter Class Information', self)
# #         self.class_info_button.clicked.connect(self.enter_class_info)
# #         self.convert_button = QPushButton('Start Conversion', self)
# #         self.convert_button.clicked.connect(self.start_conversion)
# #         self.convert_progress_bar = QProgressBar(self)
# #         self.convert_progress_bar.setAlignment(Qt.AlignCenter)
# #         self.convert_progress_bar.setMinimum(0)
# #         self.convert_progress_bar.setMaximum(100)

# #         # Adding Widgets to Conversion Layout
# #         conversion_layout.addWidget(json_folder_group)
# #         conversion_layout.addWidget(output_folder_group)
# #         conversion_layout.addWidget(self.class_info_button)
# #         conversion_layout.addWidget(self.convert_button)
# #         conversion_layout.addWidget(self.convert_progress_bar)

# #         conversion_group.setLayout(conversion_layout)

# #         main_layout.addWidget(conversion_group)

# #         self.setLayout(main_layout)
# #         self.class_info = []
# #         self.json_folder_path = ""

# #         # Apply Styles
# #         self.setStyleSheet("""
# #             QWidget {
# #                 font-size: 14px;
# #             }
# #             QGroupBox {
# #                 font-weight: bold;
# #                 border: 1px solid gray;
# #                 margin-top: 10px;
# #             }
# #             QGroupBox::title {
# #                 subcontrol-origin: margin;
# #                 subcontrol-position: top left;
# #                 padding: 0 3px;
# #             }
# #             QPushButton {
# #                 background-color: #4CAF50;
# #                 color: white;
# #                 border-radius: 5px;
# #                 padding: 5px;
# #             }
# #             QPushButton:hover {
# #                 background-color: #45a049;
# #             }
# #             QProgressBar {
# #                 height: 20px;
# #                 text-align: center;
# #             }
# #         """)

# #     def browse_filename(self):
# #         options = QFileDialog.Options()
# #         filename, _ = QFileDialog.getOpenFileName(self, 'Select JSON File', '', 'JSON Files (*.json)', options=options)
# #         if filename:
# #             self.filename_input.setText(filename)

# #     def browse_imagepath(self):
# #         options = QFileDialog.Options()
# #         imagepath, _ = QFileDialog.getOpenFileName(self, 'Select Image File', '', 'Image Files (*.jpg;*.jpeg;*.png)', options=options)
# #         if imagepath:
# #             self.imagepath_input.setText(imagepath)

# #     def browse_outputpath(self):
# #         options = QFileDialog.Options()
# #         outputpath = QFileDialog.getExistingDirectory(self, 'Select Output Directory', options=options)
# #         if outputpath:
# #             self.outputpath_input.setText(outputpath)

# #     def start_augmentation(self):
# #         filename = self.filename_input.text()
# #         image_path = self.imagepath_input.text()
# #         output_path = self.outputpath_input.text()
# #         aug_times = self.aug_times_input.value()

# #         if not filename or not image_path or not output_path:
# #             QMessageBox.warning(self, 'Input Error', 'Please provide all the required inputs.')
# #             return

# #         if not os.path.exists(output_path):
# #             os.makedirs(output_path)

# #         image = imageio.imread(image_path)
# #         rotation_list = list(range(15, 360, 15))

# #         with open(filename) as f:
# #             original_squad_box = json.load(f)

# #         ia.seed(42)

# #         sometimes = lambda aug: iaa.Sometimes(1, aug)
# #         seq = None

# #         if self.rotation_dropout_radio.isChecked():
# #             seq = iaa.Sequential(
# #                 [
# #                     iaa.OneOf([
# #                         sometimes(iaa.Dropout((0.01, 0.1), per_channel=0.5)),
# #                         sometimes(iaa.CoarseDropout(
# #                             (0.03, 0.15), size_percent=(0.02, 0.05),
# #                             per_channel=0.2
# #                         )),
# #                         sometimes(iaa.ElasticTransformation(alpha=(0.5, 3.5), sigma=0.25)),
# #                     ]),
# #                 ],
# #                 random_order=True
# #             )
# #         elif self.full_augmentation_radio.isChecked():
# #             seq = iaa.Sequential(
# #                 [
# #                     iaa.OneOf([
# #                         sometimes(iaa.Dropout((0.01, 0.1), per_channel=0.5)),
# #                         sometimes(iaa.CoarseDropout(
# #                             (0.03, 0.15), size_percent=(0.02, 0.05),
# #                             per_channel=0.2
# #                         )),
# #                         sometimes(iaa.ElasticTransformation(alpha=(0.5, 3.5), sigma=0.25)),
# #                         sometimes(iaa.GaussianBlur(sigma=(0.0, 3.0))),
# #                         sometimes(iaa.MultiplyBrightness(mul=(0.7, 1.3))),
# #                         sometimes(iaa.MultiplyHueAndSaturation(mul_hue=(0.8, 1.2), mul_saturation=(0.8, 1.2))),
# #                         sometimes(iaa.AddToHue(value=(-10, 10))),
# #                         sometimes(iaa.AddToSaturation(value=(-10, 10)))
# #                     ]),
# #                 ],
# #                 random_order=True
# #             )

# #         total_operations = len(rotation_list) * (aug_times if seq else 1)
# #         progress = 0

# #         self.progress_bar.setValue(0)

# #         for theta in rotation_list:
# #             squad_box = copy.deepcopy(original_squad_box)

# #             file_prefix = os.path.splitext(os.path.basename(filename))[0]
# #             new_json_name = f"{file_prefix}{theta}.json"
# #             new_image_name = f"{file_prefix}{theta}.jpg"
# #             new_image_path = os.path.join(output_path, new_image_name)

# #             bbs_list = []
# #             for shape in squad_box['shapes']:
# #                 bbox = shape['points']
# #                 x1, y1 = bbox[0]
# #                 x2, y2 = bbox[1]
# #                 bbs_list.append(BoundingBox(x1=x1, x2=x2, y1=y1, y2=y2))

# #             bbs = BoundingBoxesOnImage(bbs_list, shape=image.shape)
# #             rot = iaa.Affine(rotate=theta, fit_output=True)
# #             image_aug, bbs_aug = rot(image=image, bounding_boxes=bbs)

# #             if seq:
# #                 for i in range(aug_times):
# #                     aug_image_name = f"{file_prefix}{theta}_aug_{i}.jpg"
# #                     aug_image_path = os.path.join(output_path, aug_image_name)
# #                     image_aug_temp, bbs_aug_temp = seq(image=image_aug, bounding_boxes=bbs_aug)
# #                     self.save_augmented_image(image_aug_temp, bbs_aug_temp, squad_box, aug_image_name, aug_image_path, output_path)
# #                     progress += 1
# #                     self.progress_bar.setValue(int((progress / total_operations) * 100))
# #             else:
# #                 self.save_augmented_image(image_aug, bbs_aug, squad_box, new_image_name, new_image_path, output_path)
# #                 progress += 1
# #                 self.progress_bar.setValue(int((progress / total_operations) * 100))

# #         QMessageBox.information(self, 'Success', 'Augmentation completed successfully.')

# #     def save_augmented_image(self, image_aug, bbs_aug, squad_box, image_name, image_path, output_path):
# #         imageio.imwrite(image_path, image_aug)

# #         pil_img = Image.fromarray(image_aug)
# #         buff = io.BytesIO()
# #         pil_img.save(buff, format="JPEG")
# #         base64_string = base64.b64encode(buff.getvalue()).decode("utf-8")

# #         for i, bb_aug in enumerate(bbs_aug.bounding_boxes):
# #             x1_new, y1_new = bb_aug.x1, bb_aug.y1
# #             x2_new, y2_new = bb_aug.x2, bb_aug.y2
# #             squad_box['shapes'][i]['points'] = [[x1_new, y1_new], [x2_new, y2_new]]

# #         squad_box['imagePath'] = image_name
# #         squad_box['imageData'] = base64_string
# #         squad_box['imageHeight'], squad_box['imageWidth'] = image_aug.shape[0:2]
# #         squad_box = convert_float32(squad_box)

# #         json_name = os.path.splitext(image_name)[0] + '.json'
# #         with open(os.path.join(output_path, json_name), 'w') as f:
# #             json.dump(squad_box, f, indent=4)

# #     def browse_json_folder(self):
# #         options = QFileDialog.Options()
# #         folder_path = QFileDialog.getExistingDirectory(self, 'Select JSON Folder', options=options)
# #         if folder_path:
# #             self.json_folder_input.setText(folder_path)
# #             self.json_folder_path = folder_path

# #     def browse_output_folder(self):
# #         options = QFileDialog.Options()
# #         folder_path = QFileDialog.getExistingDirectory(self, 'Select Output Folder', options=options)
# #         if folder_path:
# #             self.output_folder_input.setText(folder_path)

# #     def enter_class_info(self):
# #         if not self.json_folder_path:
# #             QMessageBox.warning(self, 'Input Error', 'Please select a JSON folder path first.')
# #             return
        
# #         class_labels = set()
# #         for filename in os.listdir(self.json_folder_path):
# #             if filename.endswith('.json'):
# #                 json_path = os.path.join(self.json_folder_path, filename)
# #                 with open(json_path) as f:
# #                     data = json.load(f)
# #                     for shape in data['shapes']:
# #                         class_labels.add(shape['label'])
        
# #         if class_labels:
# #             dialog = ClassDialog(class_labels)
# #             if dialog.exec_():
# #                 self.class_info = dialog.class_info

# #     def start_conversion(self):
# #         json_folder_path = self.json_folder_input.text()
# #         output_folder_path = self.output_folder_input.text()

# #         if not json_folder_path or not output_folder_path or not self.class_info:
# #             QMessageBox.warning(self, 'Input Error', 'Please provide all the required inputs and class information.')
# #             return

# #         if not os.path.exists(output_folder_path):
# #             os.makedirs(output_folder_path)

# #         json_files = [f for f in os.listdir(json_folder_path) if f.endswith('.json')]
# #         total_files = len(json_files)
# #         self.convert_progress_bar.setValue(0)

# #         for idx, filename in enumerate(json_files):
# #             json_path = os.path.join(json_folder_path, filename)
# #             output_txt_name = filename.replace('.json', '.txt')
# #             output_txt_path = os.path.join(output_folder_path, output_txt_name)
            
# #             with open(json_path) as f:
# #                 data = json.load(f)
            
# #             image_width = data['imageWidth']
# #             image_height = data['imageHeight']

# #             with open(output_txt_path, 'w') as txt_file:
# #                 for shape in data['shapes']:
# #                     bbox = shape['points']
# #                     x1, y1 = bbox[0]
# #                     x2, y2 = bbox[1]
# #                     x, y, w, h = self.bbox_to_xywh(x1, y1, x2, y2, image_width, image_height)

# #                     label = shape['label']
# #                     class_id = next((class_id for lbl, class_id in self.class_info if lbl == label), None)
# #                     if class_id is not None:
# #                         txt_file.write(f"{class_id} {x} {y} {w} {h}\n")

# #             self.convert_progress_bar.setValue(int((idx + 1) / total_files * 100))

# #         QMessageBox.information(self, 'Success', 'All JSON files have been successfully converted to TXT files.')

# #     def bbox_to_xywh(self, x1, y1, x2, y2, img_w, img_h):
# #         w = x2 - x1
# #         h = y2 - y1
# #         x = x1 + w / 2
# #         y = y1 + h / 2
# #         return x / img_w, y / img_h, w / img_w, h / img_h


# # if __name__ == '__main__':
# #     app = QApplication(sys.argv)
# #     ex = CombinedApp()
# #     ex.show()
# #     sys.exit(app.exec_())


# import sys
# import os
# import json
# import shutil
# import random
# from PyQt5.QtWidgets import (QApplication, QGroupBox, QWidget, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QProgressBar, QRadioButton, QHBoxLayout, QMessageBox, QButtonGroup, QSpinBox, QDialog, QFormLayout, QDialogButtonBox, QLabel)
# from PyQt5.QtCore import Qt
# import imageio.v2 as imageio
# import imgaug as ia
# from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
# from imgaug import augmenters as iaa
# from PIL import Image
# import io
# import base64
# import copy
# import numpy as np
# from PyQt5.QtGui import QFont

# # Define a recursive function to handle and convert all float32 values
# def convert_float32(obj):
#     if isinstance(obj, list):
#         return [convert_float32(item) for item in obj]
#     elif isinstance(obj, dict):
#         return {k: convert_float32(v) for k, v in obj.items()}
#     elif isinstance(obj, np.float32):
#         return float(obj)
#     return obj

# def bbox_to_xywh(x1, y1, x2, y2, img_w, img_h):
#     w = x2 - x1
#     h = y2 - y1
#     x = x1 + w / 2
#     y = y1 + h / 2
#     return x / img_w, y / img_h, w / img_w, h / img_h

# class ClassDialog(QDialog):
#     def __init__(self, class_labels, parent=None):
#         super(ClassDialog, self).__init__(parent)
#         self.class_labels = class_labels
#         self.class_info = []
#         self.setWindowTitle('Class Information Input')

#         layout = QVBoxLayout()
#         self.form_layout = QFormLayout()
#         self.class_id_inputs = []

#         for i, label in enumerate(class_labels):
#             class_id_input = QLineEdit(self)
#             self.form_layout.addRow(f'Class "{label}" ID:', class_id_input)
#             self.class_id_inputs.append(class_id_input)

#         layout.addLayout(self.form_layout)

#         self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
#         self.button_box.accepted.connect(self.accept)
#         self.button_box.rejected.connect(self.reject)

#         layout.addWidget(self.button_box)
#         self.setLayout(layout)

#     def accept(self):
#         for class_id_input, label in zip(self.class_id_inputs, self.class_labels):
#             class_id = class_id_input.text().strip()
#             if class_id:
#                 self.class_info.append((label, int(class_id)))
#         super(ClassDialog, self).accept()

# class CombinedApp(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()

#     def initUI(self):
#         self.setWindowTitle('Image Augmentation, JSON to TXT Conversion, and Dataset Splitter')
#         main_layout = QVBoxLayout()

#         # Augmentation section
#         aug_layout = QHBoxLayout()
#         aug_left_layout = QVBoxLayout()
#         aug_right_layout = QVBoxLayout()

#         # JSON File Group
#         json_group = QGroupBox("JSON File")
#         json_layout = QHBoxLayout()
#         self.filename_input = QLineEdit(self)
#         self.filename_button = QPushButton('Browse', self)
#         self.filename_button.clicked.connect(self.browse_filename)
#         json_layout.addWidget(self.filename_input)
#         json_layout.addWidget(self.filename_button)
#         json_group.setLayout(json_layout)

#         # Image File Group
#         image_group = QGroupBox("Image File")
#         image_layout = QHBoxLayout()
#         self.imagepath_input = QLineEdit(self)
#         self.imagepath_button = QPushButton('Browse', self)
#         self.imagepath_button.clicked.connect(self.browse_imagepath)
#         image_layout.addWidget(self.imagepath_input)
#         image_layout.addWidget(self.imagepath_button)
#         image_group.setLayout(image_layout)

#         # Output Path Group
#         output_group = QGroupBox("Output Path")
#         output_layout = QHBoxLayout()
#         self.outputpath_input = QLineEdit(self)
#         self.outputpath_button = QPushButton('Browse', self)
#         self.outputpath_button.clicked.connect(self.browse_outputpath)
#         output_layout.addWidget(self.outputpath_input)
#         output_layout.addWidget(self.outputpath_button)
#         output_group.setLayout(output_layout)

#         # Number of Augmentations Group
#         aug_times_group = QGroupBox("Number of Augmentations")
#         aug_times_layout = QHBoxLayout()
#         self.aug_times_input = QSpinBox(self)
#         self.aug_times_input.setMinimum(1)
#         aug_times_layout.addWidget(self.aug_times_input)
#         aug_times_group.setLayout(aug_times_layout)

#         # Add groups to left layout
#         aug_left_layout.addWidget(json_group)
#         aug_left_layout.addWidget(image_group)
#         aug_left_layout.addWidget(output_group)
#         aug_left_layout.addWidget(aug_times_group)

#         # Radio Buttons for Augmentation Levels
#         self.rotation_only_radio = QRadioButton("Rotation Only")
#         self.rotation_dropout_radio = QRadioButton("Rotation + Dropout")
#         self.full_augmentation_radio = QRadioButton("Full Augmentation")

#         self.radio_group = QButtonGroup()
#         self.radio_group.addButton(self.rotation_only_radio)
#         self.radio_group.addButton(self.rotation_dropout_radio)
#         self.radio_group.addButton(self.full_augmentation_radio)
        
#         self.rotation_only_radio.setChecked(True)

#         aug_right_layout.addWidget(self.rotation_only_radio)
#         aug_right_layout.addWidget(self.rotation_dropout_radio)
#         aug_right_layout.addWidget(self.full_augmentation_radio)

#         # Progress Bar and Start Button
#         self.start_button = QPushButton('Start Augmentation', self)
#         self.start_button.clicked.connect(self.start_augmentation)
#         self.progress_bar = QProgressBar(self)
#         self.progress_bar.setAlignment(Qt.AlignCenter)
#         self.progress_bar.setMinimum(0)
#         self.progress_bar.setMaximum(100)

#         aug_right_layout.addWidget(self.start_button)
#         aug_right_layout.addWidget(self.progress_bar)

#         # Add left and right layouts to main layout
#         aug_layout.addLayout(aug_left_layout)
#         aug_layout.addLayout(aug_right_layout)

#         main_layout.addLayout(aug_layout)

#         # Conversion section
#         conversion_group = QGroupBox("Conversion Section")
#         conversion_layout = QVBoxLayout()

#         # JSON Folder Group
#         json_folder_group = QGroupBox("JSON Folder Path")
#         json_folder_layout = QHBoxLayout()
#         self.json_folder_input = QLineEdit(self)
#         self.json_folder_button = QPushButton('Browse', self)
#         self.json_folder_button.clicked.connect(self.browse_json_folder)
#         json_folder_layout.addWidget(self.json_folder_input)
#         json_folder_layout.addWidget(self.json_folder_button)
#         json_folder_group.setLayout(json_folder_layout)
        
#         # Output Folder Group
#         output_folder_group = QGroupBox("Output Folder Path")
#         output_folder_layout = QHBoxLayout()
#         self.output_folder_input = QLineEdit(self)
#         self.output_folder_button = QPushButton('Browse', self)
#         self.output_folder_button.clicked.connect(self.browse_output_folder)
#         output_folder_layout.addWidget(self.output_folder_input)
#         output_folder_layout.addWidget(self.output_folder_button)
#         output_folder_group.setLayout(output_folder_layout)
        
#         # Progress Bar and Start Button
#         self.class_info_button = QPushButton('Enter Class Information', self)
#         self.class_info_button.clicked.connect(self.enter_class_info)
#         self.convert_button = QPushButton('Start Conversion', self)
#         self.convert_button.clicked.connect(self.start_conversion)
#         self.convert_progress_bar = QProgressBar(self)
#         self.convert_progress_bar.setAlignment(Qt.AlignCenter)
#         self.convert_progress_bar.setMinimum(0)
#         self.convert_progress_bar.setMaximum(100)

#         # Adding Widgets to Conversion Layout
#         conversion_layout.addWidget(json_folder_group)
#         conversion_layout.addWidget(output_folder_group)
#         conversion_layout.addWidget(self.class_info_button)
#         conversion_layout.addWidget(self.convert_button)
#         conversion_layout.addWidget(self.convert_progress_bar)

#         conversion_group.setLayout(conversion_layout)

#         main_layout.addWidget(conversion_group)

#         # Splitter section
#         splitter_group = QGroupBox("Dataset Splitter")
#         splitter_layout = QVBoxLayout()

#         # Root Path Group
#         root_path_group = QGroupBox("Root Path")
#         root_path_layout = QHBoxLayout()
#         self.root_path_input = QLineEdit()
#         self.root_path_button = QPushButton('Browse')
#         self.root_path_button.clicked.connect(self.browse_root_path)
#         root_path_layout.addWidget(self.root_path_input)
#         root_path_layout.addWidget(self.root_path_button)
#         root_path_group.setLayout(root_path_layout)
        
#         # Train/Test/Validation Percentages Group
#         percent_group = QGroupBox("Train/Test/Validation Percentages")
#         percent_layout = QVBoxLayout()
        
#         self.train_test_percent_label = QLabel('Train/Test Percent (0-100):')
#         self.train_test_percent_input = QSpinBox()
#         self.train_test_percent_input.setRange(0, 100)
#         self.train_test_percent_input.setValue(90)

#         self.train_valid_percent_label = QLabel('Train/Valid Percent (0-100):')
#         self.train_valid_percent_input = QSpinBox()
#         self.train_valid_percent_input.setRange(0, 100)
#         self.train_valid_percent_input.setValue(90)

#         percent_layout.addWidget(self.train_test_percent_label)
#         percent_layout.addWidget(self.train_test_percent_input)
#         percent_layout.addWidget(self.train_valid_percent_label)
#         percent_layout.addWidget(self.train_valid_percent_input)
#         percent_group.setLayout(percent_layout)

#         # Split Button
#         self.split_button = QPushButton('Split and Organize Dataset')
#         self.split_button.clicked.connect(self.split_dataset)

#         # Adding Widgets to Splitter Layout
#         splitter_layout.addWidget(root_path_group)
#         splitter_layout.addWidget(percent_group)
#         splitter_layout.addWidget(self.split_button)

#         splitter_group.setLayout(splitter_layout)
#         main_layout.addWidget(splitter_group)

#         self.setLayout(main_layout)
#         self.class_info = []
#         self.json_folder_path = ""

#         # Apply Styles
#         self.setStyleSheet("""
#             QWidget {
#                 font-size: 14px;
#             }
#             QGroupBox {
#                 font-weight: bold;
#                 border: 1px solid gray;
#                 margin-top: 10px;
#             }
#             QGroupBox::title {
#                 subcontrol-origin: margin;
#                 subcontrol-position: top left;
#                 padding: 0 3px;
#             }
#             QPushButton {
#                 background-color: #4CAF50;
#                 color: white;
#                 border-radius: 5px;
#                 padding: 5px;
#             }
#             QPushButton:hover {
#                 background-color: #45a049;
#             }
#             QProgressBar {
#                 height: 20px;
#                 text-align: center;
#             }
#         """)

#     def browse_filename(self):
#         options = QFileDialog.Options()
#         filename, _ = QFileDialog.getOpenFileName(self, 'Select JSON File', '', 'JSON Files (*.json)', options=options)
#         if filename:
#             self.filename_input.setText(filename)

#     def browse_imagepath(self):
#         options = QFileDialog.Options()
#         imagepath, _ = QFileDialog.getOpenFileName(self, 'Select Image File', '', 'Image Files (*.jpg;*.jpeg;*.png)', options=options)
#         if imagepath:
#             self.imagepath_input.setText(imagepath)

#     def browse_outputpath(self):
#         options = QFileDialog.Options()
#         outputpath = QFileDialog.getExistingDirectory(self, 'Select Output Directory', options=options)
#         if outputpath:
#             self.outputpath_input.setText(outputpath)

#     def start_augmentation(self):
#         filename = self.filename_input.text()
#         image_path = self.imagepath_input.text()
#         output_path = self.outputpath_input.text()
#         aug_times = self.aug_times_input.value()

#         if not filename or not image_path or not output_path:
#             QMessageBox.warning(self, 'Input Error', 'Please provide all the required inputs.')
#             return

#         if not os.path.exists(output_path):
#             os.makedirs(output_path)

#         image = imageio.imread(image_path)
#         rotation_list = list(range(15, 360, 15))

#         with open(filename) as f:
#             original_squad_box = json.load(f)

#         ia.seed(42)

#         sometimes = lambda aug: iaa.Sometimes(1, aug)
#         seq = None

#         if self.rotation_dropout_radio.isChecked():
#             seq = iaa.Sequential(
#                 [
#                     iaa.OneOf([
#                         sometimes(iaa.Dropout((0.01, 0.1), per_channel=0.5)),
#                         sometimes(iaa.CoarseDropout(
#                             (0.03, 0.15), size_percent=(0.02, 0.05),
#                             per_channel=0.2
#                         )),
#                         sometimes(iaa.ElasticTransformation(alpha=(0.5, 3.5), sigma=0.25)),
#                     ]),
#                 ],
#                 random_order=True
#             )
#         elif self.full_augmentation_radio.isChecked():
#             seq = iaa.Sequential(
#                 [
#                     iaa.OneOf([
#                         sometimes(iaa.Dropout((0.01, 0.1), per_channel=0.5)),
#                         sometimes(iaa.CoarseDropout(
#                             (0.03, 0.15), size_percent=(0.02, 0.05),
#                             per_channel=0.2
#                         )),
#                         sometimes(iaa.ElasticTransformation(alpha=(0.5, 3.5), sigma=0.25)),
#                         sometimes(iaa.GaussianBlur(sigma=(0.0, 3.0))),
#                         sometimes(iaa.MultiplyBrightness(mul=(0.7, 1.3))),
#                         sometimes(iaa.MultiplyHueAndSaturation(mul_hue=(0.8, 1.2), mul_saturation=(0.8, 1.2))),
#                         sometimes(iaa.AddToHue(value=(-10, 10))),
#                         sometimes(iaa.AddToSaturation(value=(-10, 10)))
#                     ]),
#                 ],
#                 random_order=True
#             )

#         total_operations = len(rotation_list) * (aug_times if seq else 1)
#         progress = 0

#         self.progress_bar.setValue(0)

#         jpegimages_path = os.path.join(output_path, 'dataset/voc/JPEGImages')
#         worktxt_path = os.path.join(output_path, 'dataset/voc/worktxt')

#         if not os.path.exists(jpegimages_path):
#             os.makedirs(jpegimages_path)
#         if not os.path.exists(worktxt_path):
#             os.makedirs(worktxt_path)

#         for theta in rotation_list:
#             squad_box = copy.deepcopy(original_squad_box)

#             file_prefix = os.path.splitext(os.path.basename(filename))[0]
#             new_json_name = f"{file_prefix}{theta}.json"
#             new_image_name = f"{file_prefix}{theta}.jpg"
#             new_image_path = os.path.join(output_path, new_image_name)

#             bbs_list = []
#             for shape in squad_box['shapes']:
#                 bbox = shape['points']
#                 x1, y1 = bbox[0]
#                 x2, y2 = bbox[1]
#                 bbs_list.append(BoundingBox(x1=x1, x2=x2, y1=y1, y2=y2))

#             bbs = BoundingBoxesOnImage(bbs_list, shape=image.shape)
#             rot = iaa.Affine(rotate=theta, fit_output=True)
#             image_aug, bbs_aug = rot(image=image, bounding_boxes=bbs)

#             if seq:
#                 for i in range(aug_times):
#                     aug_image_name = f"{file_prefix}{theta}_aug_{i}.jpg"
#                     aug_image_path = os.path.join(output_path, aug_image_name)
#                     image_aug_temp, bbs_aug_temp = seq(image=image_aug, bounding_boxes=bbs_aug)
#                     self.save_augmented_image(image_aug_temp, bbs_aug_temp, squad_box, aug_image_name, aug_image_path, jpegimages_path, worktxt_path)
#                     progress += 1
#                     self.progress_bar.setValue(int((progress / total_operations) * 100))
#             else:
#                 self.save_augmented_image(image_aug, bbs_aug, squad_box, new_image_name, new_image_path, jpegimages_path, worktxt_path)
#                 progress += 1
#                 self.progress_bar.setValue(int((progress / total_operations) * 100))

#         QMessageBox.information(self, 'Success', 'Augmentation completed successfully.')

#     def save_augmented_image(self, image_aug, bbs_aug, squad_box, image_name, image_path, jpegimages_path, worktxt_path):
#         imageio.imwrite(image_path, image_aug)

#         shutil.copy(image_path, jpegimages_path)
#         pil_img = Image.fromarray(image_aug)
#         buff = io.BytesIO()
#         pil_img.save(buff, format="JPEG")
#         base64_string = base64.b64encode(buff.getvalue()).decode("utf-8")

#         for i, bb_aug in enumerate(bbs_aug.bounding_boxes):
#             x1_new, y1_new = bb_aug.x1, bb_aug.y1
#             x2_new, y2_new = bb_aug.x2, bb_aug.y2
#             squad_box['shapes'][i]['points'] = [[x1_new, y1_new], [x2_new, y2_new]]

#         squad_box['imagePath'] = image_name
#         squad_box['imageData'] = base64_string
#         squad_box['imageHeight'], squad_box['imageWidth'] = image_aug.shape[0:2]
#         squad_box = convert_float32(squad_box)

#         json_name = os.path.splitext(image_name)[0] + '.json'
#         json_path = os.path.join(worktxt_path, json_name)
#         with open(json_path, 'w') as f:
#             json.dump(squad_box, f, indent=4)

#     def browse_json_folder(self):
#         options = QFileDialog.Options()
#         folder_path = QFileDialog.getExistingDirectory(self, 'Select JSON Folder', options=options)
#         if folder_path:
#             self.json_folder_input.setText(folder_path)
#             self.json_folder_path = folder_path

#     def browse_output_folder(self):
#         options = QFileDialog.Options()
#         folder_path = QFileDialog.getExistingDirectory(self, 'Select Output Folder', options=options)
#         if folder_path:
#             self.output_folder_input.setText(folder_path)

#     def enter_class_info(self):
#         if not self.json_folder_path:
#             QMessageBox.warning(self, 'Input Error', 'Please select a JSON folder path first.')
#             return
        
#         class_labels = set()
#         for filename in os.listdir(self.json_folder_path):
#             if filename.endswith('.json'):
#                 json_path = os.path.join(self.json_folder_path, filename)
#                 with open(json_path) as f:
#                     data = json.load(f)
#                     for shape in data['shapes']:
#                         class_labels.add(shape['label'])
        
#         if class_labels:
#             dialog = ClassDialog(class_labels)
#             if dialog.exec_():
#                 self.class_info = dialog.class_info

#     def start_conversion(self):
#         json_folder_path = self.json_folder_input.text()
#         output_folder_path = self.json_folder_input.text()

#         if not json_folder_path or not output_folder_path or not self.class_info:
#             QMessageBox.warning(self, 'Input Error', 'Please provide all the required inputs and class information.')
#             return

#         if not os.path.exists(output_folder_path):
#             os.makedirs(output_folder_path)

#         json_files = [f for f in os.listdir(json_folder_path) if f.endswith('.json')]
#         total_files = len(json_files)
#         self.convert_progress_bar.setValue(0)

#         for idx, filename in enumerate(json_files):
#             json_path = os.path.join(json_folder_path, filename)
#             output_txt_name = filename.replace('.json', '.txt')
#             output_txt_path = os.path.join(output_folder_path, output_txt_name)
            
#             with open(json_path) as f:
#                 data = json.load(f)
            
#             image_width = data['imageWidth']
#             image_height = data['imageHeight']

#             with open(output_txt_path, 'w') as txt_file:
#                 for shape in data['shapes']:
#                     bbox = shape['points']
#                     x1, y1 = bbox[0]
#                     x2, y2 = bbox[1]
#                     x, y, w, h = self.bbox_to_xywh(x1, y1, x2, y2, image_width, image_height)

#                     label = shape['label']
#                     class_id = next((class_id for lbl, class_id in self.class_info if lbl == label), None)
#                     if class_id is not None:
#                         txt_file.write(f"{class_id} {x} {y} {w} {h}\n")

#             self.convert_progress_bar.setValue(int((idx + 1) / total_files * 100))

#         QMessageBox.information(self, 'Success', 'All JSON files have been successfully converted to TXT files.')

#     def bbox_to_xywh(self, x1, y1, x2, y2, img_w, img_h):
#         w = x2 - x1
#         h = y2 - y1
#         x = x1 + w / 2
#         y = y1 + h / 2
#         return x / img_w, y / img_h, w / img_w, h / img_h

#     def browse_root_path(self):
#         dir = QFileDialog.getExistingDirectory(self, 'Select Root Directory')
#         if dir:
#             self.root_path_input.setText(dir)

#     def split_dataset(self):
#         root_path = self.root_path_input.text()
#         train_test_percent = self.train_test_percent_input.value() / 100
#         train_valid_percent = self.train_valid_percent_input.value() / 100

#         jpegimages_path = os.path.join(root_path, 'dataset/voc/JPEGImages')
#         txtsavepath = os.path.join(root_path, 'dataset/voc/worktxt')
#         ImageSetspath = os.path.join(root_path,'dataset/voc/ImageSets')
#         if not os.path.exists(ImageSetspath):
#             os.makedirs(ImageSetspath)
#         if not os.path.exists(jpegimages_path) or not os.path.exists(txtsavepath):
#             QMessageBox.warning(self, 'Error', 'Required directories not found. Ensure augmentation and conversion are completed.')
#             return

#         total_images = [f for f in os.listdir(jpegimages_path) if f.endswith('.jpg')]
#         total_txts = [f for f in os.listdir(txtsavepath) if f.endswith('.txt')]

#         num = len(total_images)
#         if num == 0:
#             QMessageBox.warning(self, 'Error', 'No files found in the specified directory.')
#             return

#         list_indices = list(range(num))
#         tv = int(num * train_test_percent)
#         tr = int(tv * train_valid_percent)
#         trainval = random.sample(list_indices, tv)
#         train = random.sample(trainval, tr)

#         train_txt = open(os.path.join(ImageSetspath, 'train.txt'), 'w')
#         valid_txt = open(os.path.join(ImageSetspath, 'valid.txt'), 'w')
#         test_txt = open(os.path.join(ImageSetspath, 'test.txt'), 'w')

#         train_img_txt = open(os.path.join(ImageSetspath, 'img_train.txt'), 'w')
#         valid_img_txt = open(os.path.join(ImageSetspath, 'img_valid.txt'), 'w')
#         test_img_txt = open(os.path.join(ImageSetspath, 'img_test.txt'), 'w')

#         for i in list_indices:
#             txt_name = total_txts[i][:-4] + '.txt' + '\n'
#             img_path = os.path.abspath(os.path.join(jpegimages_path, total_images[i]))
#             img_path = img_path.replace('\\', '/')  # 替换路径中的反斜杠为正斜杠
#             img_name = img_path + '\n'
#             if i in trainval:
#                 if i in train:
#                     train_txt.write(txt_name)
#                     train_img_txt.write(img_name)
#                 else:
#                     valid_txt.write(txt_name)
#                     valid_img_txt.write(img_name)
#             else:
#                 test_txt.write(txt_name)
#                 test_img_txt.write(img_name)

#         train_txt.close()
#         valid_txt.close()
#         test_txt.close()
#         train_img_txt.close()
#         valid_img_txt.close()
#         test_img_txt.close()

#         self.organize_dataset(root_path, txtsavepath,ImageSetspath)

#     def organize_dataset(self, root_path, txtsavepath,ImageSetspath):
#         img_txt_cg_train = []
#         img_txt_cg_test = []
#         img_txt_cg_valid = []
#         label_txt_cg_train = []
#         label_txt_cg_test = []
#         label_txt_cg_valid = []

#         for line in open(os.path.join(ImageSetspath, "img_train.txt")):
#             img_txt_cg_train.append(line.strip('\n'))
#         for line in open(os.path.join(ImageSetspath, "img_test.txt")):
#             img_txt_cg_test.append(line.strip('\n'))
#         for line in open(os.path.join(ImageSetspath, "img_valid.txt")):
#             img_txt_cg_valid.append(line.strip('\n'))

#         for line in open(os.path.join(ImageSetspath, "train.txt")):
#             label_txt_cg_train.append(line.strip('\n'))
#         for line in open(os.path.join(ImageSetspath, "test.txt")):
#             label_txt_cg_test.append(line.strip('\n'))
#         for line in open(os.path.join(ImageSetspath, "valid.txt")):
#             label_txt_cg_valid.append(line.strip('\n'))

#         new_dataset_train = os.path.join(root_path, 'dataset/voc/data/train/images')
#         new_dataset_test = os.path.join(root_path, 'dataset/voc/data/test/images')
#         new_dataset_valid = os.path.join(root_path, 'dataset/voc/data/valid/images')

#         new_dataset_trainl = os.path.join(root_path, 'dataset/voc/data/train/labels')
#         new_dataset_testl = os.path.join(root_path, 'dataset/voc/data/test/labels')
#         new_dataset_validl = os.path.join(root_path, 'dataset/voc/data/valid/labels')

#         if not os.path.exists(new_dataset_train):
#             os.makedirs(new_dataset_train)
#         if not os.path.exists(new_dataset_test):
#             os.makedirs(new_dataset_test)
#         if not os.path.exists(new_dataset_valid):
#             os.makedirs(new_dataset_valid)
#         if not os.path.exists(new_dataset_trainl):
#             os.makedirs(new_dataset_trainl)
#         if not os.path.exists(new_dataset_testl):
#             os.makedirs(new_dataset_testl)
#         if not os.path.exists(new_dataset_validl):
#             os.makedirs(new_dataset_validl)

#         fimg = os.path.join(root_path, 'dataset/voc/JPEGImages')
#         flabel = os.path.join(root_path, 'dataset/voc/worktxt')

#         for i in img_txt_cg_train:
#             shutil.copy(os.path.join(fimg, i), new_dataset_train)
#         for i in label_txt_cg_train:
#             shutil.copy(os.path.join(flabel, i), new_dataset_trainl)
#         for i in img_txt_cg_test:
#             shutil.copy(os.path.join(fimg, i), new_dataset_test)
#         for i in label_txt_cg_test:
#             shutil.copy(os.path.join(flabel, i), new_dataset_testl)
#         for i in img_txt_cg_valid:
#             shutil.copy(os.path.join(fimg, i), new_dataset_valid)
#         for i in label_txt_cg_valid:
#             shutil.copy(os.path.join(flabel, i), new_dataset_validl)

#         QMessageBox.information(self, 'Success', 'Dataset organized successfully.')

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = CombinedApp()
#     window.show()
#     sys.exit(app.exec_())
import sys
import os
import json
import shutil
import random
import yaml
from PyQt5.QtWidgets import (QApplication, QGroupBox, QWidget, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QProgressBar, QRadioButton, QHBoxLayout, QMessageBox, QButtonGroup, QSpinBox, QDialog, QFormLayout, QDialogButtonBox, QLabel)
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
from PyQt5.QtGui import QFont

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

        # Image File Group
        image_group = QGroupBox("Image File")
        image_layout = QHBoxLayout()
        self.imagepath_input = QLineEdit(self)
        self.imagepath_button = QPushButton('Browse', self)
        self.imagepath_button.clicked.connect(self.browse_imagepath)
        image_layout.addWidget(self.imagepath_input)
        image_layout.addWidget(self.imagepath_button)
        image_group.setLayout(image_layout)

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
        aug_left_layout.addWidget(image_group)
        aug_left_layout.addWidget(output_group)
        aug_left_layout.addWidget(aug_times_group)

        # Radio Buttons for Augmentation Levels
        self.rotation_only_radio = QRadioButton("Rotation Only")
        self.rotation_dropout_radio = QRadioButton("Rotation + Dropout")
        self.full_augmentation_radio = QRadioButton("Full Augmentation")

        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.rotation_only_radio)
        self.radio_group.addButton(self.rotation_dropout_radio)
        self.radio_group.addButton(self.full_augmentation_radio)
        
        self.rotation_only_radio.setChecked(True)

        aug_right_layout.addWidget(self.rotation_only_radio)
        aug_right_layout.addWidget(self.rotation_dropout_radio)
        aug_right_layout.addWidget(self.full_augmentation_radio)

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

    def browse_filename(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, 'Select JSON File', '', 'JSON Files (*.json)', options=options)
        if filename:
            self.filename_input.setText(filename)

    def browse_imagepath(self):
        options = QFileDialog.Options()
        imagepath, _ = QFileDialog.getOpenFileName(self, 'Select Image File', '', 'Image Files (*.jpg;*.jpeg;*.png)', options=options)
        if imagepath:
            self.imagepath_input.setText(imagepath)

    def browse_outputpath(self):
        options = QFileDialog.Options()
        outputpath = QFileDialog.getExistingDirectory(self, 'Select Output Directory', options=options)
        if outputpath:
            self.outputpath_input.setText(outputpath)

    def start_augmentation(self):
        filename = self.filename_input.text()
        image_path = self.imagepath_input.text()
        output_path = self.outputpath_input.text()
        aug_times = self.aug_times_input.value()

        if not filename or not image_path or not output_path:
            QMessageBox.warning(self, 'Input Error', 'Please provide all the required inputs.')
            return

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        image = imageio.imread(image_path)
        rotation_list = list(range(15, 360, 15))

        with open(filename, 'r', encoding='utf-8') as f:
            original_squad_box = json.load(f)

        ia.seed(42)

        sometimes = lambda aug: iaa.Sometimes(1, aug)
        seq = None

        if self.rotation_dropout_radio.isChecked():
            seq = iaa.Sequential(
                [
                    iaa.OneOf([
                        sometimes(iaa.Dropout((0.01, 0.1), per_channel=0.5)),
                        sometimes(iaa.CoarseDropout(
                            (0.03, 0.15), size_percent=(0.02, 0.05),
                            per_channel=0.2
                        )),
                        sometimes(iaa.ElasticTransformation(alpha=(0.5, 3.5), sigma=0.25)),
                    ]),
                ],
                random_order=True
            )
        elif self.full_augmentation_radio.isChecked():
            seq = iaa.Sequential(
                [
                    iaa.OneOf([
                        sometimes(iaa.Dropout((0.01, 0.1), per_channel=0.5)),
                        sometimes(iaa.CoarseDropout(
                            (0.03, 0.15), size_percent=(0.02, 0.05),
                            per_channel=0.2
                        )),
                        sometimes(iaa.ElasticTransformation(alpha=(0.5, 3.5), sigma=0.25)),
                        sometimes(iaa.GaussianBlur(sigma=(0.0, 3.0))),
                        sometimes(iaa.MultiplyBrightness(mul=(0.7, 1.3))),
                        sometimes(iaa.MultiplyHueAndSaturation(mul_hue=(0.8, 1.2), mul_saturation=(0.8, 1.2))),
                        sometimes(iaa.AddToHue(value=(-10, 10))),
                        sometimes(iaa.AddToSaturation(value=(-10, 10)))
                    ]),
                ],
                random_order=True
            )

        total_operations = len(rotation_list) * (aug_times if seq else 1)
        progress = 0

        self.progress_bar.setValue(0)

        jpegimages_path = os.path.join(output_path, 'dataset/voc/JPEGImages')
        worktxt_path = os.path.join(output_path, 'dataset/voc/worktxt')

        if not os.path.exists(jpegimages_path):
            os.makedirs(jpegimages_path)
        if not os.path.exists(worktxt_path):
            os.makedirs(worktxt_path)

        for theta in rotation_list:
            squad_box = copy.deepcopy(original_squad_box)

            file_prefix = os.path.splitext(os.path.basename(filename))[0]
            new_json_name = f"{file_prefix}{theta}.json"
            new_image_name = f"{file_prefix}{theta}.jpg"
            new_image_path = os.path.join(output_path, new_image_name)

            bbs_list = []
            for shape in squad_box['shapes']:
                bbox = shape['points']
                x1, y1 = bbox[0]
                x2, y2 = bbox[1]
                bbs_list.append(BoundingBox(x1=x1, x2=x2, y1=y1, y2=y2))

            bbs = BoundingBoxesOnImage(bbs_list, shape=image.shape)
            rot = iaa.Affine(rotate=theta, fit_output=True)
            image_aug, bbs_aug = rot(image=image, bounding_boxes=bbs)

            if seq:
                for i in range(aug_times):
                    aug_image_name = f"{file_prefix}{theta}_aug_{i}.jpg"
                    aug_image_path = os.path.join(output_path, aug_image_name)
                    image_aug_temp, bbs_aug_temp = seq(image=image_aug, bounding_boxes=bbs_aug)
                    self.save_augmented_image(image_aug_temp, bbs_aug_temp, squad_box, aug_image_name, aug_image_path, jpegimages_path, worktxt_path)
                    progress += 1
                    self.progress_bar.setValue(int((progress / total_operations) * 100))
            else:
                self.save_augmented_image(image_aug, bbs_aug, squad_box, new_image_name, new_image_path, jpegimages_path, worktxt_path)
                progress += 1
                self.progress_bar.setValue(int((progress / total_operations) * 100))

        QMessageBox.information(self, 'Success', 'Augmentation completed successfully.')

    def save_augmented_image(self, image_aug, bbs_aug, squad_box, image_name, image_path, jpegimages_path, worktxt_path):
        imageio.imwrite(image_path, image_aug)

        shutil.copy(image_path, jpegimages_path)
        pil_img = Image.fromarray(image_aug)
        buff = io.BytesIO()
        pil_img.save(buff, format="JPEG")
        base64_string = base64.b64encode(buff.getvalue()).decode("utf-8")

        for i, bb_aug in enumerate(bbs_aug.bounding_boxes):
            x1_new, y1_new = bb_aug.x1, bb_aug.y1
            x2_new, y2_new = bb_aug.x2, bb_aug.y2
            squad_box['shapes'][i]['points'] = [[x1_new, y1_new], [x2_new, y2_new]]

        squad_box['imagePath'] = image_name
        squad_box['imageData'] = base64_string
        squad_box['imageHeight'], squad_box['imageWidth'] = image_aug.shape[0:2]
        squad_box = convert_float32(squad_box)

        json_name = os.path.splitext(image_name)[0] + '.json'
        json_path = os.path.join(worktxt_path, json_name)
        with open(json_path, 'w') as f:
            json.dump(squad_box, f, indent=4)

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
                with open(json_path, 'r', encoding='utf-8') as f:
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
        self.convert_progress_bar.setValue(0)

        for idx, filename in enumerate(json_files):
            json_path = os.path.join(json_folder_path, filename)
            output_txt_name = filename.replace('.json', '.txt')
            output_txt_path = os.path.join(output_folder_path, output_txt_name)
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            image_width = data['imageWidth']
            image_height = data['imageHeight']

            with open(output_txt_path, 'w', encoding='utf-8') as txt_file:
                for shape in data['shapes']:
                    bbox = shape['points']
                    x1, y1 = bbox[0]
                    x2, y2 = bbox[1]
                    x, y, w, h = self.bbox_to_xywh(x1, y1, x2, y2, image_width, image_height)

                    label = shape['label']
                    class_id = next((class_id for lbl, class_id in self.class_info if lbl == label), None)
                    if class_id is not None:
                        txt_file.write(f"{class_id} {x} {y} {w} {h}\n")

            self.convert_progress_bar.setValue(int((idx + 1) / total_files * 100))

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
        root_path = self.root_path_input.text()
        train_test_percent = self.train_test_percent_input.value() / 100
        train_valid_percent = self.train_valid_percent_input.value() / 100

        jpegimages_path = os.path.join(root_path, 'dataset/voc/JPEGImages')
        txtsavepath = os.path.join(root_path, 'dataset/voc/worktxt')
        ImageSetspath = os.path.join(root_path, 'dataset/voc/ImageSets')
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
            img_path = os.path.abspath(os.path.join(jpegimages_path, total_images[i]))
            img_path = img_path.replace('\\', '/')  # 替换路径中的反斜杠为正斜杠
            img_name = img_path + '\n'
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

        for line in open(os.path.join(ImageSetspath, "img_train.txt"), encoding='utf-8'):
            img_txt_cg_train.append(line.strip('\n'))
        for line in open(os.path.join(ImageSetspath, "img_test.txt"), encoding='utf-8'):
            img_txt_cg_test.append(line.strip('\n'))
        for line in open(os.path.join(ImageSetspath, "img_valid.txt"), encoding='utf-8'):
            img_txt_cg_valid.append(line.strip('\n'))

        for line in open(os.path.join(ImageSetspath, "train.txt"), encoding='utf-8'):
            label_txt_cg_train.append(line.strip('\n'))
        for line in open(os.path.join(ImageSetspath, "test.txt"), encoding='utf-8'):
            label_txt_cg_test.append(line.strip('\n'))
        for line in open(os.path.join(ImageSetspath, "valid.txt"), encoding='utf-8'):
            label_txt_cg_valid.append(line.strip('\n'))

        new_dataset_train = os.path.join(root_path, 'dataset/voc/data/train/images')
        new_dataset_test = os.path.join(root_path, 'dataset/voc/data/test/images')
        new_dataset_valid = os.path.join(root_path, 'dataset/voc/data/valid/images')

        new_dataset_trainl = os.path.join(root_path, 'dataset/voc/data/train/labels')
        new_dataset_testl = os.path.join(root_path, 'dataset/voc/data/test/labels')
        new_dataset_validl = os.path.join(root_path, 'dataset/voc/data/valid/labels')

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

        fimg = os.path.join(root_path, 'dataset/voc/JPEGImages')
        flabel = os.path.join(root_path, 'dataset/voc/worktxt')

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

        self.generate_yaml(root_path, ImageSetspath)

    def generate_yaml(self, root_path, ImageSetspath):
        data_path = os.path.abspath(os.path.join(root_path, 'dataset'))
        data_path = data_path.replace('\\', '/')  # Ensure path uses forward slashes
        train_path = os.path.abspath(os.path.join(ImageSetspath, 'img_train.txt'))
        train_path = train_path.replace('\\', '/')  # Ensure path uses forward slashes
        val_path = os.path.abspath(os.path.join(ImageSetspath, 'img_valid.txt'))
        val_path = val_path.replace('\\', '/')  # Ensure path uses forward slashes
        test_path = os.path.abspath(os.path.join(ImageSetspath, 'img_test.txt'))
        test_path = test_path.replace('\\', '/')  # Ensure path uses forward slashes

        class_dict = {cls_id: label for label, cls_id in self.class_info}

        yaml_content = {
            'path': data_path,
            'train': train_path,
            'val': val_path,
            'test': test_path,
            'names': class_dict
        }

        yaml_save_path, _ = QFileDialog.getSaveFileName(self, 'Save YAML File', '', 'YAML Files (*.yaml)')
        if yaml_save_path:
            with open(yaml_save_path, 'w', encoding='utf-8') as yaml_file:
                yaml.dump(yaml_content, yaml_file, default_flow_style=False, allow_unicode=True)

            QMessageBox.information(self, 'Success', f'YAML file saved to {yaml_save_path}')
        else:
            QMessageBox.warning(self, 'Save Error', 'YAML file was not saved.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CombinedApp()
    window.show()
    sys.exit(app.exec_())
