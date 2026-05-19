from utils.varia import mm, nm
from light import plane_source_class
from elements import spherical_lens_class
from display import display_class

def load_scene():
    beam_red   = plane_source_class.PlaneSourceClass(p0=[-20,0.0], n0=[ 1,0], diameter=20*mm, wavelength=660*nm, intensity_distribution='equidistant', plot_color='wavelength')
    beam_green = plane_source_class.PlaneSourceClass(p0=[-20,0.2], n0=[ 1,0], diameter=20*mm, wavelength=520*nm, intensity_distribution='equidistant', plot_color='wavelength')
    beam_blue  = plane_source_class.PlaneSourceClass(p0=[-20,0.4], n0=[ 1,0], diameter=20*mm, wavelength=450*nm, intensity_distribution='equidistant', plot_color='wavelength')
    lens = spherical_lens_class.SphericalLensClass ( p0=[  0,0.0], n0=[-1,0], thickness=5*mm, f=40*mm, diameter=25 * mm, N=[1.7, 0.05])
    display = display_class.DisplayClass(            p0=[ 35,0.0], n0=[-1,0], length=20 * mm)

    info = ('Chromatic aberration with single lens')

    return [beam_red, beam_green, beam_blue, lens, display, info]
