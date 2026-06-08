from utils.varia import mm, nm, µm, deg
from utils.material import N_glass
from light import plane_source_class
from elements import spherical_lens_class
from display import imager_class

def load_scene():
    beam1 = plane_source_class.PlaneSourceClass(p0=[-10, 0], n0=[1,0.0], diameter=10*mm, angle= 0*deg, wavelength=660*nm, intensity_distribution='random', plot_color=(1,0,0,1))
    beam2 = plane_source_class.PlaneSourceClass(p0=[-10,-4], n0=[1,0.0], diameter=10*mm, angle=15*deg, wavelength=660*nm, intensity_distribution='random', plot_color=(0,1,0,1))
    lens = spherical_lens_class.SphericalLensClass(p0=[0, 0], n0=[-1,0], f=20*mm, diameter=18*mm, thickness=5*mm, N=N_glass)
    imager = imager_class.ImagerClass(p0=[23.25, 4], n0=[-1,0], length=10 * mm, pixel_size=1*µm)
    info = ('Coma in off-axis beams, with imager')
    return [beam1, beam2, lens, imager, info]
