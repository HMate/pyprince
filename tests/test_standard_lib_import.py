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
                "main", "io", "abc", "_py_abc", "_io", "_abc", "_weakrefset", "_weakref", "types", "_collections_abc", 
                "functools", "sys", "typing", "reprlib", "collections", "warnings", "re", "copyreg", "linecache", "_warnings", 
                "sre_constants", "weakref", "builtins", "itertools", "traceback", "heapq", "contextlib", "sre_compile", 
                "os", "tokenize", "_functools", "doctest", "copy", "unittest", "_collections", "collections.abc", 
                "unittest.suite", "unittest.util", "_sre", "nt", "argparse", "posixpath", "token", "unittest.runner", 
                "subprocess", "threading", "__future__", "difflib", "genericpath", "enum", "ntpath", "_heapq", "atexit", 
                "operator", "sre_parse", "os.path", "selectors", "keyword", "unicodedata", "inspect", "unittest.main", 
                "_locale", "time", "gc", "stat", "_thread", "importlib.machinery", "tracemalloc", "grp", "textwrap", "select", 
                "_winapi", "pdb", "unittest.signals", "signal", "_stat", "shutil", "unittest.case", "pydoc", "posix", "math", 
                "code", "http.server", "unittest.result", "importlib.util", "sysconfig", "base64", "getopt", "importlib", 
                "ast", "_aix_support", "importlib._bootstrap", "_tracemalloc", "importlib.abc", "platform", 
                "_frozen_importlib_external", "_ast", "vms_lib", "tempfile", "lzma", "socketserver", "zlib", "__main__", 
                "struct", "email.utils", "tty", "readline", "zipfile", "pwd", "_threading_local", "socket", "errno", 
                "http.client", "dis", "pickle", "msvcrt", "glob", "codecs", "unittest._log", "_signal", "shlex", "mimetypes", 
                "org.python.core", "codeop", "_posixsubprocess", "fnmatch", "unittest.loader", "unittest.async_case", "runpy", 
                "pprint", "cmd", "pkgutil", "java.lang", "gettext", "_imp", "_pickle", "winreg", "pydoc_data.topics", "string", 
                "email.message", "bz2", "importlib._bootstrap_external", "random", "zipimport", "asyncio", "_bz2", 
                "asyncio.threads", "bisect", "bdb", "_operator", "email.charset", "html", "marshal", "tarfile", "binascii", 
                "importlib.metadata", "html.entities", "_bisect", "asyncio.events", "asyncio.format_helpers", "_osx_support", 
                "datetime", "http", "statistics", "opcode", "_frozen_importlib", "email._parseaddr", "asyncio.exceptions", 
                "_string", "contextvars", "_sha512", "_bootsubprocess", "fractions", "pathlib", "logging", "py_compile", 
                "email.parser", "_random", "plistlib", "quopri", "uu", "_compat_pickle", "asyncio.unix_events", 
                "asyncio.queues", "asyncio.selector_events", "encodings", "asyncio.transports", "encodings.mbcs", 
                "asyncio.locks", "gzip", "decimal", "asyncio.trsock", "email.errors", "csv", "email", "_asyncio", 
                "email.feedparser", "distutils.log", "termios", "_codecs", "_strptime", "webbrowser", "_compression", 
                "urllib.parse", "hashlib", "optparse", "asyncio.log", "asyncio.base_subprocess", "email.quoprimime", 
                "_struct", "_socket", "asyncio.coroutines", "_datetime", "_winreg", "locale", "_lzma", "asyncio.runners", 
                "asyncio.windows_events", "email._policybase", "asyncio.streams", "_opcode", "email.encoders", 
                "asyncio.tasks", "email.policy", "array", "ssl", "asyncio.subprocess", "asyncio.base_events", "_statistics", 
                "asyncio.futures", "_bootlocale", "asyncio.staggered", "asyncio.protocols", "_decimal", "email.base64mime", 
                "numbers", "_md5", "asyncio.constants", "_contextvars", "asyncio.windows_utils", "email._encoded_words", 
                "email.contentmanager", "pep517", "email.headerregistry", "_sha256", "email.header", "email.generator", 
                "email.iterators", "_blake2", "_sha1", "asyncio.base_futures", "configparser", "xml.parsers.expat", "_csv", 
                "_pydecimal", "asyncio.sslproto", "calendar", "encodings.aliases", "_sha3", "asyncio.base_tasks", 
                "asyncio.proactor_events", "email._header_value_parser", "_hashlib", "concurrent.futures", "pyexpat", 
                "_overlapped", "_ssl", "concurrent.futures.thread", "queue", "concurrent.futures._base", "urllib", "_queue", 
                "concurrent.futures.process", "multiprocessing.queues", "multiprocessing.context", "multiprocessing.util", 
                "multiprocessing.reduction", "multiprocessing.popen_forkserver", "multiprocessing.synchronize", 
                "multiprocessing.managers", "_multiprocessing", "multiprocessing.popen_spawn_win32", "multiprocessing.pool", 
                "multiprocessing.heap", "test.support", "ctypes.wintypes", "distutils.errors", "mmap", "multiprocessing", 
                "multiprocessing.spawn", "_testcapi", "multiprocessing.resource_sharer", "multiprocessing.process", 
                "distutils.sysconfig", "_testinternalcapi", "distutils.text_file", "multiprocessing.connection", "tkinter", 
                "multiprocessing.resource_tracker", "_posixshmem", "ctypes.util", "multiprocessing.forkserver", 
                "multiprocessing.shared_memory", "multiprocessing.popen_fork", "test.support.testresult", "distutils.spawn", 
                "multiprocessing.popen_spawn_posix", "tkinter.constants", "hmac", "urllib.request", "multiprocessing.dummy", 
                "multiprocessing.sharedctypes", "distutils.ccompiler", "ctypes._aix", "xmlrpc.client", "faulthandler", 
                "_tkinter", "ctypes.macholib.dyld", "xml.etree.ElementTree", "ctypes.macholib.framework", "resource", 
                "urllib.response", "distutils.fancy_getopt", "ctypes", "xml.etree.ElementPath", "http.cookiejar", 
                "distutils.util", "multiprocessing.dummy.connection", "distutils.dep_util", "distutils.debug", 
                "lib2to3.refactor", "distutils.file_util", "lib2to3.fixer_util", "_scproxy", "urllib.error", "getpass", 
                "secrets", "ftplib", "_elementtree", "distutils.dir_util", "nturl2path", "lib2to3.btm_matcher", "_ctypes", 
                "ctypes.macholib.dylib", "distutils.filelist", "ctypes._endian", "lib2to3.pytree", "lib2to3.pgen2.driver", 
                "lib2to3.pgen2.tokenize", "lib2to3.pygram", "lib2to3.pgen2.token", "lib2to3.patcomp", "netrc", 
                "lib2to3.btm_utils", "lib2to3.pgen2.grammar", "lib2to3.pgen2.literals", "lib2to3.pgen2.pgen", "lib2to3.pgen2.parse"
            ]
        elif sys.version_info.major == 3 and sys.version_info.minor == 10:
            expected_nodes = [
                "main", "io", "_io", "abc", "_abc", "_py_abc", "warnings", "builtins", "re", "_locale", "traceback", "sys", 
                "linecache", "sre_parse", "functools", "_weakrefset", "copyreg", "_warnings", "sre_constants", "os", "enum", 
                "operator", "_functools", "nt", "itertools", "stat", "typing", "_stat", "_weakref", "os.path", "collections", 
                "tracemalloc", "unicodedata", "sre_compile", "weakref", "_sre", "subprocess", "pwd", "string", "_collections_abc", 
                "pickle", "select", "copy", "contextlib", "collections.abc", "gc", "genericpath", "struct", "fnmatch", "_tracemalloc", 
                "tokenize", "types", "selectors", "reprlib", "doctest", "codecs", "threading", "posix", "token", "_operator", 
                "_thread", "atexit", "_string", "fcntl", "posixpath", "_winapi", "errno", "_struct", "inspect", "keyword", 
                "signal", "difflib", "_collections", "heapq", "org.python.core", "ast", "dis", "_posixsubprocess", "_compat_pickle", 
                "argparse", "encodings", "ntpath", "time", "importlib.machinery", "_pickle", "encodings.mbcs", "_threading_local", 
                "importlib._bootstrap", "msvcrt", "pprint", "grp", "pdb", "shutil", "unittest", "zlib", "__future__", "_ast", "bz2", 
                "unittest.case", "cmd", "_signal", "_compression", "math", "shlex", "getopt", "unittest.async_case", "unittest.loader", 
                "_frozen_importlib_external", "readline", "__main__", "importlib._bootstrap_external", "gettext", "_codecs", 
                "unittest.main", "_heapq", "zipfile", "unittest.util", "importlib", "pydoc", "opcode", "_opcode", "asyncio", "locale", 
                "lzma", "asyncio.windows_events", "asyncio.locks", "encodings.aliases", "asyncio.log", "pkgutil", "asyncio.queues", 
                "asyncio.proactor_events", "email.message", "asyncio.base_events", "platform", "uu", "quopri", "runpy", "dataclasses", 
                "asyncio.unix_events", "tarfile", "email._policybase", "asyncio.selector_events", "glob", "asyncio.threads", "binascii", 
                "asyncio.base_subprocess", "asyncio.transports", "email._encoded_words", "marshal", "vms_lib", "gzip", "urllib.parse", 
                "importlib.util", "importlib.readers", "sysconfig", "email.errors", "asyncio.trsock", "asyncio.futures", "http.server", 
                "ssl", "email.iterators", "asyncio.runners", "zipimport", "logging", "bdb", "textwrap", "unittest.signals", 
                "asyncio.exceptions", "asyncio.tasks", "asyncio.events", "asyncio.sslproto", "asyncio.coroutines", "asyncio.windows_utils", 
                "socketserver", "optparse", "unittest.result", "_bz2", "pathlib", "_aix_support", "unittest.runner", "java.lang", "code", 
                "unittest.suite", "unittest._log", "email.header", "asyncio.constants", "email.utils", "importlib.metadata", 
                "importlib.metadata._itertools", "_winreg", "http.client", "codeop", "webbrowser", "_bootsubprocess", "_imp", 
                "pydoc_data.topics", "winreg", "socket", "concurrent.futures", "plistlib", "asyncio.base_futures", "asyncio.subprocess", 
                "_frozen_importlib", "asyncio.protocols", "email.charset", "importlib.abc", "importlib.metadata._meta", "py_compile", 
                "asyncio.streams", "tty", "tempfile", "asyncio.mixins", "asyncio.staggered", "_overlapped", "_lzma", "http", 
                "email.generator", "email.policy", "asyncio.format_helpers", "base64", "_asyncio", "csv", "contextvars", "_socket", 
                "importlib._abc", "email.encoders", "_osx_support", "pep517", "concurrent.futures.thread", "_csv", "mimetypes", 
                "importlib.metadata._functools", "_ssl", "calendar", "email.parser", "importlib.metadata._adapters", 
                "importlib.metadata._collections", "_contextvars", "datetime", "html", "email.quoprimime", "asyncio.base_tasks", 
                "html.entities", "email._parseaddr", "array", "email", "random", "importlib.metadata._text", "_strptime", 
                "_random", "concurrent.futures.process", "email.base64mime", "_sha512", "email.contentmanager", "email.feedparser", 
                "concurrent.futures._base", "xml.parsers.expat", "queue", "multiprocessing", "termios", "email.headerregistry", 
                "pyexpat", "multiprocessing.synchronize", "email._header_value_parser", "_datetime", "multiprocessing.heap", 
                "statistics", "multiprocessing.resource_tracker", "_posixshmem", "_queue", "mmap", "numbers", "hashlib", 
                "multiprocessing.connection", "_multiprocessing", "multiprocessing.queues", "_statistics", "bisect", "xmlrpc.client", 
                "_sha1", "multiprocessing.process", "_sha256", "multiprocessing.util", "_bisect", "multiprocessing.context", 
                "multiprocessing.forkserver", "test.support", "urllib", "distutils.sysconfig", "test.support.testresult", 
                "urllib.request", "multiprocessing.spawn", "multiprocessing.resource_sharer", "resource", "distutils.ccompiler", 
                "distutils.debug", "decimal", "multiprocessing.reduction", "_hashlib", "_sha3", "_md5", "_blake2", "_pydecimal", 
                "ctypes.wintypes", "urllib.response", "distutils.errors", "tkinter", "ftplib", "nturl2path", "distutils.file_util", 
                "faulthandler", "hmac", "_testinternalcapi", "distutils.util", "_testcapi", "multiprocessing.pool", "distutils.log", 
                "ctypes.util", "distutils.fancy_getopt", "test.support.os_helper", "multiprocessing.sharedctypes", "http.cookiejar", 
                "multiprocessing.popen_spawn_win32", "_scproxy", "multiprocessing.popen_forkserver", "distutils", "distutils.text_file", 
                "multiprocessing.managers", "urllib.error", "xml.etree.ElementTree", "multiprocessing.popen_fork", "getpass", 
                "distutils.dir_util", "multiprocessing.popen_spawn_posix", "distutils.spawn", "fractions", "test.support.import_helper", 
                "multiprocessing.dummy", "ctypes", "multiprocessing.shared_memory", "ctypes.macholib.dyld", "distutils.dep_util", 
                "_ctypes", "_decimal", "lib2to3.refactor", "ctypes.macholib.dylib", "secrets", "netrc", "lib2to3.pytree", 
                "ctypes.macholib.framework", "distutils.filelist", "lib2to3.btm_matcher", "ctypes._aix", "lib2to3.pgen2.tokenize", 
                "xml.etree.ElementPath", "_elementtree", "lib2to3.pgen2.driver", "lib2to3.btm_utils", "lib2to3.fixer_util", 
                "multiprocessing.dummy.connection", "ctypes._endian", "lib2to3.pygram", "lib2to3.pgen2.token", "lib2to3.pgen2.pgen",
                "lib2to3.pgen2.parse", "lib2to3.patcomp", "lib2to3.pgen2.grammar", "lib2to3.pgen2.literals"
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
