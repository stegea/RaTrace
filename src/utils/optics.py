import numpy as np

from utils import material
from utils.varia import mm, nm, X, Y, deg
from utils.configuration_class import config


def calculate_image_distance(object_distance, focal_length):
    image_distance = 1 / (1 / focal_length - 1 / object_distance)
    return image_distance


def refract_and_reflect_ray(ray, n_coll, Ni, No, element_generates_reflection=False):
    from light import light_class
    rays_new = list()

    # In the formula, ri, ro and n all point away from the surface
    n = n_coll  if  np.dot(ray.r, n_coll)<0  else  -n_coll  # Assure that n points away from the surface
    ri = -ray.r     # r should point away from the surface

    # The orientation of the refracted ray. Is [nan,nan] is case of total reflection
    r_refracted = calculate_refracted_orientation(ri, n, Ni, No)
    total_reflection = np.any(np.isnan(r_refracted))

    max_number_of_reflections = config.getint('simulation', 'max_number_of_reflections')
    reflections_enabled_in_UI = config.getboolean('simulation', 'generate_reflected_rays')

    # Calculate the reflected ray, if enabled
    if reflections_enabled_in_UI  and  element_generates_reflection  and  ray.reflection_count < max_number_of_reflections:     # Partial reflection and transmission
        if not total_reflection:
            cos_ai = np.dot(ray.r, n)
            cos_ao = np.dot(r_refracted, n)
            [R, T, Rs, Rp, Ts, Tp] = calculate_reflectance_and_transmittance_coefficients(Ni, No, cos_ai, cos_ao)
        else:   # There is total reflection
            R = 1
        r_reflected = calculate_reflected_orientation(ray.r, n)
        ray_reflected = light_class.RayClass(p0=ray.p1, r=r_reflected, intensity=R * ray.intensity, wavelength=ray.wavelength, ray_parent=ray, N=Ni, plot_color=ray.plot_color, is_active=True, is_visible=True)
        ray_reflected.reflection_count = ray.reflection_count + 1  # Keep track of the reflection count
        rays_new.append(ray_reflected)
    else:
        T = 1

    # When there is no total reflection, there is refraction too
    if not total_reflection:
        ray_refracted = light_class.RayClass(p0=ray.p1, r=r_refracted, intensity=T * ray.intensity, wavelength=ray.wavelength, ray_parent=ray, N=No, plot_color=ray.plot_color, is_active=True, is_visible=True)
        rays_new.append(ray_refracted)

    return rays_new


def calculate_reflected_orientation(ri, n):
    # Reflection around a normal vector in 2D
    r_refl = 2 * np.dot(n, -ri) * n + ri
    return r_refl


def calculate_refracted_orientation(ri, n, Ni, No):
        # Snell's law in 2D vector format, see:  https://www.slideshare.net/dieulinh299/ray-tracing
        Nr = Ni/No
        x = 1 - Nr ** 2 * (1 - np.dot(n, ri) ** 2)
        if x>=0:
            r_refr = (Nr*np.dot(n,ri) - np.sqrt(x))*n - Nr*ri
            return r_refr
        else:
            return np.array([np.nan, np.nan])


def calculate_reflectance_and_transmittance_coefficients(Ni, No, cos_ai, cos_ao):
    # Fresnel's equations for refracted (or transmitted) and reflected light: https://www.rp-photonics.com/fresnel_equations.html
    # Legend: r=reflection, t=transmission, s=s-polarised (perpendicular), p=p-polarised (parallel), i=incoming, o=outgoing

    # Amplitude coefficients
    rs = (Ni*cos_ai-No*cos_ao)/(Ni*cos_ai+No*cos_ao)
    rp = (No*cos_ai-Ni*cos_ao)/(No*cos_ai+Ni*cos_ao)
    ts = 2*Ni*cos_ai/(Ni*cos_ai+No*cos_ao)
    tp = 2*Ni*cos_ai/(No*cos_ai+Ni*cos_ao)

    # Intensities
    Rs = rs**2
    Rp = rp**2
    Ts = No*cos_ao/(Ni*cos_ai) * ts**2
    Tp = No*cos_ao/(Ni*cos_ai) * tp**2

    # For unpolarised light
    R = (Rs+Rp)/2
    T = (Ts+Tp)/2
    return [R, T, Rs, Rp, Ts, Tp]


