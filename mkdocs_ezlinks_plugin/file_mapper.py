import os
from typing import List

import pygtrie
import mkdocs

from .types import EzLinksOptions


class FileMapper:
    def __init__(
            self,
            options: EzLinksOptions,
            root: str,
            files: List[mkdocs.structure.pages.Page],
            logger=None):
        self.options = options
        self.root = root
        self.file_trie = pygtrie.StringTrie(separator=os.sep)
        self.logger = logger

        # Drop any files outside of the root of the docs dir
        self.files = [file for file in files if root in file.abs_src_path]

        for file in self.files:
            self._store_file(file.src_path)

    def _store_file(self, file_path):
        # Store the pathwise reversed representation of the file with and
        # without file extension.
        search_exprs = [file_path, os.path.splitext(file_path)[0]]
        for search_expr in search_exprs:
            components = list(search_expr.split(os.sep))
            components.reverse()
            self.file_trie[os.sep.join(components)] = file_path

    def search(self, from_file: str, file_name: str):
        abs_to = file_name
        if abs_to.startswith('/'):
            abs_to = abs_to[1:]
        else:
            search_for = list(file_name.split(os.sep))
            search_for.reverse()
            search_for = f"{os.sep}".join(search_for)

            if self.file_trie.has_subtrie(search_for):
                values = self.file_trie.values(search_for)
                abs_to = values[0]
                if len(values) > 1:
                    ambiguities = ""
                    for idx, file in enumerate(values):
                        active = "<--- (Selected)" if idx == 0 else ""
                        ambiguities += f"  {idx}: {file} {active}\n"

                    log_fn = self.logger.warning if self.options.warn_ambiguities else self.logger.debug
                    log_fn(f"[EzLink] Link ambiguity detected.\n"
                           f"File: '{from_file}'\n"
                           f"Link: '{search_for}'\n"
                           "Ambiguities:\n" + ambiguities)

        abs_to = abs_to + '.md' if '.' not in abs_to else abs_to
        return os.path.join(self.root, abs_to)
