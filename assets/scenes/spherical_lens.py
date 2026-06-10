from utils.varia import mm,nm
from utils.material import N_glass
from light import plane_source_class
from elements import spherical_lens_class, black_plate_class

def load_scene():
    light = plane_source_class.PlaneSourceClass(p0=[0, 0], n0=[1,0], wavelength=450*nm, diameter=3*mm, intensity_distribution='equidistant')
    lens_concave = spherical_lens_class.SphericalLensClass(p0=[5, 0],  n0=[-1,0], f=-5*mm, diameter= 6*mm, thickness=1.0*mm, N=N_glass, material=None, plot_resolution=0.1, generate_reflections=True)
    lens_convex = spherical_lens_class.SphericalLensClass(p0=[11.8, 0],  n0=[ 1,0], f=10*mm, diameter=8*mm, thickness=2.5*mm, N=N_glass, material=None, plot_resolution=0.1, generate_reflections=True)
    beam_dump = black_plate_class.BlackPlateClass(p0=[50, 0], n0=[-1,0], length=10*mm, thickness=0.1*mm)
    info = 'Spherical lenses'
    return [light, lens_concave, lens_convex, beam_dump, info]
