import json
import os
import base64
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QLineEdit, QFileDialog, QGraphicsView, QGraphicsScene, 
                             QGraphicsRectItem, QInputDialog, QApplication, QTableWidget, QTableWidgetItem, 
                             QLabel, QVBoxLayout, QWidget, QHeaderView, QHBoxLayout, QSplitter, QDialog, QTabWidget, QMessageBox,QGraphicsPolygonItem )
from PyQt5.QtGui import QPixmap, QImage, QPen, QPolygonF, QPainter
from PyQt5.QtCore import Qt, QRectF, QPointF, QByteArray, QBuffer

from PyQt5.QtWidgets import QGraphicsPolygonItem
from PyQt5.QtCore import pyqtSignal

class LabelingTool(QMainWindow):
    label_index_updated = pyqtSignal()  # 添加信号

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Image Labeling Tool')
        self.setGeometry(100, 100, 1200, 600)

        self.image_path = ""
        self.image_data = None

        self.annotations = []
        self.current_rect = None
        self.current_polygon = None
        self.polygon_points = []
        self.rect_start_point = QPointF()
        self.last_label = ""
        self.label_colors = {}
        self.color_palette = [Qt.red, Qt.green, Qt.blue, Qt.yellow, Qt.cyan, Qt.magenta]
        self.color_index = 0
        self.annotation_mode = "rectangle"  # 默认是矩形标注模式
        self.index_folder = "label_indices"
        os.makedirs(self.index_folder, exist_ok=True)
        self.detailed_index_file_path = os.path.join(self.index_folder, "detailed_label_index.json")
        self.simple_index_file_path = os.path.join(self.index_folder, "label_index.json")

        self.init_ui()
        self.init_label_index()

    def init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        self.tab_widget = QTabWidget(self)
        main_layout.addWidget(self.tab_widget)

        self.annotation_tab = QWidget()
        self.index_tab = QWidget()

        self.tab_widget.addTab(self.annotation_tab, "Annotation")
        self.tab_widget.addTab(self.index_tab, "Index Table")

        self.init_annotation_tab()
        self.init_index_tab()

    def init_annotation_tab(self):
        annotation_layout = QVBoxLayout(self.annotation_tab)

        self.splitter = QSplitter(Qt.Horizontal, self.annotation_tab)
        annotation_layout.addWidget(self.splitter)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.splitter.addWidget(self.view)

        control_layout = QHBoxLayout()

        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_annotations)
        control_layout.addWidget(self.save_button)

        self.open_button = QPushButton('Open Image')
        self.open_button.clicked.connect(self.open_image)
        control_layout.addWidget(self.open_button)

        self.mode_button = QPushButton('Switch to Polygon')
        self.mode_button.clicked.connect(self.switch_annotation_mode)
        control_layout.addWidget(self.mode_button)

        annotation_layout.addLayout(control_layout)

        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

    def switch_annotation_mode(self):
        if self.annotation_mode == "rectangle":
            self.annotation_mode = "polygon"
            self.mode_button.setText("Switch to Rectangle")
        else:
            self.annotation_mode = "rectangle"
            self.mode_button.setText("Switch to Polygon")

    def init_index_tab(self):
        index_layout = QVBoxLayout(self.index_tab)

        self.label_table = QTableWidget()
        self.label_table.setColumnCount(4)
        self.label_table.setHorizontalHeaderLabels(["Index", "Label", "Screenshot", "Remark"])
        self.label_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.label_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.label_table.cellDoubleClicked.connect(self.open_image_from_table)
        index_layout.addWidget(self.label_table)

    def init_label_index(self):
        if not os.path.exists(self.detailed_index_file_path):
            self.label_index = {i: f'M{i+1}' for i in range(80)}
            self.detailed_label_index = {i: f'M{i+1}' for i in range(80)}
            self.save_label_index()
        else:
            with open(self.detailed_index_file_path, 'r') as f:
                self.detailed_label_index = json.load(f)
            self.label_index = {}
            for k, v in self.detailed_label_index.items():
                parts = v.split(':')
                if len(parts) >= 2:
                    self.label_index[k] = parts[0] + ':' + parts[1]
                else:
                    self.label_index[k] = parts[0]
        self.load_label_table()

    def save_label_index(self):
        with open(self.detailed_index_file_path, 'w') as f:
            json.dump(self.detailed_label_index, f, indent=4)
        with open(self.simple_index_file_path, 'w') as f:
            json.dump(self.label_index, f, indent=4)
        
        self.label_index_updated.emit()  # 发出信号

    def load_label_table(self):
        self.label_table.setRowCount(0)
        for class_id, class_info in self.detailed_label_index.items():
            parts = class_info.split(':')
            label = parts[1] if len(parts) > 1 else ""

            row_position = self.label_table.rowCount()
            self.label_table.insertRow(row_position)

            self.label_table.setItem(row_position, 0, QTableWidgetItem(str(class_id)))
            self.label_table.setItem(row_position, 1, QTableWidgetItem(label))

            screenshot_item = QTableWidgetItem("")
            if len(parts) > 2:
                screenshot_path = parts[2]
                if os.path.exists(screenshot_path):
                    self.update_table_image(row_position, 2, screenshot_path)
            self.label_table.setItem(row_position, 2, screenshot_item)
            remark_item = QTableWidgetItem("")
            remark_item.setFlags(remark_item.flags() | Qt.ItemIsEditable)  # 使单元格可编辑
            self.label_table.setItem(row_position, 3, remark_item)

    def open_image(self):
        self.image_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Image Files (*.png *.jpg *.bmp)")
        if self.image_path:
            self.image_data = QImage(self.image_path)
            self.scene.clear()
            pixmap = QPixmap.fromImage(self.image_data)
            self.scene.addPixmap(pixmap)
            self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def eventFilter(self, source, event):
        if event.type() == event.MouseButtonPress and event.buttons() == Qt.LeftButton:
            if self.annotation_mode == "rectangle":
                self.rect_start_point = self.view.mapToScene(event.pos())
            elif self.annotation_mode == "polygon":
                self.add_polygon_point(event)
            return True
        elif event.type() == event.MouseMove and event.buttons() == Qt.LeftButton and self.annotation_mode == "rectangle":
            self.draw_rect(event)
            return True
        elif event.type() == event.MouseButtonRelease and event.button() == Qt.LeftButton:
            if self.annotation_mode == "rectangle":
                self.finalize_rect(event)
            elif self.annotation_mode == "polygon" and self.is_polygon_closed(event):
                self.finalize_polygon()
            return True
        return super().eventFilter(source, event)

    def add_polygon_point(self, event):
        scene_pos = self.view.mapToScene(event.pos())
        self.polygon_points.append(scene_pos)
        if not self.current_polygon:
            # 使用 QGraphicsPolygonItem 而不是 QGraphicsRectItem 来处理多边形
            self.current_polygon = QGraphicsPolygonItem(QPolygonF(self.polygon_points))
            pen = QPen(Qt.red)
            pen.setWidth(2)
            self.current_polygon.setPen(pen)
            self.scene.addItem(self.current_polygon)
        else:
            polygon = QPolygonF(self.polygon_points)
            self.current_polygon.setPolygon(polygon)

    def is_polygon_closed(self, event):
        if len(self.polygon_points) < 3:
            return False
        first_point = self.polygon_points[0]
        current_point = self.view.mapToScene(event.pos())
        return (first_point - current_point).manhattanLength() < 10  # 允许一个小的容差来闭合

    def finalize_polygon(self):
        label, ok = QInputDialog.getText(self, 'Input Label', 'Enter label:', QLineEdit.Normal, self.last_label)
        if ok and label:
            self.last_label = label
            class_id = self.assign_class_id(label)
            if label not in self.label_colors:
                self.label_colors[label] = self.color_palette[self.color_index % len(self.color_palette)]
                self.color_index += 1
            color = self.label_colors[label]
            pen = QPen(color)
            pen.setWidth(2)
            self.current_polygon.setPen(pen)

            points_list = [(point.x(), point.y()) for point in self.polygon_points]
            annotation = {
                "label": label,
                "class_id": class_id,
                "points": points_list,
                "shape_type": "polygon",
                "description": "",
                "flags": {}
            }
            self.annotations.append(annotation)

            # Capture screenshot for polygon
            self.capture_polygon_screenshot(class_id, points_list)

            self.polygon_points = []
            self.current_polygon = None

            self.save_label_index()
            print(f"Polygon label '{label}' with class ID '{class_id}' saved.")

    def capture_polygon_screenshot(self, class_id, points_list):
        screenshot_folder = os.path.join(self.index_folder, "screenshots")
        os.makedirs(screenshot_folder, exist_ok=True)
        screenshot_path = os.path.join(screenshot_folder, f"screenshot_{class_id}.png")

        # Create a QImage to render the polygon
        image = QImage(self.image_data.size(), QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawImage(0, 0, self.image_data)
        painter.setPen(QPen(Qt.red, 2))
        polygon = QPolygonF([QPointF(x, y) for x, y in points_list])
        painter.drawPolygon(polygon)
        painter.end()

        # Crop the image to the bounding box of the polygon
        bounding_rect = polygon.boundingRect().toRect()
        cropped_image = image.copy(bounding_rect)
        cropped_image.save(screenshot_path)

        parts = self.detailed_label_index[class_id].split(':')
        if len(parts) == 2:
            self.detailed_label_index[class_id] = f"{parts[0]}:{parts[1]}:{screenshot_path}"
        self.save_label_index()
        self.load_label_table()

    def draw_rect(self, event):
        end_point = self.view.mapToScene(event.pos())
        if not self.current_rect:
            self.current_rect = QGraphicsRectItem(QRectF(self.rect_start_point, end_point))
            pen = QPen(Qt.red)
            pen.setWidth(2)
            self.current_rect.setPen(pen)
            self.scene.addItem(self.current_rect)
        else:
            rect = QRectF(self.rect_start_point, end_point)
            self.current_rect.setRect(rect)

    def finalize_rect(self, event):
        if self.current_rect:
            rect = self.current_rect.rect()
            label, ok = QInputDialog.getText(self, 'Input Label', 'Enter label:', QLineEdit.Normal, self.last_label)
            if ok and label:
                self.last_label = label
                class_id = self.assign_class_id(label)
                if label not in self.label_colors:
                    self.label_colors[label] = self.color_palette[self.color_index % len(self.color_palette)]
                    self.color_index += 1
                color = self.label_colors[label]
                pen = QPen(color)
                pen.setWidth(2)
                self.current_rect.setPen(pen)
                annotation = {
                    "label": label,
                    "class_id": class_id,
                    "points": [[rect.left(), rect.top()], [rect.right(), rect.bottom()]],
                    "shape_type": "rectangle",
                    "description": "",
                    "flags": {}
                }
                self.annotations.append(annotation)
                if len(self.detailed_label_index[class_id].split(':')) == 2:
                    self.capture_screenshot(class_id, rect)
                self.current_rect = None

                self.save_label_index()
                print(f"Label '{label}' with class ID '{class_id}' saved to index.")

    def capture_screenshot(self, class_id, rect):
        screenshot_folder = os.path.join(self.index_folder, "screenshots")
        os.makedirs(screenshot_folder, exist_ok=True)
        screenshot_path = os.path.join(screenshot_folder, f"screenshot_{class_id}.png")
        screenshot = self.image_data.copy(int(rect.left()), int(rect.top()), int(rect.width()), int(rect.height()))
        screenshot.save(screenshot_path)

        parts = self.detailed_label_index[class_id].split(':')
        if len(parts) == 2:
            self.detailed_label_index[class_id] = f"{parts[0]}:{parts[1]}:{screenshot_path}"
        self.save_label_index()
        self.load_label_table()

    def assign_class_id(self, label):
        for class_id, class_info in self.detailed_label_index.items():
            if len(class_info.split(':')) > 1 and class_info.split(':')[1] == label:
                return class_id

        for class_id, class_info in self.detailed_label_index.items():
            if len(class_info.split(':')) == 1:
                self.detailed_label_index[class_id] = f"{class_info}:{label}"
                self.label_index[class_id] = f"{class_info}:{label}"
                self.save_label_index()
                self.load_label_table()
                return class_id
        raise ValueError("No available class ID found for the new label.")

    def save_annotations(self):
        if not self.image_path or not self.annotations:
            print("No image or annotations to save.")
            return

        buffer = QByteArray()
        buffer_writer = QBuffer(buffer)
        buffer_writer.open(QBuffer.WriteOnly)
        self.image_data.save(buffer_writer, "JPEG")
        image_data_base64 = base64.b64encode(buffer.data()).decode('utf-8')
        buffer_writer.close()

        image_info = {
            "version": "1.0",
            "shapes": self.annotations,
            "imagePath": os.path.basename(self.image_path),
            "imageData": image_data_base64,
            "imageHeight": self.image_data.height(),
            "imageWidth": self.image_data.width()
        }

        base_name = os.path.basename(self.image_path)
        save_name = os.path.splitext(base_name)[0] + ".json"

        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Annotations", save_name, "JSON Files (*.json)", options=options)
        
        if save_path:
            try:
                with open(save_path, 'w') as f:
                    json.dump(image_info, f, indent=4)
                print(f"Annotations saved to {save_path}")
                QMessageBox.information(self, 'Success', f'Annotations saved to {save_path}')
            except Exception as e:
                print(f"Failed to save annotations: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to save annotations: {e}')

    def open_image_from_table(self, row, column):
        if column == 2 or column == 3:
            cell_widget = self.label_table.cellWidget(row, column)
            if isinstance(cell_widget, QLabel):
                image_path = cell_widget.pixmap().toImage().text()
                self.show_full_image(image_path)
            elif isinstance(cell_widget, QPushButton):
                self.upload_remark(row)

    def upload_remark(self, row):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Remark Image", "", "Image Files (*.png *.jpg *.bmp)", options=options)
        if file_path:
            self.update_table_image(row, 3, file_path)
            class_id = int(self.label_table.item(row, 0).text())
            parts = self.detailed_label_index[class_id].split(':')
            if len(parts) == 3:
                self.detailed_label_index[class_id] = f"{parts[0]}:{parts[1]}"
            self.save_label_index()
            self.load_label_table()

    def update_table_image(self, row, column, image_path):
        if image_path:
            pixmap = QPixmap(image_path)
            label = QLabel()
            label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
            label.mouseDoubleClickEvent = lambda event, img=image_path: self.show_full_image(img)
            self.label_table.setCellWidget(row, column, label)
            self.adjust_table_row_height(row)

    def adjust_table_row_height(self, row):
        max_height = 0
        for column in range(self.label_table.columnCount()):
            widget = self.label_table.cellWidget(row, column)
            if widget and isinstance(widget, QLabel):
                height = widget.pixmap().height()
                if height > max_height:
                    max_height = height
        if max_height > 0:
            self.label_table.setRowHeight(row, max_height)

    def show_full_image(self, image_path):
        dialog = QDialog(self)
        dialog.setWindowTitle("View Image")
        dialog_layout = QVBoxLayout()
        label = QLabel(dialog)
        pixmap = QPixmap(image_path)
        label.setPixmap(pixmap)
        dialog_layout.addWidget(label)
        dialog.setLayout(dialog_layout)
        dialog.exec_()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = LabelingTool()
    window.show()
    sys.exit(app.exec_())
