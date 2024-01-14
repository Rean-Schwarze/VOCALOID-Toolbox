import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTranslator, QLocale
from PyQt5.QtGui import QIcon, QColor, QPixmap
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import FluentTranslator, SplitFluentWindow, NavigationItemPosition, \
    MessageBox, setThemeColor

from common.config import cfg
from view.bpm_key_finder_interface import BPMKeyFinderInterface
from view.lyric_interface import LyricInterface
from view.metronome_interface import MetronomeInterface
from view.scale_interface import ScaleInterface
from view.setting_interface import SettingInterface


class Window(SplitFluentWindow):

    def __init__(self):
        super().__init__()

        # create sub interface
        self.BPMKeyFinderInterface = BPMKeyFinderInterface(self)
        self.MetronomeInterface = MetronomeInterface(self)
        self.LyricInterface = LyricInterface(self)
        self.ScaleInterface = ScaleInterface(self)
        self.settingInterface = SettingInterface(parent=self)

        # initialization
        self.initNavigation()
        self.initWindow()

        self.setMaximumSize(960, 540)
        self.setAcceptDrops(True)

        setThemeColor(QColor(120, 226, 27))

    # 根据当前主题是浅色还是深色模式获取不同自定义icon
    def get_icon_by_theme_mode(self):
        theme = cfg.get(cfg.themeMode.value)
        lyric_icon = QIcon(QPixmap('resources/icon/document_light.svg'))
        scale_icon = QIcon(QPixmap('resources/icon/Piano-Keyboard_light.svg'))
        if theme == 'Dark':
            lyric_icon = QIcon(QPixmap('resources/icon/document_dark.svg'))
            scale_icon = QIcon(QPixmap('resources/icon/Piano-Keyboard_dark.svg'))
        return {'lyric_icon': lyric_icon, 'scale_icon': scale_icon}  # 返回一个dict封装icon

    # 设置导航栏中图标在主题模式变化时改变
    def set_navigation_tree_widget_icon(self):
        icon_dict = self.get_icon_by_theme_mode()
        self.navigationInterface.panel.items['LyricInterface'].widget.setIcon(icon_dict['lyric_icon'])
        self.navigationInterface.panel.items['ScaleInterface'].widget.setIcon(icon_dict['scale_icon'])

    # 初始化导航栏
    def initNavigation(self):
        # add sub interface
        self.addSubInterface(self.BPMKeyFinderInterface, FIF.MUSIC, self.tr('BPM、调性检测'))
        self.addSubInterface(self.MetronomeInterface, FIF.SPEED_HIGH, self.tr('节拍器BPM'))
        # 获取自定义icon
        icon_dict = self.get_icon_by_theme_mode()
        lyric_icon = icon_dict['lyric_icon']
        scale_icon = icon_dict['scale_icon']
        self.addSubInterface(self.LyricInterface, lyric_icon, self.tr('获取歌词'))
        self.addSubInterface(self.ScaleInterface, scale_icon, self.tr('音阶查看'))
        self.addSubInterface(
            self.settingInterface, FIF.SETTING, self.tr('设置'), NavigationItemPosition.BOTTOM)

        self.navigationInterface.addItem(
            routeKey='info',
            icon=FIF.INFO,
            text=self.tr('关于软件'),
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM,
        )
        self.navigationInterface.setExpandWidth(200)

    def initWindow(self):
        self.resize(960, 540)
        self.setWindowIcon(QIcon('resources/icon/logo.png'))
        self.setWindowTitle(self.tr('术力口工具箱'))

        # 显示在屏幕中央
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def showMessageBox(self):
        w = MessageBox(
            self.tr('关于软件'),
            self.tr(
                '作者（含logo设计）：Rean\n\n提示：\n在系统设置（以Windows11为例）-个性化-颜色-关闭“在标题栏和窗口边框上显示强调色”\n以获得更好体验'),
            self
        )
        w.yesButton.setText(self.tr('确定'))
        w.cancelButton.setText(self.tr('取消'))
        if w.exec():
            w.yesButton.setText(self.tr('确定'))


if __name__ == "__main__":
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QtWidgets.QApplication(sys.argv)

    # internationalization
    locale = cfg.get(cfg.language).value
    if cfg.get(cfg.language).name == 'AUTO' and locale.name() == 'zh_CN':
        locale = QLocale(QLocale.Chinese, QLocale.China)
    directory = "resources/i18n"

    fluentTranslator = FluentTranslator(locale)
    settingTranslator = QTranslator()
    settingTranslator.load(locale, "settings", ".", directory)
    finderTranslator = QTranslator()
    finderTranslator.load(locale, 'finder', '.', directory)
    finder_ui_Translator = QTranslator()
    finder_ui_Translator.load(locale, 'UI_BPMKeyFinderInterface', '_', directory)
    metronome_ui_Translator = QTranslator()
    metronome_ui_Translator.load(locale, 'UI_MetronomeInterface', '_', directory)
    lyric_Translator = QTranslator()
    lyric_Translator.load(locale, 'lyric_interface', '_', directory)
    lyric_ui_Translator = QTranslator()
    lyric_ui_Translator.load(locale, 'UI_LyricInterface', '_', directory)
    scale_Translator = QTranslator()
    scale_Translator.load(locale, 'scale_interface', '_', directory)
    scale_ui_Translator = QTranslator()
    scale_ui_Translator.load(locale, 'UI_ScaleInterface', '_', directory)
    main_Translator = QTranslator()
    main_Translator.load(locale, 'main', '_', directory)

    app.installTranslator(fluentTranslator)
    app.installTranslator(settingTranslator)
    app.installTranslator(finderTranslator)
    app.installTranslator(finder_ui_Translator)
    app.installTranslator(metronome_ui_Translator)
    app.installTranslator(lyric_Translator)
    app.installTranslator(lyric_ui_Translator)
    app.installTranslator(scale_Translator)
    app.installTranslator(scale_ui_Translator)
    app.installTranslator(main_Translator)

    w = Window()
    w.show()
    sys.exit(app.exec_())
