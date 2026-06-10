import numpy as np
import os, sys
sys.path.append(os.path.abspath('..'))

from utils.varia import mm, deg, nm
from light import plane_source_class
from elements import black_plate_class, semi_transparent_mirror_class, flat_mirror_class


def load_scene(param=None):

    source   = plane_source_class.PlaneSourceClass(p0=np.array([-10,  0]), n0=np.array([1,0]),   diameter=5*mm, wavelength=450*nm, intensity=1, intensity_distribution='equidistant', plot_color='wavelength')
    beamsplitter1 = semi_transparent_mirror_class.SemiTransparentMirrorClass(p0=np.array([10,  0]), n0=np.array([1, 1]), length=10*mm, transmission=0.5)
    mirror1 = flat_mirror_class.FlatMirrorClass(p0=np.array([20,  0]), n0=np.array([-1, -1]), length=10*mm)
    mirror2 = flat_mirror_class.FlatMirrorClass(p0=np.array([10,-10]), n0=np.array([1, 1]), length=10*mm)
    beamsplitter2 = semi_transparent_mirror_class.SemiTransparentMirrorClass(p0=np.array([20,-10]), n0=np.array([1, 1]), length=10*mm, transmission=0.5)
    beamdump = black_plate_class.BlackPlateClass(  p0=np.array([50,-10]), n0=np.array([-1,0]),  length=100*mm, is_visible=False)

    info = 'Plane sources'
   
    return [source, beamsplitter1, beamsplitter2, mirror1, mirror2, beamdump, info]
