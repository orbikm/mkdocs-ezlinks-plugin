import re
import os
import mkdocs
from dataclasses import dataclass

# For Regex, match groups are:
#       0: Whole markdown link e.g. [Alt-text](url)
#       1: Alt text
#       2: Full URL e.g. url + hash anchor
#       3: Filename e.g. filename.md
#       4: File extension e.g. .md, .png, etc.
#       5. hash anchor e.g. #my-sub-heading-link

# For Regex, match groups are:
#       0: Whole roamlike link e.g. [[filename#title|alias]]
#       1: Whole roamlike link e.g. filename#title|alias
#       2: filename
#       3: #title
#       4: |alias
# roamlink_pattern = re.compile(
#     r'\[\[(?P<test>([^\]#\|]*)(#[^\|\]]+)*(\|[^\]]*)*)\]\]'
# 

class BrokenLink(Exception):
    pass

@dataclass
class Link:
    ''' Dataclass to hold the contents required to form a complete Link. '''
    image: bool
    text: str
    target: str
    anchor: str

@dataclass
class EzLinksOptions:
    ''' Dataclass to hold typed options from the configuration. '''
    strict: bool
    absolute: bool
    roamlinks: bool
    metalinks: bool
    extensions: list[str]

class EzLinksReplacer:
    def __init__(self, options: EzLinksOptions, filenames: list[str], root: str, page_url: str):
        self.options = options
        self.filenames = filenames
        self.root = root
        self.page_url = page_url

    def __call__(self, match: re.Match) -> str:
        groups = match.groupdict()
        try:
            # TODO: Extract the explicit check here, with more of a Chain of Responsibility pattern of
            #       link type classifier (e.g. if self.get_link_type(groups) == LinkType.Roam: ...)
            if groups['target']:
                link = self._get_md_link(match)            
            elif groups['roam_filename']:
                link = self._get_roam_link(match)
            else:
              return match.group(0)

            # Render the link
            rendered_link = f"{'!' if link.image else ''}[{link.text}]({link.target}{'#' + link.anchor if link.anchor else ''})"
            return rendered_link
        except BrokenLink as ex:
            if self.options.strict:
                print(f"ERROR -  {ex}")
            else:
                print(f"WARNING -  {ex}")
            return match.group(0)

    def _is_absolute_link(self, link):
        return link and link.startswith('/')

    def _get_md_link(self, match: re.Match) -> Link:
        groups = match.groupdict()
        search_name = EzLinksReplacer.search_name(groups['filename'])

        # Find the absolute path of the current page (Generate relative path, from here)
        abs_from = os.path.dirname(os.path.join(self.root, self.page_url))

        # Use simple strategy for absolute links
        if self._is_absolute_link(groups['filename']):
            if not self.options.absolute:
                print(f"WARNING -  Absolute link '{match.group(0)}' detected, but absolute link support disabled.")
                # Return the whole string, unaltered
                return None

            target = groups['filename']
            target = target + '.md' if '.' not in target else target
            abs_to = os.path.join(self.root, target[1:])
            
            final_link = os.path.relpath(abs_to, abs_from)              
        # Lookup the target document in the filename cache
        elif files := self.filenames.get(search_name):
            # Find the absolute path to the first instance of the filename
            abs_to = os.path.join(self.root, files[0])
            final_link = os.path.relpath(abs_to, abs_from)

            if len(files) > 1:
                print(f"WARNING: Multiple files with filename '{groups['filename']}'")
                for idx,file in enumerate(files):
                    active = "<-- Active" if idx == 0 else ""
                    print(f"   [{idx}] - {file} {active}")         
        else:
            raise BrokenLink(f"File name '{search_name}' not found in project files.")

        return Link(
          image=groups.get('is_image') or groups.get('alt_is_image'),
          text='' if not groups.get('text') else groups.get('text'),
          target=final_link,
          anchor='' if not groups.get('anchor') else groups.get('anchor'))

    def _get_roam_link(self, match: re.Match) -> Link:
        groups = match.groupdict()
        return Link(
            image=False,
            text=groups['roam_filename'],
            target=groups['roam_filename'],
            anchor=''
        )
        
    @staticmethod
    def search_name(path: str) -> str:
        # Strip the directory from the filename
        filename = os.path.basename(path)

        # If we assume_md, strip the extensions off of any md we find
        name, extension = os.path.splitext(filename)
        # If there is no .md, or if there is an extension and it _is_ .md,

        # strip it
        return name if extension and extension == '.md' else filename

        
