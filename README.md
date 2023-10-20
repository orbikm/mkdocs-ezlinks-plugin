*Fork*  
To install this fork :   
`pip install mkdocs-ezlinked-plugin`  

# mkdocs-ezlinks-plugin

![](logo.png)

Plugin for mkdocs which enables easier linking between pages.

This plugin was written in order to provide an up-to-date and
feature complete plugin for easily referencing documents
with a variety of features:

* Optimized file name lookup
* Code Block Preservation
* File name linking (e.g. `[Text](file#anchor "title")`)
* Absolute paths (e.g. `[Text](/link/to/file.md)`)
* WikiLinks support (e.g. `[[Link#anchor|Link Title]]`)
* Reference Link support (e.g. `[foo]: bar/ "Foo Title"`)

# Install
```
pip install mkdocs-ezlinks-plugin
```

Edit your mkdocs configuration file to enable the plugin:
```
plugins:
  - search
  - ezlinks
```
> **NOTE**  
>   If you have no plugins entry in your config file yet, you'll likely also want to add the search plugin. MkDocs enables it by default if there is no plugins entry set, but now you have to enable it explicitly.

# Release Log

## Release 0.1.14
This is a bugfix release.

Issues addressed:
  * GH issue #35, `Links between deeply nested subfolders fails.`
    Dev @Mara-Li reported an issue with wikilinks between deeply nested subfolders failing due to an incorrectly
    rendered relative link to the file.

  * An unreported Windows usage issue
    It's possible this bug existed for quite some time. Basically, on Windows, there was disagreement between the
    path separators used at different points in the file mapping and searching process. This unifies it to store
    and search for paths only with the `/` delimiter instead of the OS defined separator.