def refract_ray_on_ideal_lens(p0, n0, f, p, r, p_coll):
    from utils import geometry
    # p0,n0,r0 are from the lens  /  p,r are from the ray
    r0 = geometry.orientation_from_normal(n0)   # Orientation along the lens
    n_prop = n0 * np.sign(np.dot(r, n0))  # n0 is just the main orientation of the lens, for reference of constructing or plotting. However, the ray could come from "left" or "right", so n_prop is the general propagation direction of the ray, ON the optical axis

    if np.isclose( np.linalg.norm(p_coll-p0), 0 ):  # The ray goes through the center of the lens, in that case, the ray remains unaffected
        ro = r
    elif np.isclose( np.dot(r,r0), 0 ):  # Ray is parallel to the optical axis
        v = f  # The outgoing ray goes through the focal point
        p_img = p0 + v * n_prop  # "Image point" on the optical axis
        ro = geometry.normalize(p_img - p_coll)  # The outgoing ray is along the line between the ray-lens intsersection point p_coll and the image point p_img
    else:   # The general case
        t = np.dot(p0 - p, r0) / np.dot(r, r0)  # The ray p+t*r intersects the optical axis when (p+t*r - p0)Â·r0 = 0. Solving for t gives the intersection point.
        p_obj = p + t * r  # "Object point" on the optical axis

        obj_vec = p0 - p_obj  # The vector between o and p0 along the optical axis
        d_obj = np.dot(obj_vec, n_prop)  # Compute object distance (d_obj) from the object point p_obj to the lens, becomes negative for a virtual image

        if np.isclose(f - d_obj, 0):  # A converging ray whos object point is virtual and aligns with the focal point. The outgoing ray is parallel to the optical axis then.
            ro = n_prop
        else:
            v = 1 / (1 / f - 1 / d_obj)     # The thin lens equation
            p_img = p0 + v * n_prop  # "Image point" on the optical axis
            ro = geometry.normalize(p_img - p_coll)  # The outgoing ray is along the line between the ray-lens intsersection point p_coll and the image point p_img

    if np.dot(n_prop, ro) < 0:
        ro = -ro

    return ro


def derive_lens_properties(N=material.N_glass, f=None, R0=None, R1=None, T=None):
    # Using the lensmaker's equation: https://en.wikipedia.org/wiki/Lens#Lensmaker.27s_equation
    N = material.nominal_refraction_index(N)
    if R0 is not None and R1 is not None:
        f = lensmakers_equation(N, R0, R1, T)
        print(f'Lens parameters derived: R0={R0}, R1={R1} --> f={f}')
    elif f is not None:
        # If only f is given, consider a symmetric lens and thus R0 and R1 are equal
        # Reformulate the lensmaker's equation with R0=-R1=R and solve the quadratic equation for R
        A = 1
        B = -f*(N-1)*2
        C = f*(N-1)**2*T/N
        D = B**2-4*A*C
        if f>0:
            R = (-B + np.sqrt(D))/(2*A)   # The "-" solution also checks out somehow, but is not valid
        else:
            R = (-B - np.sqrt(D))/(2*A)  # The "-" solution also checks out somehow, but is not valid
        R0 = R
        R1 = -R
        f_check = lensmakers_equation(N, R0, R1, T)
        print(f'Lens parameters derived: f={f:0.2f}mm --> R0={R0:0.2f}mm, R1={R1:0.2f}mm --> f_check={f_check:0.2f}mm')
    else:
        print(f'Error: Lens definition is incorrect, either define f OR R0 and R1: f={f}, R0={R0}, R1={R1}')
        return [None, None, None]

    H0 = -f*(N-1)*T/(R1*N)  # Distance from p0 to the first principal point on the optical axis
    H1 = -f*(N-1)*T/(R0*N)  # Distance from p1 to the second principal point on the optical axis

    return [f, R0, R1, H0, H1]


def derive_planosphericallens_properties(N=material.N_glass, f=None, R=None, T=None):
    # Using the lensmaker's equation: https://en.wikipedia.org/wiki/Lens#Lensmaker.27s_equation
    N = material.nominal_refraction_index(N)
    if R is not None:
        f = R/(N-1)
        print(f'Plano-convex lens parameters derived: R={R:0.2f}mm --> f={f:0.2f}mm')
    elif f is not None:
        R = f*(N-1)
        print(f'Plano-convex lens parameters derived: f={f:0.2f}mm --> R={R:0.2f}mm')
    else:
        print(f'Error: Plano-convex lens definition is incorrect, either define f OR R: f={f}, R={R}')
        return [None, None, None]

    H = -f*(N-1)*T/(R*N)  # Distance from p1 to the principal point on the optical axis

    return [f, R, H]


