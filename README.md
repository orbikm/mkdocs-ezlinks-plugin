# mkdocs-ezlinks-plugin
Plugin for mkdocs which enables easier linking between pages.

This plugin was written in order to provide an up-to-date and
feature complete functionality for easily referencing documents
through a variety of techniques:

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

**NOTE**: If you have no plugins entry in your config file yet, you'll likely also want to add the search plugin. MkDocs enables it by default if there is no plugins entry set, but now you have to enable it explicitly. 

## Configuration Options
```
plugins:
    - search
    - ezlinks:
        - roamlinks: {TRUE|false}
        - absolute: {TRUE|false}
        - metalinks: {TRUE|false}
        - extensions: ['jpg', 'png', ...]
```

# Features
## Filename Links
Given a layout such as
```
- index.md
- folder/
+-- filename.md
```
The following links will result in the following translations
|Link|Translation|
|----|-----------|
|`[Link Text](filename)`|`[Link Text](folder/filename.md)`|
|`[Link Text](filename#Anchor)`|`[Link Text](folder/filename.md#Anchor)`|
|`[Link Text](filename.md)`|`[Link Text](folder/filename.md)`|
|`[Link Text](filename.md#Anchor)`|`[Link Text](folder/filename.md#Anchor)`|


## Absolute Links
Given a layout such as
```
- index.md
- static/
+-- image.png
- folder/
+-- document.md
```
Given that we are entering the links into the `folder/document.md` file,
|Link|Translation|
|----|-----------|
|`![Link Text](/static/image.png)`|`![Link Text](../static/image.png)`|

This behavior can be disabled by setting the `absolute` property to `false` in the mkdocs configuration file.

# WikiLink Support


# Attribution
This work is highly inspired and derived from the following excellent plugins:
  - [mkdocs-autolinks-plugin](https://github.com/midnightprioriem/mkdocs-autolinks-plugin/)
  - [mkdocs-roamlinks-plugin](https://github.com/Jackiexiao/mkdocs-roamlinks-plugin)
  - [mkdocs-abs-rel-plugin](https://github.com/sander76/mkdocs-abs-rel-plugin)

  I have combined some the features of these plugins, fixed several existing bugs, and am attempting to provide a cohesive, up-to-date, and maintained solution for the mkdocs community.
