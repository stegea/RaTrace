from utils.varia import mm, nm, deg
from light import point_source_class
from elements import diffuse_plate_class, black_plate_class

# =========================================================================================================================================================================
# In order to make the diffuse scattering visible, start with one single ray, play with the view-parameters to be able to clearly see the diffusely scattered rays.
# Since the intensity of the diffusely scattered rays is very low, the intensity_scaler should be quite high.
# =========================================================================================================================================================================

def load_scene():
    light = point_source_class.PointSourceClass(p0=[-8,-5], n0=[1,0.61], fan_angle=5*deg, wavelength=660*nm)
    surface = diffuse_plate_class.DiffusePlateClass(p0=[0,0], n0=[-1,0], length=20 * mm, thickness=1 * mm, Kd=1, Ks=2, alpha=100, nr_of_scattered_rays=100, n_light=-light.n0)
    beam_dump = black_plate_class.BlackPlateClass(p0=[-10,0], n0=[1,0], length=1000*mm, is_visible=False)
    info = 'Diffusely scattering surface'
    return [light, surface, beam_dump, info]