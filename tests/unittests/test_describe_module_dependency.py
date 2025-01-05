import textwrap

from hamcrest import assert_that, equal_to, is_
from tests import testutils
from pyprince.parser import Project, Module, ModuleIdentifier, Package, PackageType
from pyprince import generators, serializer


class TestDescribeModuleDependency(testutils.PyPrinceTestCase):
    def test_single_dependency(self):
        project = Project()
        main_mod = Module(ModuleIdentifier("main", None), "main.py", None)
        util_mod = Module(ModuleIdentifier("util", None), "util.py", None)
        main_mod.add_submodule(util_mod.id)
        project.add_root_module(main_mod.name)
        project.add_module(main_mod)
        project.add_module(util_mod)
        actual = generators.describe_module_dependencies(project)
        expected = {"nodes": ["main", "util"], "edges": {"main": ["util"]}}
        assert_that(actual.to_dict(), equal_to(expected))

    def test_describe_module_dependencies_with_packages(self):
        project = Project()
        main_mod = Module(ModuleIdentifier("main", None), "main.py", None)
        os_mod = Module(ModuleIdentifier("os", None), "os.py", None)
        main_mod.add_submodule(os_mod.id)
        project.add_root_module(main_mod.name)
        project.add_module(main_mod)
        project.add_module(os_mod)
        project.add_package(Package("main", None, PackageType.Local))
        project.add_package(Package("stdlib", None, PackageType.StandardLib))
        project.get_package("main").add_module(main_mod.id)
        project.get_package("stdlib").add_module(os_mod.id)
        actual = generators.describe_module_dependencies(project)

        expected = {
            "nodes": ["main", "os"],
            "packages": {"main": ["main"], "stdlib": ["os"]},
            "edges": {"main": ["os"]},
        }
        assert_that(actual.to_dict(), equal_to(expected))

    def test_json_serialize(self):
        deps = generators.DependencyDescriptor()
        deps.add_node("main")
        deps.add_node("util")
        deps.add_edge("main", "util")

        expected = textwrap.dedent(
            """\
            {
              "nodes": [
                "main",
                "util"
              ],
              "edges": {
                "main": [
                  "util"
                ]
              }
            }"""
        )
        actual = serializer.to_json(deps)
        assert_that(actual, equal_to(expected))

    def test_graphviz_serialize(self):
        deps = generators.DependencyDescriptor()
        deps.add_node("main")
        deps.add_node("util")
        deps.add_node("belize")
        deps.add_node("femme")
        deps.add_edge("main", "util")
        deps.add_edge("main", "belize")
        deps.add_edge("util", "femme")
        deps.add_edge("femme", "main")
        expected = textwrap.dedent(
            """\
            digraph G {
                "main" -> "util"
                "main" -> "belize"
                "util" -> "femme"
                "femme" -> "main"
            }"""
        )
        actual = serializer.to_graphviz_dot(deps)
        assert_that(actual, equal_to(expected))
