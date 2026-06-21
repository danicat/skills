# spec_v0.9.1_evolution
Source: https://a2ui.org/specification/v0.9.1-evolution-guide/

# Evolution Guide v0.9 → v0.9.1[¶](#evolution-guide-v09-v091 "Permanent link")

> This guide is automatically included from `specification/v0_9_1/docs/evolution_guide.md`. Any updates will automatically appear here.

For more information, see the following related documentation:

* [A2UI Protocol v0.9](../v0.9-a2ui/) (Previous Stable - what you're migrating from).
* [A2UI Protocol v0.9.1](../v0.9.1-a2ui/) (Current - what you're migrating to).

---

# A2UI Protocol Evolution Guide: v0.9 to v0.9.1[¶](#a2ui-protocol-evolution-guide-v09-to-v091 "Permanent link")

This document describes the changes between A2UI version 0.9 and version 0.9.1. For changes from version 0.8 to 0.9, please refer to the [v0.9 Evolution Guide](https://github.com/a2ui-project/a2ui/blob/main/v0_9/docs/evolution_guide.md).

## 1. Executive Summary[¶](#1-executive-summary "Permanent link")

Version 0.9.1 is a minor refinement of the v0.9 specification. The key changes are:

1. **MIME Type Standardization**: Standardized all references to the A2UI message payload MIME type to `application/a2ui+json` (replacing the legacy `application/json+a2ui`).
2. **Surface ID Uniqueness Relaxation**: Relaxed the requirement for `surfaceId` to be globally unique for the renderer's lifetime. It must still be unique among currently active surfaces, and it remains an error to call `createSurface` on an existing surface without first deleting it, but the explicit lifetime uniqueness constraint is removed.

## 2. Detailed Changes[¶](#2-detailed-changes "Permanent link")

### 2.1. MIME Type Standardization[¶](#21-mime-type-standardization "Permanent link")

In previous draft iterations of the v0.9 extension specification, the legacy `application/json+a2ui` MIME type was referenced. Version 0.9.1 standardizes all specification guides and extension metadata examples to use `application/a2ui+json`.

### 2.2. Surface ID Requirements[¶](#22-surface-id-requirements "Permanent link")

In `a2ui_protocol.md`, the definition and requirements for `surfaceId` were updated:

* The restriction that `surfaceId` "must be globally unique for the renderer's lifetime" is removed.
* Instead, the uniqueness constraint is limited to active surfaces: it remains an error to send `createSurface` for a `surfaceId` that already exists without first deleting it.

## 3. Migration Guide[¶](#3-migration-guide "Permanent link")

Since v0.9.1 is fully compatible with v0.9 payloads (the version fields in schemas accept both `"v0.9"` and `"v0.9.1"`), clients and servers can upgrade seamlessly.

* **Action for Implementers**: Update any hardcoded MIME type references from `application/json+a2ui` to `application/a2ui+json`.