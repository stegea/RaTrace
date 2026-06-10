from utils.varia import mm,nm, deg
from utils.material import N_glass
from light import plane_source_class
from elements import ideal_thin_lens_class, black_plate_class

def load_scene():
    light = plane_source_class.PlaneSourceClass(p0=[0, 0], n0=[1,0], wavelength=450*nm, diameter=4*mm, intensity_distribution='equidistant')
    lens_concave = ideal_thin_lens_class.IdealThinLensClass(p0=[5, 0],  n0=[-1,0], f=-5*mm, diameter=10*mm, N=N_glass)
    lens_convex = ideal_thin_lens_class.IdealThinLensClass(p0=[10, 0],  n0=[1,0], f=10*mm, diameter=10*mm, N=N_glass)
    beam_dump = black_plate_class.BlackPlateClass(p0=[50, 0], n0=[-1,0], length=10*mm, thickness=0.1*mm)
    info = 'Ideal thin lenses'
    return [light, lens_concave, lens_convex, beam_dump, info]
