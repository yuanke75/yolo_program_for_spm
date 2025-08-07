# import os
# import random
# from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, 
#                              QLineEdit, QFileDialog, QSlider, QMessageBox, QFormLayout, QGroupBox, QInputDialog)
# from PyQt5.QtCore import Qt

# class IncrementalLearningTool(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle('Incremental Learning Tool')
#         self.setGeometry(100, 100, 800, 600)

#         self.source_paths = []  # 存储源数据集路径的列表
#         self.source_percentages = []  # 存储每个源数据集百分比的列表
#         self.target_path = ""  # 目标数据集路径
#         self.new_dataset_name = ""  # 新数据集名称

#         self.init_ui()  # 初始化UI组件

#     def init_ui(self):
#         central_widget = QWidget(self)  # 创建中央窗口部件
#         self.setCentralWidget(central_widget)  # 设置中央窗口部件

#         main_layout = QVBoxLayout(central_widget)  # 创建中央部件的垂直布局

#         # 源数据集布局
#         self.source_groupbox = QGroupBox("Source Datasets")  # 创建分组框
#         self.source_layout = QFormLayout()  # 创建表单布局以显示源数据集路径和滑条
#         self.source_groupbox.setLayout(self.source_layout)
#         main_layout.addWidget(self.source_groupbox)  # 将分组框添加到主布局

#         # 添加源数据集按钮
#         self.add_source_button = QPushButton('Add Source Dataset')
#         self.add_source_button.clicked.connect(self.add_source)
#         main_layout.addWidget(self.add_source_button)  # 将“添加源数据集”按钮添加到主布局

#         # 目标数据集输入布局
#         target_groupbox = QGroupBox("Target Dataset")  # 创建分组框
#         target_layout = QFormLayout()  # 创建表单布局
#         self.target_input = QLineEdit()  # 创建输入框
#         self.target_button = QPushButton('Browse')
#         self.target_button.clicked.connect(self.browse_target)  # 连接按钮点击事件到浏览目标数据集方法
#         target_layout.addRow(QLabel('Target Dataset Path:'), self.target_input)  # 添加标签和输入框到表单布局
#         target_layout.addWidget(self.target_button)  # 将按钮添加到表单布局
#         target_groupbox.setLayout(target_layout)
#         main_layout.addWidget(target_groupbox)  # 将分组框添加到主布局

#         # 处理和保存按钮布局
#         button_layout = QHBoxLayout()
#         self.process_button = QPushButton('Process Data')  # 创建“处理数据”按钮
#         self.process_button.clicked.connect(self.process_data)  # 连接按钮点击事件到处理数据方法
#         button_layout.addWidget(self.process_button)  # 将“处理数据”按钮添加到布局

#         main_layout.addLayout(button_layout)  # 将按钮布局添加到主布局

#     def add_source(self):
#         options = QFileDialog.Options()  # 创建文件对话框选项
#         path = QFileDialog.getExistingDirectory(self, "Select Source Dataset Directory", options=options)  # 打开选择目录对话框
#         if path:
#             row_position = len(self.source_paths)  # 确定新源数据集的行位置
#             self.source_paths.append(path)  # 添加选中的路径到源路径列表
#             self.source_percentages.append(50)  # 初始化此源数据集的百分比为50%

#             # 创建新的源数据集输入框和滑动条
#             source_input = QLineEdit()
#             source_input.setText(path)  # 设置输入框文本为选中的路径
#             source_input.setReadOnly(True)  # 设置输入框为只读
#             percentage_slider = QSlider(Qt.Horizontal)  # 创建水平滑动条
#             percentage_slider.setRange(0, 100)  # 设置滑动条范围为0到100
#             percentage_slider.setValue(50)  # 设置滑动条初始值为50
#             percentage_slider.setTickInterval(10)  # 设置滑动条刻度间隔为10
#             percentage_slider.setTickPosition(QSlider.TicksBelow)  # 设置滑动条刻度位置在下方
#             percentage_slider.valueChanged.connect(lambda value, index=row_position: self.update_percentage(value, index))  # 连接滑动条值变化事件到更新百分比方法

#             percentage_label = QLabel('50%')  # 创建百分比标签
#             percentage_slider.valueChanged.connect(lambda value, label=percentage_label: label.setText(f'{value}%'))  # 连接滑动条值变化事件到更新标签方法

