import os
from typing import List
import pygtrie
import mkdocs
from pathlib import Path

from .types import EzLinksOptions
from mkdocs.structure import pages as mkpage

class FileMapper:
    def __init__(
        self,
        options: EzLinksOptions,
        root: str,
        files: List[mkpage.Page],
        logger=None,
    ):
        self.options = options
        self.root = root
        self.file_cache = {}
        self.file_trie = pygtrie.StringTrie(separator="/")
        self.logger = logger

        # Drop any files outside of the root of the docs dir
        self.files = [file for file in files if root in file.abs_src_path]

        for file in self.files:
            self._store_file(file.src_path)

    def _store_file(self, file_path):
        # Treat paths as posix format, regardless of OS
        file_path = str(Path(file_path))  # Path is a better way to normalize filepath !
        # Store the pathwise reversed representation of the file with and
        # without file extension.
        search_exprs = [file_path, os.path.splitext(file_path)[0]]
        for search_expr in search_exprs:
            # Store in fast file cache
            file_name = os.path.basename(search_expr)
            if file_name not in self.file_cache:
                self.file_cache[file_name] = [file_path]
            else:
                self.file_cache[file_name].append(file_path)
            # Store in trie
            components = list(search_expr.split("/"))
            components.reverse()
            self.file_trie["/".join(components)] = file_path

        # Reduce the dictionary to only search terms that are unique
        self.file_cache = {k: v for (k, v) in self.file_cache.items() if len(v) == 1}

    def search(self, from_file: str, file_path: str):
        abs_to = file_path
        # Detect if it's an absolute link, then just return it directly
        if abs_to.startswith("/"):
            return os.path.join(self.root, abs_to[1:])
        elif abs_to.startswith(".."):
            return os.path.join(os.path.dirname(from_file), abs_to)
        else:
            # Check if it is a direct link first
            from_dir = os.path.dirname(from_file)
            if os.path.exists(os.path.join(self.root, from_dir, file_path)):
                return os.path.join(self.root, from_dir, file_path)

            # It's an EzLink that must be searched
            file_name = os.path.basename(file_path)

            # Check fast file cache first
            if os.path.basename(file_name) in self.file_cache:
                abs_to = self.file_cache[file_name][0]
            else:

                search_for = list(file_path.split("/"))
                search_for.reverse()
                search_for = "/".join(search_for)

                # If we have an _exact_ match in the trie, we don't need to search
                if search_for in self.file_trie:
                    abs_to = self.file_trie[search_for]
                elif self.file_trie.has_subtrie(search_for):
                    # If we don't have an exact match, but have a partial prefix
                    values = self.file_trie.values(search_for)
                    abs_to = values[0]
                    has_ambiguity = len(values) > 1
                    # If we have ambiguities, attempt to auto-disambiguate by performing
                    # an iterative ascent of the link file's path. In this way, we should
                    # be able to get the result closest to the file doing the linking
                    if has_ambiguity:
                        file_path = os.path.dirname(from_file)
                        components = file_path.split("/")
                        components.reverse()
                        for path_component in components:
                            search_for += f"/{path_component}"
                            if (
                                self.file_trie.has_subtrie(search_for)
                                or search_for in self.file_trie
                            ):
                                new_vals = self.file_trie.values(search_for)
                                if len(new_vals) == 1:
                                    abs_to = new_vals[0]
                                    # We've resolved the ambiguity, so no need to warn
                                    has_ambiguity = False
                                    break

                    if has_ambiguity:
                        ambiguities = ""
                        for idx, file in enumerate(values):
                            active = "<--- (Selected)" if idx == 0 else ""
                            ambiguities += f"  {idx}: {file} {active}\n"
                        log_fn = (
                            self.logger.warning
                            if self.options.warn_ambiguities
                            else self.logger.debug
                        )
                        log_fn(
                            "[EzLink] Link ambiguity detected.\n"
                            f"File: '{from_file}'\n"
                            f"Link: '{search_for}'\n"
                            "Ambiguities:\n"
                            + ambiguities
                        )
        return os.path.join(self.root, abs_to)
