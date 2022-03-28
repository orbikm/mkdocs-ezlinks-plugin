import logging
from typing import List

import mkdocs
from mkdocs.utils import warning_filter
from mkdocs.structure import files as fl
from .file_mapper import FileMapper
from .replacer import EzLinksReplacer
from .scanners.md_link_scanner import MdLinkScanner
from .scanners.wiki_link_scanner import WikiLinkScanner
from .scanners.reference_link_scanner import ReferenceLinkScanner
from .types import EzLinksOptions

LOGGER = logging.getLogger(f"mkdocs.plugins.{__name__}")
LOGGER.addFilter(warning_filter)


class EzLinksPlugin(mkdocs.plugins.BasePlugin):
    config_scheme = (
        ("wikilinks", mkdocs.config.config_options.Type(bool, default=True)),
        ("warn_ambiguities", mkdocs.config.config_options.Type(bool, default=False)),
        ("reference_links", mkdocs.config.config_options.Type(bool, default=False)),
    )

    def init(self, config):
        self.replacer = EzLinksReplacer(
            root=config["docs_dir"],
            file_map=self.file_mapper,
            use_directory_urls=config["use_directory_urls"],
            options=EzLinksOptions(**self.config),
            logger=LOGGER,
        )

        self.replacer.add_scanner(MdLinkScanner())
        if self.config["wikilinks"]:
            self.replacer.add_scanner(WikiLinkScanner())

        if self.config["reference_links"]:
            self.replacer.add_scanner(ReferenceLinkScanner())

        # Compile the regex once
        self.replacer.compile()

    # Build a fast lookup of all files (by file name)
    def on_files(self, files: List[fl.File], config):
        self.file_mapper = FileMapper(
            options=EzLinksOptions(**self.config),
            root=config["docs_dir"],
            files=files,
            logger=LOGGER,
        )

        # After the file map has been built, initialize what we can that will
        # remain static
        self.init(config)

    def on_page_markdown(self, markdown, page, config, **kwargs):
        return self.replacer.replace(page.file.src_path, markdown)
