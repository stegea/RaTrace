import numpy as np
import math
from utils import varia
from utils.varia import mm, µm, X, Y
from utils import geometry
from utils.configuration_class import config
from display import display_class

IAS_min   = 0.15
IAS_width = 25
IAS_slope = 12


class ImagerClass(display_class.DisplayClass):
    def __init__(self, p0=np.array([0, 0]), n0=np.array([-1, 0]), length=10 * mm, pixel_size=100*µm, is_active=True, is_visible=True):
        self.pixel_size = pixel_size

        # Instantiate the display class
        super().__init__(p0=p0, n0=n0, length=length, is_active=is_active, is_visible=is_visible)
        self.name = 'Imager'

        # pts_1D   0   3   6   9  12  15   --> PHYSICAL distances of pixel boundaries ALONG the imager. Each pixel has a width of 3, so the imager has a total length of 15
        # t_1D     0  0.2 0.4 0.6 0.8  1   --> PROPORTIONAL distances of pixel boundaries ALONG the imager, with a total length of 1
        #          |   |   |   |   |   |
        #          |---|---|---|---|---|
        # i          0   1   2   3   4     --> Pixel indices, with a total number of 15/3=5
        #            |   |   |   |   |
        # pt0_1D   1.5 4.5 7.5 10.5 13.5   --> PHYSICAL distances of pixel centers ALONG the imager, which are in the middle of the pixel boundaries

        # Derived parameters & reset
        self.nr_of_pixels = int(np.floor(self.length / self.pixel_size))

        # The N pixel indices, between 0 and N-1
        self.px_i  = np.arange(self.nr_of_pixels)

        # The N+1 pixel boundaries in 2D coordinates 
        self.px_pts_2D = np.zeros((2, self.nr_of_pixels + 1))   # pixel boundaries
        self.px_pts_2D[X] = np.linspace(self.pts[0][X], self.pts[1][X], self.nr_of_pixels+1, endpoint=True)    # The pixel boundaries in 2D coordinates
        self.px_pts_2D[Y] = np.linspace(self.pts[0][Y], self.pts[1][Y], self.nr_of_pixels+1, endpoint=True)

        # The N pixel centers in 2D coordinates
        self.px_pt0_2D = np.zeros((2, self.nr_of_pixels))       # pixel centers
        self.px_pt0_2D[X] = (self.px_pts_2D[X][:-1] + self.px_pts_2D[X][1:]) / 2                                         # The pixel centers in 2D coordinates
        self.px_pt0_2D[Y] = (self.px_pts_2D[Y][:-1] + self.px_pts_2D[Y][1:]) / 2

        # The N pixel centers in 1D coordinates along the imager, between s_px/2 and length-s_px/2
        self.px_x0_1D  = np.linspace(self.pixel_size/2, self.length-self.pixel_size/2, self.nr_of_pixels, endpoint=True)    # The pixel centers, in relative coordinates along the imager, between 

        self.reset()

    def reset(self):
        # Initializing the image, i.e. the result from the impact points
        self.intensity = np.zeros((self.nr_of_pixels,))
        self.phase     = np.zeros((self.nr_of_pixels,))
        self.E         = np.zeros((self.nr_of_pixels,))
        self.img_2D    = np.zeros((10,self.nr_of_pixels,))
        self.COG_x_1D  = np.empty(1)
        self.COG_2D    = np.empty(2)

        super().reset()

    def i_from_x_rel(self, x_1D):
        i = (np.floor(x_1D/self.length*self.nr_of_pixels)).astype(int)
        return np.clip(i, 0, self.nr_of_pixels - 1)     # For the extreme case (x_1D==self.length), in which case i would be equal to self.nr_of_pixels, which is out of bounds, so we set it to the last pixel index

    # TODO: image_multiplicator implementation, is now 1
    # Process the cast rays, i.e. calculate the intensity and phase of the image, and the COG of the image, from the impact points
    def process_image(self):
        E_tot = 0

        # -------------- IMPORTANT NOTE ----------------------------------------------------------------------------------------
        # THE FOLLOWING ONLY WORKS FOR MONOCHROMATIC LIGHT, BECAUSE THE TEMPORAL PHASE INTEGRATION IS NOT TAKEN INTO ACCOUNT.
        # 2 POLYCHROMATIC BEAMS WILL NORMALLY NOT INTERFERE, BUT THAT IS THUS NOT TAKEN INTO ACCOUNT INTO THIS IMPLEMENTATION.
        # ALL RAYS WILL INTERFERE WITH EACH OTHER, WHEN THE "use_phase_information" OPTION IS ENABLED IN THE CONFIG FILE OR UI.
        # ----------------------------------------------------------------------------------------------------------------------

        # Loop over the impact points, and add the complex electric field of each impact point to the corresponding pixel
        for i_pt in range(self.nr_of_IPs):
            # imager_pixel_ID = int(np.round(ray.p1_element_rel*(self.nr_of_pixels - 1)))  # The rays belongs to, or is cast into a pixel with this ID
            incoming_intensity = self.IP_intensity[i_pt] * self.calculate_imager_angular_sensitivity(-self.IP_r[i_pt])  # Minus direction because the ray comes in the opposite direction of the imager normal
            
            # Retrieve the phase information of the ray, if the use_phase_information option is enabled in the config file, otherwise set it to 0
            if  config.getboolean('simulation', 'use_phase_information'):
                phase = self.IP_phase[i_pt]  # Treat all light as coherent and monochromatic, taking into account the ray's phase, so we can do interference calculations
            else:
                phase = 0                    # Ignore the ray's phases, treating all light decoherently
            
            # Calculate the complex electric field of the ray, which is a complex number whose magnitude corresponds to the square root of the intensity
            # and whose angle corresponds to the phase of the ray, and add it to the complex electric field of the pixel
            E_ray = np.sqrt(incoming_intensity) * np.exp(1j * np.array(phase))

            # The ray is cast into a pixel with the following index:
            i_px = self.i_from_x_rel(self.IP_pts_1D[i_pt])  
            self.E[i_px] += E_ray    # Add all complex intensities to each pixel

        # Transfer pixel intensity values into a 1D-array
        for i_px in range(self.nr_of_pixels):
            # The intensity of the pixel is the square of the magnitude of the complex electric field, and the phase is the angle of that field
            self.intensity[i_px] = np.abs(  self.E[i_px]) ** 2
            self.phase[i_px]     = np.angle(self.E[i_px])

        # For better visual interpretation, make a 2D image
        self.img_2D = np.tile(self.intensity, (10, 1))

        self.process_results()

    def process_results(self):
        # Calculate the peak intensity
        self.peak_intensity   = np.max(self.intensity)

        # Masking the image above a certain intensity threshold
        self.peak_cutoff_threshold = 0.00 * self.peak_intensity  # The intensity threshold for background removal
        self.intensity_masked = np.copy(self.intensity)
        self.intensity_masked[self.intensity_masked < self.peak_cutoff_threshold] = 0.0  # Background-substracted image
        self.summed_intensity_masked = np.sum(self.intensity_masked)

        # Center-of-gravity (or COG) of the pulse, along the imager.
        # Suppose the intensities are centered at the pixel centers, then the COG is the weighted average of the pixel centers and intensity of each pixel
        self.COG_x_1D = np.dot(self.intensity_masked, self.px_x0_1D) / self.summed_intensity_masked

        # The COG expressed in absolute 2D coordinates
        fraction = self.COG_x_1D / self.length  # Fraction of the total imager length the COG is positioned
        pts = varia.sort_x_left_to_right(self.pts)  # Sort the imager points in +X order because it might be inverted, corrupting the following calculation
        self.COG_2D[X] = pts[0,X] + fraction * (pts[1,X] - pts[0,X])  # Position of the COG in world frame coordinates
        self.COG_2D[Y] = pts[0,Y] + fraction * (pts[1,Y] - pts[0,Y])

        # Calculating the FWHM of the intensity distribution, expressed in absolute coordinates along the imager, and the corresponding points at which the FWHM is reached
        [self.pulse_width, self.pulse_pts] = varia.calculate_width_of_pulse(self.intensity, threshold_rel=0.5, x=self.px_x0_1D)
        print(f'COG_x_1D: {self.COG_x_1D:.3f}mm, pulse_width: {self.pulse_width:.3f}mm, pulse_pts: {self.pulse_pts}')

    def calculate_imager_angular_sensitivity(self, r, verbose=False):
        # Empirical formula that approximates the experimental results, see screenshot from Matlab simulation
        # Also, see report:  " REP - LS - SG18003 VITA5000 imager efficiency vs incident angle.docx "
        # TODO: Pre-compute the erf-function

        r = geometry.normalize(r)
        angle = geometry.angle_between_vectors(self.n0, r) * 180 / math.pi
        multiplicator = 1
        # multiplicator = (1 / 2) * ((1 + IAS_min) + (1 - IAS_min) * math.erf((-angle + IAS_width) / IAS_slope))
        return multiplicator

    # def plot_imager_efficiency_map(self, p, scale=1, col='black'):
    #     print("Plotting imager efficiency map")
    #
    #     angle_normal = misc.angle_from_vector(self.n)
    #     self.efficiency_map_angle = np.arange(angle_normal + 90 * deg, angle_normal - 90 * deg, -1 * deg)
    #     self.efficiency_map_points = np.zeros((len(self.efficiency_map_angle), 2))
    #     self.efficiency_map = np.zeros((len(self.efficiency_map_angle, )))
    #
    #     for i_angle in range(len(self.efficiency_map_angle)):
    #         angle = self.efficiency_map_angle[i_angle]
    #         V = np.array([np.cos(angle), np.sin(angle)])
    #         self.efficiency_map[i_angle] = self.calculate_imager_angular_sensitivity(V, verbose=False)
    #         self.efficiency_map_points[i_angle, X] = p[X] + V[X] * scale * self.efficiency_map[i_angle]
    #         self.efficiency_map_points[i_angle, Y] = p[Y] + V[Y] * scale * self.efficiency_map[i_angle]
    #     plt.plot(self.efficiency_map_points[:, X], self.efficiency_map_points[:, Y], color=col, linewidth=2)
    #     return

    def __str__(self):
        txt = f'Imager --> Element ID={self.ID}, p0={self.p0}, n0={self.n0}, length={self.length}, pixel size={self.pixel_size}, number of pixels={self.nr_of_pixels}'
        return txt

    def plot(self, graph):
        super().plot(graph)
        if config.getboolean('view', 'show_pixels'):

            # Plot the pixel boundaries
            dn = self.pixel_size/2 * self.n0
            for i_px in range(self.nr_of_pixels + 1):
                graph.plot(self.px_pts_2D[X][i_px]+dn[X]*np.array([-1,1]), self.px_pts_2D[Y][i_px]+dn[Y]*np.array([-1,1]), color='g', linewidth=1)

            # Plot the start, middle and end of the imager
            graph.scatter(self.px_pts_2D[X][0],   self.px_pts_2D[Y][0],   s=20, facecolor='g', marker='o')
            graph.scatter(self.px_pts_2D[X][-1],  self.px_pts_2D[Y][-1],  s=20, facecolor='g', marker='o')
            graph.scatter(self.p0[X],             self.p0[Y],             s=20, facecolor='g', marker='o')

            # Plot the positions of the start, middle and end of the imager
            graph.text(self.px_pts_2D[X][0]  - 0.2*self.n0[X], self.px_pts_2D[Y][0]  - 0.2*self.n0[Y],  f'pixel 0: p=[{self.px_pts_2D[X][0]:.3f}, {self.px_pts_2D[Y][0]:.3f}]', color='g', horizontalalignment='left', verticalalignment='center', fontsize=8)
            graph.text(self.p0[X]            - 0.2*self.n0[X], self.p0[Y]            - 0.2*self.n0[Y],  f'pixel {self.nr_of_pixels/2-1}: p=[{self.p0[X]:.3f}, {self.p0[Y]:.3f}]', color='g', horizontalalignment='left', verticalalignment='center', fontsize=8)
            graph.text(self.px_pts_2D[X][-1] - 0.2*self.n0[X], self.px_pts_2D[Y][-1] - 0.2*self.n0[Y],  f'pixel {self.nr_of_pixels-1}: p=[{self.px_pts_2D[X][-1]:.3f}, {self.px_pts_2D[Y][-1]:.3f}]', color='g', horizontalalignment='left', verticalalignment='center', fontsize=8)

