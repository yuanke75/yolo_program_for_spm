
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QLineEdit, QMessageBox, QComboBox
from PyQt5.QtCore import Qt
from PIL import Image

class LabelAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Label Analyzer')
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        self.select_mode_label = QLabel('Select Mode:', self)
        self.layout.addWidget(self.select_mode_label)

        self.select_mode_combo = QComboBox(self)
        self.select_mode_combo.addItem('Single File')
        self.select_mode_combo.addItem('Batch Folder')
        self.layout.addWidget(self.select_mode_combo)

        self.select_file_button = QPushButton('Select Label Path', self)
        self.select_file_button.clicked.connect(self.select_label_path)
        self.layout.addWidget(self.select_file_button)

        self.path_label = QLabel('Selected Path: None', self)
        self.layout.addWidget(self.path_label)

        self.scale_label = QLabel('Enter Scale (length in nm):', self)
        self.layout.addWidget(self.scale_label)

        self.length_scale_input = QLineEdit(self)
        self.length_scale_input.setPlaceholderText("Length in nm")
        self.layout.addWidget(self.length_scale_input)

        self.width_scale_input = QLineEdit(self)
        self.width_scale_input.setPlaceholderText("Width in nm")
        self.layout.addWidget(self.width_scale_input)

        self.analysis_mode_label = QLabel('Select Analysis Mode:', self)
        self.layout.addWidget(self.analysis_mode_label)

        self.analysis_mode_combo = QComboBox(self)
        self.analysis_mode_combo.addItem('Classification Count')
        self.analysis_mode_combo.addItem('Calculate Area')
        self.layout.addWidget(self.analysis_mode_combo)

        self.result_button = QPushButton('Show Result', self)
        self.result_button.clicked.connect(self.show_result)
        self.layout.addWidget(self.result_button)

        self.result_label = QLabel('', self)
        self.layout.addWidget(self.result_label)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

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

    def select_label_path(self):
        mode = self.select_mode_combo.currentText()
        options = QFileDialog.Options()
        if mode == 'Single File':
            file_path, _ = QFileDialog.getOpenFileName(self, "Select Label File", "", "Text Files (*.txt);;All Files (*)", options=options)
            if file_path:
                self.path_label.setText(f'Selected Path: {file_path}')
                self.file_path = file_path
                self.folder_path = None
                self.image_path = self.find_image(file_path)
        else:
            folder_path = QFileDialog.getExistingDirectory(self, "Select Label Folder", options=options)
            if folder_path:
                self.path_label.setText(f'Selected Path: {folder_path}')
                self.folder_path = folder_path
                self.file_path = None
                self.image_path = None  # Folder mode doesn't handle a single image

    def find_image(self, label_path):
        parent_dir = os.path.dirname(os.path.dirname(label_path))
        base_name = os.path.splitext(os.path.basename(label_path))[0]
        for ext in ['.jpg', '.png', '.jpeg']:
            image_path = os.path.join(parent_dir, base_name + ext)
            if os.path.exists(image_path):
                return image_path
        return None

    def show_result(self):
        if hasattr(self, 'file_path') and self.file_path:
            self.analyze_single_file(self.file_path)
        elif hasattr(self, 'folder_path') and self.folder_path:
            self.analyze_folder(self.folder_path)
        else:
            QMessageBox.warning(self, "No Path Selected", "Please select a valid file or folder path.")

    def analyze_single_file(self, file_path):
        analysis_mode = self.analysis_mode_combo.currentText()
        scale = self.get_scale() if analysis_mode == 'Calculate Area' else None

        if analysis_mode == 'Classification Count':
            classifications = self.read_label_file(file_path)
            self.display_classifications(classifications)
        elif analysis_mode == 'Calculate Area' and scale is not None:
            areas = self.calculate_areas(file_path, scale, self.image_path)
            self.display_areas(areas)

    def analyze_folder(self, folder_path):
        analysis_mode = self.analysis_mode_combo.currentText()
        scale = self.get_scale() if analysis_mode == 'Calculate Area' else None

        if analysis_mode == 'Classification Count':
            all_classifications = {}
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.txt'):
                    file_path = os.path.join(folder_path, file_name)
                    classifications = self.read_label_file(file_path)
                    for cls, count in classifications.items():
                        if cls in all_classifications:
                            all_classifications[cls] += count
                        else:
                            all_classifications[cls] = count
            self.display_classifications(all_classifications)
        elif analysis_mode == 'Calculate Area' and scale is not None:
            area_dict = {}
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.txt'):
                    file_path = os.path.join(folder_path, file_name)
                    image_path = self.find_image(file_path)
                    if not image_path:
                        QMessageBox.warning(self, "Image Not Found", f"No corresponding image found for the label file: {file_path}")
                        continue
                    areas = self.calculate_areas(file_path, scale, image_path)
                    for cls, area in areas:
                        if cls in area_dict:
                            area_dict[cls].append(area)
                        else:
                            area_dict[cls] = [area]
            avg_areas = {cls: sum(areas)/len(areas) for cls, areas in area_dict.items()}
            self.display_avg_areas(avg_areas)

    def read_label_file(self, file_path):
        classifications = {}
        with open(file_path, 'r') as file:
            for line in file:
                data = line.strip().split()
                cls = int(data[0])  # 类别
                if cls in classifications:
                    classifications[cls] += 1
                else:
                    classifications[cls] = 1
        return classifications
    
    def polygon_area(self, polygon):
        n = len(polygon)  # 顶点个数
        area = 0.0
        for i in range(n):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i + 1) % n]  # 与下一个顶点相连，最后一个顶点与第一个顶点相连
            area += x1 * y2 - x2 * y1
        return abs(area) / 2.0  # 面积为绝对值的一半

    def calculate_areas(self, file_path, scale, image_path):
        areas = []
        if not image_path:
            QMessageBox.warning(self, "Image Not Found", "No corresponding image found for the label file.")
            return areas

        with Image.open(image_path) as img:
            img_width, img_height = img.size

        length_nm, width_nm = scale
        length_scale = length_nm / img_height  # 转换为 nm/像素
        width_scale = width_nm / img_width     # 转换为 nm/像素

        with open(file_path, 'r') as file:
            for line in file:
                data = line.strip().split()
                cls = int(data[0])  # 读取类别
                points = list(map(float, data[1:]))

                if len(points) == 4:  # 如果有4个数值，说明是矩形
                    x, y, w, h = points
                    actual_w = w * img_width * width_scale  # 将宽度转换为纳米
                    actual_h = h * img_height * length_scale  # 将高度转换为纳米
                    area = actual_w * actual_h  # 计算矩形面积
                    areas.append((cls, area))
                elif len(points) >= 6 and len(points) % 2 == 0:  # 如果有6个以上的数值且成对出现，说明是多边形
                    polygon_points = [(points[i], points[i+1]) for i in range(0, len(points), 2)]
                    scaled_polygon = [(x * img_width * width_scale, y * img_height * length_scale) for (x, y) in polygon_points]
                    area = self.polygon_area(scaled_polygon)  # 计算多边形面积
                    areas.append((cls, area))
                else:
                    QMessageBox.warning(self, "Invalid Data", "The label data is invalid. Each object must have valid points.")
                    continue

        return areas


    def display_classifications(self, classifications):
        result_text = 'Classifications:\n'
        for cls, count in classifications.items():
            result_text += f'Class {cls}: {count} objects\n'
        self.result_label.setText(result_text)

    def display_areas(self, areas):
        area_dict = {}
        for cls, area in areas:
            if cls in area_dict:
                area_dict[cls].append(area)
            else:
                area_dict[cls] = [area]
        avg_areas = {cls: sum(areas)/len(areas) for cls, areas in area_dict.items()}

        result_text = '\nAreas:\n'
        for cls, avg_area in avg_areas.items():
            result_text += f'Class {cls}: Average Area: {avg_area:.2f} square nanometers\n'
        self.result_label.setText(self.result_label.text() + result_text + '\n')

    def display_avg_areas(self, avg_areas):
        result_text = 'Average Areas:\n'
        for cls, avg_area in avg_areas.items():
            result_text += f'Class {cls}: Average Area: {avg_area:.2f} square nanometers\n'
        self.result_label.setText(result_text)

    def get_scale(self):
        try:
            length_nm = float(self.length_scale_input.text())
            width_nm = float(self.width_scale_input.text())
            if length_nm <= 0 or width_nm <= 0:
                raise ValueError
            return (length_nm, width_nm)  # Scale in nanometers for the entire image
        except ValueError:
            QMessageBox.warning(self, "Invalid Scale", "Please enter valid scales (positive numbers).")
            return None

if __name__ == '__main__':
    app = QApplication([])
    window = LabelAnalyzer()
    window.show()
    app.exec_()
