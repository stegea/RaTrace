from utils.varia import mm,nm, deg
from utils.material import N_glass
from light import point_source_class
from elements import black_plate_class

def load_scene():
    light = point_source_class.PointSourceClass(p0=[0, 0], n0=[1,0], wavelength=450*nm, fan_angle=45*deg, intensity_distribution='equiangular')
    plate1 = black_plate_class.BlackPlateClass(p0=[20, 5], n0=[-0.05,-1], length=40*mm, thickness=1*mm, plot_color='lightgray')
    plate2 = black_plate_class.BlackPlateClass(p0=[35, 3], n0=[-1,0],    length= 5*mm, thickness=1*mm, plot_color='grey')
    plate3 = black_plate_class.BlackPlateClass(p0=[20,-5], n0=[-0.05,1],  length=40*mm, thickness=1*mm, plot_color='darkgray')
    info = 'Black plate'
    return [light, plate1, plate2, plate3, info]
