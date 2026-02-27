# Google Codelab Markdown Formatting Guide

## File Extension
Source files must have a `.lab.md` extension.

## Metadata (Frontmatter)
Must be at the top of the file.

```yaml
---
id: my-codelab-id
description: One sentence description.
authors: Author Name
project: /path/to/_project.yaml
book: /path/to/_book.yaml
layout: scrolling # or paginated
minutes: 20 # Overall duration estimation
---
```

## Structure
- **Title**: The first line after metadata must be a Heading 1 (`# Title`).
- **Steps**: Each step must be a Heading 2 (`## Step Title`).
- **Duration**: Optional duration for a step in `MM:SS` format. Place it immediately after the step title.
  ```md
  ## Step Title
  Duration: 05:00
  ```

## Special Components

### Info Boxes (Asides)
Use blockquotes with specific classes.

**Positive (Green/Tip):**
```md
> aside positive
> This is a tip or best practice.
```

**Negative (Yellow/Warning):**
```md
> aside negative
> This is a warning or important instruction.
```

### Code Blocks
- **Standard**: Triple backticks.
- **Terminal/Console**: Use `console` language identifier for non-colorized output.
  ```md
  ```console
  $ echo "hello"
  ```
  ```

### Fragments (Imports)
Import another markdown file (e.g., shared setup).
```md
<<codelabs/shared/_install_go_macos.lab.md>>
```

### Buttons
Direct download buttons.
```md
<button>[Download Zip](https://example.com/file.zip)</button>
```

### Videos
Embed YouTube videos by ID.
```md
<video id="VIDEO_ID"></video>
```

### Surveys
Simple multiple-choice surveys.
```md
<form>
  <name>Question text?</name>
  <input value="Option 1"/>
  <input value="Option 2"/>
</form>
```
