import numpy as np
import os, sys
sys.path.append(os.path.abspath('..'))

from utils.varia import mm, deg, nm
from light import plane_source_class
from elements import black_plate_class, glass_prism_class


def load_scene(param=None):

    source = plane_source_class.PlaneSourceClass(p0=np.array([2,-8]), n0=np.array([1,-1]), diameter=5*mm, angle= 0*deg, wavelength=450*nm, intensity=1, intensity_distribution='equidistant',    plot_color='wavelength')
    prism1 = glass_prism_class.GlassPrismRectangularClass(p0=np.array([10,-10]), n0=np.array([-1, 1]), angle=35*deg, length=10*mm, N=1.5, generate_reflections=True)
    prism2 = glass_prism_class.GlassPrismIsoscelesClass(p0=np.array([30,-20]), n0=np.array([0,-1]), angle=20*deg, length=5*mm, N=1.8, generate_reflections=False)
    beamdump = black_plate_class.BlackPlateClass( p0=np.array([50,  0]), n0=np.array([-1,0]), length=1000*mm, is_visible=False)

    info = 'Plane sources'
   
    return [source, prism1, prism2, beamdump, info]
