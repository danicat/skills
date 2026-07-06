# Polyglot Extension

## Features
- Splits content by language or platform.
- Shows matching sections based on user choice.
- Remembers user choice.

## Installation
Turn on the polyglot extension in your configuration.

## Usage
Wrap content in a `<section class="polyglot">` tag. Use H6 titles with the `.pg-tab` class.

```markdown
<section class="polyglot">

###### Java {.pg-tab}
Java content...

###### Kotlin {.pg-tab}
Kotlin content...

</section>
```

## Inline Text
Use `.pg-inline` with language classes (like `.java` or `.kotlin`) to show or hide text elements.

```markdown
The code is written in `Java`{.pg-inline .java} `Kotlin`{.pg-inline .kotlin}.
```
