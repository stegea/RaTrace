import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
from utils.configuration_class import config
from display import imager_class

PLOT_COLOR_BLACK = 'grey'
MAX_NR_OF_SCATTERPOINTS_PLOTTED = 100000
rng = np.random.default_rng()

# Assign random values to the random_angle array once, to ensure that the same random angles are used for all polar plots, to avoid the points jumping around when switching between graph types
random_angle = 2 * np.pi * np.random.random(MAX_NR_OF_SCATTERPOINTS_PLOTTED)


class CanvasClass(FigureCanvasQTAgg):

    def __init__(self, simulation=None, width=5, height=4, dpi=100):
        self.simulation = simulation
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.graph = fig.add_subplot(111)
        super().__init__(fig)
        fig.subplots_adjust(left=0.055, right=0.99, bottom=0.03, top=0.99)
        self.axis_lims = []

    def set_nr_of_rays_to_plot(self, value):
        self.nr_of_rays_to_plot = value

    def clear(self):
        if config.getboolean('scenes', 'reset_axis_after_loading_scene'):
            self.axis_lims = []

    def update_entire_scene(self):
        # Store the current axis limits before plotting, to set again later on
        if self.axis_lims:
            self.axis_lims = self.graph.axis()

        # Clear the figure and plot all the items
        self.update_items()

        # Set the correct axis limits
        if not self.axis_lims:
            self.axis_lims = self.graph.axis()
        self.graph.axis(self.axis_lims)

        # Set the background to black if required
        col = 'black'   if    config.getboolean('view','black_background')    else    'white'
        self.graph.set_facecolor(col)

        # Some graph aesthetics
        SHOW_AXIS_AND_GRID = config.getboolean('view', 'show_axis_and_grid')
        # self.graph.grid(visible=SHOW_AXIS_AND_GRID, alpha=0.2*SHOW_AXIS_AND_GRID, which='both')
        self.graph.grid(alpha=0.2*SHOW_AXIS_AND_GRID, which='both')
        self.graph.tick_params(axis='both', which='both', bottom=SHOW_AXIS_AND_GRID, top=SHOW_AXIS_AND_GRID, left=SHOW_AXIS_AND_GRID, right=SHOW_AXIS_AND_GRID)
        self.graph.tick_params(axis='both', which='both', labelbottom=SHOW_AXIS_AND_GRID, labelleft=SHOW_AXIS_AND_GRID)
        self.graph.spines['top'].set_visible(SHOW_AXIS_AND_GRID)
        self.graph.spines['right'].set_visible(SHOW_AXIS_AND_GRID)
        self.graph.spines['bottom'].set_visible(SHOW_AXIS_AND_GRID)
        self.graph.spines['left'].set_visible(SHOW_AXIS_AND_GRID)
        self.draw()

    def update_items(self):
        self.graph.cla()
        for source in self.simulation.sources:
            source.plot(self.graph)
        for element in self.simulation.elements:
            element.plot(self.graph)
        for display in self.simulation.displays:
            display.plot(self.graph)
        self.graph.axis('equal')
        self.draw()


