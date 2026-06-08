import numpy as np
from utils import varia
from utils.varia import nm, deg, X, Y
from utils.material import N_air
from light  import light_class
from utils import geometry


class PointSourceClass(light_class.LightSourceClass):

    def __init__(self, p0=np.array([0, 0]), n0=np.array([1, 0]), fan_angle=30*deg, wavelength=660*nm, intensity=1, intensity_distribution='equiangular', plot_color='wavelength'):
        self.fan_angle = fan_angle
        self.intensity_distribution = intensity_distribution

        super().__init__(wavelength=wavelength, p0=p0, n0=n0, intensity=intensity, plot_color=plot_color)
        self.name = 'point source'

    def generate_rays(self, N_rays):
        # First, reset all ray information
        super().reset()

        # Set the number of rays originating from the source
        self.nr_of_original_rays = N_rays

        # Setting the plotting colors
        cols = varia.load_colormap(color=self.plot_color, N_rays=N_rays, wavelength=self.wavelength)

        # Generate the rays according to a given distribution
        if self.intensity_distribution == 'equiangular':
            d_angle_range = np.linspace(-1, 1, N_rays, endpoint=True) * self.fan_angle/2
            d_angle_range = d_angle_range if N_rays>1 else np.array([0])
        elif self.intensity_distribution == 'gaussian':
            (angles, probability_cumsum) = varia.generate_gaussian_pcs(FWHM=self.fan_angle)
            d_angle_range = varia.generate_samples_from_pcs(angles, probability_cumsum, nr_of_samples=N_rays, randomize=False)
            d_angle_range = d_angle_range if N_rays>1 else np.array([0])
        elif self.intensity_distribution == 'gaussianrandom':
            (angles, probability_cumsum) = varia.generate_gaussian_pcs(FWHM=self.fan_angle)
            d_angle_range = varia.generate_samples_from_pcs(angles, probability_cumsum, nr_of_samples=N_rays, randomize=True)
            d_angle_range = d_angle_range if N_rays>1 else np.array([0])
        elif self.intensity_distribution == 'random':
            d_angle_range = (np.random.rand(N_rays) * 2 - 1) * self.fan_angle/2
        else:
            raise ValueError(
                f'Error in PointSourceClass: intensity distribution. '
                f'{self.intensity_distribution!r} not recognized. '
                f'Choose one of: (equiangular, gaussian, gaussianrandom, random).'
            )
        
        d_angle_range = np.sort(d_angle_range)

        main_angle = geometry.angle_from_vector(self.n0)
        for ind in range(len(d_angle_range)):
            angle = main_angle + d_angle_range[ind]
            r = geometry.vector_from_angle(angle)
            intensity = self.intensity/N_rays
            col = cols[round(ind / max([(self.nr_of_original_rays - 1), 1]) * (len(cols) - 1))]
            ray = light_class.RayClass(p0=self.p0, r=r, intensity=intensity, wavelength=self.wavelength, N=N_air, ray_parent=None, source_element=self, lightsource_ID=self.ID, plot_color=col)
            self.add_ray(ray)

    def __str__(self):
        n0_str = varia.format_1D_array(arr=self.n0, fmt='7.4f')
        p0_str = varia.format_1D_array(arr=self.p0, fmt='7.4f')
        txt = f'Point source nr {self.ID+1}/{light_class.LightSourceClass.nr_of_sources} --> ID={self.ID}, p0={p0_str}, n0={n0_str}, nr of rays={self.nr_of_rays}, wavelength={self.wavelength/nm}nm, intensity={self.intensity}, fan angle={self.fan_angle/deg:.2f}°, intensity distribution={self.intensity_distribution}, plot color={self.plot_color}'
        return txt

    def plot(self, graph):
        # Plotting the origin of the source, e.g. a plane, a point, a laser source, ...
        print(f' --> Plotting origin of source {self.ID+1}/{light_class.LightSourceClass.nr_of_sources}')
        col = varia.load_colormap(color=self.plot_color, N_rays=1, wavelength=self.wavelength)
        graph.scatter(self.p0[X], self.p0[Y], c=col, s=10)
        # Plot the rays
        super().plot(graph)

