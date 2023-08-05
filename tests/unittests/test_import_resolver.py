# pyright: reportOptionalMemberAccess=false

from typing import Optional
import unittest
import textwrap
from pathlib import Path

from tests import testutils
from tests.testutils import PackageGenerator, PyPrinceTestCase
from pyprince.parser.Project import Module, Project
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


class TestImportResolver(PyPrinceTestCase):
    def setUp(self):
        self.test_root = testutils.get_test_scenarios_dir()
        testutils.remove_imported_modules()

    def test_hiding_toplevel_import(self):
        """Test importing a package that exist in the stdlib as a subdirectory from the entrypoint works.
        It should shadow the builtin logging module."""
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import logging

                logging.say("hello main")
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "logging" / "__init__.py",
            textwrap.dedent(
                """
                def say(msg):
                    print(msg)
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        test_main = self.test_root / test_name / "main.py"
        project: Project = parse_project(test_main)
        log_module = project.get_module("logging")
        assert log_module is not None and log_module.path is not None
        self.assertEqual(Path(log_module.path), self.test_root / test_name / "logging/__init__.py")

    def test_relative_import(self):
        """Test relative import from package"""
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import reltest
                reltest.say("hello main")
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "reltest" / "__init__.py",
            textwrap.dedent(
                """
                from .impl import say
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "reltest" / "impl.py",
            textwrap.dedent(
                """
                def say(msg):
                    print(msg)
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        test_main = self.test_root / test_name / "main.py"
        project: Project = parse_project(test_main)
        self.assertIsNotNone(project.get_module("reltest"))
        self._assert_module_path(project.get_module("reltest.impl"), self.test_root / test_name / "reltest/impl.py")

    def test_resolving_sibling_module_import(self):
        """Test if a submodules imports a sibling package their parents gets resolved correctly"""
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import reltest
                reltest.say("hello main")
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "reltest" / "__init__.py",
            textwrap.dedent(
                """
                from .impl import say
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "reltest" / "impl.py",
            textwrap.dedent(
                """
                from .other import say
                def say(msg):
                    print(msg)
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "reltest" / "other.py",
            textwrap.dedent(
                """
                def say(msg):
                    print(msg)
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        test_main = self.test_root / test_name / "main.py"
        project: Project = parse_project(test_main)
        self.assertIsNotNone(project.get_module("reltest"))
        self._assert_module_path(project.get_module("reltest.impl"), self.test_root / test_name / "reltest/impl.py")
        self._assert_module_path(project.get_module("reltest.other"), self.test_root / test_name / "reltest/other.py")

    def test_import_from_dot(self):
        """Test if a submodules imports a sibling package their parents gets resolved correctly"""
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import reltest
                reltest.say("hello main")
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "reltest" / "__init__.py",
            textwrap.dedent(
                """
                from . import impl
                say = impl.say
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "reltest" / "impl.py",
            textwrap.dedent(
                """
                def say(msg):
                    print(msg)
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        test_main = self.test_root / test_name / "main.py"
        project: Project = parse_project(test_main)
        self.assertEqual(project.get_module("reltest").submodules[0].name, "reltest.impl")
        self._assert_module_path(project.get_module("reltest.impl"), self.test_root / test_name / "reltest/impl.py")

    def test_skipping_non_module_import(self):
        """if a from dot import contains an alias to a non-module name, it should be skipped"""
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import reltest
                reltest.say("hello main")
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "reltest" / "__init__.py",
            textwrap.dedent(
                """
                fixed_message = "Carpe Diem"
                from .impl import say
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "reltest" / "impl.py",
            textwrap.dedent(
                """
                from . import fixed_message
                def say(msg):
                    print(fixed_message + msg)
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        test_main = self.test_root / test_name / "main.py"
        project: Project = parse_project(test_main)
        self.assertEqual(project.get_module("reltest.impl").submodules[0].name, "reltest")

    def test_resolving_from_import_submodule_(self):
        """if we import with 'from package' a regular module, only the imported submodule
        should be in the dependencies and the empty parent package should be skipped"""
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                from reltest import impl
                impl.say("hello main")
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "reltest" / "__init__.py",
            textwrap.dedent(
                """
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "reltest" / "impl.py",
            textwrap.dedent(
                """
                def say(msg):
                    print(fixed_message + msg)
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        test_main = self.test_root / test_name / "main.py"
        project: Project = parse_project(test_main)
        main = project.get_module("main")
        self.assertEqual(len(main.submodules), 1)
        self.assertEqual(main.submodules[0].name, "reltest.impl")

    # TODO: test: from .. import util
    # TODO: test: from asd import *

    def _assert_module_path(self, module: Optional[Module], expected_path: Path):
        assert module is not None and module.path is not None
        self.assertEqual(Path(module.path), expected_path)


if __name__ == "__main__":
    unittest.main()
