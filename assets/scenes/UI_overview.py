from utils.varia import mm,nm, deg
from utils.material import
from light import point_source_class
from elements import spherical_lens_class, black_plate_class

def load_scene():
    light = point_source_class.PointSourceClass(p0=[0, 0], n0=[1,0], wavelength=660*nm, fan_angle=30*deg)
    lens = spherical_lens_class.SphericalLensClass(p0=[16, 0],  n0=[-1,0], f=11*mm, diameter=12*mm, thickness=3*mm,N=1.7)
    beam_dump = black_plate_class.BlackPlateClass(p0=[50, 0], n0=[-1,0], length=10*mm, thickness=0.1*mm)
    info = 'Ideal lens projecting a point source'
    return [light, lens, beam_dump, info]
