import numpy as np
import os, sys
sys.path.append(os.path.abspath('..'))

from utils.varia import mm, deg, nm
from light import plane_source_class
from elements import black_plate_class


def load_scene(param=None):

    source1 = plane_source_class.PlaneSourceClass(p0=np.array([ 0,  0]), n0=np.array([1,0]),   diameter=3*mm, angle= 0*deg, wavelength=450*nm, intensity=1, intensity_distribution='equidistant',    plot_color='wavelength')
    source2 = plane_source_class.PlaneSourceClass(p0=np.array([11,  0]), n0=np.array([1,0]),   diameter=3*mm, angle= 0*deg, wavelength=450*nm, intensity=1, intensity_distribution='random',         plot_color='wavelength')

    source3 = plane_source_class.PlaneSourceClass(p0=np.array([ 0,-7]),  n0=np.array([1,0]),   diameter=3*mm, angle= 0*deg, wavelength=450*nm, intensity=1, intensity_distribution='gaussian',       plot_color='wavelength')
    source4 = plane_source_class.PlaneSourceClass(p0=np.array([11,-7]),  n0=np.array([1,0]),   diameter=3*mm, angle= 0*deg, wavelength=450*nm, intensity=1, intensity_distribution='gaussianrandom', plot_color='wavelength')

    source5 = plane_source_class.PlaneSourceClass(p0=np.array([ 0,-15]), n0=np.array([1,0.1]), diameter=3*mm, angle= 0*deg, wavelength=450*nm, intensity=1, intensity_distribution='equidistant',    plot_color='wavelength')
    source6 = plane_source_class.PlaneSourceClass(p0=np.array([11,-15]), n0=np.array([1,0.0]), diameter=3*mm, angle=10*deg, wavelength=450*nm, intensity=1, intensity_distribution='equidistant',    plot_color='wavelength')

    beamdump1 = black_plate_class.BlackPlateClass( p0=np.array([10,  0]), n0=np.array([-1,0]), length=100*mm, is_visible=False)
    beamdump2 = black_plate_class.BlackPlateClass( p0=np.array([21,  0]), n0=np.array([-1,0]), length=100*mm, is_visible=False)

    info = 'Plane sources'
   
    return [source1, source2, source3, source4, source5, source6, beamdump1, beamdump2, info]
