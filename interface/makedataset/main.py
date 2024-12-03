import sys
from PyQt5.QtWidgets import QApplication
from combined_app import CombinedApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CombinedApp()
    window.show()
    sys.exit(app.exec_())