#             # 添加源数据集输入框、滑动条和百分比标签到表单布局
#             row_layout = QHBoxLayout()
#             row_layout.addWidget(source_input)
#             row_layout.addWidget(percentage_slider)
#             row_layout.addWidget(percentage_label)
#             self.source_layout.addRow(row_layout)

#     def browse_target(self):
#         options = QFileDialog.Options()  # 创建文件对话框选项
#         path = QFileDialog.getExistingDirectory(self, "Select Target Dataset Directory", options=options)  # 打开选择目录对话框
#         if path:
#             self.target_path = path  # 设置目标路径
#             self.target_input.setText(path)  # 更新目标输入框文本为选中的路径

#     def update_percentage(self, value, index):
#         self.source_percentages[index] = value  # 更新指定索引的源数据集的百分比

#     def process_data(self):
#         if not self.source_paths or not self.target_path:
#             QMessageBox.warning(self, 'Input Error', 'Please specify both source and target dataset paths.')  # 显示警告消息
#             return

#         new_dataset_name, ok = QInputDialog.getText(self, 'New Dataset Name', 'Enter name for the new dataset:')  # 弹出输入框以输入新数据集名称
#         if not ok or not new_dataset_name:
#             return  # 如果用户取消输入或输入为空，直接返回

#         new_dataset_path = os.path.join(os.path.dirname(self.target_path), new_dataset_name)  # 使用自定义名称创建新数据集路径
#         os.makedirs(new_dataset_path, exist_ok=True)  # 如果目录不存在则创建

#         source_files = ['img_test.txt', 'img_train.txt', 'img_valid.txt']  # 要处理的源文件列表
#         combined_lines = {file: [] for file in source_files}  # 用于保存每个文件的合并行的字典

#         for i, source_path in enumerate(self.source_paths):
#             source_dir = os.path.join(source_path, 'voc', 'ImageSets', 'Main')  # 源数据集的路径
#             percentage = self.source_percentages[i]  # 获取该源数据集的百分比

#             for file_name in source_files:
#                 file_path = os.path.join(source_dir, file_name)
#                 if os.path.exists(file_path):
#                     with open(file_path, 'r') as f:
#                         lines = f.readlines()  # 读取文件中的所有行
#                         num_lines = len(lines)
#                         selected_lines = random.sample(lines, int(percentage / 100 * num_lines))  # 随机选取指定百分比的行
#                         combined_lines[file_name].extend(selected_lines)  # 将选取的行添加到合并行列表中

#         target_dir = os.path.join(self.target_path, 'voc', 'ImageSets', 'Main')
#         for file_name in source_files:
#             file_path = os.path.join(target_dir, file_name)
#             if os.path.exists(file_path):
#                 with open(file_path, 'r') as f:
#                     target_lines = f.readlines()  # 读取目标文件中的所有行
#                     combined_lines[file_name].extend(target_lines)  # 将目标文件中的行添加到合并行列表中

#             # 将合并的行写入新的数据集文件
#             new_file_path = os.path.join(new_dataset_path, 'voc', 'ImageSets', 'Main', file_name)
#             os.makedirs(os.path.dirname(new_file_path), exist_ok=True)  # 如果目录不存在则创建
#             with open(new_file_path, 'w') as new_f:
#                 new_f.writelines(combined_lines[file_name])  # 写入合并的行

#         self.save_new_dataset(new_dataset_path)  # 调用保存新数据集方法

#         QMessageBox.information(self, 'Process Complete', f'New dataset created at {new_dataset_path}')  # 显示处理完成消息

#     def save_new_dataset(self, new_dataset_path):
#         yaml_path = os.path.join(new_dataset_path, 'dataset.yaml')  # YAML文件路径

#         yaml_content = f"""path: '{new_dataset_path.replace(os.sep, '/')}'  # dataset root dir
# train: '{new_dataset_path.replace(os.sep, '/')}/voc/ImageSets/Main/img_train.txt'
# val: '{new_dataset_path.replace(os.sep, '/')}/voc/ImageSets/Main/img_valid.txt'
# test: '{new_dataset_path.replace(os.sep, '/')}/voc/ImageSets/Main/img_test.txt'
# # Classes
# names:
# """
#         for i in range(80):
#             yaml_content += f"  {i}: M{i+1}\n"  # 添加类别名称到YAML内容

#         with open(yaml_path, 'w') as f:
#             f.write(yaml_content)  # 将YAML内容写入文件

#         QMessageBox.information(self, 'Save Complete', f'YAML file created at {yaml_path}')  # 显示保存完成消息


