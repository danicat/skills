# Google Codelab Formatting Guide

## File Extension
Use the `.lab.md` file extension.

## Metadata
Put metadata at the top.

```yaml
---
id: my-codelab-id
description: Short text.
authors: Author Name
project: path/to/project.yaml
book: path/to/book.yaml
layout: scrolling # or paginated
minutes: 20 # Codelab minutes
---
```

## Structure
- **Title**: Put the main title on the first line after metadata.
- **Steps**: Use Heading 2 (`## Step Title`) for steps.
- **Duration**: Add times in `MM:SS` right after step titles.
  ```md
  ## Step Title
  Duration: 05:00
  ```

## Components

### Info Boxes
Use blockquotes.

**Tips (Green):**
```md
> aside positive
> This is a tip.
```

**Warnings (Yellow):**
```md
> aside negative
> This is a warning.
```

### Code Blocks
- Use standard backticks.
- Use `console` for terminal.
  ```md
  ```console
  $ echo "hello"
  ```
  ```

### Imports
Import files:
```md
<<codelabs/shared/_install_go_macos.lab.md>>
```

### Buttons
Add buttons.
```md
<button>[Download Zip](https://example.com/file.zip)</button>
```

### Videos
Embed YouTube videos.
```md
<video id="VIDEO_ID"></video>
```

### Surveys
Create surveys:
```md
<form>
  <name>Question?</name>
  <input value="Yes"/>
  <input value="No"/>
</form>
```
