from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox

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
