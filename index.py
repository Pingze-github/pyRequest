
import sys
from PyQt5 import QtWidgets


class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.__render()
        self.show()
    def __render(self):
        label = QtWidgets.QLabel(self)  # 在窗口中绑定label
        label.setText("hello world")


app = QtWidgets.QApplication(sys.argv)
window = Window()

sys.exit(app.exec_())