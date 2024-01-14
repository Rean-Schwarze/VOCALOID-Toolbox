# coding:utf-8
import os
import shutil

from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QFileDialog
from qfluentwidgets import FluentIcon as FIF, HyperlinkCard
from qfluentwidgets import InfoBar
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, OptionsSettingCard, PushSettingCard,
                            PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, CustomColorSettingCard,
                            setTheme, setThemeColor, RangeSettingCard, MessageBox)

from common.config import cfg, AUTHOR, VERSION, YEAR, isWin11, HELP_URL, FEEDBACK_URL
from common.signal_bus import signalBus


class SettingInterface(ScrollArea):
    """ Setting interface """

    checkUpdateSig = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.set_navigation_tree_widget_icon=parent.set_navigation_tree_widget_icon
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.basicGroup = SettingCardGroup(
            self.tr("Basic Setting"), self.scrollWidget)
        # self.musicFolderCard = FolderListSettingCard(
        #     cfg.musicFolders,
        #     self.tr("Local music library"),
        #     directory=QStandardPaths.writableLocation(
        #         QStandardPaths.MusicLocation),
        #     parent=self.basicGroup
        # )
        self.dataFolderCard = PushSettingCard(
            self.tr('Choose folder'),
            FIF.FOLDER,
            self.tr("data directory"),
            cfg.get(cfg.dataFolder),
            self.basicGroup
        )
        self.auto_save_Card = ComboBoxSettingCard(
            cfg.auto_save_time,
            FIF.STOP_WATCH,
            self.tr('Auto Save Time'),
            self.tr('Decide the auto save time of BPM&key detected\'s result'),
            texts=['30s', '1min', '3min', '5min', '10min', '15min', '20min', '25min', '30min'],
            parent=self.basicGroup
        )

        # personalization
        self.personalGroup = SettingCardGroup(
            self.tr('Personalization'), self.scrollWidget)
        # self.micaCard = SwitchSettingCard(
        #     FIF.TRANSPARENT,
        #     self.tr('Mica effect'),
        #     self.tr('Apply semi transparent to windows and surfaces'),
        #     cfg.micaEnabled,
        #     self.personalGroup
        # )
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr('Application theme'),
            self.tr("Change the appearance of your application"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personalGroup
        )
        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            self.tr('Theme color'),
            self.tr('Change the theme color of you application'),
            self.personalGroup
        )
        # self.zoomCard = OptionsSettingCard(
        #     cfg.dpiScale,
        #     FIF.ZOOM,
        #     self.tr("Interface zoom"),
        #     self.tr("Change the size of widgets and fonts"),
        #     texts=[
        #         "100%", "125%", "150%", "175%", "200%",
        #         self.tr("Use system setting")
        #     ],
        #     parent=self.personalGroup
        # )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            texts=['简体中文', 'English', self.tr('Use system setting')],
            parent=self.personalGroup
        )

        # # material
        # self.materialGroup = SettingCardGroup(
        #     self.tr('Material'), self.scrollWidget)
        # self.blurRadiusCard = RangeSettingCard(
        #     cfg.blurRadius,
        #     FIF.ALBUM,
        #     self.tr('Acrylic blur radius'),
        #     self.tr('The greater the radius, the more blurred the image'),
        #     self.materialGroup
        # )

        # update software
        # self.updateSoftwareGroup = SettingCardGroup(
        #     self.tr("Software update"), self.scrollWidget)
        # self.updateOnStartUpCard = SwitchSettingCard(
        #     FIF.UPDATE,
        #     self.tr('Check for updates when the application starts'),
        #     self.tr('The new version will be more stable and have more features'),
        #     configItem=cfg.checkUpdateAtStartUp,
        #     parent=self.updateSoftwareGroup
        # )

        # application
        self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)
        self.helpCard = HyperlinkCard(
            HELP_URL,
            self.tr('Open help page'),
            FIF.HELP,
            self.tr('Help'),
            self.tr(
                'Discover new features and learn useful tips'),
            self.aboutGroup
        )
        self.feedbackCard = PrimaryPushSettingCard(
            self.tr('Provide feedback'),
            FIF.FEEDBACK,
            self.tr('Provide feedback'),
            self.tr('Help us improve by providing feedback'),
            self.aboutGroup
        )
        self.aboutCard = PrimaryPushSettingCard(
            self.tr('Check update'),
            FIF.INFO,
            self.tr('About'),
            '© ' + self.tr('Copyright') + f" {YEAR}, {AUTHOR}. " +
            self.tr('Version') + " " + VERSION,
            self.aboutGroup
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(900, 575)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')
        self.setStyleSheet('background:transparent')

        # initialize style sheet
        self.scrollWidget.setObjectName('scrollWidget')
        # self.settingLabel.setObjectName('settingLabel')

        # self.micaCard.setEnabled(isWin11())

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        # self.settingLabel.move(36, 30)

        # add cards to group
        # self.basicGroup.addSettingCard(self.musicFolderCard)
        self.basicGroup.addSettingCard(self.dataFolderCard)
        self.basicGroup.addSettingCard(self.auto_save_Card)

        # self.personalGroup.addSettingCard(self.micaCard)
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        # self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)

        # self.materialGroup.addSettingCard(self.blurRadiusCard)

        # self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)
        #
        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.basicGroup)
        self.expandLayout.addWidget(self.personalGroup)
        # self.expandLayout.addWidget(self.materialGroup)
        # self.expandLayout.addWidget(self.updateSoftwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.success(
            self.tr('Updated successfully'),
            self.tr('Configuration takes effect after restart'),
            duration=1500,
            parent=self
        )

    def move_file(self, old_path, new_path):
        filelist = os.listdir(old_path)  # 列出该目录下的所有文件,listdir返回的文件列表是不包含路径的。
        print(filelist)
        for file in filelist:
            src = os.path.join(old_path, file)
            dst = os.path.join(new_path, file)
            print('src:', src)  # 原文件路径下的文件
            print('dst:', dst)  # 移动到新的路径下的文件
            shutil.move(src, dst)

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

    def __onDataFolderCardClicked(self):
        """ download folder card clicked slot """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), "./")
        if not folder or cfg.get(cfg.dataFolder) == folder:
            return

        self.move_file(cfg.get(cfg.dataFolder), folder)
        self.showMessageBox(self.tr('Hint'), self.tr('Files have been moved to the new folder.'))
        cfg.set(cfg.dataFolder, folder)
        self.dataFolderCard.setContent(folder)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.__showRestartTooltip)

        # data folder
        self.dataFolderCard.clicked.connect(
            self.__onDataFolderCardClicked)

        # personalization
        self.themeCard.optionChanged.connect(lambda ci: setTheme(cfg.get(ci)))
        self.themeCard.optionChanged.connect(self.set_navigation_tree_widget_icon)
        self.themeColorCard.colorChanged.connect(setThemeColor)
        # self.micaCard.checkedChanged.connect(signalBus.micaEnableChanged)

        # about
        self.aboutCard.clicked.connect(self.checkUpdateSig)
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))
