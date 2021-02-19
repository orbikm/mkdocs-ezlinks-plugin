import re
import os
import mkdocs
from dataclasses import dataclass

class BrokenLink(Exception):
    pass

@dataclass
class Link:
    ''' Dataclass to hold the contents required to form a complete Link. '''
    image: bool
    text: str
    target: str
    anchor: str
    title: str

@dataclass
class EzLinksOptions:
    ''' Dataclass to hold typed options from the configuration. '''
    strict: bool
    absolute: bool
    wikilinks: bool

class EzLinksReplacer:
    def __init__(self, options: EzLinksOptions, filenames: list[str], root: str, page_url: str):
        self.options = options
        self.filenames = filenames
        self.root = root
        self.page_url = page_url

    def __call__(self, match: re.Match) -> str:
        groups = match.groupdict()
        try:
            if groups['md_target']:
                link = self._get_md_link(match)
            elif groups['wiki_link']:
                link = self._get_wiki_link(match)
            else:
              return match.group(0)

            # Render the link
            img = '!' if link.image else ''
            anchor = f"#{link.anchor}" if link.anchor else ''
            title = f' "{link.title}"' if link.title else ''

            return f"{img}[{link.text}]({link.target}{anchor}{title})"
        except BrokenLink as ex:
            if self.options.strict:
                print(f"ERROR -  {ex}")
            else:
                print(f"WARNING -  {ex}")
            return match.group(0)

    def _is_absolute_link(self, link):
        return link and link.startswith('/')

    # Attempts to convert a filename to a relative path to the specified file.
    # It uses the prebuilt map of filename -> list of file paths to speed the search
    # If the link is absolute, it appends the path to the root, enabling absolute links.
    # If the link is a filename, it will perform the search.
    def _get_link_to_file(self, filename: str) -> str:
        search_names = EzLinksReplacer.search_names(filename)
        # Always searches for full filename with the extension first
        for search_name in search_names:
            abs_from = os.path.dirname(os.path.join(self.root, self.page_url))
            if filename.startswith('/'):
                abs_to = os.path.join(self.root, filename[1:])
                if not self.options.absolute:
                    print(f"WARNING -  Absolute link '{filename}' detected, but absolute link support disabled.")
                    return filename
            else:
                files = self.filenames.get(search_name)
                if not files:
                    raise BrokenLink(f"Unable to find filename '{search_name}', from link {filename}")
                abs_to = os.path.join(self.root, files[0])
                if len(files) > 1:
                    print(f"WARNING -  Link targeting a duplicate filename '{filename}'.")
                    for idx,file in enumerate(files):
                        active = "<-- Active" if idx == 0 else ""
                        print(f"   [{idx}] - {file} {active}")
            abs_to = abs_to + '.md' if '.' not in abs_to else abs_to
            return os.path.relpath(abs_to, abs_from)

    # Generate a Link with the details supplied by an md link
    def _get_md_link(self, match: re.Match) -> Link:
        groups = match.groupdict()
        # Straight .get doesn't work, because in absence of a capture group,
        # it is '', not None
        full_match = match.group(0)
        md_filename = groups.get('md_filename')
        filename = md_filename if md_filename not in ['', None] else self.page_url
        target = self._get_link_to_file(filename)
        return Link(
            image=groups.get('md_is_image') or groups.get('md_alt_is_image'),
            text=groups.get('md_text', ''),
            target=target,
            title=groups.get('md_title', ''),
            anchor=groups.get('md_anchor', '')
        )

    # Generate a Link with the details supplied by a wikilink
    def _get_wiki_link(self, match: re.Match) -> Link:
        full_link = match.group(0)
        groups = match.groupdict()

        wiki_link = groups.get('wiki_link')
        if wiki_link in ['', None]:
            raise BrokenLink(f"Broken wikilink detected. '{full_link}', could not extract link.")

        # Slugify the link
        link = self._slugify(wiki_link)
        # Search the cache for the linked file
        link = self._get_link_to_file(link)

        # Slugify the anchor, if it exists
        anchor = groups.get('wiki_anchor')
        if anchor not in ['', None]:
            anchor = self._slugify(anchor)

        wiki_text = groups.get('wiki_text')
        result = Link(
            image=groups.get('wiki_is_image'),
            text=wiki_text if wiki_text and wiki_text != '' else wiki_link,
            target=link,
            anchor=anchor,
            title=wiki_text
        )
        return result

    # Reference: https://gist.github.com/asabaylus/3071099
    def _slugify(self, link: str) -> str:
        # Convert to lowercase
        slug = link.lower()
        # Convert all spaces to '-'
        slug = re.sub('\ ', '-', slug)
        # Convert all unsupported characters to ''
        slug = re.sub('[^\w\u4e00-\u9fff\- ]', '', slug)
        return slug


    @staticmethod
    def search_names(path: str) -> str:
        filename = os.path.basename(path)
        name, extension = os.path.splitext(filename)
        # remove any extensions
        return (filename, name)


