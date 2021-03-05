from typing import Pattern, Match

from .base_link_scanner import BaseLinkScanner
from ..types import EzLinksOptions, Link


class MdLinkScanner(BaseLinkScanner):
    def pattern(self) -> Pattern:
        # +------------------------------+
        # | MD Link Regex Capture Groups |
        # +-------------------------------------------------------------------------------------+
        # | md_is_image      |  Contains ! when an image tag, or empty if not (check both)      |
        # | md_alt_is_image  |  Contains ! when an image tag, or empty if not (check both)      |
        # | md_text          |  Contains the Link Text between [md_text]                        |
        # | md_target        |  Contains the full target of the Link (filename.md#anchor)       |
        # | md_filename      |  Contains just the filename portion of the target (filename.md)  |
        # | md_anchor        |  Contains the anchor, if present (e.g. `file.md#anchor`)         |
        # | md_title         |  Contains the title, if present (e.g. `file.md "My Title"`)      |
        # +-------------------------------------------------------------------------------------+
        return \
            r'''
            (?:
                (?P<md_is_image>\!?)\[\]
                |
                (?P<md_alt_is_image>\!?)
                \[
                    (?P<md_text>.+)
                \]
            )
            \(
                (?P<md_target>
                    (?!http://|https://)
                    (?P<md_filename>\/?[^\#\ \)]*)?
                    (?:\#(?P<md_anchor>[^\)\"]*)?)?
                    (?:\ \"(?P<md_title>[^\"\)]*)\")?
                )
            \)
            '''

    def match(self, match: Match) -> bool:
        return bool(match.groupdict().get('md_target'))

    def extract(self, match: Match) -> Link:
        groups = match.groupdict()
        return Link(
            image=groups.get('md_is_image') or groups.get('md_alt_is_image') or '',
            text=groups.get('md_text') or '',
            target=groups.get('md_filename') or '',
            title=groups.get('md_title') or '',
            anchor=groups.get('md_anchor') or ''
        )
