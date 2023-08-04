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
            "main", "io", "abc", "_io", "_py_abc", "_abc", "_weakrefset", "types", "_collections_abc", "sys", "_weakref", "warnings", "re", "tracemalloc", "_warnings", 
            "pickle", "enum", "_locale", "traceback", "sre_parse", "struct", "collections.abc", "argparse", "codecs", "builtins", "gettext", "ntpath", "itertools", "functools", 
            "fnmatch", "linecache", "sre_compile", "genericpath", "pprint", "sre_constants", "posixpath", "weakref", "_pickle", "_compat_pickle", "unicodedata", "_codecs", 
            "atexit", "pwd", "os", "textwrap", "errno", "typing", "string", "_struct", "stat", "_stat", "copyreg", "_tracemalloc", "encodings", "doctest", "locale", "time", 
            "org.python.core", "subprocess", "shutil", "_functools", "reprlib", "collections", "copy", "bz2", "zlib", "tokenize", "posix", "_sre", "__future__", "token", 
            "gc", "_thread", "nt", "encodings.aliases", "inspect", "_compression", "_posixsubprocess", "operator", "selectors", "msvcrt", "lzma", "importlib.machinery", "pdb", 
            "heapq", "importlib._bootstrap_external", "glob", "marshal", "grp", "_collections", "_bz2", "_bootlocale", "_string", "encodings.mbcs", "dis", "_winapi", "keyword", 
            "contextlib", "winreg", "_operator", "difflib", "ast", "shlex", "code", "runpy", "importlib", "unittest", "select", "tarfile", "threading", "zipfile", "readline", 
            "_frozen_importlib", "getopt", "math", "__main__", "cmd", "_frozen_importlib_external", "importlib._bootstrap", "codeop", "gzip", "pydoc", "importlib.metadata", 
            "importlib.abc", "_threading_local", "binascii", "unittest.result", "_lzma", "configparser", "_heapq", "pep517", "signal", "_imp", "unittest.case", "unittest.async_case",
            "urllib.parse", "bdb", "opcode", "csv", "unittest.runner", "pkgutil", "unittest.suite", "webbrowser", "unittest.loader", "unittest.main", "importlib.util", "py_compile", 
            "pydoc_data.topics", "pathlib", "unittest.signals", "_ast", "http.server", "tempfile", "tty", "email.message", "email.utils", "http.client", "platform", "plistlib", 
            "socketserver", "email", "base64", "_winreg", "mimetypes", "email._parseaddr", "email.parser", "unittest._log", "sysconfig", "email.iterators", "datetime", "unittest.util", 
            "email._encoded_words", "email.policy", "email.charset", "email.base64mime", "socket", "quopri", "_csv", "uu", "xml.parsers.expat", "termios", "email._policybase", 
            "_signal", "_osx_support", "_opcode", "asyncio", "vms_lib", "asyncio.threads", "asyncio.streams", "array", "zipimport", "html", "logging", "asyncio.subprocess", 
            "contextvars", "java.lang", "email.feedparser", "asyncio.events", "asyncio.protocols", "asyncio.runners", "asyncio.format_helpers", "random", "calendar", "asyncio.exceptions", 
            "asyncio.windows_events", "email.generator", "http", "asyncio.locks", "email.contentmanager", "asyncio.tasks", "_datetime", "html.entities", "_asyncio", "pyexpat", 
            "asyncio.unix_events", "asyncio.constants", "optparse", "distutils", "ssl", "asyncio.queues", "statistics", "_sha512", "email.encoders", "_strptime", "decimal", "_aix_support", 
            "_statistics", "_bootsubprocess", "email.quoprimime", "asyncio.selector_events", "_contextvars", "_socket", "asyncio.coroutines", "asyncio.futures", "asyncio.transports",
            "asyncio.proactor_events", "bisect", "email.headerregistry", "asyncio.windows_utils", "asyncio.trsock", "_pydecimal", "_random", "asyncio.base_events", 
            "asyncio.base_subprocess", "_decimal", "fractions", "asyncio.base_tasks", "hashlib", "email.errors", "_overlapped", "concurrent.futures", 
            "asyncio.log", "_sha256", "numbers", "concurrent.format_helpers", "_bisect", "asyncio.base_futures", "asyncio.sslproto", "_ssl", "_sha3", "_md5", 
            "concurrent.exceptions", "concurrent.base_futures", "asyncio.staggered", "_blake2", "_hashlib", "concurrent.events", "_sha1", "concurrent.constants", 
            "concurrent.subprocess", "concurrent.protocols", "concurrent.tasks", "concurrent.queues", "concurrent.streams", "concurrent.log", "concurrent.coroutines", 
            "concurrent.locks", "concurrent.base_tasks"
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