# if __name__ == '__main__':
#     import sys
#     app = QApplication(sys.argv)
#     window = IncrementalLearningTool()  # 创建主窗口
#     window.show()  # 显示主窗口
#     sys.exit(app.exec_())  # 运行应用程序事件循环



import os
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, 
                             QLineEdit, QFileDialog, QSlider, QMessageBox, QFormLayout, QGroupBox, QInputDialog)
from PyQt5.QtCore import Qt

class IncrementalLearningTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Incremental Learning Tool')
        self.setGeometry(100, 100, 800, 600)

        self.source_paths = []  # 存储源数据集路径的列表
        self.source_percentages = []  # 存储每个源数据集百分比的列表
        self.target_path = ""  # 目标数据集路径
        self.new_dataset_name = ""  # 新数据集名称

        self.init_ui()  # 初始化UI组件
        self.apply_styles()  # 应用样式表

    def init_ui(self):
        central_widget = QWidget(self)  # 创建中央窗口部件
        self.setCentralWidget(central_widget)  # 设置中央窗口部件

        main_layout = QVBoxLayout(central_widget)  # 创建中央部件的垂直布局

        # 源数据集布局
        self.source_groupbox = QGroupBox("Source Datasets")  # 创建分组框
        self.source_layout = QFormLayout()  # 创建表单布局以显示源数据集路径和滑条
        self.source_groupbox.setLayout(self.source_layout)
        main_layout.addWidget(self.source_groupbox)  # 将分组框添加到主布局

        # 添加源数据集按钮
        self.add_source_button = QPushButton('Add Source Dataset')
        self.add_source_button.clicked.connect(self.add_source)
        main_layout.addWidget(self.add_source_button)  # 将“添加源数据集”按钮添加到主布局

        # 目标数据集输入布局
        target_groupbox = QGroupBox("Target Dataset")  # 创建分组框
        target_layout = QFormLayout()  # 创建表单布局
        self.target_input = QLineEdit()  # 创建输入框
        self.target_button = QPushButton('Browse')
        self.target_button.clicked.connect(self.browse_target)  # 连接按钮点击事件到浏览目标数据集方法
        target_layout.addRow(QLabel('Target Dataset Path:'), self.target_input)  # 添加标签和输入框到表单布局
        target_layout.addWidget(self.target_button)  # 将按钮添加到表单布局
        target_groupbox.setLayout(target_layout)
        main_layout.addWidget(target_groupbox)  # 将分组框添加到主布局

        # 处理和保存按钮布局
        button_layout = QHBoxLayout()
        self.process_button = QPushButton('Process Data')  # 创建“处理数据”按钮
        self.process_button.clicked.connect(self.process_data)  # 连接按钮点击事件到处理数据方法
        button_layout.addWidget(self.process_button)  # 将“处理数据”按钮添加到布局

        main_layout.addLayout(button_layout)  # 将按钮布局添加到主布局

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
            QLabel {
                font-weight: bold;
                color: #333;
            }
        """)

    def add_source(self):
        options = QFileDialog.Options()  # 创建文件对话框选项
        path = QFileDialog.getExistingDirectory(self, "Select Source Dataset Directory", options=options)  # 打开选择目录对话框
        if path:
            row_position = len(self.source_paths)  # 确定新源数据集的行位置
            self.source_paths.append(path)  # 添加选中的路径到源路径列表
            self.source_percentages.append(50)  # 初始化此源数据集的百分比为50%

            # 创建新的源数据集输入框和滑动条
            source_input = QLineEdit()
            source_input.setText(path)  # 设置输入框文本为选中的路径
            source_input.setReadOnly(True)  # 设置输入框为只读
            percentage_slider = QSlider(Qt.Horizontal)  # 创建水平滑动条
            percentage_slider.setRange(0, 100)  # 设置滑动条范围为0到100
            percentage_slider.setValue(50)  # 设置滑动条初始值为50
            percentage_slider.setTickInterval(10)  # 设置滑动条刻度间隔为10
            percentage_slider.setTickPosition(QSlider.TicksBelow)  # 设置滑动条刻度位置在下方
            percentage_slider.valueChanged.connect(lambda value, index=row_position: self.update_percentage(value, index))  # 连接滑动条值变化事件到更新百分比方法

            percentage_label = QLabel('50%')  # 创建百分比标签
            percentage_slider.valueChanged.connect(lambda value, label=percentage_label: label.setText(f'{value}%'))  # 连接滑动条值变化事件到更新标签方法

            # 添加源数据集输入框、滑动条和百分比标签到表单布局
            row_layout = QHBoxLayout()
            row_layout.addWidget(source_input)
            row_layout.addWidget(percentage_slider)
            row_layout.addWidget(percentage_label)
            self.source_layout.addRow(row_layout)

    def browse_target(self):
        options = QFileDialog.Options()  # 创建文件对话框选项
        path = QFileDialog.getExistingDirectory(self, "Select Target Dataset Directory", options=options)  # 打开选择目录对话框
        if path:
            self.target_path = path  # 设置目标路径
            self.target_input.setText(path)  # 更新目标输入框文本为选中的路径

    def update_percentage(self, value, index):
        self.source_percentages[index] = value  # 更新指定索引的源数据集的百分比

    def process_data(self):
        if not self.source_paths or not self.target_path:
            QMessageBox.warning(self, 'Input Error', 'Please specify both source and target dataset paths.')  # 显示警告消息
            return

        new_dataset_name, ok = QInputDialog.getText(self, 'New Dataset Name', 'Enter name for the new dataset:')  # 弹出输入框以输入新数据集名称
        if not ok or not new_dataset_name:
            return  # 如果用户取消输入或输入为空，直接返回

        new_dataset_path = os.path.join(os.path.dirname(self.target_path), new_dataset_name)  # 使用自定义名称创建新数据集路径
        os.makedirs(new_dataset_path, exist_ok=True)  # 如果目录不存在则创建

        source_files = ['img_test.txt', 'img_train.txt', 'img_valid.txt']  # 要处理的源文件列表
        combined_lines = {file: [] for file in source_files}  # 用于保存每个文件的合并行的字典

        for i, source_path in enumerate(self.source_paths):
            source_dir = os.path.join(source_path, 'voc', 'ImageSets', 'Main')  # 源数据集的路径
            percentage = self.source_percentages[i]  # 获取该源数据集的百分比

            for file_name in source_files:
                file_path = os.path.join(source_dir, file_name)
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        lines = f.readlines()  # 读取文件中的所有行
                        num_lines = len(lines)
                        selected_lines = random.sample(lines, int(percentage / 100 * num_lines))  # 随机选取指定百分比的行
                        combined_lines[file_name].extend(selected_lines)  # 将选取的行添加到合并行列表中

        target_dir = os.path.join(self.target_path, 'voc', 'ImageSets', 'Main')
        for file_name in source_files:
            file_path = os.path.join(target_dir, file_name)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    target_lines = f.readlines()  # 读取目标文件中的所有行
                    combined_lines[file_name].extend(target_lines)  # 将目标文件中的行添加到合并行列表中

            # 将合并的行写入新的数据集文件
            new_file_path = os.path.join(new_dataset_path, 'voc', 'ImageSets', 'Main', file_name)
            os.makedirs(os.path.dirname(new_file_path), exist_ok=True)  # 如果目录不存在则创建
            with open(new_file_path, 'w') as new_f:
                new_f.writelines(combined_lines[file_name])  # 写入合并的行

        self.save_new_dataset(new_dataset_path)  # 调用保存新数据集方法

        QMessageBox.information(self, 'Process Complete', f'New dataset created at {new_dataset_path}')  # 显示处理完成消息

    def save_new_dataset(self, new_dataset_path):
        yaml_path = os.path.join(new_dataset_path, 'dataset.yaml')  # YAML文件路径

        yaml_content = f"""path: '{new_dataset_path.replace(os.sep, '/')}'  # dataset root dir
train: '{new_dataset_path.replace(os.sep, '/')}/voc/ImageSets/Main/img_train.txt'
val: '{new_dataset_path.replace(os.sep, '/')}/voc/ImageSets/Main/img_valid.txt'
test: '{new_dataset_path.replace(os.sep, '/')}/voc/ImageSets/Main/img_test.txt'
# Classes
names:
"""
        for i in range(80):
            yaml_content += f"  {i}: M{i+1}\n"  # 添加类别名称到YAML内容

        with open(yaml_path, 'w') as f:
            f.write(yaml_content)  # 将YAML内容写入文件

        QMessageBox.information(self, 'Save Complete', f'YAML file created at {yaml_path}')  # 显示保存完成消息


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = IncrementalLearningTool()  # 创建主窗口
    window.show()  # 显示主窗口
    sys.exit(app.exec_())  # 运行应用程序事件循环
