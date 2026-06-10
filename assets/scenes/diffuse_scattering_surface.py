from utils.varia import mm, nm, deg
from light import point_source_class
from elements import diffuse_plate_class, black_plate_class

# =========================================================================================================================================================================
# In order to make the diffuse scattering visible, start with one single ray, play with the view-parameters to be able to clearly see the diffusely scattered rays.
# Since the intensity of the diffusely scattered rays is very low, the intensity_scaler should be quite high. The following parameters work quite well:
# Diffuse surface --> Kd=1, Ks=2, alpha=100, nr_of_scattered_rays=1000
# Simulation --> Nr of rays=1
# View --> Nr of plotted rays=20000, Intensity scaler=100000, Intensity-coded ray colors=True
# =========================================================================================================================================================================

def load_scene():
    light = point_source_class.PointSourceClass(p0=[-8,-4.1], n0=[8,4.1], fan_angle=5*deg, intensity=1000, wavelength=660*nm)
    surface = diffuse_plate_class.DiffusePlateClass(p0=[0,0], n0=[-1,0], length=1 * mm, thickness=0.1*mm, Kd=1, Ks=2, alpha=100, nr_of_scattered_rays=1000, n_light=-light.n0)
    beam_dump = black_plate_class.BlackPlateClass(p0=[-10,0], n0=[1,0], length=50*mm, thickness=1*mm, is_visible=False)
    info = 'Diffusely scattering surface'
    return [light, surface, beam_dump, info]