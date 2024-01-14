import time

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect

from view.UI_MetronomeInterface import Ui_MetronomeInterface


class MetronomeInterface(Ui_MetronomeInterface, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        # add shadow effect to card
        self.setShadowEffect(self.MetronomeCard)

        # 获取焦点以防空格按钮失效
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.beats_count = 0
        self.start_time = 0
        self.current_time = 0
        self.time_count = 0

        # 计时器，1s刷新一次
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.update_label)

        self.reButton.clicked.connect(self.clear)

    def setShadowEffect(self, card: QWidget):
        shadowEffect = QGraphicsDropShadowEffect(self)
        shadowEffect.setColor(QColor(0, 0, 0, 15))
        shadowEffect.setBlurRadius(10)
        shadowEffect.setOffset(0, 0)
        card.setGraphicsEffect(shadowEffect)

    def keyPressEvent(self, event):
        """
        重写了键盘检测事件函数。
        """
        print(f'检测按键{event.key()}按下！')
        if event.key() == QtCore.Qt.Key_Space:
            if self.beats_count == 0:
                self.start_time = time.time()
            else:
                self.current_time = time.time()
            self.beats_count += 1

    # 更新当前检测的BPM
    def update_label(self):
        if self.beats_count == 0:
            self.bpmLargeTitleLabel.setText('___._')
        else:
            bpm = self.beats_count / (self.current_time - self.start_time) * 60
            self.bpmLargeTitleLabel.setText('{:.2f}'.format(bpm))

    # 重置所有控件的状态
    def clear(self):
        self.beats_count = 0
        self.start_time = 0
        self.current_time = 0
        self.time_count = 0
        self.bpmLargeTitleLabel.setText('___._')
