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
            "main", "io", "_io", "abc", "_py_abc", "_weakrefset", "_weakref", "_abc", "types", "_collections_abc", 
            "functools", "_functools", "typing", "weakref", "itertools", "gc", "copy", "copyreg", "warnings", "tracemalloc", 
            "builtins", "collections", "_collections", "collections.abc", "sys", "_warnings", "reprlib", "linecache", 
            "_thread", "contextlib", "heapq", "doctest", "re", "difflib", "unittest", "__future__", "unittest.runner", 
            "unittest.case", "unittest.suite", "inspect", "enum", "dis", "_locale", "unittest.util", "sre_constants", 
            "_sre", "argparse", "token", "org.python.core", "pdb", "fnmatch", "_heapq", "ntpath", "unittest.main", "shutil", 
            "nt", "tarfile", "keyword", "pickle", "importlib", "atexit", "traceback", "shlex", "errno", "sre_compile", 
            "unittest.loader", "opcode", "operator", "_operator", "os", "importlib.machinery", "gettext", 
            "importlib._bootstrap_external", "lzma", "unittest.async_case", "getopt", "gzip", "unittest.result", "pwd", 
            "pydoc", "_frozen_importlib", "threading", "time", "posixpath", "grp", "stat", "locale", "email.message", 
            "_compression", "bz2", "_lzma", "http.server", "string", "email._policybase", "code", "importlib.metadata", 
            "select", "importlib.util", "quopri", "subprocess", "_bootlocale", "socketserver", "tokenize", "_tracemalloc", 
            "http.client", "codecs", "bdb", "_opcode", "csv", "ssl", "pprint", "ast", "_pickle", "sre_parse", "textwrap", 
            "tempfile", "struct", "runpy", "unittest._log", "signal", "_threading_local", "urllib.parse", "encodings", 
            "html", "__main__", "email.iterators", "glob", "genericpath", "email.generator", "unittest.signals", "msvcrt", 
            "pkgutil", "_bz2", "zlib", "_string", "_compat_pickle", "pathlib", "selectors", "cmd", "_csv", "tty", "zipfile", 
            "mimetypes", "pep517", "unicodedata", "posix", "sysconfig", "zipimport", "email", "http", "calendar", "logging", 
            "platform", "_osx_support", "email.utils", "readline", "_frozen_importlib_external", "pydoc_data.topics", 
            "importlib._bootstrap", "_imp", "_ast", "_struct", "email._encoded_words", "html.entities", "distutils", 
            "winreg", "_winapi", "_signal", "_aix_support", "_winreg", "marshal", "email.parser", "codeop", "uu", "_stat", 
            "encodings.mbcs", "asyncio", "_posixsubprocess", "asyncio.locks", "asyncio.tasks", "base64", "asyncio.base_tasks", 
            "email.policy", "binascii", "asyncio.queues", "webbrowser", "_ssl", "email._parseaddr", "asyncio.subprocess", 
            "py_compile", "termios", "_codecs", "optparse", "asyncio.base_events", "datetime", "vms_lib", "asyncio.sslproto", 
            "configparser", "asyncio.threads", "concurrent.futures", "math", "random", "statistics", "java.lang", "plistlib", 
            "decimal", "email.charset", "_decimal", "email.contentmanager", "_statistics", "email.quoprimime", "asyncio.log", 
            "asyncio.transports", "_pydecimal", "asyncio.trsock", "email.errors", "_bootsubprocess", "asyncio.unix_events", 
            "asyncio.events", "_datetime", "numbers", "asyncio.exceptions", "asyncio.streams", "email.encoders", "contextvars", 
            "_strptime", "asyncio.base_futures", "bisect", "_contextvars", "asyncio.staggered", "asyncio.windows_events", 
            "asyncio.coroutines", "asyncio.futures", "email.feedparser", "_asyncio", "_random", "asyncio.base_subprocess", 
            "concurrent.futures._base", "email.headerregistry", "asyncio.windows_utils", "asyncio.protocols", "asyncio.runners", 
            "socket", "importlib.abc", "encodings.aliases", "_sha512", "asyncio.constants", "fractions", "_overlapped", 
            "asyncio.proactor_events", "asyncio.format_helpers", "concurrent.futures.process", "concurrent.futures.thread", 
            "hashlib", "xml.parsers.expat", "_bisect", "email.base64mime", "array", "asyncio.selector_events", "_sha256", 
            "_hashlib", "_md5", "pyexpat", "_sha3", "multiprocessing.queues", "multiprocessing", "_blake2", 
            "multiprocessing.connection", "multiprocessing.synchronize", "_socket", "hmac", "multiprocessing.heap", 
            "multiprocessing.resource_sharer", "_sha1", "multiprocessing.util", "queue", "multiprocessing.resource_tracker", 
            "_queue", "multiprocessing.process", "_multiprocessing", "mmap", "_posixshmem", "multiprocessing.context", 
            "multiprocessing.forkserver", "multiprocessing.popen_spawn_posix", "xmlrpc.client", "multiprocessing.spawn", 
            "multiprocessing.sharedctypes", "multiprocessing.popen_forkserver", "multiprocessing.popen_fork", 
            "multiprocessing.managers", "ctypes", "multiprocessing.pool", "multiprocessing.popen_spawn_win32", 
            "multiprocessing.shared_memory", "_ctypes", "multiprocessing.reduction", "ctypes._endian", "multiprocessing.dummy", 
            "secrets", "multiprocessing.dummy.connection"
        ]
        # fmt: on
        # module dependency nodes should be unique.
        actual = generators.describe_module_dependencies(project).to_dict()
        self.assertListElementsAreUnique(actual["nodes"])
        self.maxDiff = None
        print(actual["nodes"])
        self.assertNotIn(
            "concurrent", actual["nodes"], "concurrent is an empty module, so nobody should be dependent on it"
        )
        self.assertNotIn(
            "xml.parsers", actual["nodes"], "xml.parsers is an empty module, so nobody should be dependent on it"
        )
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
