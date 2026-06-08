from utils.varia import mm,nm, deg
from utils.material import N_glass
from light import point_source_class
from elements import ideal_thin_lens_class, black_plate_class

def load_scene():
    light = point_source_class.PointSourceClass(p0=[-15, 0], n0=[1,0], wavelength=660*nm, fan_angle=30*deg)
    lens = ideal_thin_lens_class.IdealThinLensClass(p0=[0, 0],  n0=[-1,0], f=10*mm, diameter=10*mm, N=N_glass)
    beam_dump = black_plate_class.BlackPlateClass(p0=[30, 0], n0=[-1,0], length=10*mm, thickness=0.1*mm)
    info = 'Ideal lens projecting a point source'
    return [light, lens, beam_dump, info]
