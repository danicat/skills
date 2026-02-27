Source: https://developers.google.com/style/headings\n\n# Headings and titles


      
      Stay organized with collections
    

      
      Save and categorize content based on your preferences.\n\n- Home\n- Products\n- Style\n\n\n## Page Summary\n\n- Use sentence case for all headings and titles to improve readability and navigation.\n- Structure content with descriptive headings that reflect the type of content (task-based or conceptual) using bare infinitives for tasks and noun phrases for concepts.\n- Organize content hierarchically with heading tags (h1, h2, h3, etc.) and ensure each page has a unique h1 heading; avoid skipping heading levels or using empty headings.\n- Avoid using "-ing" verbs, numbers, and excessive punctuation in headings; if an abbreviation is used, define it in the first paragraph following the heading.\n- When summarizing subheadings, use the phrase "in the following sections" to clearly connect the content.\n\nUse sentence case for all headings and titles to improve readability and navigation.\n\nStructure content with descriptive headings that reflect the type of content (task-based or conceptual) using bare infinitives for tasks and noun phrases for concepts.\n\nOrganize content hierarchically with heading tags (h1, h2, h3, etc.) and ensure each page has a unique h1 heading; avoid skipping heading levels or using empty headings.\n\nAvoid using "-ing" verbs, numbers, and excessive punctuation in headings; if an abbreviation is used, define it in the first paragraph following the heading.\n\nWhen summarizing subheadings, use the phrase "in the following sections" to clearly connect the content.\n\nUse sentence case for headings and titles. Use descriptive headings and titles because they help
  a reader navigate their browser and the page. It's easier to jump between pages and sections of a
  page if the headings and titles are unique.\n\n\n## Heading and title text\n\nWrite document titles based on the primary purpose of the document. If a
document is primarily a tutorial, but it has a conceptual introduction, write a
task-based title. Write section headings based on the type of content that's in
the section.\n\n\nGuidance | Recommended | Not recommended\nFor a task-based heading, start with a
    bare infinitive,
    also known as a plain form or
    base form
    verb. In English, the imperative mood also uses the base form verb,
    so it looks the same as the bare infinitive.
Task-based headings are frequently used in quickstarts, how-to
    documents, and tutorials. | Create an instance | Creating an instance\nFor a conceptual or non-task-based heading, use a
    noun phrase that
    doesn't start with an -ing verb.
Noun-phrase headings are frequently used in concept documentation. | Migration to Google Cloud | Migrating to Google Cloud\n\nFor a task-based heading, start with a
    bare infinitive,
    also known as a plain form or
    base form
    verb. In English, the imperative mood also uses the base form verb,
    so it looks the same as the bare infinitive.\n\nTask-based headings are frequently used in quickstarts, how-to
    documents, and tutorials.\n\nFor a conceptual or non-task-based heading, use a
    noun phrase that
    doesn't start with an -ing verb.\n\nNoun-phrase headings are frequently used in concept documentation.\n\nUse a unique level-1 heading (h1) for each page in a set of documents and only use
  a level-1 heading once on a page.\n\nIt's OK to use task-based and conceptual heading styles in the same document.
If a single document includes both task-based and conceptual sections, then use
the appropriate phrasing for each section's heading.\n\nWhen possible, avoid using -ing verb forms as the first word in any heading or
title.\n\nRecommended:
Transfer data sets\n\nNot recommended:
Transferring data sets\n\nAn -ing verb form is a present participle or gerund. These verb forms
are inconsistently translated when they're used as the first word in a title,
and they increase character count in limited spaces.\n\nSometimes, there might not be a better alternative to using a gerund, such as the following
  examples:\n\n- Billing\n- Pricing\n\nIt's OK to use a gerund in these cases.\n\nIt's OK to use an -ing verb form later in a heading or title, such as
Introduction to BigQuery monitoring.\n\nAvoid repeating the exact page title in a heading on the page if possible.
For example, if you're documenting how to create a virtual machine and how to start a virtual
machine on the same task-based page, the page title could be Create and start VM instances,
with section headings Create a VM and Start a VM.\n\n\n### Example headings\n\nThe following example is a task-based document that includes a conceptual
heading and a task-based heading.\n\nRecommended:\n\n\n### HTML\n\n```\n<h1>Log serving requests by using AI Platform Prediction</h1>

<p>This task-based document shows how to monitor machine learning models. The
document title starts with a bare infinitive.</p>

<h2>ML model monitoring overview</h2>

