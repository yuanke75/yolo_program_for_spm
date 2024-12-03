import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QGroupBox, QWidget, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QProgressBar, QRadioButton, QHBoxLayout, QMessageBox, QButtonGroup, QSpinBox)
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

class CombinedApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Augmentation Tool')
        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

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
        left_layout.addWidget(json_group)
        left_layout.addWidget(image_group)
        left_layout.addWidget(output_group)
        left_layout.addWidget(aug_times_group)

        # Radio Buttons for Augmentation Levels
        self.rotation_only_radio = QRadioButton("Rotation Only")
        self.rotation_dropout_radio = QRadioButton("Rotation + Dropout")
        self.full_augmentation_radio = QRadioButton("Full Augmentation")

        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.rotation_only_radio)
        self.radio_group.addButton(self.rotation_dropout_radio)
        self.radio_group.addButton(self.full_augmentation_radio)
        
        self.rotation_only_radio.setChecked(True)

        right_layout.addWidget(self.rotation_only_radio)
        right_layout.addWidget(self.rotation_dropout_radio)
        right_layout.addWidget(self.full_augmentation_radio)

        # Progress Bar and Start Button
        self.start_button = QPushButton('Start Augmentation', self)
        self.start_button.clicked.connect(self.start_augmentation)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)

        right_layout.addWidget(self.start_button)
        right_layout.addWidget(self.progress_bar)

        # Add left and right layouts to main layout
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

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

        with open(filename) as f:
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
                    self.save_augmented_image(image_aug_temp, bbs_aug_temp, squad_box, aug_image_name, aug_image_path, output_path)
                    progress += 1
                    self.progress_bar.setValue(int((progress / total_operations) * 100))
            else:
                self.save_augmented_image(image_aug, bbs_aug, squad_box, new_image_name, new_image_path, output_path)
                progress += 1
                self.progress_bar.setValue(int((progress / total_operations) * 100))

        QMessageBox.information(self, 'Success', 'Augmentation completed successfully.')

    def save_augmented_image(self, image_aug, bbs_aug, squad_box, image_name, image_path, output_path):
        imageio.imwrite(image_path, image_aug)

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
        with open(os.path.join(output_path, json_name), 'w') as f:
            json.dump(squad_box, f, indent=4)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CombinedApp()
    ex.show()
    sys.exit(app.exec_())
