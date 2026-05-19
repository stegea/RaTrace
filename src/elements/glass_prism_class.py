from utils.configuration_class import config

import numpy as np
from utils.varia import mm, deg
from utils import varia
from utils.optics import N_glass
from utils import geometry
from elements import glass_element_class
import matplotlib.pyplot as plt


class GlassPrismIsoscelesClass(glass_element_class.GlassElementClass):
    def __init__(self, p0=np.array([0,0]), n0=np.array([1,1]), angle=90*deg, length=10*mm, N=N_glass, generate_reflections=True, is_active=True, is_visible=True):
        self.angle = angle
        self.length = length
        self.N = N

        n0 = geometry.normalize(n0)
        r = geometry.orientation_from_normal(n0)
        pts = np.empty((0, 2))
        pts = np.append(pts, [p0 + r *length/2],                                  axis=0)
        pts = np.append(pts, [p0 - n0*length/2 * np.tan((180*deg-angle)/2)], axis=0)
        pts = np.append(pts, [p0 - r *length/2],                                  axis=0)

        super().__init__(p0=p0, n0=n0, pts=pts, N=N, generate_reflections=generate_reflections, is_active=is_active, is_visible=is_visible)
        self.name = 'Isosceles prism'

    def __str__(self):
        txt = 'Isosceles prism'
        return txt

    def plot(self, graph):
        if self.is_visible:
            poly_face = plt.Polygon(self.pts, closed=True, facecolor='cyan', edgecolor='none', alpha=varia.alpha_from_N(self.N), zorder=0)
            poly_edge = plt.Polygon(self.pts, closed=True, fill=False, edgecolor='blue', linewidth=1, alpha=0.2, zorder=0)
            graph.add_patch(poly_face)
            graph.add_patch(poly_edge)
            super().plot(graph)
            # if config.getboolean('view', 'show_elements_properties'):
            #     canvas_class.plot_normals(graph, self)

class GlassPrismRectangularClass(glass_element_class.GlassElementClass):
    def __init__(self, p0=np.array([0,0]), n0=np.array([0,-1]), angle=45*deg, length=10*mm, N=N_glass, generate_reflections=False, is_active=True, is_visible=True):
        self.angle = angle
        self.length = length
        self.N = N

        n0 = geometry.normalize(n0)
        r = geometry.orientation_from_normal(n0)
        pts = np.empty((0, 2))
        pts = np.append(pts, [p0],                                      axis=0)
        pts = np.append(pts, [p0 - n0 * length * np.tan(90*deg-angle)], axis=0)
        pts = np.append(pts, [p0 - r *length],                          axis=0)

        super().__init__(p0=p0, n0=n0, pts=pts, N=N, generate_reflections=generate_reflections, is_active=is_active, is_visible=is_visible)
        self.name = 'Rectangular prism'

    def __str__(self):
        txt = 'Rectangular prism'
        return txt

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
            # if config.getboolean('view', 'show_elements_properties'):
            #     canvas_class.plot_normals(graph, self)