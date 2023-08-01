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
            "main", "io", "_io", "abc", "_abc", "_py_abc", "_weakrefset", "_weakref", "types", "sys", "functools", "collections", "warnings", "linecache", 
            "weakref", "tokenize", "heapq", "gc", "_warnings", "_collections_abc", "os", "subprocess", "contextlib", "time", "signal", "_functools", "keyword", 
            "_collections", "re", "copy", "stat", "_locale", "builtins", "grp", "_heapq", "traceback", "operator", "itertools", "_thread", "sre_constants", 
            "enum", "errno", "threading", "select", "_stat", "sre_compile", "pwd", "_winapi", "token", "codecs", "reprlib", "nt", "_signal", "typing", 
            "posix", "posixpath", "_posixsubprocess", "msvcrt", "_threading_local", "_codecs", "atexit", "tracemalloc", "doctest", "argparse", "_operator", 
            "org.python.core", "_sre", "sre_parse", "ntpath", "selectors", "_tracemalloc", "textwrap", "__future__", "inspect", "copyreg", "unicodedata", 
            "gettext", "importlib.machinery", "struct", "_struct", "math", "genericpath", "shutil", "difflib", "unittest", "suite", "ast", "collections.abc", 
            "_imp", "bz2", "_compression", "pickle", "loader", "encodings", "importlib", "locale", "encodings.aliases", "dis", "_bootlocale", "signals", 
            "_bootstrap", "pdb", "fnmatch", "readline", "_bootstrap_external", "opcode", "result", "winreg", "string", "lzma", "async_case", "_lzma", "runner", 
            "zlib", "case", "_pickle", "glob", "code", "marshal", "encodings.mbcs", "zipfile", "_log", "pprint", "tarfile", "_frozen_importlib", "binascii", 
            "shlex", "_string", "_compat_pickle", "util", "_ast", "getopt", "importlib.metadata", "_opcode", "logging", "gzip", "pathlib", "bdb", 
            "importlib.abc", "__main__", "pydoc", "cmd", "_bz2", "runpy", "tty", "_frozen_importlib_external", "configparser", "tempfile", "email", "pkgutil", 
            "platform", "importlib.util", "email.parser", "codeop", "plistlib", "datetime", "pydoc_data.topics", "asyncio", "urllib.parse", "runners", 
            "base_events", "termios", "py_compile", "unix_events", "java.lang", "http.server", "_winreg", "mimetypes", "sysconfig", "socketserver", "vms_lib", 
            "threads", "_osx_support", "csv", "_csv", "ssl", "pep517", "_ssl", "zipimport", "random", "locks", "webbrowser", "transports", "exceptions", 
            "email.message", "xml.parsers.expat", "_datetime", "queues", "streams", "windows_events", "hashlib", "uu", "log", "email.utils", "email._parseaddr", 
            "html", "concurrent.futures", "tasks", "http.client", "_aix_support", "email.generator", "email._encoded_words", "_sha256", "_md5", "statistics", 
            "numbers", "_overlapped", "email._policybase", "fractions", "_random", "socket", "email.feedparser", "base64", "_sha1", "_sha512", "futures", 
            "coroutines", "_statistics", "http", "email.iterators", "decimal", "array", "_blake2", "distutils", "_asyncio", "email.charset", "_strptime", 
            "protocols", "calendar", "_sha3", "optparse", "events", "email.quoprimime", "contextvars", "bisect", "email.policy", "_bisect", "_pydecimal", 
            "quopri", "pyexpat", "_bootsubprocess", "_hashlib", "email.encoders", "_contextvars", "email.contentmanager", "html.entities", "email.base64mime", 
            "_socket", "_decimal", "email.headerregistry", "email.errors"
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
