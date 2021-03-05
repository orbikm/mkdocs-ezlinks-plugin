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

# Configuration Options
```
plugins:
    - search
    - ezlinks:
        wikilinks: {true|false}
```
## wikilinks
Determines whether to scan for wikilinks or not (See [WikiLink Support](#wikilink-support)).
> **NOTE**  
>  This plugin feature does not function well when the 'wikilinks' markdown extension is enabled. This plugin's functionality should replace the need for enabling said extension.

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