def lensmakers_equation(N,R0,R1,T):
    # Using the lensmaker's equation: https://en.wikipedia.org/wiki/Lens#Lensmaker.27s_equation
    one_over_f = (N - 1) * (1 / R0 - 1 / R1 + (N - 1) * T / (N * R0 * R1))
    f = 1 / one_over_f
    return f


# Lens with p0 at its first surface
def construct_lens(p0, R0, R1, T, D, resolution):
    p1 = np.array([T,  0])          # p1 is at the second surface
    C0 = np.array([R0, 0])          # Centre of the circle of the first surface
    C1 = np.array([p1[X]+R1, 0])

    if not isinstance(D,list):
        D = [D, D]  # Use the same diameter for both lens surfaces, otherwise, use the ones that are given

    y0 = np.linspace(-D[0]/2,  D[0]/2, 1 + int(D[0]/resolution))
    y1 = np.linspace( D[1]/2, -D[1]/2, 1 + int(D[1]/resolution))
    x0 = C0[0] - np.sign(R0) * np.sqrt(R0**2 - y0**2)
    x1 = C1[0] - np.sign(R1) * np.sqrt(R1**2 - y1**2)
    p_corners = np.array([[x0[0], y0[0]], [x0[-1], y0[-1]], [x1[0], y1[0]], [x1[-1], y1[-1]]])
    pts = np.concatenate([x0, x1, y0, y1]).reshape(2, -1).T  # Make it an Nx2 array

    return [pts + p0, p1 + p0, C0 + p0, C1 + p0, p_corners + p0]


# Plano convex lens with its normal on the front convex surface in [-1,0] direction
def construct_planosphericallens(p0, R, T, D, resolution):
    p1 = np.array([T,  0])          # Principle point on the second flat surface
    C = np.array([R, 0])            # Centre of the circle of the first surface
    y = np.linspace(-D/2, D/2, 1 + int(D/resolution))
    x = C[0] - np.sign(R) * np.sqrt(R**2-y**2)
    p_corners = np.array([[x[0], y[0]], [x[-1], y[-1]], [T, y[-1]], [T, y[0]]])
    pts = np.concatenate([x, p_corners[2:4][:,X], y, p_corners[2:4][:,Y]]).reshape(2, -1).T  # Make it an Nx2 array
    return [pts + p0, p1 + p0, C + p0, p_corners + p0]


# Parabolic mirror with its first surface (and focal point) pointing left
def construct_parabolic_mirror(p0, f, D, T, resolution):
    p1 = np.array([T,0])      # The central point on the back of the mirror
    f0 = np.array([-f,0])      # The focal point at the front of the mirror
    y0 = np.linspace(-D/2, D/2, 1+int(D/resolution))
    x0 = -y0**2/(4*f)  # Equation for an upward facing parabola through (0,0) and focal distance f (at y=f, the derivative is 1)
    p_corners = np.array([ [x0[0],y0[0]], [x0[-1],y0[-1]], [T,D/2], [T,-D/2] ])
    pts = np.column_stack((x0, y0))
    pts = np.vstack((pts, [[T,D/2],[T,-D/2]]))
    return [pts+p0, p1+p0, f0+p0, p_corners+p0]


def construct_aperture(p0, n0, Di, Do):
    from utils import geometry
    r = geometry.orientation_from_normal(n0)
    pts = np.array([ p0 + r*Do/2,
                     p0 + r*Di/2,
                     p0 - r*Di/2,
                     p0 - r*Do/2 ])
    return pts


def GLB_calculate_ZR(w0, M2, wavelength):  # GLB = Gaussian Laser Beam
    Z_R = np.pi * np.power(w0,2) / (M2*wavelength)
    return Z_R


def GLB_calculate_width_at_z(w0, ZR, z=0*mm):  # GLB = Gaussian Laser Beam
    w = w0 * np.sqrt(1 + np.power(z/ZR, 2))
    return w


def GLB_calculate_intensity_at_P(w0, ZR, intensity_total, p0, n0, beamwaist_distance, P):  # GLB = Gaussian Laser Beam
    from utils import geometry
    v = P - p0
    z = np.dot(v,n0) - beamwaist_distance   # This is with respect to the origin
    y = np.dot(v,geometry.orientation_from_normal(n0))
    w = GLB_calculate_width_at_z(w0=w0, ZR=ZR, z=z)
    intensity_peak = GLB_calculate_peak_intensity_at_z(w0=w0, ZR=ZR, intensity_total=intensity_total, z=z)
    return intensity_peak * np.exp(-2 * (y/w)**2)


