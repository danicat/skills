Source: https://developers.google.com/style/tables\n\n# Tables


      
      Stay organized with collections
    

      
      Save and categorize content based on your preferences.\n\n- Home\n- Products\n- Style\n\n\n## Page Summary\n\n- Tables are ideal for presenting data with three or more related pieces of information per item, while lists are better for simpler data structures.\n- When using tables, introduce them with a complete sentence, use clear and concise column headings, and avoid unnecessary styling or formatting.\n- Ensure table accessibility by using proper HTML elements like caption, th, and scope, and provide descriptive alternative text for any images or symbols.\n- For single-unit items, use bulleted, lettered, or numbered lists; for paired data, consider description lists or tables depending on the context.\n- Avoid using tables for page layout, code snippets, long one-dimensional lists, or within numbered procedures, and ensure responsiveness for various viewport sizes.\n\nTables are ideal for presenting data with three or more related pieces of information per item, while lists are better for simpler data structures.\n\nWhen using tables, introduce them with a complete sentence, use clear and concise column headings, and avoid unnecessary styling or formatting.\n\nEnsure table accessibility by using proper HTML elements like caption, th, and scope, and provide descriptive alternative text for any images or symbols.\n\nFor single-unit items, use bulleted, lettered, or numbered lists; for paired data, consider description lists or tables depending on the context.\n\nAvoid using tables for page layout, code snippets, long one-dimensional lists, or within numbered procedures, and ensure responsiveness for various viewport sizes.\n\nIn many contexts, tables are the best way to represent sets of related pieces of data. However,
in some contexts, other approaches are better choices.\n\n\n## List or table?\n\nTables and lists are both ways to present a set of similarly structured
items; sometimes it's not obvious when to choose one presentation over the
other. To decide which presentation to use, consult the following table:\n\n\nItem type | Example | How to present\nEach item is a single unit. | A list of programming language names, or a list of steps to follow. | Use a numbered list, lettered list, or bulleted
list.\nEach item is a pair of pieces of related data. | A list of term/definition pairs. | Use a description list (or, in some
contexts, a table).\nEach item is three or more pieces of related data. | A set of parameters, where each parameter has a name, a data type, and a
description. | Use a table.\n\n\n### Places not to use tables\n\n- Don't use tables to lay out a page; use your site's standard CSS instead.\n- Usually if you have only one row of material, a table isn't the best
choice for how to present it. But in some contexts (especially for consistency
of layout in reference documentation), it might be.\n- If you have only one column in your table, turn the table into a list.\n- Don't use tables to lay out code snippets.\n- Don't use tables to lay out long one-dimensional lists in multiple
columns. For example, if you have a long list of function names, don't try to
save space by splitting the list in half and presenting the two halves as a
two-column table. Use tables only to present two-dimensional data—that is,
material that semantically makes sense to display in rows and columns.\n- Avoid tables in the middle of a numbered procedure.\n\n\n## Multi-paragraph table cells\n\nAny table cell can contain more than one paragraph.\n\nTo create multiple paragraphs, use the p element rather
than using the br element. (The HTML specification
describes which uses of the br
element are legitimate and which aren't.)\n\nExample of a table with some cells that contain more than one paragraph:\n\n\nAttribute name | Type | Description\nhref | HTML | Defines the URL for a link.
For example, go to the
        <a href="https://www.google.com">Google Search</a> page.\nsrc | HTML | Defines the path of the image to be displayed.
For example, <img src="kitten.jpg">.\n\nDefines the URL for a link.\n\nFor example, go to the
        <a href="https://www.google.com">Google Search</a> page.\n\nDefines the path of the image to be displayed.\n\nFor example, <img src="kitten.jpg">.\n\n\n## Introductory sentences for tables\n\nIntroduce tables with a complete sentence that describes the purpose of the table because not all
screen readers preannounce tables. The introductory sentence can end with a colon or a period;
usually a colon if it immediately precedes the table, and usually a period if there's more material
(such as a note paragraph) between the introduction and the table.\n\nRecommended: Change the environment variables
  to values for your deployment, as listed in the following table:\n\nFor more information, see the
  Tables section of the "Accessibility" page.\n\n\n## Table placement\n\n- When introducing a table, use a complete sentence and try to refer to the
table's position, using a phrase like the following table or the preceding table.\n- Don't put a table in the middle of a sentence.\n- Avoid using footnotes when possible. If your table does refer to footnotes, place them
    immediately following the table. For more information, see
    Footnotes.\n\n\n## Table captions\n\nIf your document contains only one table, the table doesn't need a caption.
However, be sure to place the table adjacent to the text that refers to it.\n\nIf your document contains more than one table in fairly close proximity to
each other, include a caption for each one, using a caption
element as the first child of the table element. Start the
caption with a number, in the form "<b>Table NUMBER.</b>
DESCRIPTION". Use sentence case for the caption, but don't place a
period at the end.\n\nWhen referring to the table from text, refer to it by its number—for example,
  ... as shown in table 2. Do not capitalize table unless it starts a sentence.\n\nYour site's CSS determines the styling and placement of the caption.\n\nRecommended:\n\n```\n<table>
  <caption><b>Table 1.</b> Prehistoric birds</caption>
  ...
</table>\n```\n\n\n## Table formatting\n\n- Don't add styling to the table element.\n- Don't apply a visual style such as a different font, font color, or background color to convey a
  header row or column by itself. Use the th element to semantically mark up headers in
  tables.\n- Don't merge cells. Don't use colspan or rowspan attributes.\n- Sort rows in a logical order, or alphabetically if there is no logical order.\n- If the table is long or complicated—for example, with multiple header rows or columns—consider
splitting it into multiple tables.\n- Don't present new information in tables through images or symbols alone; always provide a
descriptive alt attribute for the image or symbol. For more information, see
Alt text.\n\n\n## Table column heads\n\n- Use sentence case.\n- Write concise headings.\n- Don't end with punctuation, including a period, an ellipsis, or a colon.\n- Use table headings for the first column and the first row only. Use the
    th element.\n- Include the 
scope attribute as appropriate for accessibility.\n\n\n## Responsive tables\n\nWhere possible, use table CSS that adapts to different viewport sizes.\n\n\n## Link to tables\n\nWhere possible, avoid linking to tables; instead, refer to them by table number.\n