from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
import importlib.util
import time
import pathlib
import inspect
import os
import ast
from raytracer  import raytrace_class
from elements   import element_class
from light      import light_class
from display    import display_class, imager_class
from utils.configuration_class import config

INITIAL_NR_OF_RAYS = config.getint('simulation', 'nr_of_rays')
RED, WHITE = '\033[31m', '\033[0m'



class SceneModelParameterTransformer(ast.NodeTransformer):
    def __init__(self, model_parameters):
        super().__init__()
        self.model_parameters = model_parameters
        self.inside_load_scene_function = False

    def visit_FunctionDef(self, function_node):
        if function_node.name != 'load_scene':
            return function_node

        inside_load_scene_function_previous = self.inside_load_scene_function
        self.inside_load_scene_function = True
        function_node = self.generic_visit(function_node)
        self.inside_load_scene_function = inside_load_scene_function_previous
        return function_node

    def visit_Assign(self, assignment_node):
        assignment_node = self.generic_visit(assignment_node)
        if not self.inside_load_scene_function:
            return assignment_node

        scene_item_name = self.assignment_target_name(assignment_node)
        if scene_item_name not in self.model_parameters:
            return assignment_node

        if not isinstance(assignment_node.value, ast.Call):
            return assignment_node

        assignment_node.value = self.call_node_with_model_parameters(assignment_node.value, self.model_parameters[scene_item_name])
        return assignment_node

    def visit_Return(self, return_node):
        return_node = self.generic_visit(return_node)
        if not self.inside_load_scene_function:
            return return_node

        if not isinstance(return_node.value, (ast.List, ast.Tuple)):
            return return_node

        for return_item_index, return_item_node in enumerate(return_node.value.elts):
            scene_item_name = f'__return_item_{return_item_index}'
            if scene_item_name not in self.model_parameters:
                continue
            if not isinstance(return_item_node, ast.Call):
                continue
            return_node.value.elts[return_item_index] = self.call_node_with_model_parameters(return_item_node, self.model_parameters[scene_item_name])

        return return_node

    def assignment_target_name(self, assignment_node):
        if len(assignment_node.targets) != 1:
            return None
        if not isinstance(assignment_node.targets[0], ast.Name):
            return None
        return assignment_node.targets[0].id

    def call_node_with_model_parameters(self, call_node, model_parameter_information):
        parameter_values = model_parameter_information.get('parameter_values', dict())
        parameter_names = model_parameter_information.get('parameter_names', list())

        for parameter_name, parameter_value_source in parameter_values.items():
            parameter_value_node = self.model_parameter_value_node(parameter_value_source)
            parameter_was_applied = False

            for keyword_argument in call_node.keywords:
                if keyword_argument.arg == parameter_name:
                    keyword_argument.value = parameter_value_node
                    parameter_was_applied = True
                    break

            if parameter_was_applied:
                continue

            if parameter_name in parameter_names:
                parameter_index = parameter_names.index(parameter_name)
                if parameter_index < len(call_node.args):
                    call_node.args[parameter_index] = parameter_value_node
                    continue

            call_node.keywords.append(ast.keyword(arg=parameter_name, value=parameter_value_node))

        return call_node

    def model_parameter_value_node(self, parameter_value_source):
        parameter_value_source = parameter_value_source.strip()
        if not parameter_value_source:
            parameter_value_source = 'None'

        try:
            return ast.parse(parameter_value_source, mode='eval').body
        except SyntaxError as err:
            raise ValueError(f'Invalid model parameter value: {parameter_value_source}') from err