class CanvasDisplayClass(FigureCanvasQTAgg):
    def __init__(self, simulation=None, width=5, height=4, dpi=100):
        self.simulation = simulation
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.graph = fig.add_subplot(111)
        super().__init__(fig)
        fig.subplots_adjust(left=0.15, right=0.99, bottom=0.10, top=0.99)
        self.greyscale_mode = False
        self.zoom_on_centroid = True

    def update_graphs(self, graph_type_ind):
        for display in self.simulation.displays:
            self.update_graph(display=display, graph_type_ind=graph_type_ind)

    def update_graph(self, display, graph_type_ind):
        self.graph.cla()
        self.xlims, self.ylims = np.array([0, 1]),  np.array([0, 1])

        # if not hasattr(display, 'impact_points') or display.impact_points is None:
        if display.nr_of_IPs is None:
            print('No impact points to plot on the display graph')
            return

        display_is_imager = isinstance(display, imager_class.ImagerClass)

        size_pts = 100/np.power(display.nr_of_IPs, 0.3)
        if config.getboolean('view', 'intensity_coded_colors'):
            alpha    = 1/np.power(display.nr_of_IPs, 0.3)
        else:
            alpha    = 1
        alpha = min(alpha*config.getfloat('view', 'intensity_scaler'), 1)

        # TODO plot impact points in graph types 0 and 1 with intensity-coded colors
        if graph_type_ind == 0:     
            if display.nr_of_IPs <= MAX_NR_OF_SCATTERPOINTS_PLOTTED:
                print(f'Scatterplot 1D: Plotting the impact points as points on the X-axis, with the Y-coordinate being 0')
                lightsource_separation = 0.1
                self.graph.scatter(display.IP_pts_1D, np.zeros_like(display.IP_pts_1D) + lightsource_separation * display.IP_lightsource_ID, s=size_pts, c=display.IP_col, edgecolors=None, linewidths=0, alpha=alpha)
                self.ylims = display.nr_of_lightsources * (lightsource_separation-1) * np.array([-0.5,1.0])
                if self.zoom_on_centroid and display_is_imager and display.pulse_width is not None:
                    self.xlims = display.COG_x_1D + 2 * display.pulse_width * np.array([-1, 1])
                else:
                    self.xlims = np.array([0, display.length])                    
                self.graph.tick_params(axis='x', which='both', top=False, bottom=config.getboolean('view', 'show_axis_and_grid'))
                self.graph.grid(config.getboolean('view', 'show_axis_and_grid'), which='both', axis='x')
                self.graph.set_yticks([])
                self.graph.set_aspect('auto')

        elif graph_type_ind == 1:   # Scatterplot 2D: Plot the impact points as points on the X-axis, but spread out randomly along the Y-axis, to better visualize the distribution of the impact points along the X-axis 
            if display.nr_of_IPs <= MAX_NR_OF_SCATTERPOINTS_PLOTTED:
                print(f'Scatterplot 2D: Plotting the impact points as points on the X-axis, but spread out randomly along the Y-axis')
                random_y_array = 0.5 + np.random.random(size=display.IP_pts_1D.shape)
                self.graph.scatter(display.IP_pts_1D, random_y_array, s=size_pts, c=display.IP_col, edgecolors=None, linewidths=0, alpha=alpha)
                self.ylims = np.array([0, 2])
                if self.zoom_on_centroid and display_is_imager and display.pulse_width is not None:
                    self.xlims = display.COG_x_1D + 2 * display.pulse_width * np.array([-1, 1])
                else:
                    self.xlims = np.array([0, display.length])
                self.graph.grid(config.getboolean('view', 'show_axis_and_grid'), which='both', axis='x')
                self.graph.set_yticks([])
                self.graph.set_aspect('auto')

        elif graph_type_ind == 2:   # Polar plot: Plot the impact points on a polar plot, with the radius corresponding to the X-coordinate of the impact point and the angle being random, to spread out the points in a circular manner
            if display.nr_of_IPs <= MAX_NR_OF_SCATTERPOINTS_PLOTTED:
                print(f'Polar plot: Plotting the impact points on a polar plot')
                for i_lightsource in range(display.nr_of_lightsources):
                    i_of_IPs_for_lightsource = display.i_of_IPs_for_lightsource(i_lightsource)
                    x_array = display.IP_pts_1D[i_of_IPs_for_lightsource]
                    x0 = display.COG_x_1D if display_is_imager else np.median(x_array)
                    x_polar = x0 + (x_array-x0) * np.cos(random_angle[range(x_array.shape[0])])
                    y_polar =  0 + (x_array-x0) * np.sin(random_angle[range(x_array.shape[0])])
                    self.graph.scatter(x_polar, y_polar, s=size_pts, c=display.IP_col[i_of_IPs_for_lightsource], edgecolors=None, linewidths=0, alpha=alpha)
                if display_is_imager and display.pulse_width is not None:
                    self.graph.plot(x0 + display.pulse_width/2 * np.cos(np.linspace(0, 2*np.pi, 360)), display.pulse_width/2 * np.sin(np.linspace(0, 2*np.pi, 360)), marker='none', color='black', linestyle='--', linewidth=1)
                if self.zoom_on_centroid and display_is_imager and display.pulse_width is not None:
                    self.xlims = x0 + 1 * display.pulse_width * np.array([-1, 1])
                    self.ylims =  0 + 1 * display.pulse_width * np.array([-1, 1])
                else:
                    self.xlims = [np.min(x_polar), np.max(x_polar)]
                    self.ylims = [np.min(y_polar), np.max(y_polar)]
                self.graph.grid(config.getboolean('view', 'show_axis_and_grid'), which='both', axis='x')
                self.graph.set_aspect('equal', adjustable='datalim')

        elif graph_type_ind == 3  and  display_is_imager:
            print(f'Intensity plot 1D: Plotting the intensity of the pixels in a I-vs-X plot')
            x_mm  = display.px_x0_1D
            self.graph.plot(x_mm, display.intensity, color='blue', marker='.', linestyle='-', linewidth=1, markersize=4)
            self.xlims = np.array([0, display.length])
            self.ylims = np.array([0, 1.1 * display.peak_intensity])
            self.graph.grid(config.getboolean('view', 'show_axis_and_grid'), which='both')
            self.graph.plot(np.array([point[0] for point in display.pulse_pts]), np.array([point[1] for point in display.pulse_pts]), marker='o', markersize=10, markerfacecolor='black', markeredgecolor='none', linestyle='--', color='black', linewidth=1, label='FWHM points')
            if self.zoom_on_centroid and display_is_imager and display.pulse_width is not None:
                self.xlims = display.COG_x_1D + 2 * display.pulse_width * np.array([-1, 1])
            else:
                self.xlims = np.array([0, display.length])
            self.graph.set_aspect('auto')

        elif graph_type_ind == 4  and  display_is_imager:
            print(f'# Intensity plot 2D: Plotting the intensity of the pixels in a 2D colormap plot')
            cmap = 'gray' if self.greyscale_mode else 'jet'
            self.graph.imshow(display.img_2D, cmap=cmap, aspect='auto', origin='lower', extent=[0, display.length, 0, display.img_2D.shape[0]], vmin=0, vmax=display.peak_intensity)
            self.graph.tick_params(axis='x', which='both', top=False, bottom=config.getboolean('view', 'show_axis_and_grid'))
            self.xlims = np.array([0, display.length])
            self.ylims = np.array([0, display.img_2D.shape[0]])
            if self.zoom_on_centroid and display_is_imager and display.pulse_width is not None:
                self.xlims = display.COG_x_1D + 2 * display.pulse_width * np.array([-1, 1])
            else:
                self.xlims = np.array([0, display.length])
            self.graph.set_aspect('auto')

        # elif graph_type_ind == 5:   # Phase plot: Plot the phase of the pixels in a phase-vs-X plot
        #     if len(display.cast_rays) <= np.inf + MAX_NR_OF_SCATTERPOINTS_PLOTTED:
        #         size_pts = 100 / np.sqrt(len(display.cast_rays))
        #         self.graph.scatter(display.cast_rays_x, display.cast_rays_phase, s=size_pts, c=display.cast_rays_col)
        #         self.graph.scatter(display.pixels_x + display.pixel_size/2, display.phase, s=10+0*size_pts, facecolor=(1,1,1,0), edgecolor=(0,0,0,1), marker='o')
        #         self.xlims = np.array([0, display.length])
        #         self.ylims = np.array([-np.pi, np.pi])
        #         self.graph.tick_params(axis='x', which='both', top=False, bottom=config.getboolean('view', 'show_axis_and_grid'))
        #         self.graph.grid(config.getboolean('view', 'show_axis_and_grid'), which='both', axis='x')

        self.graph.set_xlim(self.xlims)
        self.graph.set_ylim(self.ylims)

        self.draw()
        print('Display graph updated')
