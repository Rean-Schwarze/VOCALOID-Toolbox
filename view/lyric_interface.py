import asyncio
import time

import pandas as pd
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect, QApplication, QTableWidgetItem
from qfluentwidgets import MessageBox, TableItemDelegate, InfoBar

import get_lyrics
from view.UI_LyricInterface import Ui_LyricInterface


class LyricInterface(Ui_LyricInterface, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.completer = None
        self.completer_set = set()
        self.setupUi(self)

        # add shadow effect to card
        self.setShadowEffect(self.LyricCard)

        # 初始化table
        self.info_table.setColumnCount(4)
        self.column_names = [self.tr('title'), self.tr('artist'), self.tr('album'), self.tr('duration')]
        self.info_table.setHorizontalHeaderLabels(self.column_names)  # 自定义列名称
        self.info_table.verticalHeader().hide()  # 隐藏第一列（序号）
        self.info_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)  # 设置表格无法被编辑
        df_column_names = [self.tr('title'), self.tr('artist'), self.tr('album'), self.tr('duration'), 'id', 'mid']
        self.df = pd.DataFrame(columns=df_column_names)

        # 初始化combobox
        self.CComboBox.addItems(['C', 'D', 'E', 'F', 'G', 'A', 'B'])
        self.bComboBox.addItems(['♮', '♯', '♭'])
        self.keyComboBox.addItems(['Major', 'Minor'])

        self.SearchLineEdit.searchSignal.connect(lambda: self.search(self.SearchLineEdit))

        self.getLyricButton.clicked.connect(self.get_lyric)
        self.lyric = ''
        self.title = ''
        self.saveButton.clicked.connect(self.save_files)

    def setShadowEffect(self, card: QWidget):
        shadowEffect = QGraphicsDropShadowEffect(self)
        shadowEffect.setColor(QColor(0, 0, 0, 15))
        shadowEffect.setBlurRadius(10)
        shadowEffect.setOffset(0, 0)
        card.setGraphicsEffect(shadowEffect)

    def __showTooltip(self):
        """ show tooltip """
        InfoBar.success(
            self.tr('Hint'),
            self.tr('Save Successfully!'),
            duration=1500,
            parent=self
        )

    def showMessageBox(self, title, content):
        w = MessageBox(
            title,
            content,
            self
        )
        w.yesButton.setText(self.tr('Confirm'))
        w.cancelButton.setText(self.tr('Cancel'))
        if w.exec():
            w.yesButton.setText(self.tr('Confirm'))

    def keyPressEvent(self, event):
        """
        重写了键盘检测事件函数。
        """
        if event.key() == QtCore.Qt.Key_Return:  # 按下回车，也可以触发搜索
            self.search(self.SearchLineEdit)

    # 开始搜索
    def search(self, line):
        # 获取搜索框上输入的文本
        keyword = self.SearchLineEdit.text()
        if keyword == '' or keyword == ' ':
            return
        # 获取音乐平台
        if self.neteaseRadioButton.isChecked():
            state, data = get_lyrics.netease_search(keyword)
        elif self.qqmusicRadioButton.isChecked():
            state, data = asyncio.run(get_lyrics.qqmusic_search(keyword))
        if state:
            self.df = self.df.drop(index=self.df.index)  # 首先清空df
            for d in data:
                title = d['title']
                artist = d['artist']
                album = d['album']
                duration = 0
                if 'duration' in d:
                    # 将时间戳处理为“分：秒”的格式
                    duration = d['duration'] / 1000
                    duration_local = time.localtime(duration)
                    duration = time.strftime("%M:%S", duration_local)
                if duration == 0:
                    duration = self.tr('Unknown')
                id = d['id']
                mid = ''
                if 'mid' in d:
                    mid = d['mid']
                self.df.loc[len(self.df)] = [title, artist, album, duration, id, mid]
        else:
            self.showMessageBox(self.tr('Error'), self.tr('Some errors occured while getting search result!'))
        self.update_table()

    # 更新info_table内容
    def update_table(self, row_start=0, col_start=0, df=None):
        if df is None:
            df = self.df
        # 获取行列数
        row_count, col_count = df.shape
        # 设置表格行数
        self.info_table.setRowCount(row_count)

        # 设置元素
        for row in range(row_start, row_count):
            for col in range(col_start, 4):  # df最后两列不显示
                item = QTableWidgetItem(str(df.iloc[row, col]))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # 设置文本居中对齐
                self.info_table.setItem(row, col, item)

        QApplication.processEvents()

    # 更新歌词预览
    def update_lyric_edit(self):
        self.lyricPlainTextEdit.clear()
        self.lyricPlainTextEdit.insertPlainText(self.lyric)
        QApplication.processEvents()  # 实时刷新

    # 获取歌词
    def get_lyric(self):
        # 获取当前选择元素的行数
        index = self.info_table.currentIndex().row()
        if index < 0:
            self.showMessageBox(self.tr('Error'), self.tr('Haven\'t selected the song!'))
        else:
            id = self.df.iloc[index, 4]
            mid = self.df.iloc[index, 5]
            self.title = self.df.iloc[index, 0]
            if self.neteaseRadioButton.isChecked():
                state, lyric = get_lyrics.netease_get_lyric(id)
                if state:
                    self.lyric = lyric
                    self.update_lyric_edit()
                else:
                    self.showMessageBox(self.tr('Error'), self.tr('Some errors occured while getting lyrics!'))
            elif self.qqmusicRadioButton.isChecked():
                state, lyric = asyncio.run(get_lyrics.qqmusic_get_lyric(id, mid))
                if state:
                    self.lyric = lyric
                    self.update_lyric_edit()
                else:
                    self.showMessageBox(self.tr('Error'), self.tr('Some errors occured while getting lyrics!'))

    # 保存歌词到文件
    def save_files(self):
        format_flag = False
        format_list = []
        index = self.info_table.currentIndex().row()
        if index < 0:
            self.showMessageBox(self.tr('Error'), self.tr('Haven\'t selected the song!'))
        artist = self.df.iloc[index, 1]
        if self.neteaseRadioButton.isChecked():
            artist = artist.replace('/', ',')  # 网易云音乐歌手的格式：xx,xx,...
        elif self.qqmusicRadioButton.isChecked():
            artist = artist.replace('/', '、')  # QQ音乐歌手的格式：xx、xx、...
        if self.lrcCheckBox.isChecked():
            format_flag = True
            format_list.append('.lrc')
        if self.txtCheckBox.isChecked():
            format_flag = True
            format_list.append('.txt')
        if self.docxCheckBox.isChecked():
            format_flag = True
            format_list.append('.docx')
        bpm = self.bpmLineEdit.text()
        bpm_flag = bpm.isdigit()  # 检测输入的BPM是否为数字
        scale = self.CComboBox.currentText()
        note = self.bComboBox.currentText()
        key = self.keyComboBox.currentText()
        if not bpm_flag:
            bpm = 0
        if format_flag is False or self.lyric == '':
            self.showMessageBox(self.tr('Error'), self.tr('Haven\'t selected the format or input bpm or got lyrics!'))
        else:
            for file_format in format_list:
                if file_format == '.lrc':
                    get_lyrics.save_to_file(self.lyric, self.title, bpm, scale, note, key, file_format, artist)
                else:
                    get_lyrics.save_to_file(get_lyrics.convert_lrc_to_others(self.lyric)[1], self.title, bpm, scale,
                                            note,
                                            key, file_format)
            self.__showTooltip()