<p>This section provides a conceptual overview of ML model monitoring. Its title is
a noun phrase.</p>

<h2>Configure notebook settings<h2>

<p>This task-based section provides a series of steps to set variables in a
notebook. Its title starts with a bare infinitive.</p>\n```\n\n\n### Markdown\n\n```\n# Log serving requests by using AI Platform Prediction

This task-based document shows how to monitor machine learning models. The
document title starts with a bare infinitive.

## ML model monitoring overview

This section provides a conceptual overview of ML model monitoring. Its title is
a noun phrase.

## Configure notebook settings

This task-based section provides a series of steps to set variables in a
notebook. Its title starts with a bare infinitive.\n```\n\n\n## Heading and title format\n\n- Use sentence case for headings and titles. For more information, see
Capitalization in titles and
  headings.\n- Don't include numbers in headings to indicate a sequence of sections.\n- Use punctuation in headings sparingly, if at all. Punctuation can be a sign that your heading is
too complicated. Consider rewriting.\n- Only use an abbreviation of a word in a page title or heading if it's the more commonly known
  version of the word. If you do use an abbreviation in the page title or heading, the first
  instance of the word in a paragraph needs to be defined.
  You can define the abbreviation in the page title or heading, but consider if the additional
  length adds value.
  For SEO, use the more prominent version of the term in headings. For more information, see
Abbreviations.\n- In general, guidance that applies to text also applies to headings—for example,
  contractions and articles.\n- Avoid using code items in headings when possible. If you must mention a code item in a heading,
  add a descriptive noun to the item in code font. For more information, see
  Grammatical treatment of code elements.\n- Use heading tags to structure your content hierarchically—for example,
<h1>, <h2>, and <h3> in HTML, or
#, ##, and ### in Markdown.\n- Use API levels for Android
versions.\n- To change the visual formatting of a heading, use CSS rather than using a heading level that
doesn't fit the hierarchy. Don't make up your own formatting for headings.\n- Don't put a link in a heading because it can easily be confused as a style applied to a heading
  instead of a link.\n- Use a heading hierarchy and take the following items under consideration:

Ensure that each page in your project includes a unique level-1 heading. In some publishing systems, a
level-1 heading might be generated automatically based on a page title that you supply.
Don't skip levels of the heading hierarchy. For example, put an <h3> tag
only under an <h2> tag.

Recommended:


HTML

<h1>Transfer data sets</h1>

<p>This document provides a high-level overview of ways to transfer your data to Google
Cloud.</p>

<h2>Estimate costs</h2>



Markdown

# Transfer data sets

This document provides a high-level overview of ways to transfer your data to Google Cloud.

## Estimate costs



Not recommended:


HTML

<h1>Transfer data sets</h1>

<p>This document provides a high-level overview of ways to transfer your data to Google
Cloud.</p>

<h3>Estimate costs</h3>



Markdown

# Transfer data sets

This document provides a high-level overview of ways to transfer your data to Google Cloud.

### Estimate costs




Don't use empty headings or headings with no associated content.

Recommended:


HTML

<h2>Migrate VMs to Compute Engine</h2>

<p>Migration is not just a single step. The following sections describe the recommended
steps.</p>

<h3>Design the migration</h3>



Markdown

## Migrate VMs to Compute Engine

Migration is not just a single step. The following sections describe the recommended steps.

### Design the migration



Not recommended:


HTML

<h2>Migrate VMs to Compute Engine</h2>

<h3>Design the migration</h3>



Markdown

## Migrate VMs to Compute Engine

### Design the migration\n- Ensure that each page in your project includes a unique level-1 heading. In some publishing systems, a
level-1 heading might be generated automatically based on a page title that you supply.\n- Don't skip levels of the heading hierarchy. For example, put an <h3> tag
only under an <h2> tag.

Recommended:


HTML

<h1>Transfer data sets</h1>

<p>This document provides a high-level overview of ways to transfer your data to Google
Cloud.</p>

<h2>Estimate costs</h2>



Markdown

# Transfer data sets

This document provides a high-level overview of ways to transfer your data to Google Cloud.

## Estimate costs



Not recommended:


HTML

<h1>Transfer data sets</h1>

<p>This document provides a high-level overview of ways to transfer your data to Google
Cloud.</p>

<h3>Estimate costs</h3>



Markdown

# Transfer data sets

This document provides a high-level overview of ways to transfer your data to Google Cloud.

### Estimate costs\n- Don't use empty headings or headings with no associated content.

Recommended:


HTML

<h2>Migrate VMs to Compute Engine</h2>

<p>Migration is not just a single step. The following sections describe the recommended
steps.</p>

<h3>Design the migration</h3>



Markdown

## Migrate VMs to Compute Engine

Migration is not just a single step. The following sections describe the recommended steps.

### Design the migration



Not recommended:


HTML

<h2>Migrate VMs to Compute Engine</h2>

<h3>Design the migration</h3>



Markdown

## Migrate VMs to Compute Engine

### Design the migration\n\n- Ensure that each page in your project includes a unique level-1 heading. In some publishing systems, a
level-1 heading might be generated automatically based on a page title that you supply.\n- Don't skip levels of the heading hierarchy. For example, put an <h3> tag
only under an <h2> tag.

Recommended:


HTML

<h1>Transfer data sets</h1>

<p>This document provides a high-level overview of ways to transfer your data to Google
Cloud.</p>

<h2>Estimate costs</h2>



Markdown

# Transfer data sets

This document provides a high-level overview of ways to transfer your data to Google Cloud.

## Estimate costs



Not recommended:


HTML

<h1>Transfer data sets</h1>

<p>This document provides a high-level overview of ways to transfer your data to Google
Cloud.</p>

<h3>Estimate costs</h3>



Markdown

# Transfer data sets

This document provides a high-level overview of ways to transfer your data to Google Cloud.

### Estimate costs\n- Don't use empty headings or headings with no associated content.

Recommended:


HTML

<h2>Migrate VMs to Compute Engine</h2>

<p>Migration is not just a single step. The following sections describe the recommended
steps.</p>

<h3>Design the migration</h3>



Markdown

## Migrate VMs to Compute Engine

Migration is not just a single step. The following sections describe the recommended steps.

### Design the migration



Not recommended:


HTML

<h2>Migrate VMs to Compute Engine</h2>

<h3>Design the migration</h3>



Markdown

## Migrate VMs to Compute Engine

### Design the migration\n\nDon't skip levels of the heading hierarchy. For example, put an <h3> tag
only under an <h2> tag.\n\nRecommended:\n\n\n### HTML\n\n```\n<h1>Transfer data sets</h1>

