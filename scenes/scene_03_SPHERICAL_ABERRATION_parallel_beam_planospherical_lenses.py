from utils.varia import mm, nm
from utils.material import N_glass
from light import plane_source_class
from elements import plano_spherical_lens_class, black_plate_class

# =========================================================================================================================================================================
# To observe caustics caused by secondary reflections, enable "Generate reflected rays in the simulation tab", and uncomment the beamdump_back in the load_scene function,
# which will catch all rays that are reflected back to the left. You might have to play with the intensity scaler in the view tab, in order to bring out the colors properly
# Because reflected rays are much less intense than the main rays. For the same reason, disable "Intensity-coded ray colors" in the same view tab.
# Some nice results can be obtained with the following settings: 
#   nr_of_rays = 1000
#   items_are_ordered = 0
#   generate_reflections = 1
#   max_number_of_reflections = 1
#   intensity_coded_colors = 0
#   intensity_scaler = 0.05
#   show_noncolliding_rays = 0
#   plot_elements_in_bw = 0
#   black_background = 1
#   show_axis_and_grid = 0
# =========================================================================================================================================================================


def load_scene():
    beam0 = plane_source_class.PlaneSourceClass(p0=[5, 6], n0=[1,0], diameter=8*mm, wavelength=450*nm, intensity_distribution='equidistant', plot_color=(1,0,0,0.5))
    lens0 = plano_spherical_lens_class.PlanoSphericalLensClass(p0=[10, 6], n0=[-1,0], f=15*mm, diameter=10*mm, thickness=3*mm, N=N_glass, plot_resolution=0.1)

    beam1 = plane_source_class.PlaneSourceClass(p0=[5, -6], n0=[1,0], diameter=8*mm, wavelength=450*nm, intensity_distribution='equidistant', plot_color=(1,0,0,0.5))
    lens1 = plano_spherical_lens_class.PlanoSphericalLensClass(p0=[10+3, -6], n0=[1,0], f=15*mm, diameter=10*mm, thickness=3*mm, N=N_glass, plot_resolution=0.1)
    
    # These beam dumps catch the rays exiting the lens on the right and caustic rays at the left, making them visible in the plot
    # They themselves are not plotted, because of the is_visible=False parameter
    beamdumpR  = black_plate_class.BlackPlateClass(p0=[30, 0], n0=[-1,0], length=25 * mm, thickness=0.5*mm, is_visible=False) 
    beamdumpL1 = black_plate_class.BlackPlateClass(p0=[0,  6], n0=[ 1,0], length=10 * mm, thickness=0.5*mm, is_visible=False) 
    beamdumpL2 = black_plate_class.BlackPlateClass(p0=[0, -6], n0=[ 1,0], length=10 * mm, thickness=0.5*mm, is_visible=False) 
    
    info = ('Spherical aberration of a plano-spherical lens, illuminated with a plane source.')

    return [beam0, lens0, beam1, lens1, beamdumpR, beamdumpL1, beamdumpL2, info]