## Release 0.1.13
Adds support for Reference Link parsing. This is to support certain Foam editors, which generate [Reference Links](https://spec.commonmark.org/0.29/#reference-link).

Issues Addressed:
  * GH Issue #31, `Add support for reference link definitions`. Allows compatibility with certain Foam editors which generate Reference Links.

## Release 0.1.12
This is a bugfix release.

Issues addressed:
  * GH issue #25, `Absolute links not using http:// or https:// are treated as relative`.
    Dev @robbcrg (thanks!) reported that links with protocol schemes other than those two should also be treated as
    absolute links. The regex will exclude any link from a conformant protocol scheme from being converted using EzLinks.

  * GH Issue #27, `Dictionary file cache is not being leveraged`.
    An inverted comparison led to the fast file cache lookup never really being exercised. Now, if a filename is unique, it will find it in the fast file cache first, saving a more expensive full trie lookup.

## Release 0.1.11
This is a bugfix release. The prior release switched from a dictionary lookup to a prefix trie lookup strategy, which allowed for better disambiguation between links, but is more expensive. The bug was that, even if a link was direct, it would trigger a full trie search. Now, direct links
are checked and returned directly if the file exists.

Additionally, a slight performance improvement was made where, in the case that a filename is unique to the entire site, it will rely on a fast dictionary lookup instead of a trie lookup.

# Configuration Options
```
plugins:
    - search
    - ezlinks:
        warn_ambiguities: {true|false}
        wikilinks: {true|false}
        reference_links: {true|false}
```
## warn_ambiguities
Determines whether to warn when an abmiguous link is encountered. An ambiguous link is one that would have more than one possible targets. For example, if you had the following document setup:

```
+ folder1/
  +-- index.md
+ folder2/
  +-- index.md
```

If you had any links that targeted `index.md`, EzLinks is not able to determine _which_ of the instances of `index.md` to target, thus it is ambiguous.

### Disambiguating links
By default, EzLinks will attempt to resolve the ambiguity automatically. It does this by searching for the file closest to the file that is linking (with respect to the folder hierarchy).

```
+ guide/
  + test.md
  + getting_started/
      + index.md
+ tutorials/
  - test.md
  + getting_started/
      + index.md
  + more_advanced/
      + index.md
```
If you placed a link inside `guide/getting_started/index.md` such as `[Test](test)`, the resulting link has ambiguity, but in the default case, the `guide/test.md` file is _closer_ than the `tutorials/test.md`, therefore, it will select that file.

In the circumstance above, it would be possible to disambiguate _which_ `test.md` by including the containing folder, e.g. `guide/test.md` or `tutorials/test.md`. Note: This also works in conjunction with extension-less targets, e.g. `guide/test` and `tutorials/test`.

This disambiguation can continue with as many parent directories are specified, for instance `folder1/subfolder1/subfolder2/test.md`, specifying as many path components as necessary to fully disambiguate the links.

This method of disambiguation is supported by each of the supported link formats (MD links, wiki/roamlinks). For instance, you can use `[[folder1/index|Link Title]]` and `[[folder2/index.md]]`.

## wikilinks
Determines whether to scan for wikilinks or not (See [WikiLink Support](#wikilink-support)).
> **NOTE**  
>  This plugin feature does not function well when the 'wikilinks' markdown extension is enabled. This plugin's functionality should replace the need for enabling said extension.

## reference_links
Determins whether to scan for Reference Links or not (See [Reference Links](https://spec.commonmark.org/0.29/#reference-link), e.g. `[foo]: /bar "Foo Bar"`)

# Features
## Filename Links
Given a layout such as
```
- index.md
- folder/
  +-- filename.md
  +-- image.png
```

The following links will result in the following translations,

|Link|Translation|
|----|-----------|
| `[Link Text](filename)` | `[Link Text](folder/filename.md)`|
| `[Link Text](filename#Anchor)` | `[Link Text](folder/filename.md#Anchor)`|
| `[Link Text](filename.md)` | `[Link Text](folder/filename.md)`|
| `[Link Text](filename.md#Anchor)` | `[Link Text](folder/filename.md#Anchor)` |
| `![Image Alt Text](image)` | `![Image Alt Text](folder/image.png)` |
| `![Image Alt Text](image.png)` | `![Image Alt Text](folder/image.png)` |
| `![Image Alt Test](image "Image Title")` | `![Image Alt Text](folder/image.png "Image Title")` |


## Absolute Links
Given a layout such as
```
- static/
  +-- image.png
- folder/
  +-- document.md
- index.md
```
Given that we are entering the links into the `folder/document.md` file,

|Link|Translation|
|----|-----------|
| `![Link Text](/static/image.png)` | `![Link Text](../static/image.png)` |

# WikiLink Support
Given a layout such as
```
- folder1/
  +-- main.md
- folder2/
  +-- page-name.md
- images/
  +-- puppy.png
```
and these links are entered in `folder1/main.md`, this is how wikilinks will be translated

|Link|Translation|
|----|-----------|
| `[[Page Name]]` | `[Page Name](../folder2/page-name.md)` |
| `![[Puppy]]` | `![Puppy](../images/puppy.png)` | `[[Page Name#Section Heading]]` | `[Page Name](../relative/path/to/page-name.md#section-heading)` |
| `[[Page Name\|Link Text]]` | `[Link Text](../folder2/page-name.md)` |
| `[[Page Name#Section Heading\|Link Text]]` | `[Link Text](../folder2/page-name.md#section-heading)` |

# Attribution
This work is highly inspired from the following plugins:
  - [mkdocs-autolinks-plugin](https://github.com/midnightprioriem/mkdocs-autolinks-plugin/)
  - [mkdocs-roamlinks-plugin](https://github.com/Jackiexiao/mkdocs-roamlinks-plugin)
  - [mkdocs-abs-rel-plugin](https://github.com/sander76/mkdocs-abs-rel-plugin)

  I have combined some the features of these plugins, fixed several existing bugs, and am adding features in order to
  provide a cohesive, up-to-date, and maintained solution for the mkdocs community.
