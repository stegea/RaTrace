from utils.varia import mm
from light import plane_source_class
from elements import semi_transparent_mirror_class, black_plate_class


def load_scene():
    light = plane_source_class.PlaneSourceClass(p0=[-30,0], n0=[1,0], diameter=5*mm)
    mirror = semi_transparent_mirror_class.SemiTransparentMirrorClass(p0=[0,0], n0=[-1,-1], length=10*mm, transmission=0.5)
    beam_dump_1 = black_plate_class.BlackPlateClass(p0=[10,0], n0=[-1,0], length=10 * mm, thickness=0.5 * mm)
    beam_dump_2 = black_plate_class.BlackPlateClass(p0=[0,-10], n0=[0,1], length=10 * mm, thickness=0.5 * mm)
    info = 'Semitransparent mirror'
    return [light, mirror, beam_dump_1, beam_dump_2, info]   
    