import numpy as np
import os, sys
sys.path.append(os.path.abspath('..'))

from utils.varia import mm, deg, nm, µm
from light import plane_source_class
from display import imager_class

def load_scene(param=None):

    source = plane_source_class.PlaneSourceClass(p0=np.array([0,0]),  n0=np.array([1,0]), diameter=3*mm, angle= 0*deg, wavelength=450*nm, intensity=1, intensity_distribution='gaussianrandom', plot_color='wavelength')
    display = imager_class.ImagerClass( p0=np.array([10, 0]), n0=np.array([-1,0]), length=10*mm, pixel_size=100*µm, is_visible=True, is_active=True)

    info = 'Imager'
   
    return [source, display, info]
