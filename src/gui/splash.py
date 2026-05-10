import os
import time
from PyQt5 import QtGui, QtWidgets
from utils.configuration_class import config


ANIMATION_TIME = config.getfloat('view', 'splash_screen_transition')
STEP = 0.01
HOLD_TIME = 1.0


def _get_splash_pixmap():
    base_dir = os.path.dirname(__file__)
    image_path = os.path.abspath(os.path.join(base_dir, '..', '..', 'assets', 'RaTrace_large.png'))
    return QtGui.QPixmap(image_path)


def show_splash(app):
    if ANIMATION_TIME==0:
        return
        
    splash_pix = _get_splash_pixmap()
    splash = QtWidgets.QSplashScreen(splash_pix)

    opaqueness = 0.0
    splash.setWindowOpacity(opaqueness)
    splash.show()
    app.processEvents()

    while opaqueness < 1.0:
        splash.setWindowOpacity(opaqueness)
        app.processEvents()
        time.sleep(STEP)
        opaqueness += STEP / max(ANIMATION_TIME, STEP)

    splash.setWindowOpacity(1.0)
    app.processEvents()
    time.sleep(HOLD_TIME)
    splash.close()
    app.processEvents()
