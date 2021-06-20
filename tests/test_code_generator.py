import unittest
from pathlib import Path
import textwrap

import tests.testutils as testutils
from tests.testutils import PackageGenerator
from pyprince.parser.Project import Project
from pyprince.parser import parse_project


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

        test_main = self.test_root / test_name / "main.py"
        project: Project = parse_project(test_main)
        expected = """print("Hello pyparser")\n"""
        actual = project.generate_code()
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

        test_main = self.test_root / test_name / "main.py"
        project: Project = parse_project(test_main)
        expected = textwrap.dedent(
            """

            def main():
                everybody = ["Mom", "Dad"] + ["Grandpa", "Cousin"]
                print(f"Family: {everybody}")
            """
        )
        actual = project.generate_code_one_level_expanded("main")
        self.assertEqual(expected, actual)

    # TODO: test scenarios:
    # - nest code in different module than main - maybe nest previously nested code -> definition maybe in another module
    # - substitute named arg
    # - substitute star, or kw args in called functions
    # - call functon from namespaced
    # - call void functon
    # - call async functon
    # - call functon nested in another function
    # - call functon nested in another expression (with statement? multiple assignments?)
    # - call multiple functons nested in another function
    # - call multiline function
    # - called functon has multiple returns
    # - called functon has multiple returns
    # - create class
    # - call class method
    # - return inside called functions loop
    # - no function implmentation found
    # - exceptions inside, outside, func called/returning in except, finally etc

    # optimization scenario: (needs dependency discovery)
    # - call Optional[], if ret is None:... -> ret is none can be merged into function code
    # - same if condition can be merged