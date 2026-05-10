from utils.varia import mm, nm
from light import plane_source_class
from elements import black_plate_class, plano_spherical_lens_class


def load_scene():
    source  = plane_source_class.PlaneSourceClass(p0=[0,0], n0=[1,0], wavelength=660*nm, diameter=5*mm, intensity=1, intensity_distribution='equidistant', plot_color='wavelength')
    lens1 = plano_spherical_lens_class.PlanoSphericalLensClass(p0=[ 20,0],  n0=[1,0], R=-30, diameter=25, thickness=5*mm, N=1.7, plot_resolution=1)
    lens2 = plano_spherical_lens_class.PlanoSphericalLensClass(p0=[100,0],  n0=[1,0], R= 30, diameter=25, thickness=5*mm, N=1.7, plot_resolution=1)
    beamdump = black_plate_class.BlackPlateClass(p0=[200,0], n0=[-1,0], length=50, thickness=1*mm)
    info = 'Plano-spherical lenses'
    return [source, lens1, lens2, beamdump, info]