def GLB_calculate_peak_intensity_at_z(w0, ZR, intensity_total, z=0*mm):  # GLB = Gaussian Laser Beam
    w = GLB_calculate_width_at_z(w0=w0, ZR=ZR, z=z)
    intensity_peak = np.sqrt(np.pi/2) * intensity_total/w
    return intensity_peak


def calculate_diffracted_orientations(n0, r, wavelength, order, pitch, isreflective):
    from utils import geometry
    # n0-->grating, p-->ray, r-->ray
    n0 = geometry.normalize(n0)
    r  = geometry.normalize(r)
    if not isinstance(order, (list, tuple)):
        order = [order]
    TR_sign = -1 if isreflective else 1

    # Incoming ray points to the grating, but for calculating the angle with the nomal, one should reverse r
    cos_theta_i = np.dot(n0,-r)
    n0 = n0  if  cos_theta_i>=0  else  -n0  # Assure that n0 is aligned with r

    # the following angle_between_vectors(a,b) method returns a positive angle FROM b TO a, if it goes CCW.
    # On the other hand, the grating equation is defined such that the angle is the zenith angle, i.e. from n0 to r
    # Theta should thus be negated
    theta_i = -geometry.angle_between_vectors(n0, -r)

    print(f'r={r}, n0={n0}, cos_theta_i={cos_theta_i:0.3f}, theta_i={theta_i/deg:0.2f}deg, reflective={isreflective}')

    ro = []
    for m in order:
        if isreflective:
            sin_theta_o = m * wavelength / pitch + np.sin(theta_i)  # Grating equation
            if abs(sin_theta_o) > 1:
                print(f"invalid diffraction order, sin(theta_o) is larger than 1 in magnitude: {sin_theta_o:0.3f}")
                ro.append(np.array([np.nan, np.nan]))
            else:
                theta_o =  np.arcsin(sin_theta_o)
                deflection_angle = (180*deg - 2*theta_i) + (theta_o - theta_i)  # first a reflection, then a deflection by the grating
                r_diffracted = geometry.rotate_direction_over_angle(r, deflection_angle)  # Rotate the incoming ray by the difference in angles
                ro.append(geometry.normalize(r_diffracted))
                print(f' m={m}, sin_theta_o={sin_theta_o:0.3f}, theta_o={theta_o/deg:0.2f}deg, deflection_angle={deflection_angle/deg:0.2f}deg, r_diffracted={r_diffracted}')
        else:
            sin_theta_o = m * wavelength / pitch + np.sin(theta_i)  # Grating equation
            if abs(sin_theta_o) > 1:
                print(f"invalid diffraction order, sin(theta_o) is larger than 1 in magnitude: {sin_theta_o:0.3f}")
                ro.append(np.array([np.nan, np.nan]))
            else:
                theta_o =  np.arcsin(sin_theta_o)
                deflection_angle = theta_o - theta_i
                r_diffracted = geometry.rotate_direction_over_angle(r, deflection_angle)  # Rotate the incoming ray by the difference in angles
                ro.append(geometry.normalize(r_diffracted))
                print(f' m={m}, sin_theta_o={sin_theta_o:0.3f}, theta_o={theta_o/deg:0.2f}deg, deflection_angle={deflection_angle/deg:0.2f}deg, r_diffracted={r_diffracted}')

    print('')
    return ro



if __name__ == '__main__':
    from utils.varia import Âµm

    order = -1

    # ro = calculate_diffracted_orientations(n0=np.array([1,0]), r=np.array([1, 0.5]), wavelength=530*nm, order=order, pitch=10*Âµm, isreflective=False)
    # ro = calculate_diffracted_orientations(n0=np.array([1,0]), r=np.array([1,-0.5]), wavelength=530*nm, order=order, pitch=10*Âµm, isreflective=False)

    ro = calculate_diffracted_orientations(n0=np.array([1,0]), r=np.array([1, 0.5]), wavelength=530*nm, order=order, pitch=10*Âµm, isreflective=True)
    ro = calculate_diffracted_orientations(n0=np.array([1,0]), r=np.array([1,-0.5]), wavelength=530*nm, order=order, pitch=10*Âµm, isreflective=True)
