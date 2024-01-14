import os
import queue
from collections import Counter

import pandas
import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect, QCompleter, QApplication, QFileDialog, \
    QTableWidgetItem
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import MessageBox, TableItemDelegate, InfoBar

import bpm_key_finder
from common.config import cfg
from view.UI_BPMKeyFinderInterface import Ui_BPMKeyFinderInterface


# 不可选中元素
class EmptyDelegate(TableItemDelegate):
    def __init__(self, parent):
        super(EmptyDelegate, self).__init__(parent)

    def createEditor(self, QWidget, QStyleOptionViewItem, QModelIndex):
        return None


# 处理检测的线程
class detectThread(QThread):
    # 自定义信号
    update_signal_dict = pyqtSignal(dict)

    def __init__(self, detect_queue, parent=None):
        super(detectThread, self).__init__(parent)
        self.detect_queue = detect_queue

    def run(self):
        while len(self.detect_queue.queue) != 0:
            # 取出队列头部的元素
            file_dict = self.detect_queue.get()
            index = file_dict['index']
            file = file_dict['filename']
            print('正在检测：{}'.format(file))
            # 检测bpm、调性
            bpm_librosa = bpm_key_finder.find_bpm_librosa(file)[2]
            bpm_wave = bpm_key_finder.find_bpm_wave(file)[2]
            key = bpm_key_finder.find_key(file)[2]
            # 将结果封装为字典
            detect_dict = {'index': index, 'bpm_librosa': bpm_librosa, 'bpm_wave': bpm_wave, 'key': key}
            print('【{}】检测完成'.format(file))
            # 激活
            self.update_signal_dict.emit(detect_dict)


