import re
from dataclasses import dataclass, replace
from functools import lru_cache
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen

import numpy as np

from utils.varia import mm, nm


N_air = 1.00
N_glass = 1.50
N_water = 1.33

FRAUNHOFER_C_UM = 0.6562725
FRAUNHOFER_D_UM = 0.5875618
FRAUNHOFER_F_UM = 0.4861327
ABBE_NUMBER_THRESHOLD = 1.0

REFRACTIVEINDEX_DB_BASE_URL = 'https://raw.githubusercontent.com/polyanskiy/refractiveindex.info-database/main/database/data'
MATERIAL_SEARCH_PATHS = (
    'specs/schott/optical',
    'specs/ohara/optical',
    'specs/hoya/optical',
    'specs/cdgm/optical',
    'specs/hikari/optical',
    'specs/sumita/optical',
    'specs/nsg/optical',
    'specs/corning/optical',
    'specs/isuzu/optical',
)
MATERIAL_ALIASES = {
    'BK7': 'specs/schott/optical/N-BK7.yml',
    'NBK7': 'specs/schott/optical/N-BK7.yml',
}


@dataclass(frozen=True)
class GlassMaterial:
    kind: str
    coefficients: tuple = ()
    name: str = ''
    reference_index: float | None = None
    abbe_number: float | None = None
    formula_type: int | None = None
    wavelength_range_um: tuple | None = None
    source: str | None = None
    tabulated_n: tuple = ()

    def index_at(self, wavelength):
        wavelength_um = wavelength_to_um(wavelength)

        if self.wavelength_range_um is not None:
            wavelength_min, wavelength_max = self.wavelength_range_um
            if not wavelength_min <= wavelength_um <= wavelength_max:
                raise ValueError(
                    f'Wavelength {wavelength_um:.4g} um is outside the valid range '
                    f'{wavelength_min:g}-{wavelength_max:g} um for material {self.name}'
                )

        if self.kind == 'constant':
            return self.coefficients[0]
        if self.kind == 'cauchy':
            return calculate_cauchy_refraction_index(self.coefficients, wavelength_um)
        if self.kind == 'abbe':
            cauchy_coefficients = abbe_to_cauchy_coefficients(*self.coefficients[:2])
            return calculate_cauchy_refraction_index(cauchy_coefficients, wavelength_um)
        if self.kind == 'database_formula':
            return calculate_database_formula_refraction_index(self.formula_type, self.coefficients, wavelength_um)
        if self.kind == 'database_tabulated':
            wavelengths = [entry[0] for entry in self.tabulated_n]
            indices = [entry[1] for entry in self.tabulated_n]
            return float(np.interp(wavelength_um, wavelengths, indices))

        raise ValueError(f'Unsupported glass material model: {self.kind}')

    def __repr__(self):
        if self.kind == 'constant':
            return f'{self.coefficients[0]:g}'
        if self.kind == 'cauchy':
            return f'Cauchy{list(self.coefficients)}'
        if self.kind == 'abbe':
            return f'Abbe{list(self.coefficients)}'
        return self.name or self.kind

    __str__ = __repr__


def wavelength_to_um(wavelength):
    return wavelength / nm / 1000 * mm


def um_to_wavelength(wavelength_um):
    return wavelength_um * 1000 * nm / mm


def calculate_cauchy_refraction_index(coefficients, wavelength_um):
    refractive_index = coefficients[0]
    for i_coefficient, coefficient in enumerate(coefficients[1:], start=1):
        refractive_index += coefficient / wavelength_um ** (2 * i_coefficient)
    return refractive_index


def abbe_to_cauchy_coefficients(nd, Vd):
    principal_dispersion = (nd - 1) / Vd
    B = principal_dispersion / (1 / FRAUNHOFER_F_UM**2 - 1 / FRAUNHOFER_C_UM**2)
    A = nd - B / FRAUNHOFER_D_UM**2
    return A, B