class SimulationClass(QObject):
    simulation_run_done_signal = pyqtSignal()
    scene_file_loaded_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.raytracer = raytrace_class.RaytracerClass()
        self.nr_of_rays_per_source = INITIAL_NR_OF_RAYS
        self.scene_file = None
        self.scene_param = None
        self.reset_simulation()

    def reset_simulation(self):
        self.reset_items()
        element_class.ElementClass.nr_of_elements  = 0
        light_class.LightSourceClass.nr_of_sources = 0
        display_class.DisplayClass.nr_of_displays  = 0

    def reset_items(self):
        self.sources  = list()
        self.elements = list()
        self.displays = list()
        self.scene_items = list()
        self.scene_model_parameter_definitions = list()
        self.info     = None

    @pyqtSlot(str)
    def load_scene(self, scene_file, param=None, model_parameters=None, start_simulation_after_loading_scene=None):
        path = pathlib.Path(scene_file)
        if not path.suffix:
            print(f'No scene file given: {scene_file}')
            return

        # First, reset the simulation
        self.reset_simulation()

        # Loading the scene file as a python module
        self.scene_file = os.path.normpath(scene_file)
        self.scene_param = param
        module_name = path.stem
        spec = importlib.util.spec_from_file_location(module_name, self.scene_file)
        module = importlib.util.module_from_spec(spec)

        try:
            if model_parameters:
                scene_ast = self.scene_ast_with_model_parameters(path, model_parameters)
                scene_code = compile(scene_ast, self.scene_file, 'exec')
                exec(scene_code, module.__dict__)
            else:
                spec.loader.exec_module(module)
        except Exception as err:
            print(f'{RED}Scene file could not be loaded: {scene_file}{WHITE}')
            print(f'{RED}Error message: {err}{WHITE}')
            self.scene_loaded_successfully = False
            return

        # Loading the scene itself, by running the "load_scene" method in the file
        try:
            func = module.load_scene
            sig = inspect.signature(func)
            if len(sig.parameters) == 0:    # If load_scene takes NO parameter, as for single static simulations, run without arguments
                items = module.load_scene()     # Run the "load_scene" method in each scene file
            else:       # If load_scene DOES take a parameter, as for multiple dynamic simulations in a loop, run with the param argument
                items = module.load_scene(param=param)
            self.scene_loaded_successfully = True
        except (RuntimeError, TypeError, NameError, OSError, AttributeError, ValueError) as err:
            print(f'{RED}Error in the scene file: {self.scene_file}{WHITE}')
            print(f'{RED}Error message: {err}{WHITE}')
            self.scene_loaded_successfully = False
            return

        scene_model_parameter_definitions = self.model_parameter_definitions_from_scene_file(path)

        if self.classify_items(items):  # Give every item in the different item lists its proper classification and ID, and check if the items are set correctly
            self.scene_model_parameter_definitions = scene_model_parameter_definitions
            print(f'Scene succesfully loaded: {self.scene_file}')
            print(self)
            self.scene_file_loaded_signal.emit()
        else:
            print(f'{RED}Scene NOT loaded, one of the items is not valid{WHITE}')

        if start_simulation_after_loading_scene is None:
            start_simulation_after_loading_scene = config.getboolean('scenes', 'start_simulation_after_loading_scene')

        if start_simulation_after_loading_scene:
            self.run()

        return

    def scene_ast_with_model_parameters(self, path, model_parameters):
        scene_source_code = path.read_text(encoding='utf-8')
        scene_ast = ast.parse(scene_source_code, filename=str(path))
        scene_ast = SceneModelParameterTransformer(model_parameters).visit(scene_ast)
        ast.fix_missing_locations(scene_ast)
        return scene_ast

    def model_parameter_definitions_from_scene_file(self, path):
        try:
            scene_source_code = path.read_text(encoding='utf-8')
            scene_ast = ast.parse(scene_source_code, filename=str(path))
        except (OSError, SyntaxError, UnicodeDecodeError) as err:
            print(f'{RED}Could not read model parameters from scene file: {path}{WHITE}')
            print(f'{RED}Error message: {err}{WHITE}')
            return list()

        load_scene_function = self.load_scene_function_from_scene_ast(scene_ast)
        if load_scene_function is None:
            return list()

        constructor_assignments = self.constructor_assignments_from_load_scene_function(load_scene_function)
        return self.model_parameter_definitions_from_return_statement(scene_source_code, load_scene_function, constructor_assignments)

    def load_scene_function_from_scene_ast(self, scene_ast):
        for scene_ast_node in scene_ast.body:
            if isinstance(scene_ast_node, ast.FunctionDef) and scene_ast_node.name == 'load_scene':
                return scene_ast_node
        return None

    def constructor_assignments_from_load_scene_function(self, load_scene_function):
        constructor_assignments = dict()
        for load_scene_node in ast.walk(load_scene_function):
            if not isinstance(load_scene_node, ast.Assign):
                continue
            if not isinstance(load_scene_node.value, ast.Call):
                continue
            for assignment_target in load_scene_node.targets:
                if isinstance(assignment_target, ast.Name):
                    constructor_assignments[assignment_target.id] = load_scene_node.value
        return constructor_assignments

    def model_parameter_definitions_from_return_statement(self, scene_source_code, load_scene_function, constructor_assignments):
        model_parameter_definitions = list()
        return_statement = self.return_statement_from_load_scene_function(load_scene_function)
        if return_statement is None:
            return model_parameter_definitions

        for return_item_index, return_item_node in enumerate(return_statement.value.elts):
            scene_item_name = None
            constructor_call_node = None

            if isinstance(return_item_node, ast.Name):
                scene_item_name = return_item_node.id
                constructor_call_node = constructor_assignments.get(scene_item_name)
            elif isinstance(return_item_node, ast.Call):
                scene_item_name = f'__return_item_{return_item_index}'
                constructor_call_node = return_item_node

            if constructor_call_node is None:
                continue

            model_parameter_definitions.append({
                'scene_item_name': scene_item_name,
                'constructor_name': self.name_from_call_node(constructor_call_node.func),
                'parameter_value_sources': self.parameter_value_sources_from_call_node(scene_source_code, constructor_call_node),
            })

        return model_parameter_definitions

    def return_statement_from_load_scene_function(self, load_scene_function):
        for load_scene_node in ast.walk(load_scene_function):
            if isinstance(load_scene_node, ast.Return) and isinstance(load_scene_node.value, (ast.List, ast.Tuple)):
                return load_scene_node
        return None

    def name_from_call_node(self, call_node):
        if isinstance(call_node, ast.Name):
            return call_node.id
        if isinstance(call_node, ast.Attribute):
            parent_name = self.name_from_call_node(call_node.value)
            if parent_name:
                return f'{parent_name}.{call_node.attr}'
            return call_node.attr
        return None

    def parameter_value_sources_from_call_node(self, scene_source_code, constructor_call_node):
        parameter_value_sources = dict()
        for keyword_argument in constructor_call_node.keywords:
            if keyword_argument.arg is None:
                continue
            parameter_value_source = ast.get_source_segment(scene_source_code, keyword_argument.value)
            if parameter_value_source is not None:
                parameter_value_sources[keyword_argument.arg] = parameter_value_source
        return parameter_value_sources

    # ToDo: items have numbers following the order of creation. Renumber the items following their order of listing
    def classify_items(self, items):
        self.reset_items()
        for item in items:
            if isinstance(item, light_class.LightSourceClass):
                self.scene_items.append(item)
                item.ID = len(self.sources)
                self.sources.append(item)
            elif isinstance(item, display_class.DisplayClass):
                self.scene_items.append(item)
                item.ID = len(self.displays)
                self.displays.append(item)
            elif isinstance(item, element_class.ElementClass):
                self.scene_items.append(item)
                item.ID = len(self.elements)
                self.elements.append(item)
            elif isinstance(item, str):
                self.info = item
            else:
                print(f'{RED}Item {item} is not recognised as a valid type{WHITE}')
                return False

        # Check if there are displays in the scene, and whether they are all imagers
        self.displays_present = True if self.displays else False
        print(f'Displays present: {self.displays_present}')
        self.displays_are_imagers = all(isinstance(display, imager_class.ImagerClass) for display in self.displays)
        print(f'All displays are imagers: {self.displays_are_imagers}')

        return True

    def run(self):
        if not self.scene_loaded_successfully:
            return

        # Explicitly reset (sources and) displays, otherwise the cast rays list keeps adding
        self.initialise_sources()
        self.initialise_displays()

        # Raytrace all beams over all elements and displays, treat a display as an element.
        for source in self.sources:
            if source.is_virtual: continue
            start_time = time.time()
            self.raytracer.raytrace_source(source=source, elements=self.elements + self.displays)   # Treat displays as a kind of beam dump too
            print(f'Processing time for ray tracing: {time.time()-start_time:.1f} s')

        # Process display information
        for display in self.displays:
            display.process_cast_rays()
            if isinstance(display, imager_class.ImagerClass):
                display.process_image()

        # Process virtual rays
        for source in self.sources:
            if not source.is_virtual: continue
            if ('imager 0' in source.origin)  and  self.displays:
                source.generate_ray(self.displays[0])
            # self.raytracer.raytrace_source(source=source, elements=self.elements + self.displays)   # Treat displays as a kind of beam dump too
            self.raytracer.raytrace_source(source=source, elements=self.elements)   # Treat displays as a kind of beam dump too
            source.process()

        self.simulation_run_done_signal.emit()

    def set_nr_of_rays_per_source(self, nr_of_rays_per_source):
        self.nr_of_rays_per_source = nr_of_rays_per_source

    def initialise_sources(self):
        for source in self.sources:
            if source.is_virtual: continue
            source.reset()      # This was grayed out, why? If not done this, rays will add up
            try:
                source.generate_rays(N_rays=self.nr_of_rays_per_source)
            except ValueError as err:
                raise ValueError(
                    f'Failed to generate rays for source ID={source.ID} ({source.name}): {err}'
                ) from err

    def initialise_displays(self):
        for display in self.displays:
            display.reset()

    def __str__(self):
        branch = '->'
        txt = ''
        txt += 'Simulation\n'
        txt += f' {branch} Sources\n'
        for source in self.sources:
            txt += f'    {branch} ' + source.__str__() + '\n'
        txt += f' {branch} Elements\n'
        for element in self.elements:
            txt += f'    {branch} ' + element.__str__() + '\n'
        txt += f' {branch} Displays\n'
        for display in self.displays:
            txt += f'    {branch} ' + display.__str__() + '\n'

        return txt