class BPMKeyFinderInterface(Ui_BPMKeyFinderInterface, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # 用于自动补全用户输入的文本
        self.completer = None
        self.completer_set = set()
        self.setupUi(self)

        # add shadow effect to card
        self.setShadowEffect(self.FinderCard)

        # 隐藏进度条
        self.IndeterminateProgressBar.hide()

        # 初始化table
        self.info_table.setColumnCount(7)
        self.column_names = [self.tr('title'), self.tr('artist'), self.tr('album'), 'BPM(librosa)', 'BPM(wave)',
                             self.tr('BPM(Manually)'), self.tr('key')]
        self.info_table.setHorizontalHeaderLabels(self.column_names)  # 自定义列名称
        self.info_table.verticalHeader().hide()  # 隐藏第一列（序号）
        self.info_table.setColumnWidth(3, 90)  # 设置第4/5/6列的宽度
        self.info_table.setColumnWidth(4, 90)
        self.info_table.setColumnWidth(5, 100)
        # 除了BPM（手动）这一列以外，其他的设为无法编辑
        for i in range(self.info_table.columnCount()):
            if i != 5:
                self.info_table.setItemDelegateForColumn(i, EmptyDelegate(self.info_table))
        # self.info_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)  # 设置表格无法被编辑
        self.info_table.cellChanged['int', 'int'].connect(self.update_df_bpm_man)
        self.df = pd.DataFrame(columns=self.column_names)  # 初始化df
        # 初始化counter，用于避免重复检测
        self.counter = Counter()

        # 读取保存的文件
        self.load_file()

        # 检测队列
        self.detect_queue = queue.Queue()

        self.addButton.setIcon(FIF.ADD_TO)
        self.addButton.clicked.connect(self.open_file)

        self.loadButton.clicked.connect(self.load_file)

        self.saveButton.clicked.connect(self.save_file)

        self.hintLabel.hide()

        # 初始化定时器，每 5分钟自动保存一次文件
        self.timer = QTimer(self)
        self.timer.start(1000 * cfg.get(cfg.auto_save_time))
        self.timer.timeout.connect(self.save_file)

        self.SearchLineEdit.searchSignal.connect(lambda: self.search(self.SearchLineEdit))
        self.SearchLineEdit.clearSignal.connect(self.update_table)

    def setShadowEffect(self, card: QWidget):
        shadowEffect = QGraphicsDropShadowEffect(self)
        shadowEffect.setColor(QColor(0, 0, 0, 15))
        shadowEffect.setBlurRadius(10)
        shadowEffect.setOffset(0, 0)
        card.setGraphicsEffect(shadowEffect)

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

    def __showTooltip(self):
        """ show tooltip """
        InfoBar.success(
            self.tr('Hint'),
            self.tr('Save Successfully!'),
            duration=1500,
            parent=self
        )

    # 更新dataFrame内容（检测结果）
    def update_df(self, update_dict):
        index = update_dict['index']
        bpm_librosa = update_dict['bpm_librosa']
        bpm_wave = update_dict['bpm_wave']
        key = update_dict['key']
        self.df.loc[index:index, ('BPM(librosa)', 'BPM(wave)', self.tr('key'))] = [bpm_librosa, bpm_wave, key]
        self.update_table(index)

    # 手动输入BPM后，更新dataFrame
    def update_df_bpm_man(self, row, col):
        self.df.iloc[row, col] = self.info_table.item(row, col).text()

    # 更新info_table内容
    def update_table(self, row_start=0, col_start=0, df=None):
        # 由于这里会触发信号槽，所以先阻断信号
        self.info_table.blockSignals(True)

        if df is None:
            df = self.df
        # 获取行列数
        row_count, col_count = df.shape
        # 设置表格行数
        self.info_table.setRowCount(row_count)

        # 设置元素
        for row in range(row_start, row_count):
            for col in range(col_start, col_count):
                item = QTableWidgetItem(df.iloc[row, col])
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # 设置文本居中对齐
                self.info_table.setItem(row, col, item)

        self.info_table.blockSignals(False)  # 释放，开始监听信号

        QApplication.processEvents()

    # 调用QFileDialog打开文件
    def open_file(self):
        file_list, file_type = QFileDialog.getOpenFileNames(self, self.tr('Choose Audio Files'), os.getcwd(),
                                                            'Audio files (*.mp3 *.m4a *.flac '
                                                            '*.ogg *.wav)')
        self.start_detect(file_list)

    # 检测结束后，启用相应控件
    def finish(self):
        self.IndeterminateProgressBar.hide()
        self.loadButton.setEnabled(True)
        self.saveButton.setEnabled(True)

    # 开始检测函数
    def start_detect(self, file_list):
        # 显示进度条
        self.IndeterminateProgressBar.show()
        self.loadButton.setDisabled(True)
        self.saveButton.setDisabled(True)

        # 先把歌曲信息加入dataFrame
        for file in file_list:
            state, title, artist, album = bpm_key_finder.get_audio_info(file)
            artist_ch, album_ch = '', ''
            if state:
                if artist == '':
                    artist = self.tr('Unknown')
                    artist_ch = '未知'
                else:
                    artist_ch = artist
                if album == '':
                    album = self.tr('Unknown')
                    album_ch = '未知'
                else:
                    album_ch = album
                audio_info = title + ' ' + artist_ch + ' ' + album_ch
                # 使用Counter统计重复歌曲
                self.counter[audio_info] = self.counter[audio_info] + 1
                # 如果歌曲重复，则不添加
                if self.counter[audio_info] <= 1:
                    self.df.loc[len(self.df)] = [title, artist, album, self.tr('detecting'), self.tr('detecting'), '0',
                                                 self.tr('detecting')]
                    # 更新最后一行
                    self.update_table(len(self.df) - 1)
                    # 更新completer
                    self.set_completer(len(self.df) - 1)
                    # 将歌曲添加到检测队列
                    self.detect_queue.put({'index': len(self.df) - 1, 'filename': file})

        # 创建、启动线程
        self.detect_thread = detectThread(self.detect_queue)
        self.detect_thread.update_signal_dict.connect(self.update_df)
        self.detect_thread.finished.connect(self.finish)
        self.detect_thread.start()

    # 加载文件
    def load_file(self):
        finder_result_path = cfg.get(cfg.dataFolder) + '/bpm_key.csv'
        if os.path.exists(finder_result_path):
            self.df = pandas.read_csv(finder_result_path, encoding='UTF-8-SIG', dtype=str)
            self.update_table()
            self.set_completer()
            # 更新Counter
            row_count, col_count = self.df.shape
            for row in range(row_count):
                audio_info = ''
                for col in range(3):
                    audio_info += self.df.iloc[row, col]
                    if col != 2:
                        audio_info += ' '
                self.counter[audio_info] = self.counter[audio_info] + 1

    # 保存检测结果到文件
    def save_file(self):
        # 保存按钮处于可用状态时才保存
        if self.saveButton.isEnabled():
            finder_result_path = cfg.get(cfg.dataFolder) + '/bpm_key.csv'
            values = {self.tr('artist'): self.tr('Unknown'), self.tr('album'): self.tr('Unknown'),
                      self.tr('BPM(Manually)'): '0'}
            self.df.fillna(value=values, inplace=True)
            self.df.to_csv(finder_result_path, encoding='UTF-8-SIG', index=False)
            self.__showTooltip()

    def keyPressEvent(self, event):
        """
        重写了键盘检测事件函数。
        """
        if event.key() == QtCore.Qt.Key_Return:  # 按下回车，也可以触发搜索
            self.search(self.SearchLineEdit)

    # 重写拖拽文件进入窗口的函数
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
            self.hintLabel.show()
        else:
            event.ignore()

    # 重写拖拽文件退出窗口的函数
    def dragLeaveEvent(self, event):
        self.hintLabel.hide()

    # 重写拖拽文件进入窗口后松手的函数
    def dropEvent(self, event):
        self.hintLabel.hide()
        # 获取拖拽的文件列表
        file_list = event.mimeData().urls()
        local_file_list = []
        for raw_file in file_list:
            file = raw_file.toLocalFile()
            local_file_list.append(file)
        self.start_detect(local_file_list)

    # 设置自动填充内容
    def set_completer(self, start_row=0):
        # 获取行列数
        row_count, col_count = self.df.shape
        for row in range(start_row, row_count):
            for col in range(3):
                self.completer_set.add(self.df.iloc[row, col])
        self.completer = QCompleter(self.completer_set, self.SearchLineEdit)
        self.completer.setMaxVisibleItems(10)
        self.SearchLineEdit.setCompleter(self.completer)

    # 搜索函数
    def search(self, line):
        # 获取搜索框上输入的文本
        keyword = self.SearchLineEdit.text()
        # 分别找出关键词在标题/艺术家/专辑列上搜索出的结果
        title_df = self.df[self.df[self.tr('title')].isin([keyword])]
        artist_df = self.df[self.df[self.tr('artist')].isin([keyword])]
        album_df = self.df[self.df[self.tr('album')].isin([keyword])]
        # 将上面结果合并、去重
        df = pd.concat([title_df, artist_df, album_df]).drop_duplicates()
        self.update_table(0, 0, df)
