# Polyglot Extension

## Features
- Divides content by language/platform.
- Surfaces matching sections based on selection.
- Persists user selection.

## Installation
Enable the polyglot extension in your codelab environment configuration.

## Usage
Wrap content in `<section class="polyglot">` and use H6 headings with `.pg-tab` class.

```markdown
<section class="polyglot">

###### Java {.pg-tab}
Java content...

###### Kotlin {.pg-tab}
Kotlin content...

</section>
```

## Inline Content
Use `.pg-inline` with language classes (e.g., `.java`, `.kotlin`) to show/hide specific elements.

```markdown
The code is written in `Java`{.pg-inline .java} `Kotlin`{.pg-inline .kotlin}.
```