def calculate_database_formula_refraction_index(formula_type, coefficients, wavelength_um):
    wavelength_squared = wavelength_um**2

    if formula_type == 1:
        n_squared = 1 + coefficients[0]
        for i_coefficient in range(1, len(coefficients), 2):
            resonance = coefficients[i_coefficient + 1] ** 2
            n_squared += coefficients[i_coefficient] * wavelength_squared / (wavelength_squared - resonance)
        return float(np.sqrt(n_squared))

    if formula_type == 2:
        n_squared = 1 + coefficients[0]
        for i_coefficient in range(1, len(coefficients), 2):
            resonance = coefficients[i_coefficient + 1]
            n_squared += coefficients[i_coefficient] * wavelength_squared / (wavelength_squared - resonance)
        return float(np.sqrt(n_squared))

    if formula_type == 3:
        n_squared = coefficients[0]
        for i_coefficient in range(1, len(coefficients), 2):
            n_squared += coefficients[i_coefficient] * wavelength_um ** coefficients[i_coefficient + 1]
        return float(np.sqrt(n_squared))

    if formula_type == 5:
        return calculate_cauchy_refraction_index(coefficients, wavelength_um)

    raise ValueError(f'Refractiveindex.info formula {formula_type} is not implemented')


def create_glass_material(N=N_glass, material=None):
    if material is not None:
        return load_refractiveindex_info_material(material)

    if isinstance(N, GlassMaterial):
        return N

    if isinstance(N, str):
        return load_refractiveindex_info_material(N)

    if isinstance(N, np.ndarray):
        N = N.tolist()

    if isinstance(N, (list, tuple)):
        coefficients = tuple(float(coefficient) for coefficient in N)
        if len(coefficients) == 0:
            raise ValueError('Glass index list cannot be empty')
        if len(coefficients) == 1:
            return GlassMaterial(kind='constant', coefficients=coefficients, reference_index=coefficients[0])
        if abs(coefficients[1]) > ABBE_NUMBER_THRESHOLD:
            return GlassMaterial(kind='abbe', coefficients=coefficients, reference_index=coefficients[0], abbe_number=coefficients[1])
        return GlassMaterial(kind='cauchy', coefficients=coefficients, reference_index=coefficients[0])

    refractive_index = float(N)
    return GlassMaterial(kind='constant', coefficients=(refractive_index,), reference_index=refractive_index)


def nominal_refraction_index(N=N_glass, material=None):
    glass_material = create_glass_material(N=N, material=material)
    if glass_material.reference_index is not None:
        return glass_material.reference_index
    return glass_material.index_at(um_to_wavelength(FRAUNHOFER_D_UM))


def calculate_refraction_index(N, wavelength):
    glass_material = create_glass_material(N)
    return glass_material.index_at(wavelength)


@lru_cache(maxsize=128)
def load_refractiveindex_info_material(material):
    errors = []

    for path in material_path_candidates(material):
        url = path if path.startswith('http') else refractiveindex_info_url(path)
        try:
            data = fetch_refractiveindex_info_yaml(url)
            return parse_refractiveindex_info_yaml(data, name_from_material_path(path), url)
        except FileNotFoundError:
            errors.append(path)

    raise ValueError(
        f'Could not find material "{material}" in the refractiveindex.info database. '
        f'Tried: {", ".join(errors)}'
    )


def material_path_candidates(material):
    material_text = str(material).strip().replace('\\', '/')
    if material_text.startswith('http://') or material_text.startswith('https://'):
        yield material_text
        return

    material_text = strip_database_prefix(material_text)
    if '/' in material_text or material_text.endswith('.yml'):
        yield material_text if material_text.endswith('.yml') else f'{material_text}.yml'
        return

    material_key = normalize_material_key(material_text)
    if material_key in MATERIAL_ALIASES:
        yield MATERIAL_ALIASES[material_key]

    for search_path in MATERIAL_SEARCH_PATHS:
        for filename in material_filename_candidates(material_text):
            yield f'{search_path}/{filename}.yml'


def strip_database_prefix(material_path):
    for prefix in ('database/data/', 'data/'):
        if material_path.startswith(prefix):
            return material_path[len(prefix):]
    return material_path