class EzLinksPlugin(mkdocs.plugins.BasePlugin):
    config_scheme = (
        ('absolute',   mkdocs.config.config_options.Type(bool, default=True)),
        ('wikilinks',  mkdocs.config.config_options.Type(bool, default=True)),
    )

    # Build a map of filenames for easier lookup at build time
    def on_files(self, files: list[mkdocs.structure.files.File], config):
        self.filenames = {}
        for file in files:
            # Ignore any files generated from files outside of the docs root,
            # which include theme files.
            if config['docs_dir'] not in file.abs_src_path:
                continue
            fmt_names = EzLinksReplacer.search_names(file.src_path)
            for fmt_name in fmt_names:
                if not self.filenames.get(fmt_name):
                    self.filenames[fmt_name] = []
                else:
                    print(f"WARNING -  Duplicate filename `{fmt_name}` detected. Linking to them will match the first (alphabetically ordered) file.")
                    print("            You can use `metalinks` to link to these files without renaming, if they're enabled.")
                self.filenames[fmt_name].append(file.src_path)

    def on_page_markdown(self, markdown, page, config, site_navigation=None, **kwargs):
        root = config["docs_dir"]

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
        md_link_pattern =\
            r'(?:'                                        \
                r'(?P<md_is_image>\!?)\[\]'               \
                r'|'                                      \
                r'(?P<md_alt_is_image>\!?)'               \
                r'\['                                     \
                    r'(?P<md_text>.+)'                    \
                r'\]'                                     \
            r')'                                          \
            r'\('                                         \
                r'(?P<md_target>'                         \
                    r'(?P<md_filename>\/?[^#\ \)]*)?'     \
                    r'(?:#(?P<md_anchor>[^\)\"]*)?)?'     \
                    r'(?:\ \"(?P<md_title>[^\"\)]*)\")?'  \
                r')'                                      \
            r'\)'

        # +--------------------------------+
        # | Wiki Link Regex Capture Groups |
        # +------------------------------------------------------------------------------------+
        # | wiki_is_image |  Contains ! when an image tag, or empty if not                     |
        # | wiki_link     |  Contains the Link Text between [[ wiki_link ]]                    |
        # | wiki_anchor   |  Contains the anchor, if present (e.g. file.md#anchor -> 'anchor') |
        # | wiki_text     |  Contains the text of the link.                                    |
        # +------------------------------------------------------------------------------------+
        wiki_link_pattern =\
            r'(?P<wiki_is_image>[\!]?)'             \
            r'\[\['                                 \
                r'(?P<wiki_link>[^#\|\]]+)'         \
                r'(?:#(?P<wiki_anchor>[^\|\]]+)?)?' \
                r'(?:\|(?P<wiki_text>[^\]]+)?)?'   \
            r'\]\]'

        patterns = [md_link_pattern]

        if self.config['wikilinks']:
          patterns.append(wiki_link_pattern)

        # Multi-Pattern search pattern, to capture  all link types at once
        uber_pattern = f"(?:{'|'.join(patterns)})"

        options = EzLinksOptions(**self.config, strict=config['strict'])
        markdown = re.sub(
            uber_pattern,
            EzLinksReplacer(
                options,
                self.filenames,
                root,
                page.file.src_path),
            markdown)
        return markdown