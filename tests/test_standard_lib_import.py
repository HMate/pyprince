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
                "main", "io", "abc", "_abc", "_py_abc", "_weakrefset", "_io", "_weakref", "types", "sys", "_collections_abc", 
                "functools", "weakref", "warnings", "atexit", "re", "typing", "traceback", "itertools", "sre_constants", 
                "tracemalloc", "gc", "reprlib", "copy", "_thread", "contextlib", "ntpath", "_sre", "stat", "string", "builtins", 
                "_functools", "_tracemalloc", "linecache", "os", "collections.abc", "collections", "genericpath", "posixpath", 
                "enum", "_locale", "sre_compile", "fnmatch", "org.python.core", "heapq", "doctest", "_string", "__future__", 
                "copyreg", "pickle", "_warnings", "_pickle", "sre_parse", "unittest", "nt", "subprocess", "keyword", "difflib", 
                "_collections", "posix", "signal", "argparse", "pprint", "unittest.case", "pwd", "gettext", "unittest.signals", 
                "errno", "tokenize", "_heapq", "unittest.result", "shutil", "operator", "pdb", "inspect", "token", "grp", 
                "shlex", "msvcrt", "unittest.runner", "_compat_pickle", "unittest.async_case", "unittest.main", "unicodedata", 
                "locale", "select", "codecs", "unittest.loader", "bz2", "cmd", "dis", "opcode", "encodings", "_compression", 
                "readline", "pydoc", "_bz2", "runpy", "unittest._log", "pydoc_data.topics", "_operator", "tarfile", "pkgutil", 
                "bdb", "_frozen_importlib_external", "zlib", "unittest.suite", "_bootlocale", "lzma", "tempfile", "email.message", 
                "importlib", "time", "zipfile", "asyncio", "quopri", "platform", "_signal", "_opcode", "ast", "glob", "code", 
                "email.iterators", "tty", "threading", "plistlib", "struct", "socket", "unittest.util", "__main__", "_winreg", 
                "codeop", "_winapi", "selectors", "importlib.machinery", "textwrap", "_threading_local", "_posixsubprocess", 
                "binascii", "datetime", "encodings.aliases", "email.charset", "winreg", "zipimport", "_imp", "getopt", 
                "vms_lib", "encodings.mbcs", "importlib.util", "_socket", "xml.parsers.expat", "email.quoprimime", "http.server", 
                "sysconfig", "urllib.parse", "http", "_aix_support", "logging", "email.errors", "_osx_support", "_lzma", "gzip", 
                "math", "distutils.log", "marshal", "uu", "email.encoders", "webbrowser", "_bootsubprocess", "_frozen_importlib", 
                "email._policybase", "py_compile", "importlib._bootstrap", "_datetime", "random", "array", "bisect", "hashlib", 
                "email.utils", "asyncio.tasks", "_struct", "java.lang", "_sha512", "importlib._bootstrap_external", "_sha1", 
                "email.generator", "email.policy", "importlib.abc", "email._encoded_words", "asyncio.base_tasks", 
                "asyncio.exceptions", "mimetypes", "pathlib", "optparse", "_asyncio", "html", "email.base64mime", "html.entities", 
                "email._parseaddr", "_random", "asyncio.base_futures", "http.client", "email.parser", "email.contentmanager", 
                "_strptime", "asyncio.futures", "_blake2", "_hashlib", "socketserver", "concurrent.futures", "_sha256", 
                "asyncio.format_helpers", "concurrent.futures.thread", "importlib.metadata", "base64", "email.header", 
                "concurrent.futures.process", "multiprocessing.queues", "ssl", "configparser", "queue", "multiprocessing.util", 
                "multiprocessing.forkserver", "asyncio.queues", "_md5", "csv", "_queue", "_csv", "multiprocessing.connection", 
                "statistics", "multiprocessing.context", "contextvars", "multiprocessing.resource_tracker", "calendar", 
                "concurrent.futures._base", "multiprocessing.process", "multiprocessing", "_statistics", "decimal", "_sha3", 
                "_contextvars", "email.feedparser", "pep517", "test.support", "multiprocessing.spawn", "multiprocessing.sharedctypes", 
                "faulthandler", "email.headerregistry", "multiprocessing.popen_spawn_win32", "ctypes.util", "_posixshmem", 
                "asyncio.events", "multiprocessing.synchronize", "tkinter", "distutils.spawn", "ctypes._aix", "_multiprocessing", 
                "_ssl", "asyncio.coroutines", "_pydecimal", "hmac", "multiprocessing.reduction", "resource", "ctypes", 
                "_testinternalcapi", "multiprocessing.popen_forkserver", "numbers", "ctypes.macholib.dyld", "_ctypes", 
                "distutils.ccompiler", "asyncio.log", "xmlrpc.client", "email", "_tkinter", "distutils.dep_util", 
                "ctypes.macholib.framework", "distutils.errors", "asyncio.locks", "fractions", "distutils.debug", 
                "multiprocessing.resource_sharer", "distutils.sysconfig", "asyncio.constants", "multiprocessing.popen_spawn_posix", 
                "_testcapi", "ctypes.macholib.dylib", "multiprocessing.popen_fork", "ctypes.wintypes", "_decimal", "distutils.util", 
                "multiprocessing.pool", "multiprocessing.heap", "multiprocessing.managers", "test.support.testresult", 
                "multiprocessing.dummy", "email._header_value_parser", "asyncio.subprocess", "ctypes._endian", 
                "urllib.request", "distutils.dir_util", "urllib", "http.cookiejar", "_scproxy", "asyncio.protocols", 
                "urllib.response", "mmap", "distutils.text_file", "multiprocessing.dummy.connection", "urllib.error", "nturl2path", 
                "distutils.file_util", "distutils.fancy_getopt", "multiprocessing.shared_memory", "getpass", "asyncio.streams", 
                "xml.etree.ElementTree", "ftplib", "secrets", "termios", "netrc", "xml.etree.ElementPath", "pyexpat", "_elementtree"
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
