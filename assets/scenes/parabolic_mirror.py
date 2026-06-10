import numpy as np
import os, sys
sys.path.append(os.path.abspath('..'))

from utils.varia import mm, deg, nm
from light import plane_source_class
from elements import black_plate_class, parabolic_mirror_class


def load_scene(param=None):

    source   = plane_source_class.PlaneSourceClass(p0=np.array([0, 0]), n0=np.array([1,0]),   diameter=5*mm, wavelength=450*nm, intensity=1, intensity_distribution='equidistant', plot_color='wavelength')
    mirror = parabolic_mirror_class.ParabolicMirrorClass(p0=np.array([20,0]), n0=np.array([-1, -0.1]), f=20*mm, diameter=10*mm, thickness=1*mm)
    beamdump = black_plate_class.BlackPlateClass(  p0=np.array([0.5,-4]), n0=np.array([1,0]),  length=2*mm, is_visible=False)

    info = 'Plane sources'
   
    return [source, mirror, beamdump, info]
