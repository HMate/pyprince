import sys
import os
from pathlib import Path
from typing import Optional, Union, List

import libcst
import libcst.matchers as cstm

from pyprince.parser.module_finder import ModuleFinder
from pyprince.parser.Project import ModuleIdentifier, Project, Module
from pyprince.logger import logger


def parse_project_new(entry_file: Path) -> Project:
    parser = ProjectParser()
    return parser.parse_project_from_entry_script(entry_file)


class ProjectParser:
    def __init__(self):
        self.proj = Project()
        self.finder = ModuleFinder()

    def parse_project_from_entry_script(self, entry_file: Path) -> Project:
        logger.info(f"Parsing started from {entry_file.absolute()}")

        # We need to set this, because native parser can segfault without throwing an exception
        # Also the native parser will fail when running multiple testcases,
        # because then it tries to initialize it multiple times.
        # See: https://github.com/Instagram/LibCST/issues/980
        os.environ["LIBCST_PARSER_TYPE"] = "pure"

        # For the root file of the project, it may not be in the sys.path, so we add it so importlib can find it
        sys.path = [str(entry_file.parent)] + sys.path
        self.finder.update_toplevel_module_paths(sys.path)
        
        root_name = entry_file.stem
        root: Module = self._parse_module(ModuleIdentifier(root_name))
        if root is None:
            sys.path = sys.path[1:]
            return self.proj

        self.proj.add_root_module(root.name)
        self.proj.add_module(root)

        if root.syntax_tree is not None:
            self.proj.add_syntax_tree(root.name, root.syntax_tree)
        remaining_modules = set(root.submodules)

        while len(remaining_modules) > 0:
            next_module: ModuleIdentifier = remaining_modules.pop()
            mod = self._parse_module(next_module)
            if mod is None:
                continue
            self.proj.add_module(mod)
            if mod.syntax_tree is not None:
                self.proj.add_syntax_tree(mod.name, mod.syntax_tree)
            for sub in mod.submodules:
                if not self.proj.has_module(sub.name):
                    remaining_modules.add(sub)
        sys.path = sys.path[1:]
        logger.success(f"Parsing finished for {entry_file.absolute()}")
        return self.proj

    def _parse_module(self, module_id: ModuleIdentifier) -> Module:
        try:
            return self._parse_module_unchecked(module_id)
        except Exception as e:
            logger.exception(f"Error in _parse_module for module {module_id.name}")
        mod = Module(module_id.name, None, None)
        return mod

    def _parse_module_unchecked(self, module_id: ModuleIdentifier) -> Module:
        logger.info(f"Parsing module {module_id.name}")
        spec = self.finder.find_spec(module_id.name) if module_id.spec is None else module_id.spec
        if spec is None or spec.origin is None:
            # I guess there can be multiple reasons.
            # One reason is when the import is platform specific. For example pwd is unix only
            mod = Module(module_id.name, None, None)
            return mod
        if (
            (spec.origin in ["built-in", "frozen"])
            or (spec.origin.endswith(".pyd"))
            or (spec.origin.endswith(".pyc"))
            or (spec.origin.endswith(".pyo"))
        ):
            mod = Module(module_id.name, spec.origin, None)
            return mod

        if module_id.name == "pydoc_data.topics":
            # TODO: Right now libcst crashes on this file when parsing or when enumerating imports.
            # For now it does not affect us if we just skip the file.
            # In the future we may want to switch to parso/ast module, or hope it gets fixed.
            mod = Module(module_id.name, spec.origin, None)
            return mod

        content = Path(spec.origin).read_bytes()  # TODO: DI FileLoader
        cst: libcst.Module = libcst.parse_module(content)
        mod = Module(module_id.name, spec.origin, cst)

        submodules = self._extract_module_import_names(cst)
        for sub in submodules:
            sub_id = self.finder.find_module(sub, mod)
            mod.submodules.append(sub_id)
        return mod

    def _extract_module_import_names(self, root_cst: libcst.Module) -> List[str]:
        # go through all the import statements and parse out the modules
        submodules: List[str] = []
        import_exprs = cstm.findall(root_cst, cstm.OneOf(cstm.Import(), cstm.ImportFrom()))
        for import_expr in import_exprs:
            logger.debug(f"- {root_cst.code_for_node(import_expr)}")
            # get module name. Right now we dont use the module alias name, so we dont save it.
            # TODO(0.0.3): Lets handle full import names - see modules like __main__, _bootstrap in different subfolders.
            if cstm.matches(import_expr, cstm.Import()):
                assert isinstance(import_expr, libcst.Import)
                for alias in import_expr.names:
                    import_name = alias.evaluated_name
                    if import_name not in submodules:
                        submodules.append(import_name)
            if cstm.matches(import_expr, cstm.ImportFrom()):
                # cases:
                # If module is None and relative is none, that cannot happen. -> log error
                # - from . or ..  -> module is None, and relative is not empty
                # - from .foo -> module is a Name and relative is not empty
                # - from foo -> module is a Name and relative is empty
                # - from foo.bar -> module is an Attribute and relative is empty
                assert isinstance(import_expr, libcst.ImportFrom)
                import_name = None
                if isinstance(import_expr.module, libcst.Attribute):
                    import_name = root_cst.code_for_node(import_expr.module)
                elif isinstance(import_expr.module, libcst.Name):
                    import_name = import_expr.module.value
                else:
                    logger.warning(f"Could not find import name - {import_expr}")
                if import_name and (import_name not in submodules):
                    submodules.append(import_name)
        return submodules
