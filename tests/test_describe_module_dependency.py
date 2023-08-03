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
        We check if the parser gathers all deps correctly.
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
            "main", "io", "abc", "_abc", "_io", "_py_abc", "_weakrefset", "_weakref", "types", "functools", "collections", "sys", "copy", "reprlib", "keyword", 
            "operator", "copyreg", "itertools", "_functools", "_operator", "warnings", "_collections_abc", "re", "sre_compile", "enum", "typing", "tracemalloc", 
            "_collections", "_thread", "linecache", "traceback", "_tracemalloc", "weakref", "org.python.core", "builtins", "_warnings", "_sre", "fnmatch", 
            "sre_parse", "sre_constants", "heapq", "_locale", "ntpath", "collections.abc", "os", "contextlib", "gc", "posixpath", "nt", "atexit", "pickle", 
            "posix", "tokenize", "genericpath", "_compat_pickle", "argparse", "pprint", "pwd", "struct", "unicodedata", "subprocess", "_posixsubprocess", "token", 
            "time", "signal", "_heapq", "select", "_signal", "grp", "doctest", "string", "__future__", "errno", "gettext", "pdb", "codecs", "stat", "textwrap", 
            "_struct", "_winapi", "unittest", "_pickle", "unittest.async_case", "threading", "pydoc", "encodings", "cmd", "msvcrt", "unittest.result", "email.message", 
            "unittest.case", "encodings.mbcs", "_string", "asyncio", "_threading_local", "shutil", "runpy", "shlex", "unittest.main", "selectors", "difflib", 
            "pydoc_data.topics", "tarfile", "asyncio.windows_events", "importlib.util", "asyncio.exceptions", "_codecs", "email._policybase", "zlib", "_stat", 
            "tempfile", "unittest.runner", "unittest._log", "glob", "getopt", "asyncio.subprocess", "asyncio.unix_events", "email.iterators", "locale", 
            "unittest.loader", "dis", "random", "asyncio.runners", "logging", "asyncio.protocols", "_frozen_importlib_external", "_random", "asyncio.streams", 
            "math", "platform", "socket", "encodings.aliases", "email.generator", "asyncio.threads", "importlib._bootstrap_external", "_winreg", "asyncio.events", 
            "zipfile", "asyncio.base_events", "email.policy", "bdb", "inspect", "py_compile", "email.contentmanager", "java.lang", "urllib.parse", "email._encoded_words", 
            "asyncio.locks", "opcode", "__main__", "vms_lib", "marshal", "unittest.util", "gzip", "asyncio.transports", "importlib.machinery", "unittest.signals", 
            "importlib._bootstrap", "email", "array", "_overlapped", "_asyncio", "webbrowser", "readline", "asyncio.log", "code", "unittest.suite", "binascii", 
            "tty", "statistics", "email.charset", "asyncio.tasks", "email.utils", "_socket", "_bootlocale", "asyncio.futures", "http.server", "pkgutil", "sysconfig", 
            "bz2", "email.quoprimime", "lzma", "asyncio.queues", "asyncio.coroutines", "concurrent.futures", "email.errors", "html", "email.encoders", "_imp", "base64", 
            "_sha512", "mimetypes", "quopri", "uu", "contextvars", "_frozen_importlib", "optparse", "_compression", "http", "_opcode", "hashlib", "winreg", 
            "email._parseaddr", "email.base64mime", "_md5", "plistlib", "_bz2", "bisect", "importlib", "_lzma", "_sha3", "fractions", "ast", "socketserver", "_sha256", 
            "_ast", "termios", "_statistics", "_hashlib", "importlib.metadata", "_aix_support", "ssl", "email.headerregistry", "_bootsubprocess", "_bisect", 
            "datetime", "http.client", "importlib.abc", "_sha1", "email.parser", "_contextvars", "_strptime", "xml.parsers.expat", "codeop", "numbers", "decimal", 
            "_ssl", "pep517", "zipimport", "calendar", "pyexpat", "html.entities", "csv", "_osx_support", "pathlib", "configparser", "_blake2", "distutils", 
            "_decimal", "_pydecimal", "_datetime", "email.feedparser", "_csv"
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
