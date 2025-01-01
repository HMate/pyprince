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

    def test_import_module(self):
        """Test importing a simple local module."""
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import sub
                sub.say("hello main")
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "sub.py",
            textwrap.dedent(
                """
                def say(msg):
                    print(msg)
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        test_main = self.test_root / test_name / "main.py"
        project: Project = parse_project(test_main, shallow_stdlib=False)
        self._assert_module_path(project.get_module("sub"), self.test_root / test_name / "sub.py")

    def test_import_package(self):
        """Test importing a simple local package."""
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import sub
                sub.say("hello main")
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "sub" / "__init__.py",
            textwrap.dedent(
                """
                def say(msg):
                    print(msg)
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        test_main = self.test_root / test_name / "main.py"
        project: Project = parse_project(test_main, shallow_stdlib=False)
        self._assert_module_path(project.get_module("sub"), self.test_root / test_name / "sub/__init__.py")

    def test_import_from_module(self):
        """Test importing with from module import syntax."""
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                from sub import say
                say("hello main")
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "sub.py",
            textwrap.dedent(
                """
                def say(msg):
                    print(msg)
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        test_main = self.test_root / test_name / "main.py"
        project: Project = parse_project(test_main, shallow_stdlib=False)
        self._assert_module_path(project.get_module("sub"), self.test_root / test_name / "sub.py")

    def test_import_submodule_with_absolute_name(self):
        """Test importing a submodule with an absolute module name."""
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import sub.subsub
                sub.subsub.say("hello main")
                """
            ).lstrip(),
        )
        gen.add_file(test_name / "sub" / "__init__.py", "")
        gen.add_file(
            test_name / "sub" / "subsub.py",
            textwrap.dedent(
                """
                def say(msg):
                    print(msg)
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        test_main = self.test_root / test_name / "main.py"
        project: Project = parse_project(test_main, shallow_stdlib=False)
        self._assert_module_path(project.get_module("sub.subsub"), self.test_root / test_name / "sub/subsub.py")
        self._assert_module_depends_on(project.get_module("main"), "sub.subsub")

    def test_import_submodule_with_long_absolute_name(self):
        """Test importing a submodule with an absolute module name with more then one levels."""
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import sub.subsub.moresub.evenmore
                sub.subsub.moresub.evenmore.say("hello main")
                """
            ).lstrip(),
        )
        gen.add_file(test_name / "sub" / "__init__.py", "")
        gen.add_file(test_name / "sub" / "subsub" / "__init__.py", "")
        gen.add_file(test_name / "sub" / "subsub" / "moresub" / "__init__.py", "")
        gen.add_file(
            test_name / "sub" / "subsub" / "moresub" / "evenmore" / "__init__.py",
            textwrap.dedent(
                """
                def say(msg):
                    print(msg)
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        test_main = self.test_root / test_name / "main.py"
        project: Project = parse_project(test_main, shallow_stdlib=False)
        self._assert_module_path(
            project.get_module("sub.subsub.moresub.evenmore"),
            self.test_root / test_name / "sub/subsub/moresub/evenmore/__init__.py",
        )
        self._assert_module_depends_on(project.get_module("main"), "sub.subsub.moresub.evenmore")

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
        project: Project = parse_project(test_main, shallow_stdlib=False)
        self._assert_module_path(project.get_module("logging"), self.test_root / test_name / "logging/__init__.py")

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
        project: Project = parse_project(test_main, shallow_stdlib=False)
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
        project: Project = parse_project(test_main, shallow_stdlib=False)
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
        project: Project = parse_project(test_main, shallow_stdlib=False)
        self.assertEqual(project.get_module("reltest").submodules[0].name, "reltest.impl")
        self._assert_module_path(project.get_module("reltest.impl"), self.test_root / test_name / "reltest/impl.py")

    def test_skipping_non_module_dot_import(self):
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
        project: Project = parse_project(test_main, shallow_stdlib=False)
        self.assertEqual(project.get_module("reltest.impl").submodules[0].name, "reltest")

    def test_resolving_from_import_submodule(self):
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
        gen.add_file(test_name / "reltest" / "__init__.py", "")
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
        project: Project = parse_project(test_main, shallow_stdlib=False)
        main = project.get_module("main")
        self.assertEqual(len(main.submodules), 1)
        self.assertEqual(main.submodules[0].name, "reltest.impl")

    def test_resolving_from_import_module_with_same_name(self):
        """If we import with 'from package' an object, with the same name as the module,
        check we depend on the correct module."""
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                from reltest import reltest
                reltest("hello main")
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "reltest.py",
            textwrap.dedent(
                """
                def reltest(msg):
                    print(msg)
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        test_main = self.test_root / test_name / "main.py"
        project: Project = parse_project(test_main, shallow_stdlib=False)
        self._assert_module_depends_on(project.get_module("main"), "reltest")

    def test_multidot_import(self):
        """Test is multiple dots for relative imports work."""
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import reltest.sub
                reltest.sub.say("hello main")
                """
            ).lstrip(),
        )
        gen.add_file(test_name / "reltest" / "__init__.py", "")
        gen.add_file(
            test_name / "reltest" / "sub" / "__init__.py",
            textwrap.dedent(
                """
                from ..sayer import say
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "reltest" / "sayer.py",
            textwrap.dedent(
                """
                def say(msg):
                    print(msg)
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        test_main = self.test_root / test_name / "main.py"
        project: Project = parse_project(test_main, shallow_stdlib=False)
        self._assert_module_depends_on(project.get_module("reltest.sub"), "reltest.sayer")

    def test_relative_sub_import(self):
        """Test relative import with a complex package name works."""
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import reltest.rootsub
                reltest.rootsub.say_hello("main")
                """
            ).lstrip(),
        )
        gen.add_file(test_name / "reltest" / "__init__.py", "")
        gen.add_file(
            test_name / "reltest" / "rootsub.py",
            textwrap.dedent("""from .sometest.sub import say_hello""").lstrip(),
        )
        gen.add_file(test_name / "reltest" / "sometest" / "__init__.py", "")
        gen.add_file(
            test_name / "reltest" / "sometest" / "sub.py",
            textwrap.dedent(
                """
                def say_hello(msg):
                    print("hello " + msg)
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        test_main = self.test_root / test_name / "main.py"
        project: Project = parse_project(test_main, shallow_stdlib=False)
        self._assert_module_depends_on(project.get_module("reltest.rootsub"), "reltest.sometest.sub")

    def test_star_import(self):
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                from reltest import *
                say("main")
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "reltest" / "__init__.py",
            textwrap.dedent(
                """
                def say(msg):
                    print(fixed_message + msg)
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        test_main = self.test_root / test_name / "main.py"
        project: Project = parse_project(test_main, shallow_stdlib=False)
        self._assert_module_depends_on(project.get_module("main"), "reltest")

    def _assert_module_path(self, module: Optional[Module], expected_path: Path):
        assert module is not None and module.path is not None
        self.assertEqual(Path(module.path), expected_path)

    def _assert_module_depends_on(self, module: Optional[Module], *expected_module_names: str):
        assert module is not None
        self.assertGreaterEqual(len(module.submodules), len(expected_module_names))
        submodules = [sub.name for sub in module.submodules]
        self.assertCountEqual(submodules, expected_module_names)


if __name__ == "__main__":
    unittest.main()
