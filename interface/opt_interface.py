import sys
import optuna
from optuna.pruners import MedianPruner
import subprocess
from copy import deepcopy
import yaml
import os
import pandas as pd
from pathlib import Path
import time
import traceback
import matplotlib.pyplot as plt
import optuna.visualization as vis
from PyQt5 import QtWidgets, QtCore, QtGui

class ParameterSelectionWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Optuna Parameter Selection")
        self.setGeometry(100, 100, 600, 800)
        self.setStyleSheet("background-color: #f0f0f0;")

        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QtWidgets.QWidget()
        self.scroll_layout = QtWidgets.QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)

        self.parameters = {
            'optimizer': ['SGD'],
            'lr0': [1e-5, 1e-1],
            'momentum': [0.85, 0.99],
            'lrf': [0.01, 1.0],
            'weight_decay': [1e-10, 0.01],
            'warmup_epochs': [0, 5],
            'warmup_momentum': [0.5, 0.95],
            'warmup_bias_lr': [0.01, 0.1],
            'box': [0.5, 10.0],
            'cls': [0.5, 1.0],
            'cls_pw': [0.5, 2.0],
            'obj': [0.5, 1.0],
            'obj_pw': [0.5, 2.0],
            'dfl': [0.5, 2.0],
            'iou_t': [0.1, 0.7],
            'anchor_t': [2.0, 10.0],
            'fl_gamma': [0, 5.0],
            'mosaic': [0.5, 1],
            'hsv_h': [0, 0.015],
            'hsv_s': [0, 0.7],
            'hsv_v': [0, 0.4],
            'degrees': [0.0, 0.5],
            'translate': [0.1, 0.5],
            'scale': [0.7, 0.9],
            'shear': [0.0, 0.3],
            'perspective': [0.0],
            'flipud': [0.0, 0.5],
            'fliplr': [0, 0.5],
            'mixup': [0.15, 0.3],
            'copy_paste': [0, 0.3],
        }
        self.param_checkboxes = {}
        self.param_inputs = {}

        for param, values in self.parameters.items():
            checkbox = QtWidgets.QCheckBox(param, self.scroll_content)
            checkbox.setChecked(True)
            checkbox.setFont(QtGui.QFont("Arial", 10))
            self.scroll_layout.addWidget(checkbox)
            self.param_checkboxes[param] = checkbox

            range_layout = QtWidgets.QHBoxLayout()
            min_input = QtWidgets.QLineEdit(str(values[0]), self.scroll_content)
            max_input = QtWidgets.QLineEdit(str(values[1]) if len(values) > 1 else '', self.scroll_content)
            min_input.setFont(QtGui.QFont("Arial", 10))
            max_input.setFont(QtGui.QFont("Arial", 10))
            min_input.setFixedWidth(100)
            max_input.setFixedWidth(100)
            min_input.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 5px;")
            max_input.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 5px;")
            range_layout.addWidget(min_input)
            range_layout.addWidget(max_input)
            self.scroll_layout.addLayout(range_layout)
            self.param_inputs[param] = (min_input, max_input)

        self.start_button = QtWidgets.QPushButton('Start Optimization', self.scroll_content)
        self.start_button.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border: none; border-radius: 5px;")
        self.start_button.clicked.connect(self.start_optimization)
        self.scroll_layout.addWidget(self.start_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)

    def start_optimization(self):
        selected_params = {}
        for param, checkbox in self.param_checkboxes.items():
            if checkbox.isChecked():
                try:
                    min_value = float(self.param_inputs[param][0].text())
                    max_input_text = self.param_inputs[param][1].text()
                    max_value = float(max_input_text) if max_input_text else None
                    if max_value is not None and min_value >= max_value:
                        raise ValueError(f"Minimum value must be less than maximum value for {param}.")
                    selected_params[param] = (min_value, max_value) if max_value is not None else (min_value,)
                except ValueError as e:
                    QtWidgets.QMessageBox.critical(self, "Invalid Input", str(e))
                    return
        self.optimize(selected_params)

    def optimize(self, selected_params):
        def objective(trial):
            params = {}
            for param, values in selected_params.items():
                if param == 'optimizer':
                    params['optimizer'] = trial.suggest_categorical('optimizer', ['SGD'])
                elif param == 'lr0':
                    params['lr0'] = trial.suggest_loguniform('lr0', values[0], values[1])
                elif param == 'momentum':
                    params['momentum'] = trial.suggest_uniform('momentum', values[0], values[1])
                elif param == 'lrf':
                    params['lrf'] = trial.suggest_uniform('lrf', values[0], values[1])
                elif param == 'weight_decay':
                    params['weight_decay'] = trial.suggest_loguniform('weight_decay', values[0], values[1])
                elif param == 'warmup_epochs':
                    params['warmup_epochs'] = trial.suggest_uniform('warmup_epochs', values[0], values[1])
                elif param == 'warmup_momentum':
                    params['warmup_momentum'] = trial.suggest_uniform('warmup_momentum', values[0], values[1])
                elif param == 'warmup_bias_lr':
                    params['warmup_bias_lr'] = trial.suggest_uniform('warmup_bias_lr', values[0], values[1])
                elif param == 'box':
                    params['box'] = trial.suggest_uniform('box', values[0], values[1])
                elif param == 'cls':
                    params['cls'] = trial.suggest_uniform('cls', values[0], values[1])
                elif param == 'cls_pw':
                    params['cls_pw'] = trial.suggest_uniform('cls_pw', values[0], values[1])
                elif param == 'obj':
                    params['obj'] = trial.suggest_uniform('obj', values[0], values[1])
                elif param == 'obj_pw':
                    params['obj_pw'] = trial.suggest_uniform('obj_pw', values[0], values[1])
                elif param == 'dfl':
                    params['dfl'] = trial.suggest_uniform('dfl', values[0], values[1])
                elif param == 'iou_t':
                    params['iou_t'] = trial.suggest_uniform('iou_t', values[0], values[1])
                elif param == 'anchor_t':
                    params['anchor_t'] = trial.suggest_uniform('anchor_t', values[0], values[1])
                elif param == 'fl_gamma':
                    params['fl_gamma'] = trial.suggest_uniform('fl_gamma', values[0], values[1])
                elif param == 'mosaic':
                    params['mosaic'] = trial.suggest_uniform('mosaic', values[0], values[1])
                elif param == 'hsv_h':
                    params['hsv_h'] = trial.suggest_uniform('hsv_h', values[0], values[1])
                elif param == 'hsv_s':
                    params['hsv_s'] = trial.suggest_uniform('hsv_s', values[0], values[1])
                elif param == 'hsv_v':
                    params['hsv_v'] = trial.suggest_uniform('hsv_v', values[0], values[1])
                elif param == 'degrees':
                    params['degrees'] = trial.suggest_uniform('degrees', values[0], values[1])
                elif param == 'translate':
                    params['translate'] = trial.suggest_uniform('translate', values[0], values[1])
                elif param == 'scale':
                    params['scale'] = trial.suggest_uniform('scale', values[0], values[1])
                elif param == 'shear':
                    params['shear'] = trial.suggest_uniform('shear', values[0], values[1])
                elif param == 'perspective':
                    params['perspective'] = trial.suggest_uniform('perspective', values[0], values[0])
                elif param == 'flipud':
                    params['flipud'] = trial.suggest_uniform('flipud', values[0], values[1])
                elif param == 'fliplr':
                    params['fliplr'] = trial.suggest_uniform('fliplr', values[0], values[1])
                elif param == 'mixup':
                    params['mixup'] = trial.suggest_uniform('mixup', values[0], values[1])
                elif param == 'copy_paste':
                    params['copy_paste'] = trial.suggest_uniform('copy_paste', values[0], values[1])

            return trial.suggest_uniform('objective_value', 0, 1)

        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=10)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = ParameterSelectionWidget()
    widget.show()
    sys.exit(app.exec_())