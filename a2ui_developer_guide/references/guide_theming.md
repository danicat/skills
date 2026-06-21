# guide_theming
Source: https://a2ui.org/guides/theming/

# Theming & Styling[¶](#theming-styling "Permanent link")

Customize the look and feel of A2UI components to match your brand.

## The A2UI Styling Philosophy[¶](#the-a2ui-styling-philosophy "Permanent link")

A2UI follows a **renderer-controlled styling** approach by default, but allows for flexibility through catalogs:

* **Agents describe *what* to show** (components and structure)
* **Renderers decide *how* it looks** (colors, fonts, spacing)

However, the protocol is flexible enough to allow agents to influence styling when needed.

## Styling Layers[¶](#styling-layers "Permanent link")

A2UI styling works in layers:

```
flowchart TD
    A["Agent-provided styling<br/>Semantic hints and theme data<br/>(e.g., usageHint: 'h1')"]
    B["Catalog Theming<br/>Catalog interprets theme data<br/>or uses defaults"]
    C["Platform theming<br/>Developer customizes<br/>(CSS variables, stylesheets...)"]
    D["Rendered Output"]

    A --> B --> C --> D
```

## Agent-provided styling information[¶](#agent-provided-styling-information "Permanent link")

### Semantic hints[¶](#semantic-hints "Permanent link")

Agents provide semantic hints (not visual styles) to guide rendering. In the *basic catalog*:

```
{
  "id": "title",
  "component": {
    "Text": {
      "text": {"literalString": "Welcome"},
      "usageHint": "h1"
    }
  }
}
```

**Common `usageHint` values:**

* Text: `h1`, `h2`, `h3`, `h4`, `h5`, `body`, `caption`
* Other components have their own hints (see [Component Reference](../../reference/components/))

The catalog elements map these semantic hints to actual components on the target platform, and styles them.

### `theme` property[¶](#theme-property "Permanent link")

The A2UI protocol allows for an arbitrary `theme` property in the `createSurface` message. For now, this property is
defined as `z.any().optional()` in the Zod schema, meaning the agent can pass any JSON structure that the client
renderer and catalog understand.

* See the schema definition in [server-to-client.ts](https://github.com/a2ui-project/a2ui/blob/main/renderers/web_core/src/v0_9/schema/server-to-client.ts).
* See the `Catalog` class and `themeSchema` in [catalog/types.ts](https://github.com/a2ui-project/a2ui/blob/main/renderers/web_core/src/v0_9/catalog/types.ts).

**Note:** The *basic catalog* components are not wired to use the `theme` coming from the agent.

*Want to influence this design? Chime in here: [#1118](https://github.com/a2ui-project/a2ui/issues/1118).*

## Catalog theming[¶](#catalog-theming "Permanent link")

Theming is a responsibility of the catalog implementation. Each catalog can provide whatever theming solution it wants.
As an example, this is how the default *basic catalog* does it:

### The Web Basic Catalog Theming[¶](#the-web-basic-catalog-theming "Permanent link")

On the web, the *basic catalog* provided by the default A2UI renderers is themed by overriding CSS variables.

Basic catalog components inject a small stylesheet with default values for these variables. The stylesheet targets
`:where(:root)` so their specificity is minimal, and the host app can override them easily.

For example, to override the primary color, you can simply add this to your app's CSS:

```
:root {
  --a2ui-color-primary: #ff5722;
}
```

See the default styles in [default.ts](https://github.com/a2ui-project/a2ui/blob/main/renderers/web_core/src/v0_9/basic_catalog/styles/default.ts).

**See some examples per-platform:**

* [Lit samples](https://github.com/a2ui-project/a2ui/blob/main/samples/client/lit)
* [Angular samples](https://github.com/a2ui-project/a2ui/blob/main/samples/client/angular)
* [React samples](https://github.com/a2ui-project/a2ui/blob/main/samples/client/react)

### Per-component overrides[¶](#per-component-overrides "Permanent link")

Beyond global theming, each component of the *basic catalog* exposes custom variables to further refine its appearance.
For example, the `Card` component exposes a `--a2ui-card-background` variable.

Check the documentation of each component to see what variables it exposes.

## Common Styling Features[¶](#common-styling-features "Permanent link")

### Dark Mode[¶](#dark-mode "Permanent link")

The default web renderers support automatic dark mode based on system preferences (`prefers-color-scheme`).

To always force dark or light mode (or to programmatically control switching), use the classnames `a2ui-light` or
`a2ui-dark` in an ancestor element of the generated code.

### Custom Fonts[¶](#custom-fonts "Permanent link")

Fonts can be loaded as in any other web application. The *basic catalog* components attempt to inherit the font family
of their container, but offer two overridable values: `--a2ui-font-family-title` and `--a2ui-font-family-monospace` to
set a different font for headings and monospace text blocks.

## Flutter[¶](#flutter "Permanent link")

Flutter has built-in theming support. See:

* [Use themes to share colors and font styles](https://docs.flutter.dev/cookbook/design/themes) from the Flutter docs.

## Best Practices[¶](#best-practices "Permanent link")

### 1. Use Semantic Hints, Not Visual Properties[¶](#1-use-semantic-hints-not-visual-properties "Permanent link")

When defining your components, agents should provide semantic hints (`usageHint`), never visual styles:

```
// ✅ Good: Semantic hint
{
  "component": {
    "Text": {
      "text": {"literalString": "Welcome"},
      "usageHint": "h1"
    }
  }
}

// ❌ Bad: Visual properties (not supported)
{
  "component": {
    "Text": {
      "text": {"literalString": "Welcome"},
      "fontSize": 24,
      "color": "#FF0000"
    }
  }
}
```

### 2. Maintain Accessibility[¶](#2-maintain-accessibility "Permanent link")

* Ensure sufficient color contrast (WCAG AA: 4.5:1 for normal text, 3:1 for large text)
* Test with screen readers
* Support keyboard navigation
* Test in both light and dark modes

### 3. Use Design Tokens[¶](#3-use-design-tokens "Permanent link")

Define reusable design tokens (colors, spacing, etc.) and reference them throughout your styles for consistency.

### 4. Test Across Platforms[¶](#4-test-across-platforms "Permanent link")

* Test your theming on all target platforms (web, mobile, desktop)
* Verify both light and dark modes
* Check different screen sizes and orientations
* Ensure consistent brand experience across platforms

## Next Steps[¶](#next-steps "Permanent link")

* **[Defining Your Own Catalog](../defining-your-own-catalog/)**: Build custom components with your styling
* **[Component Reference](../../reference/components/)**: See styling options for all components
* **[Client Setup](../client-setup/)**: Set up the renderer in your app