class EzLinksPlugin(mkdocs.plugins.BasePlugin):
    config_scheme = (
        ('absolute', mkdocs.config.config_options.Type(bool, default=True)),
        ('roamlinks',  mkdocs.config.config_options.Type(bool, default=True)),
        ('metalinks',  mkdocs.config.config_options.Type(bool, default=True)),
        ('extensions', mkdocs.config.config_options.Type(list, default=['png', 'jpg', 'gif', 'bmp', 'jpeg']))
    )

    # Build a map of filenames for easier lookup at build time
    def on_files(self, files: list[mkdocs.structure.files.File], config):
        self.filenames = {}

        for file in files:
            fmt_name = EzLinksReplacer.search_name(file.src_path)
            if not self.filenames.get(fmt_name):
                self.filenames[fmt_name] = []
            else:
                print(f"WARNING -  Duplicate filename `{fmt_name}` detected. Linking to them will match the first (alphabetically ordered) file.")
                print("            You can use `metalinks` to link to these files without renaming, if they're enabled.")
            self.filenames[fmt_name].append(file.src_path)

    def on_page_markdown(self, markdown, page, config, site_navigation=None, **kwargs):
        root = config["docs_dir"]

        # First conditional, checks explicitly for an empty image text, which is
        # allowed, but not an empty text regular link.
        #
        #  Check for Empty Image Text (Allowed)
        #    ![]     --   match   --+->  (?P<is_image>\!?)\[\]
        #    ![Text] -- no match --/
        #
        #  Check for Text of the link, between square brackets, 
        #  at least one of any character.
        #
        #    [The Text [of] the Link]  --   match   --+->  (?P<text>.+)
        #    ![Text]
        #    []        ----------------  no match  --/
        #
        #   Check for the Target, Filename, and Anchor (TODO: Link Titles),
        #   between parentheses, all characters except ' ' or '#'.
        #       Capture: target - The full link target, including file name and anchor
        #       Capture: filename - The name of the target file, any characters except
        #
        #       Capture: anchor - After a '#', any characters except ' ' or ')'
        #       TODO: Capture: title - Any character except '"' between quotations found
        #                              after a 
        #  ()
        # TODO: Support - [Alt Text](my-page.md "My Title") (Link titles)
        md_link_pattern =\
            r'(?:'                                  \
              r'(?P<is_image>\!?)\[\]'              \
              r'|'                                  \
              r'(?P<alt_is_image>\!?)'              \
              r'\['                                 \
                  r'(?P<text>.+)'                   \
              r'\]'                                 \
            r')'                                    \
            r'\('                                   \
              r'(?P<target>'                        \
                r'(?P<filename>\/?[^#\ \)]+)'       \
                    r'(?:#(?P<anchor>[^ \)]+?)?)?'  \
              r')'                                  \
            r'\)'

        #    r'\[\[(?P<roam_filename>([^\]#\|]*)#(?P<title>[^\|\]]+)*(?P<alias>\|[^\]]*)*)\]\]' if self.config['roamlinks'] else ""      # Roam Links 
        roam_link_pattern =\
            r'\['                                   \
              r'\['                                 \
                r'(?P<roam_filename>([^\]#\|]*)'    \
                  r'#(?P<title>[^\|\]]+)*'          \
                  r'(?P<alias>\|[^\]]*)*)'          \
              r'\]'                                 \
            r'\]' if self.config['roamlinks'] else ""
        
        if self.config['roamlinks']:
          print("WARNING  - roamlinks support enabled, but not currently supported. This message is harmless.")

        patterns = [md_link_pattern, roam_link_pattern]

        # Multi-Pattern search pattern, to capture all link types at once
        uber_pattern = f"(?:{'|'.join(patterns)})"
        
        options = EzLinksOptions(**self.config, strict=config['strict'])
        markdown = re.sub(uber_pattern, EzLinksReplacer(
                                            options,
                                            self.filenames,
                                            root,
                                            page.file.src_path), markdown)
        return markdown