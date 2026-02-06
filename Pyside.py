from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

app = QApplication()

loader = QUiLoader()

file = QFile('GUI.ui')
file.open(QFile.ReadOnly)

window = loader.load(file)
file.close()

window.show()

app.exec()