import os

import mkdocs

from .types import BrokenLink


class FileMapper:
    def __init__(
            self,
            root: str,
            files: list[mkdocs.structure.pages.Page],
            logger=None):
        self.root = root
        self.file_map = {}
        self.logger = logger

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
                    self.logger.debug("[EzLinks] Duplicate filename "
                                      f"`{search_name}` detected.")
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
                    duplicates = ""
                    for idx, file in enumerate(files):
                        active = "<-- Active" if idx == 0 else ""
                        duplicates += f"  [{idx}]   - {file} {active}\n"
                    self.logger.warning("[EzLinks] Link targeting a duplicate "
                                        f"file '{file_name}'.\n{duplicates}")
            abs_to = abs_to + '.md' if '.' not in abs_to else abs_to
            return os.path.join(self.root, abs_to)

    # Takes a file path, returns a tuple of:
    #   (file name with extension, file name without extension)
    def _get_search_names(self, path: str):
        file_name = os.path.basename(path)
        name, extension = os.path.splitext(file_name)
        return (file_name, name)
