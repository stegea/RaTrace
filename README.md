<p align="center">
  <img src="assets/RaTrace_medium.png", alt="RaTrace", width=400, height=400, style="display: block; margin: 0 auto" />
</p>

<p align="center">
  A 2D raytracer with a easy-to-use graphical user interface, written in Python.
</p>

---

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-support%20my%20work-FFDD00?style=flat&labelColor=101010&logo=buy-me-a-coffee&logoColor=white)](https://coff.ee/stelejaci)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

<p><i>!! Disclaimer !! Mind you that this is very much a work-in-progress. This started as a personal hobby project and I never had the intent to release this publicly.
The code is in many places sub-optimal and buggy, but it works for my intent of use. Ok ... most of the time ... in Windows.</i></p>

The information in this README will later be formatted into a Wiki page of this project. But for the time being I'll just put it all in this one extensive document.

---

## Table of contents
* [Overview](#Overview)
* [Usage](#Usage)
* [Examples](#Examples)
* [GUI](#GUI)
* [Syntax](#Syntax)

---

## Overview

<p align="center"> <img src="assets/screenshot_01.png", alt="scene_01_Hello_world", height=600, style="display: block; margin: 0 auto" /> </p>

<b>Implemented features</b>
* GUI for 2D raytracing
* Scene creation via Python scripts
* Simulation of static scenes, with or without UI
* Automated scripts for looped simulations with different scenes
* Exact raytracing for analytically described elements (spherical, parabolic, flat surfaces)
* Accurate raytracing for segments-based, more "complex" elements
* "Fast" raytrace mode for ordered elements or "slow" mode for full raytracing
* Internal & total reflections
* Wavelength dispersion
* Tracking of ray phase information
* Export ray information to a text file
* Color coding rays: wavelength, rainbow, fixed, intensity-scaling
* Support for:
  * Light sources: point source, diffusing plane source, parallel plane source, laser source, virtual rays, double coherent point source
  * Lenses: spherical lens, plano-spherical lens, ideal lens
  * Glass elements: glass slab, prism, biprism
  * Mirrors: flat, parabolic, semi-transparent
  * Surfaces: black absorber, aperture, diffuse scattering plane
  * Targets: display surface, imager

<b>To be implemented features (& priority)</b>
* Lenses: aspherical lens
* Glass elements: sphere, microlens array
* Mirrors: spherical mirror, dichroic mirror
* Light source: B/W image source
* Varia: Bandpass filter
* Better error handling when there is a bug in the scene
* Better plotting of properties
* Diffusely scattering sphere
* A library of glass materials
* Glass dispersion described with Abbe numbers
* Multi-node surfaces instead of simple lines
* Show a list of elements (properties) in the UI
* Edit elements in the UI itself

<b>Known bugs</b>
* First screenshot in looped gui does not set the axis correctly
* Warning concerning colors
* Contact surfaces (e.g. lens doublet) not working
* Crash when selecting an intensity plot in the display tab, when no imager is present 
* Inactive surfaces at the top and bottom of (plano-)spherical lenses
* Many others ...

<p align="center">
  <img src="assets/scene_01_Hello_world_02.png", alt="scene_01_Hello_world", height=300, style="display: block; margin: 0 auto" />
</p>

---

## Usage

Clone the repository:

```sh
git clone https://github.com/stelejaci/RaTrace.git
cd RaTrace
```

Install the dependencies with `uv`:

```sh
uv sync
```

Run RaTrace from the `src` folder:

```sh
cd src
uv run python main_GUI.py
```

Alternatively, use a standard local Python virtual environment:

```sh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
cd src
python main_GUI.py
```

The project is configured for Python 3.12. Dependencies are listed in `pyproject.toml`; `uv sync` also uses `uv.lock`.

### Running
RaTrace can be used in a couple of ways: with or without a GUI, as a single instance, or in a looped environment. 4 example scripts are provided under /src, on how to use RaTrace in these 4 ways:

1. The primary way to use RaTrace is with the GUI. This way most of the settings can be changed, and new scenes can be loaded:

```sh
main_GUI.py
```

2. With a GUI but automated and the possibility for taking screenshots. Each time a simulation in the loop is finished, the GUI closes and the next iteration starts.

```sh
main_GUI_in_loop.py
```

3. Running simulations without a GUI, with the possibility to export ray data to a text file when the simulation is finished.

```sh
main_noGUI.py
```

4. The same GUI-less approach, but running in a loop:

```sh
main_noGUI_in_loop.py
```

When using `uv`, prefix the same commands with `uv run`:

```sh
uv run python main_GUI.py
uv run python main_GUI_in_loop.py
uv run python main_noGUI.py
uv run python main_noGUI_in_loop.py
```

### Config file
The default scene and startup options are set in `src/config.ini`. If the default scene does not load after cloning, check the `[scenes]` section. The `scenes_folder` value can be relative to `src`, such as `..\scenes`, or an absolute path on your machine.

### Scene files

The scenes itself are Python scripts and are dynamically loaded whenever a new scene is loaded. See the next chapter for examples.

---

## Examples

I invite u to browse and try out the different example scenes that are available in the scenes folder.

### Simple on-axis lens
Below you find the content of a very simple scene file. 
First, all the modules used in the scene are imported. Next the ```load_scene``` module must always be present and contains all necessary elements, in this case a point light, an ideal lens and a beam dump to receive the rays:
```
import numpy as np
from utils.varia import mm,nm, deg
from utils.material import N_glass
from light import point_source_class
from elements import ideal_thin_lens_class, black_plate_class

def load_scene():
    light = point_source_class.PointSourceClass(p0=np.array([-15, 0]), n0=np.array([1,0]), wavelength=660*nm, fan_angle=30*deg)
    lens = ideal_thin_lens_class.IdealThinLensClass(p0=np.array([0,0]),  n0=np.array([-1,0]), f=10*mm, diameter=10*mm, N=N_glass)
    beam_dump = black_plate_class.BlackPlateClass(p0=np.array([30, 0]), n0=np.array([-1,0]), length=10*mm)
    info = 'Ideal lens projecting a point source'
    return [light, lens, beam_dump, info]
```

When the simulation is run in the GUI, this results in the following (clipped) screenshot:   

![](scenes/scene_01_SIMPLE_ON_AXIS_LENS_fan_beam_spherical_lens_beamdump.png)

### Chromatic aberration
In this example I ony show what's essential in the load_scene module and skip all boilerplate code before and after this section:
```
beam_red  = plane_source_class.PlaneSourceClass(p0=np.array([-20,0]), n0=np.array([1,0]),  diameter=20*mm, wavelength=660*nm, intensity_distribution='equidistant', plot_color='wavelength')
beam_green = plane_source_class.PlaneSourceClass(p0=np.array([-20,0.2]), n0=np.array([1,0]),  diameter=20*mm, wavelength=520*nm, intensity_distribution='equidistant', plot_color='wavelength')
beam_blue = plane_source_class.PlaneSourceClass(p0=np.array([-20,0.4]), n0=np.array([1,0]),  diameter=20*mm, wavelength=450*nm, intensity_distribution='equidistant', plot_color='wavelength')
lens = spherical_lens_class.SphericalLensClass (p0=np.array([0,  0]), n0=np.array([-1,0]), thickness=5*mm, f=40*mm, diameter=25 * mm, N=[1.7, 0.05])
beam_dump = black_plate_class.BlackPlateClass(  p0=np.array([40, 0]), n0=np.array([-1,0]), length=20 * mm, thickness=1*mm)
```
![](scenes/scene_04_CHROMATIC_ABERRATION_spherical_lens_with_dispersion.png)

### Newtonian telescope
The list of elements in the load_scene module becomes a bit too long to show here, so please look at example 8 in the examples folder for details.

![](scenes/scene_08_NEWTONIAN_TELESCOPE_parabolic_mirror_lenses_display_1.png)

---

## GUI

The GUI has a rather limited number of controls to keep things simple (for now). Most of the controls in the several tabs are self-explanatory, but we will give some clarification nevertheless:

<p align="center">
<img src="assets/UI_Setup.png" alt="UI_Setup.png" height=300/>
<img src="assets/UI_Simulation.png" alt="UI_Simulation.png" height=300/>
<img src="assets/UI_View.png" alt="UI_View.png" height=300/>
<img src="assets/UI_Display.png" alt="UI_Display.png" height=300/>
</p>

### Setup

* <b>Browse / Reload -</b> This tab allow for loading scenes, as well as reloading scenes. The latter is handy when editing a scene file, and quickly viewing the results without the need to push the load-button and browse to the file over and over.
* <b>Start simulation -</b> When a scene is loaded and this checkbox is enabled, the UI immediately starts simulating the scene when loaded. This also quickens the iterative process of scene editing.
* <b>Reset axis -</b> Auto-zooms the scene to the entire scene space when a scene is loaded.
* <b>Model parameters - </b> Shows the editable element parameters from the currently loaded scene in a tree view. Change values directly in the tree and click Apply to reload the scene with the updated model parameters; use the "Start simulation after changing parameters" option to automatically rerun the simulation.

### Simulation

* <b>Number of rays - </b>The number of <u><b>initial</b></u> rays that is generated, per light source. 
* <b>Use phase information - </b>Taking into account the phase information of the rays to generate an interfered image. This is only relevant when using an imager, since then the phase is integrated within the extent of a pixel.
* <b>Items are ordered - </b>When selecting this option, the raytracer checks the elements for collision with the rays in the order that was given in the scene file. If the optical path is "more complex", unselect this checkbox.
* <b>Generate reflected rays - </b>Enables the generation of reflected child rays at refractive interfaces in addition to transmitted rays. When enabled, glass elements can create reflected rays that follow Fresnel reflection rules, and the tracing depth is limited by the "Max nr of reflections" setting.
* <b>Start simulation - </b>you're a smart person, you can figure out what this button does.
* <b>Export ray data - </b>Export all ray data to a structured ascii-file.
* <b>Add timestamp - </b>Add or omit a timestamp to the export file name.

### View

* <b>Number of plotted rays - </b>How much of the initially generated rays that are plotted. If each rays breaks down in multiple child-rays, this can quickly slow down the drawing process. It is advised to start low, and increase the number if required. This number can not be higher than the number of simulated rays.   
* <b>Intensity scaler - </b>A slider that can dim down or enhance the intensity of rays. 
* <b>Auto redraw - </b>When a simulation finishes, the entire scene is automatically redrawn when enabled.
* <b>Show axis and grid - </b>Show or hide the axis and grid
* <b>Intensity-coded ray colors - </b>When enabled the transparency of plotted rays scales with their intensity  
* <b>Show element properties - </b>Draws the element's name and properties
* <b>Black background - </b>Show a black instead of white background. Usefull for dark-themed presentations, or in some cases the rays display better with a black background.
* <b>Show pixels - </b>When enabled, this shows the center and extent of all pixels of an imager. This could slow down the plotting process when the imager has many pixels.
* <b>Show non-colliding rays - </b>Show/hide rays that do not collide with any of the elements. Useful to speed up the plotting process or declutter the image in some cases.
* <b>Redraw scene - </b>Guess what ... it redraws the scene.

Note that the intensity and line width of plotted rays automatically scales up or down with the number of plotted rays. 

### Display

The display tab is only enabled when there is a display or an imager present in the scene. The graph in this tab shows the impact points of the rays with the display, in various ways. 

#### Display graph modes

* <b>Scatterplot 1D : </b>The intersection points of the rays with the display, shown in 1D
* <b>Scatterplot pseudo 2D : </b>The same as the 1D version, but shown in pseudo-2D, where each point gets a random vertical displacement. Useful for better visualisation. 
* <b>Scatterplot pseudo polar : </b>Plots impact points in a radial layout by mapping the display X-position to radius and randomizing the angle. This spreads the 1D distribution into a circular cloud for compact visual comparison of multiple rays or sources.
* <b>Intensity plot 1D : </b>Only works with pixel-based imagers. This graph shows the intensity registered in all the pixels of the 1D imager.
* <b>Intensity plot pseudo 2D : </b>Same as the 1D version, but shown as a pseudo-2D color image. 
* <b>Phase plot : </b>This too only works with imagers. This shows the phases of the rays at the intersection points, as well as the resulting phase.

<p align="center">
<img src="assets/UI_Display_Scatterplot_1D.png", alt="UI_Display_Scatterplot_1D.png", height=100/>
<img src="assets/UI_Display_Scatterplot_2D.png", alt="UI_Display_Scatterplot_2D.png", height=100/>
<img src="assets/UI_Display_Pseudo_polar_scatter_plot.png", alt="UI_Display_Pseudo_polar_scatter_plot.png", height=100/>
<img src="assets/UI_Display_Intensity_plot_1D.png", alt="UI_Display_Intensity_plot_1D.png", height=100/>
<img src="assets/UI_Display_Intensity_plot_2D.png", alt="UI_Display_Intensity_plot_2D.png", height=100/>
<img src="assets/UI_Display_Phase_plot.png", alt="UI_Display_Phase_plot.png", height=100/>
</p>


---

## Miscellaneous

### Units

The standard units for calculations in RaTrace are <b>mm</b> and <b>radians</b>. For ease-of-use you can import and use other units from the utils.varia module in the following way:

```
from utils.varia import m, cm, mm, µm, nm, rad, deg
wavelength = 660*nm  # Gets converted into mm
angle = 30*deg       # Gets converted into radians
```

### Refractive index and material

Refractive-index defaults and material helpers live in the material module:

```
from utils.material import N_air, N_glass, N_water
```

Glass elements and lenses accept both `N` and `material`.

Use `N` when you want to define the refractive index directly:

* `N=1.7` uses a constant refractive index for every wavelength.
* `N=[1.7, 0.05]` uses Cauchy dispersion, where the first value is the base index and the following values are Cauchy coefficients in micrometer units.
* `N=[1.5168, 64.17]` uses an Abbe description, because the second value is larger than 1. The first value is `nd` and the second value is `Vd`.
* `N='N-BK7'` loads a named glass from the refractiveindex.info database.

Use `material` when you want to name a database material explicitly:

```
lens = spherical_lens_class.SphericalLensClass(
    p0=np.array([0, 0]),
    n0=np.array([-1, 0]),
    f=40*mm,
    diameter=25*mm,
    material='N-BK7',
)
```

When `material` is provided, it takes precedence over `N`. This means `material='N-BK7'` will define the glass even if `N` is also passed. Internally, `N` and `material` are converted into a `GlassMaterial`; during ray tracing the material is evaluated at each ray wavelength, so chromatic rays can see different refractive indices.

### Colors

Colors can be described in a number of ways: 
* <b>(R,G,B,A)</b> : A 4-element tuple of 3 RGB values and a transparency (or alpha) value
* <b>'red', 'green', 'blue', ... </b> : A string describing the color 
* <b>'rainbow'</b> : The colors of the n initial rays are given by ordered n colors of the rainbow    
* <b>'wavelength'</b> : The color of rays is determined by their wavelength

## Elements

### Light sources

The following object classes should be imported from the 'light' folder:

```
from light import point_source_class, plane_source_class, diffuse_plane_source_class, laser_class, virtual_ray_class
```

#### Directed point source

A directed point light source object with an origin, orientation and spread fan angle. The figure below shows some possible configurations for a fixed fan angle of 20°. First row: equiangular and random distribution of rays. Second row: uniformly and randomly sampled Gaussian distribution of rays.

Note that the total angular range of rays exceeds the "fan angle" of the beam in case of Gaussian distribution of rays. Since a Gaussian beam has theoretical infinite width, the fan angle given as a parameter is considered to be the "full angular width at half max" (FWHM) of the beam.


<p align="center">
<img src="assets/Syntax_point_source.png", alt="Syntax_point_source.png", height=200/>
</p>

<i>Object initialisation:</i>
```
point_source_class.PointSourceClass(p0, n0, fan_angle wavelength, intensity, intensity_distribution, plot_color)
```

<i>Input parameters:</i>
* <b>p0</b> (np.array | default=np.array([0,0])) : Position of the point source
* <b>n0</b> (np.array | default=np.array([1,0])) : Direction of the point source 
* <b>fan_angle</b> (float | default=30*deg) : Fan angle of the cone of light. For 'gaussian' intensity distribution, this represents the full (angular) width at half of the height (FWHM) of the Gaussian beam.
* <b>wavelength</b> (float | default=660*nm) : Wavelength of the light rays 
* <b>intensity</b> (float | default=1) : Intensity of the initial light rays
* <b>intensity_distribution</b>  ('equiangular', 'gaussian', 'gaussianrandom', 'random' | default='equiangular') : Intensity distribution of the rays along the light fan 
* <b>plot_color</b> (color | default='wavelength'): Plot color of the light rays

#### Parallel plane source

A directed parallel light source object with an origin, orientation, width and exit angle. The figure below shows some possible configurations for a fixed source diameter. First row: equidistant and random distribution of rays. Second row: uniformly and randomly sampled Gaussian distribution of rays. Third row: plane source at an angle and exit angle at zero, plane source at zero angle but non-zero exit angle of rays.

Note that the total range of rays exceeds the "diameter" of the beam in case of Gaussian distribution of rays. Since a Gaussian beam has theoretical infinite width, the diameter given as a parameter is considered to be the "full width at half max" (FWHM) of the beam.

<p align="center">
<img src="assets/Syntax_plane_source.png", alt="Syntax_plane_source.png", height=300/>
</p>

<i>Object initialisation:</i>
```
plane_source_class.PlaneSourceClass(p0, n0, diameter, angle, wavelength, intensity, intensity_distribution='equidistant', plot_color='wavelength')
```

<i>Input parameters:</i>
* <b>p0</b> (np.array | default=np.array([0,0])) : Position of the plane source
* <b>n0</b> (np.array | default=np.array([1,0])) : Direction of the plane source 
* <b>diameter</b> (float | default=10*mm) : Diameter, extent or size of the plane source. For 'gaussian' intensity distribution, this represents the full width at half of the height (FWHM) of the Gaussian beam.
* <b>angle</b> (float | default=0*deg) : Angle by which the emitted rays are leaving the plane source, relative to n0
* <b>wavelength</b> (float | default=660*nm) : Wavelength of the light rays 
* <b>intensity</b> (float | default=1) : Intensity of the initial light rays
* <b>intensity_distribution</b>  ('equidistant', 'gaussian', 'gaussianrandom', 'random' | default='equidistant') : Intensity distribution of the rays along the plane. 'equidistant' creates evenly spaced rays, 'gaussian' creates rays following a Gaussian distribution with width defined by diameter, 'gaussianrandom' creates randomly sampled Gaussian-distributed ray positions, 'random' creates uniformly random ray positions
* <b>plot_color</b> (color | default='wavelength'): Plot color of the light rays

#### Diffuse plane source

A directed diffuse parallel light source object with an origin, orientation, width and spread angle. The ray distribution along its diameter, as well as the ray orientation is random within the limits defined. The example below shows the situation for a 20° fan angle.

<p align="center">
<img src="assets/Syntax_diffuse_plane_source.png", alt="Syntax_diffuse_plane_source.png", height=150/>
</p>

<i>Object initialisation:</i>
```
plane_source_class.DiffusePlaneSourceClass(p0, n0, diameter, fan_angle, wavelength, intensity, intensity_distribution, plot_color)
```

<i>Input parameters:</i>
* <b>p0</b> (np.array | default=np.array([0,0])) : Position of the plane source
* <b>n0</b> (np.array | default=np.array([1,0])) : Direction of the plane source 
* <b>diameter</b> (float | default=10*mm) : Diameter, extent or size of the plane source
* <b>fan_angle</b> (float | default=30*deg) : Fan angle, or angular 'spread' of the rays in the cone of light
* <b>wavelength</b> (float | default=660*nm) : Wavelength of the light rays 
* <b>intensity</b> (float | default=1) : Intensity of the initial light rays
* <b>plot_color</b> (color | default='wavelength'): Plot color of the light rays

#### Laser

(To be documented) 

#### Virtual ray

(To be documented) 

### Lenses

The following object classes should be imported from the 'light' folder:

```
from elements import ideal_thin_lens_class, spherical_lens_class, glass_element_class
```

#### Ideal (thin) lens

An ideal lens (perfect focus, no aberrations) with a certain focal distance f and diameter.

<p align="center">
<img src="assets/Syntax_ideal_lens.png", alt="Syntax_ideal_lens.png", height=200/>
</p>

<i>Object initialisation:</i>
```
ideal_thin_lens_class.IdealThinLensClass(p0, n0, f, diameter, N, material)
```

<i>Input parameters:</i>
* <b>p0</b> (np.array | default=np.array([10,0])) : Position of the plane source
* <b>n0</b> (float | default=np.array([-1,0])) : Orientation of the lens' optical axis
* <b>f</b> (float | default=100*mm) : Focal distance of the lens
* <b>diameter</b> (float | default=10*mm) : Diameter of the lens
* <b>N</b> (float, list, str | default=N_glass) : Refractive index or material name of the lens
* <b>material</b> (str | default=None) : Optional database material name; when provided, it overrides `N`

#### Spherical lens

A glass lens with focal distance f and spherical surfaces with radii R0 and R1. If R0 and R1 are given, f is calculated from those radii. If only f is given, R0 and R1 are calculated from f and the lens is considered symmetrical, i.e. R0 and R1 are equal in magnitude.

<p align="center">
<img src="assets/Syntax_spherical_lens.png", alt="Syntax_spherical_lens.png", height=200/>
</p>

<i>Object initialisation:</i>
```
spherical_lens_class.SphericalLensClass(p0, n0, R0, R1, f, thickness, diameter, N, material, plot_resolution)
```

<i>Input parameters:</i>
* <b>p0</b> (np.array([0,0]) : Position of the first surface of the lens
* <b>n0</b> (np.array([1,0]) : Orientation of the optical axis of the spherical lens
* <b>f</b> (float | default=None) : Focal distance
* <b>R0</b> (float | default=None) : The radius of the first surface 
* <b>R1</b> (float | default=None) : The radius of the second surface
* <b>thickness</b> (float | default=2*mm) : Thickness of the lens along the optical axis
* <b>diameter</b> (float, [float, float] | default=10*mm) : Diameter of the entire lens when one value is given. When a 2-element list is passed, it defines the diameters of the first and second surface, e.g. [20,10]
* <b>N</b> (float, list, str | default=N_glass) : Refractive index or material name
* <b>material</b> (str | default=None) : Optional database material name; when provided, it overrides `N`
* <b>plot_resolution</b> (float | default=1*mm) : Resolution of the plotted lens shape

#### Plano-spherical lens

A glass lens with focal distance f and spherical front surface with radius R and flat back surface. If R is given, f is calculated from that radius. If only f is given, R is calculated from f.

<p align="center">
<img src="assets/Syntax_plano_spherical_lens.png", alt="Syntax_plano_spherical_lens.png", height=200/>
</p>

<i>Object initialisation:</i>
```
plano_spherical_lens_class.PlanoSphericalLensClass(p0, n0, R, f, thickness, diameter, N, material, plot_resolution)
```

<i>Input parameters:</i>
* <b>p0</b> (np.array([0,0]) : Position of the first (spherical) surface of the lens
* <b>n0</b> (np.array([1,0]) : Orientation of the optical axis of the spherical lens
* <b>f</b> (float | default=None) : Focal distance
* <b>R</b> (float | default=None) : The radius of the frontal spherical surface 
* <b>thickness</b> (float | default=5*mm) : Thickness of the lens along the optical axis
* <b>diameter</b> (float | default=10*mm) : Diameter of the entire lens when one value is given.
* <b>N</b> (float, list, str | default=N_glass) : Refractive index or material name
* <b>material</b> (str | default=None) : Optional database material name; when provided, it overrides `N`
* <b>plot_resolution</b> (float | default=1*mm) : Resolution of the plotted lens shape


### Various glass elements

#### Glass parallel plate

A simple glass parallel plate with a length and a thickness

<p align="center">
<img src="assets/Syntax_glass_parallel_plate.png", alt="Syntax_glass_parallel_plate.png", height=200/>
</p>

<i>Object initialisation:</i>
```
glass_parallel_plate_class.GlassParallelPlate(p0, n0, , thickness, length, N, generate_reflections)
```

<i>Input parameters:</i>
* <b>p0</b> (np.array([0,0]) : Position of the first surface of the plate.
* <b>n0</b> (np.array([-1,0]) : Orientation of the plate's normal.
* <b>thickness</b> (float | default=1*mm) : Thickness of the plate, in the direction along the normal.
* <b>length</b> (float | default=10*mm) : Length of the plate, perpendicular to the normal.
* <b>N</b> (float, list, str | default=N_glass) : Refractive index or material name.
* <b>material</b> (str | default=None) : Optional material database name; overrides `N` when provided.
* <b>generate_reflections</b> (bool | default=True) : Enable or disable reflected ray generation at the plate surfaces.
* <b>is_active</b> (bool | default=True) : Whether the plate participates in ray tracing.
* <b>is_visible</b> (bool | default=True) : Whether the plate is drawn in the scene.

#### Prism

There are two types of prism elements that live in ```glass_prism_class```. For the first one, a "rectangular prism", one of its internal angles is at 90°, while the other angles are not. The second prism is an isoscele prism, where its internal angles are not (necessarily) 90°, but are defined by the "apex angle". Both prism types can be seen in the image below.

<p align="center">
<img src="assets/Syntax_prism.png", alt="Syntax_prism.png", height=200/>
</p>

##### Rectangular prism

<i>Object initialisation:</i>
```
glass_prism_class.GlassPrismRectangularClass(p0, n0, angle, length, N, generate_reflections)
```

<i>Input parameters:</i>
* <b>p0</b> (np.array([0,0]) : Position of the prism's 90° corner.
* <b>n0</b> (np.array([0,-1]) : Orientation of the prism normal.
* <b>angle</b> (float | default=45*deg) : Internal angle that defines the prism's shape.
* <b>length</b> (float | default=10*mm) : Length of the prism base.
* <b>N</b> (float, list, str | default=N_glass) : Refractive index or material name.
* <b>material</b> (str | default=None) : Optional material database name; overrides `N` when provided.
* <b>generate_reflections</b> (bool | default=False) : Enable reflected ray generation at the prism surfaces.
* <b>is_active</b> (bool | default=True) : Whether the prism participates in ray tracing.
* <b>is_visible</b> (bool | default=True) : Whether the prism is drawn in the scene.

##### Isoscele prism

<i>Object initialisation:</i>
```
glass_prism_class.GlassPrismIsoscelesClass(p0, n0, angle_apex, length, N, generate_reflections)
```

<i>Input parameters:</i>
* <b>p0</b> (np.array([0,0]) : Position of the prism's base surface.
* <b>n0</b> (np.array([1,1]) : Orientation of the prism normal.
* <b>angle_apex</b> (float | default=90*deg) : Apex angle between the prism faces.
* <b>length</b> (float | default=10*mm) : Length of the prism base.
* <b>N</b> (float, list, str | default=N_glass) : Refractive index or material name.
* <b>material</b> (str | default=None) : Optional material database name; overrides `N` when provided.
* <b>generate_reflections</b> (bool | default=True) : Enable reflected ray generation at the prism surfaces.
* <b>is_active</b> (bool | default=True) : Whether the prism participates in ray tracing.
* <b>is_visible</b> (bool | default=True) : Whether the prism is drawn in the scene.


### Surfaces

Surfaces are imported from the elements folder:

```
from elements import diffuse_plate_class, black_plate_class
```

#### Diffuse scattering plate

A diffuse scattering surface scatters an incoming ray in a way defined by its bidirectional reflectance distribution function (BRDF). This BRDF is described by a diffuse scattering component with strength Kd and a specular component with strength Ks. The extent, or width, of the specular component is defined by the parameter alpha, according to the Blinn–Phong model.

The figures below show a single incoming ray (coming from the bottom left) casted onto a surface with BRDF parameters Kd=1, Ks=2, alpha=100. The peak of the plotted BRDF points in the reflected direction of the incoming ray.

<p align="center">
<img src="assets/Syntax_diffuse_scattering_plate_1.png", alt="Syntax_diffuse_scattering_plate_1.png", height=150/><img src="assets/Syntax_diffuse_scattering_plate_2.png", alt="Syntax_diffuse_scattering_plate_2.png", height=150/>
</p>

<i>Object initialisation:</i>
```
diffuse_plate_class.DiffusePlateClass(p0, n0, length, thickness, Kd=1, Ks, alpha, n_light)
```

<i>Input parameters:</i>
* <b>p0</b> (np.array | default=np.array([0,0])) : Position of the surface
* <b>n0</b> (np.array | default=np.array([-1,0])) : Orientation of the surface
* <b>length</b> (np.array | default=10*mm) : Length of the surface
* <b>thickness</b> (np.array | default=1*mm) : Thickness of the surface
* <b>Kd</b> (np.array | default=0) : Specular scattering component
* <b>Ks</b> (np.array | default=0) : Diffuse scattering component
* <b>alpha</b> (np.array | default=1) : Extent of the specular component
* <b>n_light</b>  (np.array | default=None) : An optional preferential direction of incoming light, only useful when plotting the BRDF in the reflected direction.

#### Black plate (Beam dump)

A black plate can be used as a beam dump, or for outlining light absorbing walls like lens tubes, telescopic tubes, etc. In the figure below, note that non-colliding rays are colored differently, IF at all (see "view" settings).

<p align="center">
<img src="assets/Syntax_black_plate.png", alt="Syntax_black_plate.png", height=200/>
</p>

<i>Object initialisation:</i>
```
black_plate_class.BlackPlateClass(p0, n0, length, thickness, plot_color)
```

<i>Input parameters:</i>
* <b>p0</b> (np.array | default=np.array([0,0])) : Position of the plate
* <b>n0</b> (np.array | default=np.array([-1,0])) : Orientation of the plate
* <b>length</b> (float | default=10*mm) : Length of the plate
* <b>thickness</b> (float | default=1*mm) : Thickness of the plate
* <b>plot_color</b> (color | default=(0.5,0.5,0.5,1)): Plot color of the plate

#### Aperture

An aperture with an inner and outer diameter

<p align="center">
<img src="assets/Syntax_aperture.png", alt="Syntax_aperture.png", height=200/>
</p>

<i>Object initialisation:</i>
```
aperture_class.ApertureClass(p0, n0, diameter_inner, diameter_outer, plot_color)
```

<i>Input parameters:</i>
* <b>p0</b> (np.array | default=np.array([0,0])) : Position of the aperture
* <b>n0</b> (np.array | default=np.array([-1,0])) : Orientation of the aperture
* <b>diameter_inner</b> (float | default=10*mm) : Inner (passing) diameter of the aperture
* <b>diameter_outer</b> (float | default=20*mm) : Outer (blocking) diameter of the aperture
* <b>plot_color</b> (color | default=(0.5,0.5,0.5,1)): Plot color of the aperture


### Mirrors

Mirrors are imported from the elements folder: 

```
from elements import flat_mirror_class, semi_transparent_mirror_class, parabolic_mirror_class
```

The figure below shows 2 types of mirrors: regular fully reflecting mirrors and semitransparent mirrors:

<p align="center">
<img src="assets/Syntax_flat_mirrors.png", alt="Syntax_flat_mirrors.png", height=200/>
</p>

#### Flat mirror

A flat, fully reflecting mirror

<i>Object initialisation:</i>
```
flat_mirror_class.FlatMirrorClass(p0, n0, length, thickness, plot_color)
```

<i>Input parameters:</i>
* <b>p0</b> (np.array | default=np.array([0,0])) : Position of the mirror
* <b>n0</b> (np.array | default=np.array([-1,0])) : Orientation of the mirror
* <b>length</b> (float | default=10*mm) : Length of the mirror
* <b>thickness</b> (float | default=1*mm) : Thickness of the mirror
* <b>plot_color</b> (color | default=(0,0,0.5,1)): Plot color of the mirror

#### Semi-transparent mirror

A semi-transparent mirror with a transmission coefficient

<i>Object initialisation:</i>
```
semi_transparent_mirror_class.SemiTransparentMirror(p0, n0, length, transmission)
```

<i>Input parameters:</i>
* <b>p0</b> (np.array | default=np.array([0,0])) : Position of the mirror
* <b>n0</b> (np.array | default=np.array([-1,0])) : Orientation of the mirror
* <b>length</b> (float | default=10*mm) : Length of the mirror
* <b>transmission</b> (float | default=0.5) : Transmission coefficient, 1-transmission represents the reflection coefficient

#### Parabolic mirror

A parabolic mirror with a focal distance and a diameter

<p align="center">
<img src="assets/Syntax_parabolic_mirror.png", alt="Syntax_parabolic_mirror.png", height=200/>
</p>

<i>Object initialisation:</i>
```
parabolic_mirror_class.ParabolicMirrorClass(p0, n0, f, diameter, thickness, plot_color)
```

<i>Input parameters:</i>
* <b>p0</b> (np.array | default=np.array([0,0])) : Position of the parabolic mirror
* <b>n0</b> (np.array | default=np.array([-1,0])) : Orientation of the parabolic mirror
* <b>f</b> (float | default=100*mm) : Focal distance
* <b>diameter</b> (float | default=100*mm) : Diameter of the mirror
* <b>thickness</b> (float | default=10*mm) : Thickness of the mirror
* <b>plot_color</b> (color | default=(0,0,0.5,1)): Plot color of the light rays
* <b>plot_resolution</b> (float | default=0.1*mm) : Resolution of the plotted mirror


### Displays

Displays are imported from the display folder:

```
from display import display_class, imager_class
```

#### Display

A display is a stopping surface for colliding rays. Contrary to black and other surfaces, the collision points can be processed and displayed in the 'view' tab.

<p align="center">
<img src="assets/Syntax_display_1.png", alt="Syntax_display_1.png", width=200, height=200/><img src="assets/Syntax_display_2.png", alt="Syntax_display_2.png", width=200, height=200/>
</p>

<i>Object initialisation:</i>
```
display_class.DisplayClass(p0, n0, length)
```

<i>Input parameters:</i>
* <b>p0</b> (np.array | default=np.array([0,0])) : Position of the display
* <b>n0</b> (np.array | default=np.array([-1,0])) : Orientation of the display
* <b>length</b> (float | default=10*mm) : Length of the display


#### Imager

An imager is a display with pixels of a finite width. If 'use phase information' is enabled, the phases of different rays coming together in a pixel will combine and result in an interfered intensity. When this option is disabled, all rays are presumed to have the same phase, and intensities are just added up.

<p align="center">
<img src="assets/Syntax_imager_1.png", alt="Syntax_imager_1.png", width=200, height=200/><img src="assets/Syntax_imager_2.png", alt="Syntax_imager_2.png", width=200, height=200/>
</p>

<i>Object initialisation:</i>
```
imager_class.ImagerClass(p0, n0, length, pixel_size)
```

<i>Input parameters:</i>
* <b>p0</b> (np.array | default=np.array([0,0])) : Position of the imager
* <b>n0</b> (np.array | default=np.array([-1,0])) : Orientation of the imager
* <b>length</b> (float | default=10*mm) : Length of the imager
* <b>pixel_size</b> (float | default=100*µm) : Pixel size of the imager. The number of pixels is determined by the length divided by the pixel size.