def material_filename_candidates(material):
    material_text = material.strip()
    material_base = material_text[:-4] if material_text.lower().endswith('.yml') else material_text
    material_key = normalize_material_key(material_base)

    candidates = [
        material_base,
        material_base.upper(),
        material_base.replace(' ', '-').upper(),
        material_key,
    ]

    if material_key == 'NBK7':
        candidates.insert(0, 'N-BK7')
    elif material_key.startswith('N') and len(material_key) > 1:
        candidates.append(f'N-{material_key[1:]}')

    return unique_preserve_order(candidates)


def normalize_material_key(material):
    return re.sub(r'[^A-Z0-9]', '', material.upper())


def unique_preserve_order(values):
    unique_values = []
    for value in values:
        if value and value not in unique_values:
            unique_values.append(value)
    return unique_values


def refractiveindex_info_url(material_path):
    return f'{REFRACTIVEINDEX_DB_BASE_URL}/{quote(material_path, safe="/-_.")}'


def name_from_material_path(material_path):
    material_path = material_path.rstrip('/')
    return material_path.rsplit('/', 1)[-1].removesuffix('.yml')


def fetch_refractiveindex_info_yaml(url):
    try:
        with urlopen(url, timeout=15) as response:
            return response.read().decode('utf-8')
    except HTTPError as error:
        if error.code == 404:
            raise FileNotFoundError(url) from error
        raise
    except URLError as error:
        raise ConnectionError(f'Could not retrieve refractiveindex.info material data from {url}: {error}') from error


def parse_refractiveindex_info_yaml(data, material_name, source_url=None):
    nd = scalar_yaml_value(data, 'nd')
    Vd = scalar_yaml_value(data, 'Vd')

    formula_match = re.search(
        r'type:\s*formula\s+([0-9]+)\s+wavelength_range:\s*([^\n\r]+)\s+coefficients:\s*([^\n\r]+)',
        data,
        flags=re.IGNORECASE,
    )
    if formula_match is not None:
        formula_type = int(formula_match.group(1))
        wavelength_range = tuple(parse_float_sequence(formula_match.group(2))[:2])
        coefficients = tuple(parse_float_sequence(formula_match.group(3)))
        glass_material = GlassMaterial(
            kind='database_formula',
            coefficients=coefficients,
            name=material_name,
            reference_index=nd,
            abbe_number=Vd,
            formula_type=formula_type,
            wavelength_range_um=wavelength_range,
            source=source_url,
        )
        if glass_material.reference_index is None:
            glass_material = replace(glass_material, reference_index=glass_material.index_at(um_to_wavelength(FRAUNHOFER_D_UM)))
        return glass_material

    tabulated_n = parse_tabulated_n_data(data)
    if tabulated_n:
        wavelength_range = (tabulated_n[0][0], tabulated_n[-1][0])
        glass_material = GlassMaterial(
            kind='database_tabulated',
            name=material_name,
            reference_index=nd,
            abbe_number=Vd,
            wavelength_range_um=wavelength_range,
            source=source_url,
            tabulated_n=tuple(tabulated_n),
        )
        if glass_material.reference_index is None:
            glass_material = replace(glass_material, reference_index=glass_material.index_at(um_to_wavelength(FRAUNHOFER_D_UM)))
        return glass_material

    raise ValueError(f'Material {material_name} does not contain a supported refractive-index formula or n table')


def scalar_yaml_value(data, key):
    match = re.search(rf'^\s*{re.escape(key)}:\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*$', data, flags=re.MULTILINE)
    return None if match is None else float(match.group(1))


def parse_float_sequence(text):
    return [float(value) for value in re.findall(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?', text)]


def parse_tabulated_n_data(data):
    match = re.search(r'type:\s*tabulated\s+n\s+data:\s*\|\s*(.*?)(?:\n\s*-\s*type:|\n[A-Z_]+:|\Z)', data, flags=re.IGNORECASE | re.DOTALL)
    if match is None:
        return []

    rows = []
    for line in match.group(1).splitlines():
        values = parse_float_sequence(line)
        if len(values) >= 2:
            rows.append((values[0], values[1]))
    return rows
