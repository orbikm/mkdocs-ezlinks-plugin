import re
from typing import Pattern, Match

from .base_link_scanner import BaseLinkScanner
from ..types import Link, BrokenLink


class WikiLinkScanner(BaseLinkScanner):
    def pattern(self) -> str:
        # +--------------------------------+
        # | Wiki Link Regex Capture Groups |
        # +------------------------------------------------------------------------------------+
        # | wiki_is_image |  Contains ! when an image tag, or empty if not                     |
        # | wiki_link     |  Contains the Link Text between [[ wiki_link ]]                    |
        # | wiki_anchor   |  Contains the anchor, if present (e.g. file.md#anchor -> 'anchor') |
        # | wiki_text     |  Contains the text of the link.                                    |
        # +------------------------------------------------------------------------------------+
        return \
            r'''
            (?P<wiki_is_image>[\!]?)
            \[\[
                (?P<wiki_link>[^#\|\]]+)
                (?:\#(?P<wiki_anchor>[^\|\]]+)?)?
                (?:\|(?P<wiki_text>[^\]]+)?)?
            \]\]
            '''

    def match(self, match: Match) -> bool:
        return match.groupdict().get('wiki_link') not in ['', None]

    def extract(self, match: Match) -> Link:
        groups = match.groupdict()

        image = groups.get('wiki_is_image') or ''
        link = groups.get('wiki_link') or ''
        text = groups.get('wiki_text') or link
        anchor = groups.get('wiki_anchor') or ''

        if not (link or text):
            raise BrokenLink(f"Could not extract required field `wiki_link` from {match.group(0)}")

        link = self._slugify(link)
        if anchor:
            anchor = self._slugify(anchor)

        return Link(
            image=image,
            text=text,
            target=link,
            title=text,
            anchor=anchor
        )

    def _slugify(self, link: str) -> str:
        # Convert to lowercase
        slug = link.lower()
        # Convert all spaces to '-'
        slug = re.sub(r'\ ', r'-', slug)
        # Convert all unsupported characters to ''
        slug = re.sub(r'[^\w\u4e00-\u9fff\- ]', '', slug)
        return slug
