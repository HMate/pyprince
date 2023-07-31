from pathlib import Path
import textwrap

import tests.testutils as testutils
from tests.testutils import PackageGenerator, PyPrinceTestCase
from pyprince.parser import parse_project, Project
from pyprince import generators, serializer


class TestDescribeModuleDependency(PyPrinceTestCase):
    def setUp(self):
        self.test_root = testutils.get_test_scenarios_dir()
        testutils.remove_imported_modules()

    def test_single_dependency(self):
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
        expected = {"nodes": ["main", "util"], "edges": {"main": ["util"]}}
        actual = generators.describe_module_dependencies(project)
        self.assertDictEqual(expected, actual.to_dict())

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
        self.assertEqual(expected, actual)

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
        self.assertEqual(expected, actual)

    def test_io_module(self):
        """io modue has built-in dependencies on _io, _abc and import inside try-catch blocks
        We check if the parser gathers these correctly.
        """
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import io
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        project: Project = parse_project(self.test_root / test_name / "main.py")
        # fmt: off
        expectedNodes = [
            "main", "io", "abc", "_py_abc", "_abc", "_io", "_weakrefset", "types", 
            "sys", "functools", "_weakref", "typing", "contextlib", "_collections_abc", "collections", "reprlib", "operator", 
            "copy", "re", "enum", "sre_constants", "_operator", "builtins", "_locale", "warnings", "heapq", "copyreg", "itertools", "collections.abc", 
            "keyword", "weakref", "_warnings", "_functools", "traceback", "_collections", "tracemalloc", "org.python.core", "_heapq", "_thread", 
            "sre_compile", "sre_parse", "_sre", "gc", "atexit", "fnmatch", "pickle", "ntpath", "linecache", "unicodedata", "pprint", "struct", "_struct", 
            "time", "_pickle", "_compat_pickle", "genericpath", "posixpath", "tokenize", "stat", "doctest", "os", "nt", "_tracemalloc", "inspect", "argparse", 
            "codecs", "unittest", "runner", "async_case", "encodings", "textwrap", "_winapi", "dis", "posix", "suite", "signals", "_codecs", "importlib.machinery", 
            "_imp", "gettext", "string", "subprocess", "loader", "result", "opcode", "_bootstrap_external", "case", "__future__", "shutil", "_stat", "_string", 
            "token", "pwd", "encodings.mbcs", "importlib", "ast", "signal", "_opcode", "pdb", "grp", "zipfile", "difflib", "locale", "_bootstrap", "_ast", 
            "_bootlocale", "tarfile", "bdb", "binascii", "importlib.util", "errno", "msvcrt", "selectors", "lzma", "code", "codeop", "threading", "runpy", 
            "readline", "_lzma", "getopt", "bz2", "zlib", "_posixsubprocess", "pkgutil", "select", "gzip", "_threading_local", "glob", "pydoc", "_signal", 
            "platform", "__main__", "plistlib", "math", "pydoc_data.topics", "webbrowser", "_frozen_importlib", "zipimport", "shlex", "_bz2", "tempfile", 
            "cmd", "_frozen_importlib_external", "email.message", "urllib.parse", "random", "vms_lib", "hashlib", "uu", "_sha3", "py_compile", "_md5", 
            "encodings.aliases", "_sha1", "_hashlib", "_sha256", "http.server", "optparse", "_random", "_blake2", "sysconfig", "email.iterators", 
            "mimetypes", "_osx_support", "_compression", "email.policy", "_aix_support", "quopri", "email.utils", "winreg", "socketserver", "socket", 
            "marshal", "datetime", "email", "email._policybase", "java.lang", "statistics", "email.contentmanager", "_statistics", "_socket", 
            "email.generator", "_sha512", "_datetime", "tty", "_winreg", "email.headerregistry", "email._encoded_words", "_strptime", "distutils", 
            "xml.parsers.expat", "base64", "fractions", "pyexpat", "http", "logging", "numbers", "termios", "calendar", "html", "http.client", 
            "_bootsubprocess", "decimal", "array", "email.parser", "ssl", "email.errors", "email.charset", "email._parseaddr", "bisect", "_bisect", 
            "email.feedparser", "html.entities", "email.encoders", "email.quoprimime", "_decimal", "_ssl", "_pydecimal", "email.base64mime", "contextvars", "_contextvars"
        ]
        # fmt: on
        # module dependency nodes should be unique.
        actual = generators.describe_module_dependencies(project).to_dict()
        self.assertListElementsAreUnique(actual["nodes"])
        self.maxDiff = None
        self.assertCountEqual(actual["nodes"], expectedNodes)

    def test_argparse_module(self):
        """argparse module has 2 interesting scenarios:
        - dependecies on pyd modules (unicodedata.pyd)
        - uses the pwd module which is unix only
        We dont parse the code for these but we should still register the modules.
        """
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import argparse
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        project: Project = parse_project(self.test_root / test_name / "main.py")
        expectedNodes = ["main", "argparse", "unicodedata", "pwd"]
        actual = generators.describe_module_dependencies(project).to_dict()
        self.assertContains(actual["nodes"], expectedNodes)

    # TODO: Additional test case: create 2 submodules with the same name, see if node names are unique
