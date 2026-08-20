# ref_components
Source: https://a2ui.org/reference/components/

# Component Gallery

This page showcases all A2UI components with examples and usage patterns.

> NOTE: Schema Files
>
> v0.8v0.9
>
> [Standard Catalog Definition (JSON Schema)](https://github.com/a2ui-project/a2ui/blob/main/specification/v0_8/json/standard_catalog_definition.json)
>
> [Basic Catalog Definition (JSON Schema)](https://github.com/a2ui-project/a2ui/blob/main/specification/v0_9/catalogs/basic/catalog.json)

---

## Layout Components

### Row

Horizontal layout container. Children are arranged left-to-right.

v0.8v0.9

**Properties:** `children` (`explicitList` or `template`), `distribution`, `alignment`

```
{
  "id": "toolbar",
  "component": {
    "Row": {
      "children": { "explicitList": ["btn1", "btn2", "btn3"] },
      "distribution": "spaceBetween",
      "alignment": "center"
    }
  }
}
```

**Properties:** `children` (array or template), `justify`, `align`

```
{
  "id": "toolbar",
  "component": "Row",
  "children": ["btn1", "btn2", "btn3"],
  "justify": "spaceBetween",
  "align": "center"
}
```

### Column

Vertical layout container. Children are arranged top-to-bottom.

v0.8v0.9

**Properties:** `children` (`explicitList` or `template`), `distribution`, `alignment`

```
{
  "id": "content",
  "component": {
    "Column": {
      "children": { "explicitList": ["header", "body", "footer"] },
      "distribution": "start",
      "alignment": "stretch"
    }
  }
}
```

**Properties:** `children` (array or template), `justify`, `align`

```
{
  "id": "content",
  "component": "Column",
  "children": ["header", "body", "footer"],
  "justify": "start",
  "align": "stretch"
}
```

### List

Scrollable list of items. Supports static children and dynamic templates.

v0.8v0.9

**Properties:** `children` (`explicitList` or `template`), `direction`, `alignment`

```
{
  "id": "message-list",
  "component": {
    "List": {
      "children": {
        "template": {
          "dataBinding": "/messages",
          "componentId": "message-item"
        }
      },
      "direction": "vertical"
    }
  }
}
```

**Properties:** `children` (array or template), `direction`, `align`

```
{
  "id": "message-list",
  "component": "List",
  "children": {
    "componentId": "message-item",
    "path": "/messages"
  },
  "direction": "vertical"
}
```

---

## Display Components

### Text

Display text content with styling hints.

v0.8v0.9

**Properties:** `text` (BoundValue), `usageHint`

`usageHint` values: `h1`, `h2`, `h3`, `h4`, `h5`, `caption`, `body`

```
{
  "id": "title",
  "component": {
    "Text": {
      "text": { "literalString": "Welcome to A2UI" },
      "usageHint": "h1"
    }
  }
}
```

**Properties:** `text` (string or DataBinding), `variant`

`variant` values: `h1`, `h2`, `h3`, `h4`, `h5`, `caption`, `body`

```
{
  "id": "title",
  "component": "Text",
  "text": "Welcome to A2UI",
  "variant": "h1"
}
```

### Image

Display images from URLs.

v0.8v0.9

**Properties:** `url` (BoundValue), `fit`, `usageHint`

```
{
  "id": "hero",
  "component": {
    "Image": {
      "url": { "literalString": "https://example.com/hero.png" },
      "fit": "cover",
      "usageHint": "hero"
    }
  }
}
```

**Properties:** `url` (string or DataBinding), `fit`, `variant`

```
{
  "id": "hero",
  "component": "Image",
  "url": "https://example.com/hero.png",
  "fit": "cover",
  "variant": "hero"
}
```

### Icon

Display icons from the basic set defined in the catalog.

v0.8v0.9

**Properties:** `name` (BoundValue)

```
{
  "id": "check-icon",
  "component": {
    "Icon": {
      "name": { "literalString": "check" }
    }
  }
}
```

**Properties:** `name` (string or DataBinding)

```
{
  "id": "check-icon",
  "component": "Icon",
  "name": "check"
}
```

### Divider

Visual separator line.

v0.8v0.9

**Properties:** `axis`

```
{
  "id": "separator",
  "component": {
    "Divider": {
      "axis": "horizontal"
    }
  }
}
```

**Properties:** `axis`

```
{
  "id": "separator",
  "component": "Divider",
  "axis": "horizontal"
}
```

---

## Interactive Components

### Button

Clickable button that triggers an action.

v0.8v0.9

**Properties:** `child` (component ID), `primary` (boolean), `action`

```
{
  "id": "submit-btn",
  "component": {
    "Button": {
      "child": "submit-text",
      "primary": true,
      "action": {
        "name": "submit_form"
      }
    }
  }
}
```

**Properties:** `child` (component ID), `variant`, `action`

```
{
  "id": "submit-btn",
  "component": "Button",
  "child": "submit-text",
  "variant": "primary",
  "action": {
    "event": {
      "name": "submit_form"
    }
  }
}
```

### TextField

Text input field with optional validation.

v0.8v0.9

**Properties:** `label` (BoundValue), `text` (BoundValue), `textFieldType`, `validationRegexp`

`textFieldType` values: `shortText`, `longText`, `number`, `obscured`, `date`

```
{
  "id": "email-input",
  "component": {
    "TextField": {
      "label": { "literalString": "Email Address" },
      "text": { "path": "/user/email" },
      "textFieldType": "shortText"
    }
  }
}
```

**Properties:** `label` (string), `value` (string or DataBinding), `textFieldType`, `validationRegexp`

`textFieldType` values: `shortText`, `longText`, `number`, `obscured`, `date`

```
{
  "id": "email-input",
  "component": "TextField",
  "label": "Email Address",
  "value": { "path": "/user/email" },
  "textFieldType": "shortText"
}
```

### CheckBox

Boolean toggle.

v0.8v0.9

**Properties:** `label` (BoundValue), `value` (BoundValue, boolean)

```
{
  "id": "terms-checkbox",
  "component": {
    "CheckBox": {
      "label": { "literalString": "I agree to the terms" },
      "value": { "path": "/form/agreedToTerms" }
    }
  }
}
```

**Properties:** `label` (string), `value` (DataBinding, boolean)

```
{
  "id": "terms-checkbox",
  "component": "CheckBox",
  "label": "I agree to the terms",
  "value": { "path": "/form/agreedToTerms" }
}
```

### Slider

Numeric range input.

v0.8v0.9

**Properties:** `value` (BoundValue), `minValue`, `maxValue`

```
{
  "id": "volume",
  "component": {
    "Slider": {
      "value": { "path": "/settings/volume" },
      "minValue": 0,
      "maxValue": 100
    }
  }
}
```

**Properties:** `value` (DataBinding), `minValue`, `maxValue`

```
{
  "id": "volume",
  "component": "Slider",
  "value": { "path": "/settings/volume" },
  "minValue": 0,
  "maxValue": 100
}
```

### DateTimeInput

Date and/or time picker.

v0.8v0.9

**Properties:** `value` (BoundValue), `enableDate`, `enableTime`

```
{
  "id": "date-picker",
  "component": {
    "DateTimeInput": {
      "value": { "path": "/booking/date" },
      "enableDate": true,
      "enableTime": false
    }
  }
}
```

**Properties:** `value` (DataBinding), `enableDate`, `enableTime`

```
{
  "id": "date-picker",
  "component": "DateTimeInput",
  "value": { "path": "/booking/date" },
  "enableDate": true,
  "enableTime": false
}
```

### MultipleChoice (v0.8) / ChoicePicker (v0.9)

Select one or more options from a list.

v0.8v0.9

**Properties:** `options` (array), `selections` (BoundValue), `maxAllowedSelections`

```
{
  "id": "country-select",
  "component": {
    "MultipleChoice": {
      "options": [
        { "label": { "literalString": "USA" }, "value": "us" },
        { "label": { "literalString": "Canada" }, "value": "ca" }
      ],
      "selections": { "path": "/form/country" },
      "maxAllowedSelections": 1
    }
  }
}
```

**Properties:** `options` (array), `selections` (DataBinding), `maxAllowedSelections`

```
{
  "id": "country-select",
  "component": "ChoicePicker",
  "options": [
    { "label": "USA", "value": "us" },
    { "label": "Canada", "value": "ca" }
  ],
  "selections": { "path": "/form/country" },
  "maxAllowedSelections": 1
}
```

---

## Container Components

### Card

Container with elevation/border and padding.

v0.8v0.9

**Properties:** `child` (component ID)

```
{
  "id": "info-card",
  "component": {
    "Card": {
      "child": "card-content"
    }
  }
}
```

**Properties:** `child` (component ID)

```
{
  "id": "info-card",
  "component": "Card",
  "child": "card-content"
}
```

### Modal

Overlay dialog triggered by an entry point component.

v0.8v0.9

**Properties:** `entryPointChild` (component ID), `contentChild` (component ID)

```
{
  "id": "confirmation-modal",
  "component": {
    "Modal": {
      "entryPointChild": "open-modal-btn",
      "contentChild": "modal-content"
    }
  }
}
```

**Properties:** `entryPointChild` (component ID), `contentChild` (component ID)

```
{
  "id": "confirmation-modal",
  "component": "Modal",
  "entryPointChild": "open-modal-btn",
  "contentChild": "modal-content"
}
```

### Tabs

Tabbed interface for organizing content into switchable panels.

v0.8v0.9

**Properties:** `tabItems` (array of `{ title, child }`)

```
{
  "id": "settings-tabs",
  "component": {
    "Tabs": {
      "tabItems": [
        { "title": { "literalString": "General" }, "child": "general-tab" },
        { "title": { "literalString": "Privacy" }, "child": "privacy-tab" }
      ]
    }
  }
}
```

**Properties:** `tabItems` (array of `{ title, child }`)

```
{
  "id": "settings-tabs",
  "component": "Tabs",
  "tabItems": [
    { "title": "General", "child": "general-tab" },
    { "title": "Privacy", "child": "privacy-tab" }
  ]
}
```

---

## Common Properties

All components share:

* `id` (required): Unique identifier within the surface.
* `accessibility`: Accessibility attributes (label, role).
* `weight`: Flex-grow value when inside a Row or Column.

## Version Differences Summary

The component names and properties are largely the same across versions. The structural differences are:

| Aspect | v0.8 | v0.9 |
| --- | --- | --- |
| Component wrapper | `"component": { "Text": { ... } }` | `"component": "Text", ...props` |
| String values | `{ "literalString": "Hello" }` | `"Hello"` |
| Children | `{ "explicitList": ["a", "b"] }` | `["a", "b"]` |
| Data binding | `{ "path": "/data" }` | `{ "path": "/data" }` (same) |
| Text/Image styling | `usageHint` | `variant` |
| Button styling | `primary: true` | `variant: "primary"` |
| Action format | `{ "name": "..." }` | `{ "event": { "name": "..." } }` |
| Choice component | `MultipleChoice` | `ChoicePicker` |
| Layout alignment | `distribution`, `alignment` | `justify`, `align` |
| TextField value | `text` | `value` |

## Live Examples

To see all components in action:

```
cd samples/client/angular
yarn start gallery
```

**Package Manager Usage:** Running the built-in sample applications within the A2UI repository requires Yarn (`yarn start gallery`) as configured by Corepack workspaces. For your own regular usage and standalone projects outside this repository, use the package manager of your choice (e.g. npm, pnpm).

## Further Reading

> NOTE: Schema Files
>
> v0.8v0.9
>
> [Standard Catalog Definition (JSON Schema)](https://github.com/a2ui-project/a2ui/blob/main/specification/v0_8/json/standard_catalog_definition.json)
>
> [Basic Catalog Definition (JSON Schema)](https://github.com/a2ui-project/a2ui/blob/main/specification/v0_9/catalogs/basic/catalog.json)

* **[Defining Your Own Catalog](./guide_defining_own_catalog.md)**: Build your own components
* **[Theming Guide](./guide_theming.md)**: Style components to match your brand
