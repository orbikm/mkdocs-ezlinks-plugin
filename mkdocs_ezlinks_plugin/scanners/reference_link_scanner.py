from typing import Pattern, Match
from .base_link_scanner import BaseLinkScanner
from ..types import Link


class ReferenceLinkScanner(BaseLinkScanner):
    def pattern(self) -> str:
        # +--------------------------------------+
        # | Reference Link Regex Capture Groups  |
        # +--------------------------------------+
        # | Example: [text]: url "title"         |
        # |                                      |
        # |  text: Required                      |
        # |   url: Required                      |
        # | title: Optional, up to one newline   |
        # +--------------------------------------+
        return r"""
        (?:
        \[
            (?P<ref_text>[^\]]+)
        \]
        )\:\ 
        (?!(?P<ref_protocol>[a-z][a-z0-9+\-.]*:\/\/))
        (?P<ref_target>\/?[^\#\ \)(\r\n|\r|\n)]*)?
        (?:\#(?P<ref_anchor> [^\(\ ]*)?)?
        (?:(\r\n|\r|\n)?)?(?P<ref_title>\ ?\"[^(\r\n|\r|\n)\"]*\")?
        """

    def match(self, match: Match) -> bool:
        return bool(
            match.groupdict().get("ref_text") and match.groupdict().get("ref_target")
        )

    def extract(self, match: Match) -> Link:
        groups = match.groupdict()
        return Link(
            image=False,
            text=groups.get("ref_text") or "",
            target=groups.get("ref_target") or "",
            title=groups.get("ref_title") or "",
            anchor=groups.get("ref_anchor") or "",
        )
