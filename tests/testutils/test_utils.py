from pyprince.parser.project import Module, ModuleIdentifier


def create_module(name: str, path: str = None) -> Module:
    module = Module(ModuleIdentifier(name, None), path, None)
    return module
