import unittest
import textwrap
from pathlib import Path

from tests import testutils
from tests.testutils import PackageGenerator
from pyprince.parser.Project import Project
from pyprince.parser import parse_project

# Python import possibilities:
# import os
# import os.path
# from os import path
# from os.path import join
# from pathlib import Path
# from pathlib import *
# import .sub
# import ..sub
# import .sub.sub2
# from . import os
# import os as oo
# from os import path as osp
# from os.path import join as js
# import os, os.path
# import os, os.path as osp


class TestImportResolver(unittest.TestCase):
    def setUp(self):
        self.test_root = testutils.get_test_scenarios_dir()
        testutils.remove_imported_modules()

    def test_imported_names(self):
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import os
                import pathlib as pl
                import os.path
                import sys, abc
                from time import thread_time

                import other
                from utils import print_hello
                from utils import print_different_hello as diff
                from other import SomeGood, SomeDifferent as Diff

                print("hello main")
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "other.py",
            textwrap.dedent(
                """
                class SomeGood:
                    def __init__(self, name):
                        self.name = name


                class SomeDifferent:
                    def __init__(self, name_other):
                        self.name = name_other
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "utils.py",
            textwrap.dedent(
                """
                def print_hello():
                    print("Hello")

                def print_different_hello():
                    print("Hello")
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        test_main = self.test_root / test_name / "main.py"

        project: Project = parse_project(test_main)
        self.assertIsNotNone(project)
        self.assertIsNotNone(project.get_syntax_tree("os"))
        self.assertIsNotNone(project.get_syntax_tree("pathlib"))
        self.assertIsNotNone(project.get_syntax_tree("ntpath"))  # os.path gets "renamed"
        self.assertIsNone(project.get_syntax_tree("sys"))  # builtin
        self.assertIsNotNone(project.get_syntax_tree("abc"))
        self.assertIsNone(project.get_syntax_tree("time"))  # builtin

        self.assertIsNotNone(project.get_syntax_tree("utils"))
        self.assertIsNotNone(project.get_syntax_tree("other"))

    # TODO: test relative imports in subpackage
    # TODO: test start imports


if __name__ == "__main__":
    unittest.main()
