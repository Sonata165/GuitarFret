import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PyQt5.QtGui import QPainter, QPen, QFont
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox, QPushButton
import fluidsynth
import subprocess

class Fretboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.string_count = 6   # 琴弦数量
        self.fret_count = 20    # 品格数量
        self.string_spacing = 45  # 琴弦间距，原来的1.5倍
        self.fret_spacing = 60   # 品格间距，原来的1.5倍
        self.initial_width = self.fret_spacing * (self.fret_count + 1)
        self.initial_height = self.string_spacing * (self.string_count + 1)
        self.setMinimumSize(self.fret_spacing * (self.fret_count + 1), 
                            self.string_spacing * (self.string_count + 1))
        self.selectedFrets = []  # 存储被选中的品位
        self.setFocusPolicy(Qt.StrongFocus)
        self.rootNote = set()

    def resizeEvent(self, event):
        # 重设组件的尺寸为初始尺寸，防止随窗口变化而改变
        self.resize(self.initial_width, self.initial_height)

    def drawFrets(self, painter):
        for i in range(1, self.fret_count + 1):
            x = i * self.fret_spacing
            if i == 1:  # 紧邻数字1的左侧竖线不透明
                pen = QPen(Qt.black, 2)
            else:  # 其他竖线带透明度
                pen = QPen(QColor(0, 0, 0, 120), 2)
            painter.setPen(pen)
            # 调整竖线的起点和终点
            top_y = self.string_spacing  # 第一根弦的位置
            bottom_y = self.string_spacing * self.string_count  # 第六根弦的位置
            painter.drawLine(x, top_y, x, bottom_y)

    def drawStrings(self, painter):
        pen = QPen(QColor(160, 82, 45, 120), 4)  # 更淡的棕色
        painter.setPen(pen)
        for i in range(1, self.string_count + 1):
            y = i * self.string_spacing
            painter.drawLine(self.fret_spacing, y, self.width() - self.fret_spacing, y)

    def drawFretNumbers(self, painter):
        painter.setPen(Qt.black)
        painter.setFont(QFont('Arial', 15))
        fm = painter.fontMetrics()
        for i in range(1, self.fret_count):
            text = str(i)
            text_width = fm.width(text)
            x = int(i * self.fret_spacing + (self.fret_spacing / 2) - (text_width / 2))
            y = self.height() - 10  # 将 y 坐标向上调整，使其更接近指板
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
                    painter.drawEllipse(int(circle_x), int(circle_y), circle_diameter, circle_diameter)

                    painter.setFont(QFont('Arial', 15, QFont.Bold))
                    painter.setPen(QColor(Qt.white))
                    painter.drawText(int(x), y + 5, note)
                else:
                    # 正常显示逻辑
                    painter.setFont(QFont('Arial', 15))
                    painter.setPen(QColor(128, 128, 128, 130))
                    painter.drawText(int(x), y + 5, note)

                # For root note, highlight
                if (fret, string) in self.rootNote:
                    if (fret, string) not in self.selectedFrets:
                        self.rootNote.remove((fret, string))
                    else:
                        # 绘制根音的黑色空心圆
                        root_circle_diameter = 40  # 根音圆的直径
                        root_circle_x = fret * self.fret_spacing + (self.fret_spacing / 2) - (root_circle_diameter / 2)
                        root_circle_y = (string + 1) * self.string_spacing - (root_circle_diameter / 2)
                        painter.setBrush(Qt.NoBrush)
                        painter.setPen(QPen(Qt.black, 2))  # 黑色，线宽度 2
                        painter.drawEllipse(int(root_circle_x), int(root_circle_y), root_circle_diameter, root_circle_diameter)

    def drawFretMarkers(self, painter):
        marker_frets = [3, 5, 7, 9, 12, 15, 17, 19]
        marker_color = QColor(0, 0, 180, 50)  # 降低蓝色的饱和度，增加透明度
        marker_diameter = 15  # 点点直径
        # painter.setPen(QPen(Qt.black, 2))  # 黑色，线宽度 2
        # painter.setPen(QColor(128, 128, 128, 130)) # 灰色
        painter.setPen(Qt.NoPen)
        painter.setBrush(marker_color)

        center_y = (self.string_spacing + (self.string_spacing * self.string_count)) / 2

        for fret in marker_frets:
            t = fret + 1
            x = t * self.fret_spacing - (self.fret_spacing / 2)

            if fret != 12:
                # 除了12品外的点点
                painter.drawEllipse(int(x - marker_diameter / 2), int(center_y - marker_diameter / 2), marker_diameter, marker_diameter)
            else:
                # 12品的两个点点，分别与第2弦和第5弦对齐
                string2_y = 2 * self.string_spacing
                string5_y = 5 * self.string_spacing
                painter.drawEllipse(int(x - marker_diameter / 2), int(string2_y - marker_diameter / 2), marker_diameter, marker_diameter)
                painter.drawEllipse(int(x - marker_diameter / 2), int(string5_y - marker_diameter / 2), marker_diameter, marker_diameter)


    def paintEvent(self, event):
        painter = QPainter(self)

        self.drawFrets(painter)
        self.drawFretMarkers(painter)  # 添加绘制点点的调用
        self.drawStrings(painter)
        self.drawFretNumbers(painter)
        self.drawNotes(painter)  # 添加绘制音名的调用
        

        # 绘制边框
        self.drawFretboardEdge(painter)

    def drawFretboardEdge(self, painter):
        pen = QPen(QColor(128, 128, 128, 180))  # 灰色，带有透明度
        pen.setWidth(2)  # 设置线条宽度
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)  # 设置无填充
        # 绘制边框，留出一定边距
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()
        # 计算最接近的品位（水平方向）
        fret = round((x - (self.fret_spacing / 2)) / self.fret_spacing)
        # 计算最接近的弦（垂直方向）
        string = int((y - (self.string_spacing / 2)) / self.string_spacing)

        if 0 <= fret <= self.fret_count and 0 <= string < self.string_count:
            currentFret = (fret, string)

            # 检查是否是鼠标右键点击
            if event.button() == Qt.RightButton:
                if currentFret in self.rootNote:
                    # 如果当前fret已经是root note，则取消root highlight
                    self.rootNote.remove(currentFret)
                elif currentFret in self.selectedFrets:
                    # 设置当前fret为root note
                    self.rootNote.add(currentFret)
                self.update()
            else:
                if currentFret in self.selectedFrets:
                    self.selectedFrets.remove(currentFret)
                else:
                    self.selectedFrets.append(currentFret)
                    self.playNote(fret, string)
                self.update()
            

    def showNoteInfo(self, fret, string):
        open_strings = ['E', 'A', 'D', 'G', 'B', 'E']
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        note_index = (notes.index(open_strings[string - 1]) + fret) % 12
        note = notes[note_index]
        QMessageBox.information(self, "音名", f"弦：{string}, 品位：{fret}, 音名：{note}")

    def initSynth(self):
        self.synth = fluidsynth.Synth(samplerate=44100.0, gain=1.0)
        self.synth.start()

        # 检查应用是否被打包
        if getattr(sys, 'frozen', False):
            # 如果应用被打包，则调整文件路径
            application_path = os.path.dirname(sys.executable)
            sf_path = os.path.join(application_path, "resources", "Tyros Nylon.sf2")
        else:
            # 如果应用未被打包，则使用原始路径
            sf_path = "resources/Tyros Nylon.sf2"

        print('Opening SoundFont: {}'.format(sf_path))
        sfid = self.synth.sfload(sf_path)
        self.synth.program_select(0, sfid, 0, 0)

    def getNoteNumber(self, string, fret):
        # 吉他弦的标准音符编号（从最低音弦到最高音弦）
        standard_tuning = [64, 59, 55, 50, 45, 40]  # reverse(E2, A2, D3, G3, B3, E4)
        return standard_tuning[string] + fret
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_C:
            self.clearHighlights()
        elif event.key() == Qt.Key_Q:
            self.playSelectedNotes()
    
    def clearHighlights(self):
        self.selectedFrets = []
        self.rootNote.clear()
        self.update()

    def playNote(self, fret, string):
        note = self.getNoteNumber(string, fret)
        self.synth.noteon(0, note, 127)  # channel 0, note, velocity 127
        
        # 延时关闭音符，防止声音持续播放
        duration=1000
        QTimer.singleShot(duration, lambda: self.synth.noteoff(0, note))
    
    def playSelectedNotes(self):
        for fret, string in self.selectedFrets:
            self.playNote(fret, string)


class GuitarApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.fretboard.initSynth()

    def initUI(self):
        window_width = 1260   # Original set to 1200, but will be resized to 1260
        window_height = 360

        # 设置窗口标题和尺寸
        self.setWindowTitle('GuitarFret')
        self.setGeometry(0, 0, window_width, window_height)
        self.centerWindow()

        # 设置指板
        self.fretboard = Fretboard(self)
        fretboard_x = 0
        fretboard_y = 70
        fretboard_width = window_width
        fretboard_height = self.fretboard.height()
        print(self.fretboard.width(), self.fretboard.height())
        self.fretboard.setGeometry(fretboard_x, fretboard_y, fretboard_width, fretboard_height)
        self.setCentralWidget(self.fretboard)

        # 按钮和说明文本的配置
        button_width = 80
        button_height = 30
        instructions_width = 400
        instructions_height = 20
        component_gap = 10  # 组件间隔

        # 总宽度
        total_width = 2 * button_width + instructions_width + 2 * component_gap
        start_x = (window_width - total_width) / 2
        vertical_center_y = fretboard_height + button_height//2 + 5      # 垂直位置

        # 清除按钮
        clearButton_x = start_x
        clearButton = QPushButton('Clear: C', self)
        clearButton.setGeometry(clearButton_x, vertical_center_y - button_height / 2, button_width, button_height)
        clearButton.clicked.connect(self.clearHighlights)

        # 播放按钮
        playButton_x = clearButton_x + button_width + component_gap
        playButton = QPushButton('Play: Q', self)
        playButton.setGeometry(playButton_x, vertical_center_y - button_height / 2, button_width, button_height)
        playButton.clicked.connect(self.playSelectedNotes)

        # 说明文本
        instructions_x = playButton_x + button_width + component_gap
        instructions = QLabel('Select note: left click; Highlight root: right click.', self)
        instructions.setGeometry(instructions_x, vertical_center_y - instructions_height / 2, instructions_width, instructions_height)


    def centerWindow(self):
        # 将窗口移动到屏幕中心
        qr = self.frameGeometry()
        cp = QApplication.desktop().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def clearHighlights(self):
        self.fretboard.clearHighlights()

    def playSelectedNotes(self):
        for fret, string in self.fretboard.selectedFrets:
            self.fretboard.playNote(fret, string)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GuitarApp()
    ex.show()
    sys.exit(app.exec_())
