from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, QMainWindow, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

import logging
import sys
logging.basicConfig(level=logging.DEBUG)
import signal

from tandyberg.controller import Controller

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.controller = Controller('COM5')

        self.setWindowTitle('Tandberg Controller')

        wid = QWidget(self)
        self.setCentralWidget(wid)
        self.mainGridLayout = QGridLayout()
        wid.setLayout(self.mainGridLayout)

        self.mainGridLayout.addWidget(self.__getNavButtons(), 0, 0)
        self.mainGridLayout.addWidget(self.__getZoomButtons(), 0, 1)

        self.controller.autofocus('on')

    def __getZoomButtons(self):
        zoomButtonWidget = QWidget()
        buttonGridLayout = QGridLayout()
        zoomButtonWidget.setLayout(buttonGridLayout)
        buttonList = [
            'in',
            'out'
        ]
        v = 0
        zoomButtons = {}
        for buttonName in buttonList:
            zoomButtons[buttonName] = QPushButton()
            zoomButtons[buttonName].setText(buttonName)
            zoomButtons[buttonName].pressed.connect(self.controller.getZoomFunc(buttonName))
            zoomButtons[buttonName].released.connect(self.controller.stopZoom)
            buttonGridLayout.addWidget(zoomButtons[buttonName], v, 0)

            v += 1
        
        return zoomButtonWidget
        

    def __getNavButtons(self):
        navButtonWidget = QWidget()
        buttonGridLayout = QGridLayout()
        navButtonWidget.setLayout(buttonGridLayout)
        buttonList = {
            'up': (0,1),
            'left': (1,0),
            'right': (1,2),
            'down': (2, 1)
        }
        h = 0
        v = 0
        navButtons = {}
        for buttonName, buttonPos in buttonList.items():
            navButtons[buttonName] = QPushButton()
            navButtons[buttonName].setText(buttonName)
            navButtons[buttonName].pressed.connect(self.controller.getSteerFunc(buttonName))
            navButtons[buttonName].released.connect(self.controller.stopSteer)
            buttonGridLayout.addWidget(navButtons[buttonName], buttonPos[0], buttonPos[1])
            h += 1
            if h > 2:
                h = 0
                v += 1
            if h == 1 and v == 1:
                # Skip the middle spot
                h += 1
        
        return navButtonWidget

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())