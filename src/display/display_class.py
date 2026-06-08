import numpy as np
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
        if DisplayClass.nr_of_displays > 0:
            raise Exception(f'Maximally 1 display supported for the moment.')
        
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
        # We add cast rays to a list first, because the raytrace_ray function adds ray information only after the check_collision function
        self.cast_rays = list()
        self.nr_of_IPs = None

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
        # Add the ray to the list of rays cast onto the imager, because the raytrace_ray function adds ray information only after the propagate_ray function
        self.cast_rays.append(ray)
      
        return

    def process_cast_rays(self):
        # Retrieve the impact point (IP) information from the cast rays
        self.IP_pts             = np.array([ray.p1                           for ray in self.cast_rays])   # The 2D coordinates of the IPs, which are the points where the rays hit the display
        self.IP_pts_1D          = np.array([ray.p1_element_rel * self.length for ray in self.cast_rays])   # The 1D position of the impact point along the display, in absolute coordinates, between 0 and the length of the display
        self.IP_t_1D            = np.array([ray.p1_element_rel               for ray in self.cast_rays])   # The 1D scalar between 0 and 1, representing the position of the impact point along the display, relative to the start of the display
        self.IP_phase           = np.array([ray.phase_end                    for ray in self.cast_rays])
        self.IP_intensity       = np.array([ray.intensity                    for ray in self.cast_rays])
        self.IP_r               = np.array([ray.r                            for ray in self.cast_rays])
        self.IP_col             = np.array([ray.plot_color                   for ray in self.cast_rays])
        self.IP_ray_ID          = np.array([ray.ID                           for ray in self.cast_rays])
        self.IP_lightsource_ID  = np.array([ray.lightsource_ID               for ray in self.cast_rays])

        self.nr_of_IPs          = len(self.IP_pts_1D)
        self.nr_of_lightsources = 0   if   (self.nr_of_IPs == 0)   else   max(self.IP_lightsource_ID)+1

        print('End of processing cast rays on the display. Number of impact points: ', self.nr_of_IPs)

    def i_of_IPs_for_lightsource(self, lightsource_ID):
        return [i for i, ID in enumerate(self.IP_lightsource_ID) if ID == lightsource_ID]
  
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



# # NamedTuple makes it a lightweight tuple-like data container where each position also has a name, making it easier to access the data. 
# # This means that members can be accessed both by name and by index, e.g. SIP.x or SIP[0] will give you the same list of x positions.
# # The immutability of NamedTuple means that once an instance is created, its fields cannot be modified.
# # NamedTuple itself is immutable, so you cannot reassign sip.x. 
# # But in this case sip.x is a list, and the list contents are still mutable, so you can modify the list
# # (e.g., by appending new points) without changing the reference to the list itself.
# class ImpactPointsClass(NamedTuple):
#     x_rel: list              
#     t_rel: list              
#     pts_abs: list              
#     phase: list          
#     intensity: list      
#     r: list
#     col: list            
#     ID: list             
#     lightsource_ID: list 

#     @property
#     def nr_of_points(self):
#         return len(self.x_rel)

#     @property
#     def nr_of_lightsources(self):
#         return max(self.lightsource_ID)+1

#     def ind_lightsource(self, lightsource_ID):
#         return [ind for ind, ID in enumerate(self.lightsource_ID) if ID == lightsource_ID]
