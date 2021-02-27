import os

import mkdocs

from .types import BrokenLink


class FileMapper:
    def __init__(self, root: str, files: list[mkdocs.structure.pages.Page]):
        self.root = root
        self.file_map = {}

        for file in files:
            # Ignore any files generated from files outside of the docs root,
            # which include theme files.
            if root not in file.abs_src_path:
                continue
            search_names = self._get_search_names(file.src_path)
            for search_name in search_names:
                if not self.file_map.get(search_name):
                    self.file_map[search_name] = []
                else:
                    print(f"WARNING -  Duplicate filename `{search_name}` detected. Linking to it will only match the first file.")
                self.file_map[search_name].append(file.src_path)

    def search(self, file_name: str):
        for search_name in self._get_search_names(file_name):
            if file_name.startswith('/'):
                abs_to = file_name[1:]
            else:
                if not (files := self.file_map.get(search_name)):
                    return None
                abs_to = files[0]
                if len(files) > 1:
                    print(f"WARNING -  Link targeting a duplicate file '{file_name}'.")
                    for idx, file in enumerate(files):
                        active = "<-- Active" if idx == 0 else ""
                        print(f"  [{idx}]   - {file} {active}")
            abs_to = abs_to + '.md' if '.' not in abs_to else abs_to
            return os.path.join(self.root, abs_to)

    # Takes a file path, returns a tuple of:
    #   (file name with extension, file name without extension)
    def _get_search_names(self, path: str):
        file_name = os.path.basename(path)
        name, extension = os.path.splitext(file_name)
        return (file_name, name)
