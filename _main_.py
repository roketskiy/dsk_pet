import sys
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class DesktopPet(QLabel):
    def __init__(self):
        super().__init__()
        # 加载桌宠图片
        self.pet_image = QPixmap("C:/Users/潘雷/Downloads/shimeji-main/shimeji-main/img/Len/shime2.png")
        self.setPixmap(self.pet_image)

        # 设置无边框、始终置顶和工具窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.drag_position = None
        # 设置窗口背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
                # 记录点击时鼠标位置与窗口左上角的偏移
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton:
                # 根据鼠标当前位置和记录的偏移移动窗口
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    sys.exit(app.exec_())