<p>This document provides a high-level overview of ways to transfer your data to Google
Cloud.</p>

<h2>Estimate costs</h2>\n```\n\n\n### Markdown\n\n```\n# Transfer data sets

This document provides a high-level overview of ways to transfer your data to Google Cloud.

## Estimate costs\n```\n\nNot recommended:\n\n\n### HTML\n\n```\n<h1>Transfer data sets</h1>

<p>This document provides a high-level overview of ways to transfer your data to Google
Cloud.</p>

<h3>Estimate costs</h3>\n```\n\n\n### Markdown\n\n```\n# Transfer data sets

This document provides a high-level overview of ways to transfer your data to Google Cloud.

### Estimate costs\n```\n\nDon't use empty headings or headings with no associated content.\n\nRecommended:\n\n\n### HTML\n\n```\n<h2>Migrate VMs to Compute Engine</h2>

<p>Migration is not just a single step. The following sections describe the recommended
steps.</p>

<h3>Design the migration</h3>\n```\n\n\n### Markdown\n\n```\n## Migrate VMs to Compute Engine

Migration is not just a single step. The following sections describe the recommended steps.

### Design the migration\n```\n\nNot recommended:\n\n\n### HTML\n\n```\n<h2>Migrate VMs to Compute Engine</h2>

<h3>Design the migration</h3>\n```\n\n\n### Markdown\n\n```\n## Migrate VMs to Compute Engine

### Design the migration\n```\n\n\n## Refer to a group of sections\n\nIf you're introducing a group of related H3 or lower sections within a larger H2 section, use the
  phrase the following sections. Don't refer to the group of sections using the phrases
  this section or these sections because those phrases are ambiguous.\n\nRecommended:\n\n\n### HTML\n\n```\n<h2>Views in the data preparation editor</h2>

<p>The following sections describe the views in the data preparation editor.</p>

<h3>Data view</h3>

<p>...</p>

<h3>Graph view</h3>

<p>...</p>

<h3>Schema view</h3>

<p>...</p>\n```\n\n\n### Markdown\n\n```\n## Views in the data preparation editor

The following sections describe the views in the data preparation editor.

### Data view

...

### Graph view

...

### Schema view

...\n```\n