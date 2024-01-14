from functools import partial

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

import music_scale
from view.UI_ScaleInterface import Ui_ScaleInterface


class ScaleInterface(Ui_ScaleInterface, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        # 创建一个音频播放器，用于播放钢琴声音
        self.player = QMediaPlayer()

        # 初始化combobox
        self.CComboBox.addItems(['C', 'D', 'E', 'F', 'G', 'A', 'B'])
        self.bComboBox.addItems(['♮', '♯', '♭'])
        self.keyComboBox.addItems(
            [self.tr('Major'), self.tr('Harmonic Major'), self.tr('Melodic Major'), self.tr('Minor'),
             self.tr('Harmonic Minor'), self.tr('Melodic Minor'), self.tr('Pentatonic Major'),
             self.tr('Pentatonic Minor')])

        self.white_key_style_sheet_off = ''
        self.black_key_style_sheet_off = ''
        self.read_style_sheet()

        self.scale = music_scale.Scale('C♮', 'Major')

        self.key_button_list = []
        self.key_label_list = []
        self.white_y = 1800
        self.black_y = 1800
        # 初始化钢琴按钮
        for i in range(73):
            key_button = QPushButton(self.CardWidget)
            key_button.setFont(QFont('微软雅黑', 8))
            if self.is_white_key(i):
                y = self.white_y - 42 - 1
                key_button.setGeometry(-5, y, 62, 42)
                key_button.setStyleSheet(self.white_key_style_sheet_off)
                key_button.lower()
                if i % 12 == 0:
                    key_button.setText('C' + str(int(i / 12 + 2)))
                self.white_y = y
            else:
                y = self.black_y - 24 - 1
                if i % 12 == 6 or i % 12 == 1:
                    y = y - 24 - 4
                key_button.setGeometry(-5, y, 35, 24)
                y = y - 24
                self.black_y = y
                key_button.setStyleSheet(self.black_key_style_sheet_off)
                key_button.raise_()

            key_button.clicked.connect(partial(self.__on_clicked_key_button, key_button, i))
            self.key_button_list.append(key_button)

        # 初始化卷帘背景
        self.label_y = 1798
        for i in range(73):
            key_label = QLabel(self.CardWidget)
            y = self.label_y - 24 - 1
            if i % 12 == 6:
                y -= 1
                key_label.setGeometry(0, y, 905, 26)
            else:
                key_label.setGeometry(0, y, 905, 25)
            self.label_y = y
            if self.is_white_key(i):
                key_label.setStyleSheet('background:rgba(46,46,46,200);')
            else:
                key_label.setStyleSheet('background:rgba(38,38,38,220);')
            if i % 12 == 4 or i % 12 == 11:
                line_label = QLabel(self.CardWidget)
                line_label.setGeometry(0, y, 905, 1)
                line_label.setStyleSheet('background:black')
                line_label.lower()
            key_label.lower()
            self.key_label_list.append(key_label)

            self.SwitchButton.checkedChanged.connect(self.change_scale)
            self.CComboBox.currentIndexChanged.connect(self.change_scale)
            self.bComboBox.currentIndexChanged.connect(self.change_scale)
            self.keyComboBox.currentIndexChanged.connect(self.change_scale)

    # 判断给定音符是否为白键
    def is_white_key(self, index):
        scale_now = self.scale.scale
        if scale_now[index]:
            return True
        else:
            return False

    # 读取css
    def read_style_sheet(self):
        with open('resources/qss/scale_key_white_button_off.css') as f:
            self.white_key_style_sheet_off = f.read()
        with open('resources/qss/scale_key_black_button_off.css') as f:
            self.black_key_style_sheet_off = f.read()

    # 点击钢琴按钮播放声音
    def __on_clicked_key_button(self, btn, index):
        # 此处只有E2~F#6有声音素材（
        if 4 <= index <= 66:
            music_path = 'resources/piano-asset/' + str(index + 36) + '.wav'
            self.play_audio(music_path)

    # 播放音频
    def play_audio(self, path):
        self.player.stop()
        # 创建一个音频内容
        audio = QMediaContent(QUrl.fromLocalFile(path))

        # 设置音频内容到音频播放器
        self.player.setMedia(audio)

        # 开始播放音频
        self.player.play()

    # 改变卷帘背景颜色
    def change_key_label_color(self, sheet):
        for i in range(len(self.key_label_list)):
            if self.is_white_key(i):
                self.key_label_list[i].setStyleSheet(sheet)
            else:
                self.key_label_list[i].setStyleSheet('background:rgba(38,38,38,220);')

    # unused
    def change_key_color(self, sheet_white, sheet_black):
        for i in range(len(self.key_button_list)):
            if self.is_white_key(i):
                self.key_button_list[i].setStyleSheet(sheet_white)
            else:
                self.key_button_list[i].setStyleSheet(sheet_black)

    # 更新钢琴按钮上的文本
    def change_key_text(self):
        if self.SwitchButton.isChecked():
            root_index = self.scale.root_index % 12
            for i in range(len(self.key_button_list)):
                self.key_button_list[i].setText('')
                if i % 12 == root_index:
                    self.key_button_list[i].setText(self.scale.scale_name[i])
        else:
            for i in range(len(self.key_button_list)):
                self.key_button_list[i].setText('')
                if not self.is_white_key(i):
                    self.key_button_list[i].resize(35, 24)
                else:
                    self.key_button_list[i].resize(62, 42)
                    if i % 12 == 0:
                        self.key_button_list[i].setText('C' + str(int(i / 12 + 2)))

    # 音阶改变后，改变相应控件状态
    def change_scale(self):
        if self.SwitchButton.isChecked():
            root = self.CComboBox.text()
            note = self.bComboBox.text()
            key = self.keyComboBox.text()
            self.scale = music_scale.Scale(root + note, key)
            self.change_key_label_color('background:rgba(125,178,53,200);')
            self.change_key_text()
        # off时，恢复初始状态
        else:
            self.scale = music_scale.Scale('C♮', 'Major')
            self.change_key_label_color('background:rgba(46,46,46,200);')
            self.change_key_text()
