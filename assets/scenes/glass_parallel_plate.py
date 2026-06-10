from utils.varia import mm, nm
from light import plane_source_class
from elements import glass_parallel_plate_class, black_plate_class

def load_scene():
    fan_beam  = plane_source_class.PlaneSourceClass(p0=[-20, 0], n0=[1,0], wavelength=450*nm, diameter=10*mm, intensity_distribution='equidistant')
    glass_plate = glass_parallel_plate_class.GlassParallelPlateClass(p0=[0,-2], n0=[-1,-1], thickness=10*mm, length=30*mm, N=1.5)
    beam_dump = black_plate_class.BlackPlateClass(p0=[30, 0], n0=[-1,0], length=20 * mm, thickness=0.1 * mm, is_visible=False)
    info = ('Glass parallel plate')
    return [fan_beam, glass_plate, beam_dump, info]
