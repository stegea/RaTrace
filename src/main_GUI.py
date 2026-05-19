from PyQt5 import QtWidgets
import sys
import os
from utils.configuration_class import config
from raytracer import simulation_class
from gui import splash
from gui import simulation_gui_class


app = QtWidgets.QApplication(sys.argv)
splash.show_splash(app)

simulation = simulation_class.SimulationClass()

simulation_GUI = simulation_gui_class.SimulationGuiClass(simulation)
simulation_GUI.show()

if config.getboolean('scenes', 'load_scene_at_startup'):
    scenes_folder = config.resolve_path(config.get('scenes', 'scenes_folder'))
    scene_file = os.path.join(scenes_folder, config.get('scenes', 'scene_file'))
    simulation.load_scene(scene_file)

sys.exit(app.exec_())

