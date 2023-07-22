from os import PathLike
from pathlib import Path
import shutil


class PackageGenerator:
    """Creates actual files on disk for testing purposes"""
    def __init__(self):
        self.files: dict[PathLike, str] = {}

    def add_file(self, file_path: PathLike, content: str):
        self.files[file_path] = content

    def generate_files(self, root: PathLike, clear_root: bool = True):
        root = Path(root)
        if clear_root:
            shutil.rmtree(root, ignore_errors=True)
        root.mkdir(parents=True, exist_ok=True)
        for rel_path, content in self.files.items():
            file_path = root / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)