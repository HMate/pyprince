import textwrap
import sys
from pathlib import Path

from tests import testutils
from tests.testutils import PackageGenerator, PyPrinceTestCase
from pyprince.parser.Project import Module, Project
from pyprince.parser import parse_project
from pyprince import generators


class TestImportResolver(PyPrinceTestCase):
    """Collection of long running tests that import from the actual standard library."""

    def setUp(self):
        self.test_root = testutils.get_test_scenarios_dir()
        testutils.remove_imported_modules()

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
        if sys.version_info.major == 3 and sys.version_info.minor == 9:
            expected_nodes = [
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
        elif sys.version_info.major == 3 and sys.version_info.minor == 10:
            expected_nodes = [
                "main", "io", "abc", "_py_abc", "_abc", "_io", "warnings", "sys", "builtins", "_warnings", "re", 
                "sre_constants", "_locale", "linecache", "sre_parse", "_weakrefset", "tracemalloc", "copyreg", 
                "types", "unicodedata", "_tracemalloc", "functools", "tokenize", "fnmatch", "operator", "argparse", 
                "ntpath", "pickle", "_weakref", "_operator", "collections.abc", "textwrap", "_functools", "pprint", 
                "_sre", "itertools", "dataclasses", "codecs", "struct", "_pickle", "_compat_pickle", "nt", "inspect", 
                "encodings", "copy", "stat", "traceback", "genericpath", "keyword", "doctest", "shutil", "errno", 
                "reprlib", "encodings.mbcs", "enum", "sre_compile", "string", "os", "grp", "org.python.core", 
                "collections", "typing", "_winapi", "_thread", "importlib.machinery", "weakref", "pdb", "token", 
                "encodings.aliases", "importlib._bootstrap", "_struct", "__main__", "posixpath", "gc", 
                "_frozen_importlib_external", "bdb", "getopt", "gettext", "time", "_collections_abc", "importlib", 
                "difflib", "__future__", "readline", "bz2", "ast", "pwd", "pydoc", "cmd", "tty", "posix", "subprocess", 
                "heapq", "dis", "unittest", "lzma", "select", "_lzma", "locale", "tarfile", "platform", 
                "importlib._bootstrap_external", "http.server", "unittest.signals", "_frozen_importlib", 
                "importlib.util", "base64", "zipfile", "socket", "_compression", "atexit", "zlib", "sysconfig", 
                "shlex", "_heapq", "binascii", "_string", "signal", "pkgutil", "email.message", "email._policybase", 
                "unittest.async_case", "email._encoded_words", "threading", "http", "plistlib", "gzip", "vms_lib", 
                "java.lang", "pydoc_data.topics", "quopri", "fcntl", "opcode", "unittest.loader", "webbrowser", 
                "unittest.case", "_bz2", "unittest.suite", "_winreg", "email.generator", "socketserver", "mimetypes", 
                "py_compile", "datetime", "_aix_support", "importlib.readers", "xml.parsers.expat", "_opcode", 
                "selectors", "code", "html", "runpy", "_posixsubprocess", "contextlib", "_collections", "msvcrt", 
                "array", "glob", "_signal", "random", "pathlib", "marshal", "_osx_support", "email.policy", "uu", 
                "_imp", "urllib.parse", "unittest.main", "unittest.runner", "_socket", "asyncio", "tempfile", "winreg", 
                "email.charset", "email.contentmanager", "statistics", "_sha512", "unittest.result", "_strptime", 
                "numbers", "calendar", "html.entities", "importlib.metadata", "importlib._abc", "zipimport", "_random", 
                "email.header", "unittest._log", "_datetime", "email.utils", "email.quoprimime", "logging", 
                "email.iterators", "http.client", "email.errors", "_bootsubprocess", "importlib.metadata._functools", 
                "_threading_local", "hashlib", "email._parseaddr", "bisect", "fractions", "math", "decimal", 
                "unittest.util", "csv", "importlib.metadata._collections", "email", "_sha3", "importlib.abc", 
                "optparse", "codeop", "email.base64mime", "_sha1", "_blake2", "importlib.metadata._meta", 
                "importlib.metadata._adapters", "_decimal", "email.headerregistry", "_md5", "importlib.metadata._itertools", 
                "ssl", "pep517", "email.encoders", "email.parser", "_statistics", "_sha256", "_pydecimal", "_csv", 
                "_hashlib", "importlib.metadata._text", "_ssl", "email.feedparser", "email._header_value_parser", 
                "contextvars", "_contextvars", "urllib"
            ]
        else:
            raise NotImplementedError("Unsupported python version")
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
        self.assertCountEqual(actual["nodes"], expected_nodes)

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
