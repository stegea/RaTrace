import numpy as np
from typing import NamedTuple


from utils import varia
from utils.varia import mm, X, Y
from utils import geometry
from utils.configuration_class import config
from elements import element_class

IAS_min   = 0.15
IAS_width = 25
IAS_slope = 12



class DisplayClass(element_class.ElementClass):
    nr_of_displays = 0

    def __init__(self, p0=np.array([0,0]), n0=np.array([-1,0]), length=10*mm, is_active=True, is_visible=True):
        # Basic parameters
        self.length = length
        self.name = 'Display'

        # Derived parameters
        r = geometry.orientation_from_normal(n0)
        pts = geometry.points_from_position_direction_length(p0, r, self.length, symmetric=True, sort_left_to_right=False)

        DisplayClass.reset(self)
        super().__init__(p0=p0, n0=n0,  pts=pts, is_active=is_active, is_visible=is_visible)
        DisplayClass.nr_of_displays += 1

    def reset(self):
        # # We need to temporarily add cast rays to a list  the ray to the list of rays cast onto the imager, because the raytrace_ray function adds ray information only after the check_collision function
        # self.cast_rays = list()
        
        # The indices of impact_points in the list correspond to the light source ID, 
        # so that impact_points[0] contains the list of impact points of rays originating from light source with ID=0, etc.
        self.impact_points_per_source : list[ImpactPoints] = []
        
    def check_collision(self, ray):
        if not self.is_active:
            return [None, None, None]
    
        # Calculate intersection between the 2-pt lens line and pt-and-rico ray line
        [p, t0, t1] = geometry.intersection_of_PP_line_with_PR_line(p00=self.pts[0], p01=self.pts[1], p10=ray.p0, r1=ray.r)
    
        # If the ray does not hit the imager in forward direction, return none
        if t0 > 1 or t0 < 0 or t1 < 0:  # t0<0: p lies before line segment | t0>1: p lies behind the line segment | t1<0: p lies in the backward direction of the ray
            return [None, None, None]
        
        return [p, t1, t0]

    def propagate_ray(self, ray):
        # # Add the ray to the list of rays cast onto the imager, because the raytrace_ray function adds ray information only after the propagate_ray function
        # self.cast_rays.append(ray)
        
        # Get the ray's lightsource ID, to trace from which source it originates
        lightsource_ID = ray.lightsource_ID

        # If it's the first time we encounter this light source ID, we first need to add 
        # an empty list of impact points to the list, so that we can store the impact points
        # of rays originating from this light source in the correct index of the list
        if len(self.impact_points_per_source) < lightsource_ID+1:
            self.impact_points_per_source.append(ImpactPoints(x=[], col=[], ID=[], phase=[]))

        # self.impact_points_per_source[lightsource_ID].add_point()

        self.impact_points_per_source[lightsource_ID].ID.append(ray.ID)
        self.impact_points_per_source[lightsource_ID].x.append(ray.p1_element_rel * self.length)
        self.impact_points_per_source[lightsource_ID].phase.append(ray.phase_end) 
    
        # In case of one single ray simulated, this results in a list or so --> STILL TO DEBUG !!!
        col = ray.plot_color
        if isinstance(col, list):
            col = ray.plot_color[0]
        col = varia.load_colormap(color=col ,N_rays=1, wavelength=ray.wavelength)

        self.impact_points_per_source[lightsource_ID].col.append(col[0])
    
        return

    def collect_cast_rays(self):
        print('start collecting ray impact points')
        # self.cast_rays_x     = np.empty(len(self.cast_rays))        # Position of a ray onto the display, in mm from the start of the display
        # self.cast_rays_col   = np.empty((len(self.cast_rays),4))    # Color array of the cast rays
        # self.cast_rays_ID    = np.empty(len(self.cast_rays))        # The ID list of cast rays
        # self.cast_rays_phase = np.empty(len(self.cast_rays))        # A list of ray phases

        for i_cast_ray in range(len(self.cast_rays)):
            lightsource_ID = self.cast_rays[i_cast_ray].lightsource_ID

            # self.impact_points[lightsource_ID].ID.append(self.cast_rays[i_cast_ray].ID)
            # self.impact_points[lightsource_ID].x.append(self.cast_rays[i_cast_ray].p1_element_rel * self.length)
            # self.impact_points[lightsource_ID].phase.append(self.cast_rays[i_cast_ray].phase_end)
            # self.cast_rays_ID[i_cast_ray]       = self.cast_rays[i_cast_ray].ID
            # self.cast_rays_x[i_cast_ray]        = self.cast_rays[i_cast_ray].p1_element_rel * self.length
            # self.cast_rays_phase[i_cast_ray]    = self.cast_rays[i_cast_ray].phase_end

            # In the originating cast ray, store its ID and cast position onto the display
            self.cast_rays[i_cast_ray].display_ID = self.ID
            self.cast_rays[i_cast_ray].display_x  = self.cast_rays[i_cast_ray].p1_element_rel * self.length

            # In case of one single ray simulated, this results in a list or so --> STILL TO DEBUG !!!
            col = self.cast_rays[i_cast_ray].plot_color
            if isinstance(col, list):
                col = col[0]
            col = varia.load_colormap(color=col ,N_rays=1, wavelength=self.cast_rays[i_cast_ray].wavelength)
            # self.source_impact_points[lightsource_ID].col.append(col[0])
            # self.cast_rays_col[i_cast_ray] = col[0]

            if len(self.source_impact_points) < lightsource_ID+1:  # Add a set of impact points to the list
                self.source_impact_points.append(ImpactPoints(x=[], col=[], ID=[], phase=[]))

            self.source_impact_points[lightsource_ID].add_point(x=self.cast_rays[i_cast_ray].display_x,
                                                                phase=self.cast_rays[i_cast_ray].phase_end,
                                                                ID=self.cast_rays[i_cast_ray].ID,
                                                                col=col)

        print('end of processing')

    def process_rays(self):
        pass

    def __str__(self):
        txt = f'Display --> Element ID={self.ID}, p0={self.p0}, n0={self.n0}, length={self.length}'
        return txt

    def plot(self, graph):
        if self.is_visible:
            graph.plot([self.pts[0,X], self.pts[1,X]], [self.pts[0,Y], self.pts[1,Y]], color='green', linewidth=2)
            if config.getboolean('view', 'show_elements_properties'):
                graph.scatter(self.p0[X], self.p0[Y], s=10, facecolor='g')
                p_txt = self.p0 - self.n0*0.5
                graph.text(p_txt[X], p_txt[Y], f'{self.name} {self.ID}', color='green', horizontalalignment='left', verticalalignment='bottom', fontsize=10, rotation=0)
            super().plot(graph)



# NamedTuple makes it a lightweight tuple-like data container where each position also has a name, making it easier to access the data. 
# This means that members can be accessed both by name and by index, e.g. SIP.x or SIP[0] will give you the same list of x positions.
# The immutability of NamedTuple means that once an instance is created, its fields cannot be modified.
# NamedTuple itself is immutable, so you cannot reassign sip.x. 
# But in this case sip.x is a list, and the list contents are still mutable, so you can modify the list
# (e.g., by appending new points) without changing the reference to the list itself.
class ImpactPoints(NamedTuple):
    x: list
    col: list
    ID: list
    phase: list

    @property
    def nr_of_points(self):
        return len(self.x)

    def add_point(self, x=None, col=None, ID=None, phase=None):
        self.x.append(x)
        self.ID.append(ID)
        self.col.append(col)
        self.phase.append(phase)
