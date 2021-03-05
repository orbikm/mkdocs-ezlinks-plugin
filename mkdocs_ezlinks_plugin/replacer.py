import os
import re
from typing import Match

from .types import EzLinksOptions, BrokenLink
from .scanners.base_link_scanner import BaseLinkScanner
from .file_mapper import FileMapper


class EzLinksReplacer:
    def __init__(
            self,
            root: str,
            file_map: FileMapper,
            options: EzLinksOptions,
            logger):
        self.root = root
        self.file_map = file_map
        self.options = options
        self.scanners = []
        self.logger = logger

    def add_scanner(self, scanner: BaseLinkScanner) -> None:
        self.scanners.append(scanner)

    def replace(self, path: str, markdown: str) -> str:
        self.path = path
        # Multi-Pattern search pattern, to capture  all link types at once
        return re.sub(self.regex, self._do_replace, markdown)

    # Compiles all scanner patterns as a multi-pattern search, with
    # built in code fence skipping (individual link scanners don't
    # have to worry about them.
    def compile(self):
        patterns = '|'.join([scanner.pattern() for scanner in self.scanners])
        self.regex = re.compile(
            fr'''
            (?: # Attempt to match a code block
                [`]{{3}}
                (?:[\w\W]*?)
                [`]{{3}}$
            | # Match an inline code block
                `[\w\W]*?`
            )
            | # Attempt to match any one of the subpatterns
            (?:
                {patterns}
            )
            ''', re.X | re.MULTILINE)

    def _do_replace(self, match: Match) -> str:
        abs_from = os.path.dirname(os.path.join(self.root, self.path))

        try:
            for scanner in self.scanners:
                if scanner.match(match):
                    link = scanner.extract(match)

                    # Do some massaging of the extracted results
                    if not link:
                        raise BrokenLink(f"Could not extract link from '{match.group(0)}'")

                    # Handle case of local page anchor
                    if not link.target:
                        if link.anchor:
                            link.target = os.path.join(self.root, self.path)
                        else:
                            raise BrokenLink(f"No target for link '{match.group(0)}'")
                    else:
                        # Otherwise, search for the target through the file map
                        search_result = self.file_map.search(link.target)
                        if not search_result:
                            raise BrokenLink(f"'{link.target}' not found.")
                        link.target = search_result

                    link.target = os.path.relpath(link.target, abs_from)
                    return link.render()
        except BrokenLink as ex:
            # Log these out as Debug messages, as the regular mkdocs
            # strict mode will log out broken links.
            self.logger.debug(f"[EzLinks] {ex}")

        # Fall through, return the original link unaltered, and let mkdocs handle it
        return match.group(0)
