from utils.varia import mm,nm, deg
from utils.material import N_glass
from light import plane_source_class, point_source_class
from elements import black_plate_class, aperture_class

def load_scene():
    light1 = plane_source_class.PlaneSourceClass(p0=[5, 0], n0=[1,0], wavelength=450*nm, diameter=10*mm, intensity_distribution='equidistant')
    light2 = point_source_class.PointSourceClass(p0=[5, -8], n0=[1,0.5], wavelength=660*nm, fan_angle=30*deg, intensity_distribution='equiangular')
    aperture = aperture_class.ApertureClass(p0=[20,0], n0=[-1,0], diameter_inner=5*mm, diameter_outer=15*mm)
    beamdump = black_plate_class.BlackPlateClass(p0=[30,0], n0=[-1,0],  length=100*mm, thickness=1*mm, is_visible=False)
    info = 'Aperture'
    return [light1, light2, aperture, beamdump, info]
