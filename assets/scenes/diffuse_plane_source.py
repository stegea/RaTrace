import numpy as np
import os, sys
sys.path.append(os.path.abspath('..'))

from utils.varia import mm, deg, nm
from light import diffuse_plane_source_class
from elements import black_plate_class


def load_scene(param=None):

    source = diffuse_plane_source_class.DiffusePlaneSourceClass(p0=np.array([ 0,  0]), n0=np.array([1,0]), diameter=10*mm, fan_angle=20*deg, wavelength=450*nm, intensity=1, plot_color='wavelength')
    beamdump = black_plate_class.BlackPlateClass( p0=np.array([20,  0]), n0=np.array([-1,0]), length=100*mm, is_visible=False)

    info = 'Diffuse plane sources'
    
    return [source, beamdump, info]
