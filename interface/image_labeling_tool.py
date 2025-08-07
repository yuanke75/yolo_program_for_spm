import json
import os
import base64
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLineEdit, QFileDialog, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QInputDialog
from PyQt5.QtGui import QPixmap, QImage, QPen
from PyQt5.QtCore import Qt, QRectF, QPointF, QByteArray, QBuffer

class LabelingTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Image Labeling Tool')
        self.setGeometry(100, 100, 800, 600)

        self.image_path = ""
        self.image_data = None
        
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(10, 10, 780, 500)
        
        self.save_button = QPushButton('Save', self)
        self.save_button.setGeometry(10, 520, 100, 30)
        self.save_button.clicked.connect(self.save_annotations)

        self.open_button = QPushButton('Open Image', self)
        self.open_button.setGeometry(120, 520, 100, 30)
        self.open_button.clicked.connect(self.open_image)

        self.annotations = []
        self.current_rect = None
        self.rect_start_point = QPointF()
        self.last_label = ""
        self.label_colors = {}
        self.color_palette = [Qt.red, Qt.green, Qt.blue, Qt.yellow, Qt.cyan, Qt.magenta]
        self.color_index = 0

        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

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
            self.rect_start_point = self.view.mapToScene(event.pos())
            return True
        elif event.type() == event.MouseMove and event.buttons() == Qt.LeftButton:
            self.draw_rect(event)
            return True
        elif event.type() == event.MouseButtonRelease and event.button() == Qt.LeftButton:
            self.finalize_rect(event)
            return True
        return super().eventFilter(source, event)

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
                if label not in self.label_colors:
                    self.label_colors[label] = self.color_palette[self.color_index % len(self.color_palette)]
                    self.color_index += 1
                color = self.label_colors[label]
                pen = QPen(color)
                pen.setWidth(2)
                self.current_rect.setPen(pen)
                annotation = {
                    "label": label,
                    "points": [[rect.left(), rect.top()], [rect.right(), rect.bottom()]],
                    "shape_type": "rectangle",
                    "description": "",
                    "flags": {}
                }
                self.annotations.append(annotation)
                self.current_rect = None

    def save_annotations(self):
        if not self.image_path or not self.annotations:
            print("No image or annotations to save.")
            return

        # Encode image data to base64
        buffer = QByteArray()
        buffer_writer = QBuffer(buffer)
        buffer_writer.open(QBuffer.WriteOnly)
        self.image_data.save(buffer_writer, "JPEG")
        image_data_base64 = base64.b64encode(buffer.data()).decode('utf-8')
        buffer_writer.close()

        # Create JSON structure
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
            except Exception as e:
                print(f"Failed to save annotations: {e}")

