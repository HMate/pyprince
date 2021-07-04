import unittest
from pathlib import Path
import textwrap

import tests.testutils as testutils
from tests.testutils import PackageGenerator
from pyprince.parser import parse_project, Project
from pyprince.transformators import Transformator
from pyprince import generators


class TestCodeGenerator(unittest.TestCase):
    def setUp(self):
        self.test_root = testutils.get_test_scenarios_dir()
        testutils.remove_imported_modules()

    def test_code_generate_simplest(self):
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent("""print("Hello pyparser")\n"""),
        )
        gen.generate_files(self.test_root)

        project: Project = parse_project(self.test_root / test_name / "main.py")
        expected = """print("Hello pyparser")\n"""
        actual = generators.generate_code(project)
        self.assertEqual(expected, actual)

    def test_code_generate_local_func(self):
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                def some_functionality(parents, relatives):
                    return parents + relatives


                def main():
                    everybody = some_functionality(["Mom", "Dad"], ["Grandpa", "Cousin"])
                    print(f"Family: {everybody}")
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        project: Project = parse_project(self.test_root / test_name / "main.py")
        expected = textwrap.dedent(
            """
            def main():
                everybody = ["Mom", "Dad"] + ["Grandpa", "Cousin"]
                print(f"Family: {everybody}")
            """
        ).strip()
        transformed = Transformator(project).expand_function("main").proj.get_function("main")
        actual = generators.render_node(transformed).strip()  # type: ignore
        self.assertEqual(expected, actual)

    def test_code_inject_void_func(self):
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                def some_functionality(parents, relatives):
                    print(f"Family: {parents + relatives}")


                def main():
                    some_functionality(["Mom", "Dad"], ["Grandpa", "Cousin"])
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        project: Project = parse_project(self.test_root / test_name / "main.py")
        expected = textwrap.dedent(
            """
            def main():
                print(f"Family: {["Mom", "Dad"] + ["Grandpa", "Cousin"]}")
            """
        ).strip()
        transformed = Transformator(project).expand_function("main").proj.get_function("main")
        actual = generators.render_node(transformed).strip()  # type: ignore
        self.assertEqual(expected, actual)

    def test_code_inject_module_func(self):
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                from util import some_functionality

                def main():
                    some_functionality(["Mom", "Dad"], ["Grandpa", "Cousin"])
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "util.py",
            textwrap.dedent(
                """
                def some_functionality(parents, relatives):
                    print(f"Family: {parents + relatives}")
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        project: Project = parse_project(self.test_root / test_name / "main.py")
        expected = textwrap.dedent(
            """
            def main():
                print(f"Family: {["Mom", "Dad"] + ["Grandpa", "Cousin"]}")
            """
        ).strip()
        transformed = Transformator(project).expand_function("main").proj.get_function("main")
        actual = generators.render_node(transformed).strip()  # type: ignore
        self.assertEqual(expected, actual)

    # TODO: test scenarios:
    # - substitute named arg
    # - substitute star, or kw args in called functions
    # - call functon from namespace
    # - call functon from alias
    # - call empty return functon
    # - call async functon
    # - call functon nested in another function
    # - call functon nested in another expression (with statement? multiple assignments?)
    # - call multiple functons nested in another function
    # - call multiline function
    # - expand function that originated from another expanded function, and is declared in module thats unimported by main
    # - expand function that is declared in module thats unimported by main, and function with this name can be found in multiple modules
    # - called functon has multiple returns
    # - called recursive functon
    # - walrus := assignment
    # - create class
    # - call class method
    # - threads
    # - return inside called functions loop
    # - no function implementation found
    # - exceptions inside, outside, func called/returning in except, finally etc

    # Normalization - Convert/transform complicated language constructs to a given simplified language subset
    # - Classes are functions that receive a common data structure
    # - walrus := assignment
    # - async/await
    # - exception try/catch/finally
    # - threads
    # - decorators/wrappers
    # - generators/comprehensions
    # - lambdas
    # - for <-> while
    # - list.map() -> to for loop
    # - multiple assigns, statements can be spread to multiple lines

    # optimization scenario: (needs dependency discovery)
    # - call Optional[], if ret is None:... -> ret is none can be merged into function code
    # - same if condition can be merged
    # - operations on literals can be executed statically. eg [1]+[2] = [1, 2]
    #   - This can be generlaized-> move literal operations together as possible, execute statically
