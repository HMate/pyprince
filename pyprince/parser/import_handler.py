import collections.abc
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

import libcst
import libcst.matchers as cstm

from pyprince.parser import constants
from pyprince.parser.module_finder import ModuleFinder
from pyprince.parser.project import Module
from pyprince.logger import logger


class ImportHandler:
    def __init__(self, module_finder: ModuleFinder) -> None:
        self.finder = module_finder

    def resolve_module_imports(self, mod: Module):
        if mod.syntax_tree is None:
            return

        # TODO: If submodule is just an alias from an import, we will have to interpret code, or load the parent module.
        module_imports, from_imports = self._extract_module_import_names(mod.syntax_tree)
        for imp in module_imports:
            sub_id = self.finder.find_top_level_module(imp.package_name)
            mod.add_submodule(sub_id)
        for imp in from_imports:
            if imp.is_relative_import():
                assert imp.relative_level is not None
                package_id = self.finder.find_relative_module(imp.package_name, imp.relative_level, mod.id)
                if package_id is None:
                    continue
            else:
                if imp.package_name is None:
                    logger.warning(f"Empty import name for an absolute import - {imp}")
                    continue
                package_id = self.finder.find_top_level_module(imp.package_name)

            if (
                (package_id.spec is None)
                or (not self.finder.is_package_module(package_id.spec.origin))
                or imp.targets == constants.STAR_IMPORT
            ):
                mod.add_submodule(package_id)
                continue
            for target in imp.targets:
                module_candidate = f"{package_id.name}.{target}"
                sub_id = self.finder.try_find_top_level_module(module_candidate)
                if sub_id is None:
                    mod.add_submodule(package_id)
                else:
                    mod.add_submodule(sub_id)

    def _extract_module_import_names(
        self, root_cst: libcst.Module
    ) -> Tuple[List["ImportDescription"], List["FromImportDescription"]]:
        # go through all the import statements and parse out the modules
        package_imports: List[ImportDescription] = []
        from_imports: List[FromImportDescription] = []
        import_exprs = cstm.findall(root_cst, cstm.OneOf(cstm.Import(), cstm.ImportFrom()))
        for import_expr in import_exprs:
            logger.debug(f"- {root_cst.code_for_node(import_expr)}")
            # get module name. Right now we dont use the module alias name, so we dont save it.
            if cstm.matches(import_expr, cstm.Import()):
                assert isinstance(import_expr, libcst.Import)
                for alias in import_expr.names:
                    import_desc = ImportDescription(alias.evaluated_name)
                    if import_desc not in package_imports:
                        package_imports.append(import_desc)
            if cstm.matches(import_expr, cstm.ImportFrom()):
                # cases:
                # If module is None and relative is none, that cannot happen. -> log error
                # - from . or ..  -> module is None, and relative is not empty
                # - from .foo -> module is a Name and relative is not empty
                # - from foo -> module is a Name and relative is empty
                # - from foo.bar -> module is an Attribute and relative is empty
                assert isinstance(import_expr, libcst.ImportFrom)
                step_level = len(import_expr.relative)
                module_name = None
                if isinstance(import_expr.module, libcst.Attribute):
                    module_name = root_cst.code_for_node(import_expr.module)
                elif isinstance(import_expr.module, libcst.Name):
                    module_name = import_expr.module.value

                if isinstance(import_expr.names, collections.abc.Sequence):
                    targets = [alias.evaluated_name for alias in import_expr.names]
                    desc = FromImportDescription(module_name, targets, step_level)
                    if desc not in from_imports:
                        from_imports.append(desc)
                else:
                    desc = FromImportDescription(module_name, constants.STAR_IMPORT, step_level)
                    if desc not in from_imports:
                        from_imports.append(desc)

        return package_imports, from_imports


@dataclass(eq=True, frozen=True)
class ImportDescription:
    """ex: import package_name"""

    package_name: str


@dataclass(eq=True, frozen=True)
class FromImportDescription:
    """ex: from package_name import target
    ex: from ..package_name import target
             ^^-- relative_level = 2
    """

    package_name: Optional[str]
    targets: Union[str, List[str]]
    relative_level: Optional[int] = None

    def is_relative_import(self) -> bool:
        return self.relative_level is not None and self.relative_level > 0
