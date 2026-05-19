from utils.configuration_class import config

import numpy as np
from utils import varia
from utils.varia import mm
from utils.optics import N_glass
from utils import geometry
from elements import glass_element_class
import matplotlib.pyplot as plt


class GlassParallelPlateClass(glass_element_class.GlassElementClass):
    def __init__(self, p0=np.array([0,0]), n0=np.array([-1,0]), thickness=1*mm, length=10*mm, N=N_glass, generate_reflections=True, is_active=True, is_visible=True):
        self.thickness = thickness
        self.length = length

        pts = geometry.construct_plate(p0=p0, n=n0, thickness=thickness, length=length)
        super().__init__(p0=p0, n0=n0, pts=pts, N=N, is_active=is_active, is_visible=is_visible, generate_reflections=generate_reflections)
        self.name = 'glass parallel plate'

    def __str__(self):
        s = f'Glass parallel plate --> ID= {self.ID}, p0={self.p0}, n0={self.n0}, thickness={self.thickness}, length={self.length}, N={self.N}, nr_of_points={self.nr_of_pts}'
        return s

    def plot(self, graph):
        if self.is_visible:
            if config.getboolean('view', 'plot_elements_in_BW'):
                facecolor = 'none'
                edgecolor = 'black'
                edgealpha = 1
            else:
                facecolor = 'cyan'
                edgecolor = 'blue'
                edgealpha = 0.2
            poly_face = plt.Polygon(self.pts, closed=True, facecolor=facecolor, edgecolor='none', alpha=varia.alpha_from_N(self.N), zorder=0)
            poly_edge = plt.Polygon(self.pts, closed=True, fill=False, edgecolor=edgecolor, linewidth=1, alpha=edgealpha, zorder=0)
            graph.add_patch(poly_face)
            graph.add_patch(poly_edge)
            super().plot(graph)