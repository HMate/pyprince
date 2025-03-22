import textwrap
import sys
from pathlib import Path

from hamcrest import assert_that, contains_inanyorder, has_item, has_items, is_, none, not_, not_none
from tests import testutils
from pyprince.parser.project import Module, Project
from pyprince.parser import parse_project
from pyprince import generators
from pyprince.utils import logger

from tests.testutils.matchers import all_unique


class TestStandardLibImportResolver(testutils.PyPrinceTestCase):
    """Collection of long running tests that import from the actual standard library."""

    def setUp(self):
        self.test_root = testutils.get_test_scenarios_dir()
        testutils.remove_imported_modules()
        logger.info(f"----- Starting test - {self.current_test_name()} ------")

    def test_io_module(self):
        """io modue has built-in dependencies on _io, _abc and import inside try-catch blocks
        We check if the parser gathers all deps correctly.
        """
        test_name = Path(self._testMethodName)
        gen = testutils.PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import io
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        project: Project = parse_project(self.test_root / test_name / "main.py", shallow_stdlib=False)
        # fmt: off
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
        # fmt: on
        if sys.version_info.major == 3 and sys.version_info.minor == 10:
            for dep in ["_bootlocale", "configparser", "tkinter.constants", "_tkinter"]:
                expected_nodes.remove(dep)
            expected_nodes.extend(
                [
                    "fcntl",
                    "dataclasses",
                    "asyncio.mixins",
                    "importlib.readers",
                    "importlib._abc",
                    "importlib.metadata._adapters",
                    "importlib.metadata._meta",
                    "test.support.import_helper",
                    "importlib.metadata._text",
                    "importlib.metadata._functools",
                    "importlib.metadata._collections",
                    "importlib.metadata._itertools",
                    "test.support.os_helper",
                    "distutils",
                ]
            )

        actual = generators.describe_module_dependencies(project).to_dict()
        logger.debug(actual["nodes"])
        assert_that(actual["nodes"], all_unique())
        assert_that(
            actual["nodes"],
            not_(has_item("concurrent")),
            "concurrent is an empty module, so nobody should be dependent on it",
        )
        assert_that(
            actual["nodes"],
            not_(has_item("xml.parsers")),
            "xml.parsers is an empty module, so nobody should be dependent on it",
        )
        assert_that(actual["nodes"], contains_inanyorder(*expected_nodes))

    def test_imported_names(self):
        test_name = Path(self._testMethodName)
        gen = testutils.PackageGenerator()
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

        project: Project = parse_project(test_main, shallow_stdlib=True)

        assert_that(project, is_(not_none()))
        assert_that(project.get_syntax_tree("os"), is_(not_none()))
        assert_that(project.get_syntax_tree("pathlib"), is_(not_none()))
        assert_that(project.get_syntax_tree("os.path"), is_(not_none()))  # os.path <==> ntpath
        assert_that(project.get_syntax_tree("sys"), is_(none()), "sys is builtin, does not have syntaxtree")
        assert_that(project.get_syntax_tree("abc"), is_(not_none()))
        assert_that(project.get_syntax_tree("time"), is_(none()), "time is builtin, does not have syntaxtree")
        assert_that(project.get_syntax_tree("utils"), is_(not_none()))
        assert_that(project.get_syntax_tree("other"), is_(not_none()))

    def test_argparse_module(self):
        """argparse module has 2 interesting scenarios:
        - dependecies on pyd modules (unicodedata.pyd)
        - uses the pwd module which is unix only
        We dont parse the code for these but we should still register the modules.
        """
        test_name = Path(self._testMethodName)
        gen = testutils.PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import argparse
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        project: Project = parse_project(self.test_root / test_name / "main.py", shallow_stdlib=False)
        actual = generators.describe_module_dependencies(project).to_dict()
        assert_that(actual["nodes"], has_items("main", "argparse", "unicodedata", "pwd"))

    def test_parsing_package_from_site_packages(self):
        test_name = self.current_test_name()
        test_path = Path(test_name)
        gen = testutils.PackageGenerator()
        gen.add_file(
            test_path / "main.py",
            textwrap.dedent(
                """
                import libcst 

                def main():
                    some_functionality(["Mom", "Dad"], ["Grandpa", "Cousin"])
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        project: Project = parse_project(self.test_root / test_name / "main.py", shallow_stdlib=True)
        assert_that(project.list_packages(), has_items(test_name, "libcst", "stdlib"))
        assert_that(project.get_package("libcst").modules, has_items("libcst"))
