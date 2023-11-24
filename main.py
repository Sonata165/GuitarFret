import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtGui import QPainter, QPen, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox, QPushButton

class Fretboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.string_count = 6   # 琴弦数量
        self.fret_count = 20    # 品格数量
        self.string_spacing = 45  # 琴弦间距，原来的1.5倍
        self.fret_spacing = 60   # 品格间距，原来的1.5倍
        self.setMinimumSize(self.fret_spacing * (self.fret_count + 1), 
                            self.string_spacing * (self.string_count + 1)) 
        # self.selectedFret = None  # 存储被选中的品位
        self.selectedFrets = []  # 存储被选中的品位

    def paintEvent(self, event):
        painter = QPainter(self)
        self.drawFrets(painter)
        self.drawStrings(painter)
        self.drawFretNumbers(painter)

    def drawFrets(self, painter):
        for i in range(1, self.fret_count + 1):  # 从1开始，因为不再绘制最左侧的竖线
            x = i * self.fret_spacing
            if i == 1:  # 紧邻数字1的左侧竖线不透明
                pen = QPen(Qt.black, 2)
            else:  # 其他竖线带透明度
                pen = QPen(QColor(0, 0, 0, 120), 2)
            painter.setPen(pen)
            painter.drawLine(x, self.string_spacing, x, self.height() - self.string_spacing)

    def drawStrings(self, painter):
        pen = QPen(QColor(160, 82, 45, 120), 4)  # 更淡的棕色
        painter.setPen(pen)
        for i in range(1, self.string_count + 1):
            y = i * self.string_spacing
            painter.drawLine(self.fret_spacing, y, self.width() - self.fret_spacing, y)

    def drawFretNumbers(self, painter):
        painter.setPen(Qt.black)
        painter.setFont(QFont('Arial', 15))
        fm = painter.fontMetrics()  # 获取字体度量信息，用于计算文本宽度
        for i in range(1, self.fret_count):
            text = str(i)
            text_width = fm.width(text)
            x = i * self.fret_spacing + (self.fret_spacing / 2) - (text_width / 2)
            y = self.height() - 10
            painter.drawText(x, y, text)

    def drawNotes(self, painter):
        open_strings = ['E', 'B', 'G', 'D', 'A', 'E']  # 颠倒弦的顺序
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        circle_diameter = 30  # 红圈的直径
        fm = painter.fontMetrics()
        for string in range(self.string_count):
            for fret in range(self.fret_count + 1):
                note_index = (notes.index(open_strings[string]) + fret) % 12
                note = notes[note_index]
                text_width = fm.width(note)
                x = fret * self.fret_spacing + (self.fret_spacing / 2) - (text_width / 2)
                y = (string + 1) * self.string_spacing

                if (fret, string) in self.selectedFrets:
                    # 高亮显示逻辑
                    circle_x = fret * self.fret_spacing + (self.fret_spacing / 2) - (circle_diameter / 2)
                    circle_y = (string + 1) * self.string_spacing - (circle_diameter / 2)

                    painter.setBrush(QColor(139, 0, 0))  # 深红色填充
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(circle_x, circle_y, circle_diameter, circle_diameter)

                    painter.setFont(QFont('Arial', 15, QFont.Bold))
                    painter.setPen(QColor(Qt.white))
                else:
                    # 正常显示逻辑
                    painter.setFont(QFont('Arial', 15))
                    painter.setPen(QColor(128, 128, 128, 130))

                painter.drawText(x, y + 5, note)

    def paintEvent(self, event):
        painter = QPainter(self)
        self.drawFrets(painter)
        self.drawStrings(painter)
        self.drawFretNumbers(painter)
        self.drawNotes(painter)  # 添加绘制音名的调用

    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()
        # 计算最接近的品位（水平方向）
        fret = round((x - (self.fret_spacing / 2)) / self.fret_spacing)
        # 计算最接近的弦（垂直方向）
        string = int((y - (self.string_spacing / 2)) / self.string_spacing)

        if 0 <= fret <= self.fret_count and 0 <= string < self.string_count:
            currentFret = (fret, string)
            if currentFret in self.selectedFrets:
                self.selectedFrets.remove(currentFret)  # 取消已选中的品位
            else:
                self.selectedFrets.append(currentFret)  # 添加新的选中品位
            self.update()  # 重绘组件

    def showNoteInfo(self, fret, string):
        open_strings = ['E', 'A', 'D', 'G', 'B', 'E']
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        note_index = (notes.index(open_strings[string - 1]) + fret) % 12
        note = notes[note_index]
        QMessageBox.information(self, "音名", f"弦：{string}, 品位：{fret}, 音名：{note}")



class GuitarApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('模拟吉他指板')
        self.setGeometry(100, 100, 1290, 330)  # 窗口尺寸不变
        self.fretboard = Fretboard(self)
        self.setCentralWidget(self.fretboard)

        # 将清除按钮进一步向上移动
        clearButton = QPushButton('Clear', self)
        clearButton.setGeometry(10, 5, 80, 30)  # 减小按钮的 y 坐标
        clearButton.clicked.connect(self.clearHighlights)

    def clearHighlights(self):
        self.fretboard.selectedFrets = []
        self.fretboard.update()





if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GuitarApp()
    ex.show()
    sys.exit(app.exec_())
