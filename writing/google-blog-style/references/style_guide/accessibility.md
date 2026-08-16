Source: https://developers.google.com/style/accessibility\n\n# Write accessible documentation


      
      Stay organized with collections
    

      
      Save and categorize content based on your preferences.\n\n- Home\n- Products\n- Style\n\n\n## Page Summary\n\n- This guide provides best practices for writing accessible developer documentation, benefiting all readers, including those with disabilities.\n- Key areas covered include language, formatting, headings, links, lists, images, videos, tables, and interactive elements with a focus on clear, concise, and navigable content.\n- Specific recommendations are provided for using semantic HTML, keyboard navigation, screen reader compatibility, and alternative text for multimedia to enhance the user experience.\n- The guidelines aim to ensure inclusivity by prioritizing descriptive content, avoiding visual-only cues, and accommodating diverse user needs and preferences.\n- Resources from Google, WCAG, and WAI are linked for further information on web accessibility standards and best practices.\n\nThis guide provides best practices for writing accessible developer documentation, benefiting all readers, including those with disabilities.\n\nKey areas covered include language, formatting, headings, links, lists, images, videos, tables, and interactive elements with a focus on clear, concise, and navigable content.\n\nSpecific recommendations are provided for using semantic HTML, keyboard navigation, screen reader compatibility, and alternative text for multimedia to enhance the user experience.\n\nThe guidelines aim to ensure inclusivity by prioritizing descriptive content, avoiding visual-only cues, and accommodating diverse user needs and preferences.\n\nResources from Google, WCAG, and WAI are linked for further information on web accessibility standards and best practices.\n\nWe write our developer documentation with accessibility in mind. This page is not an exhaustive
  reference, but describes some general guidelines and examples that illustrate best practices to
  follow. The
  World Health Organization
  estimates that 15% of the world's population (more than 1 billion people) have an accessibility
  need. When documentation is written with accessibility in mind, it improves the overall
  experience for all readers.\n\nFor other writing best practices, see the following resources:\n\n- Write for a global audience\n- Write inclusive documentation\n- Voice and tone\n\n\n## General dos and don'ts\n\n- Don't use ableist language. Avoid bias and harm when discussing disability and accessibility.
    For more information, see
    Writing inclusive documentation.\n- Ensure that readers can reach all parts of the document (including
tabs, form-submission buttons, and interactive elements) by using only a keyboard,
without a mouse or trackpad.\n- Use a screen reader to test your documentation. This test can help you find accessibility
    issues in your content and is a good way to self-edit your content. To try out a screen reader,
  see List of screen readers.\n- In HTML, use semantic
tagging. For example, use the em element only to
indicate emphasis, not to indicate italics.\n- In HTML, prefer
    native
elements over custom styles.\n- Avoid unnecessary font formatting. (Screen readers explicitly describe
text modifications.)\n- If you're documenting a product that includes specialized accessibility
features, then explicitly document those features. For example, the Google Cloud
CLI (gcloud CLI) includes togglable accessibility features
such as percentage progress bars and ASCII box rendering.\n- Don't force line breaks (hard returns) within sentences and paragraphs. Line breaks might not
    work well in resized windows or with enlarged text.\n- Avoid when possible camel case and
    all caps. Some screen readers read
    capitalized letters individually, and some languages are
    unicase. Follow
    capitalization guidelines.\n- Depending on the screen reader (or personal settings), not all punctuation marks are read. Make
  sure that the same meaning is conveyed to the reader without punctuation marks. For that reason, avoid
   when possible the use of exclamation marks, question marks, and semicolons.\n- Don't use & instead of and in headings, text, navigation, or
tables of contents. However, it's OK to use & when referencing UI
elements that use &, or in table headings and diagram labels where space
constraints require abbreviation. Of course, it's fine to use &
for technical purposes in code.\n\n\n## Ease of reading\n\n- Break up walls of text to aid in scannability. For example, separate
      paragraphs,
      create
      headings,
      and use
      lists.\n- Use shorter sentences. Try to use fewer than 26 words per sentence.\n- Define acronyms and abbreviations on first usage and if they're used infrequently.\n- Use parallel writing structures for similar things. For example, start each list in the same
      format.\n- Place distinguishing and important information of a paragraph in the first sentence to aid in
      scannability.\n- Use clear and direct language. Avoid the use of double negatives and exceptions for exceptions.
Recommended: You can continue without a
        path.
Not recommended: A missing path won't
        prevent you from continuing.\n- Left-align text for readability. Don't center or full-justify text.\n\nUse clear and direct language. Avoid the use of double negatives and exceptions for exceptions.\n\nRecommended: You can continue without a
        path.\n\nNot recommended: A missing path won't
        prevent you from continuing.\n\n\n## Headings and titles\n\nUse descriptive headings and titles because they help a reader navigate their browser and the
   page. It's easier to jump between pages and sections of a page if the headings and titles are
   unique.\n\n- Use a heading hierarchy.\n- Don't skip levels of the heading hierarchy. For example, put an h3 element
      only after an h2 element.\n- To change the visual formatting of a heading, use CSS rather than using a heading level that
     doesn't fit the hierarchy.\n- Don't have empty headings or headings with no associated content.\n- Tag headings using heading elements. In HTML: h1,
      h2, and so on. In Markdown: #, ##, and so on.\n- Use a level-1 heading for the page title or main content heading.\n\nFor more information and examples, see Headings and titles.\n\n\n## Links\n\n- Use meaningful link text.
    Links should make sense when read out of context.\n- Don't use click here or read this document. Some people who use screen readers
    jump from link to link to scan a page and need to understand what a link contains.\n- Use see to refer to links and cross-references. For more information, see
  see.\n- When a link does anything that the reader might not expect, such as downloading a file,
    opening in a new tab, or jumping to another section on the same page, explain that behavior when
    you link. For more information, see
    Explain unexpected link behavior.\n- When possible, avoid adjacent links. Instead, put a character in between to separate them.\n\n\n## Lists\n\n- In a
      procedure,
      make each instruction a
      list item.\n- Use lists to make it easier for the reader to follow the steps.\n\n\n## Images\n\n- For every image, provide an alt attribute. For alt attributes that contain
    alt text, use alt text that adequately summarizes the
    intent of each image. If the image is purely decorative, use empty alt text.\n- Don't present new information in images. Always provide an equivalent text explanation with
    the image.\n- Don't repeat images unless absolutely necessary.\n- Don't use images of text, code samples, or terminal output. Use actual text.\n- Use SVG instead of PNG if available. SVGs stay sharp when you zoom in on the image.\n\nFor more information, see
  Text associated with images.\n\n\n## Videos, recordings, and GIFs\n\n- Provide captions, transcripts, or descriptions of audio and video content. For example, you
      can use the
      autocaption feature
      in YouTube.\n- Ensure that captions can be translated into major languages.\n- Don't use flickering or flashing elements. They can cause anything from motion sickness
      to a seizure.\n\n\n## Buttons and icons\n\n- For form-submission buttons, use the native HTML button element.\n- An icon is a symbol or image that represents an object or a function. For information
    about using icons, see the Buttons and icons section
    of the "UI elements and interaction" page.\n\n\n## UI navigation\n\nWhen you use angle brackets (>) to document menu paths, add an
aria-label attribute
to help screen readers interpret the brackets as "and then" instead of as
"greater than" or "keyboard arrow right". For more information and examples, see
Menu bar.\n\n\n## Tables\n\n- Introduce tables in the text preceding the table because not all screen readers preannounce
    tables.\n- Use table headings for the first column and the first row only. Use the
    th element.\n- If your tables include both row and column headings, then mark heading cells with the
    scope
    attribute.\n- If your tables have more than one row containing column headings, then use the
    headers
    attribute and make sure that the headings have unique IDs.\n- Avoid when possible tables in the middle of a numbered procedure.\n- Don't merge cells. Don't use colspan or rowspan attributes.\n- Don't use tables unless it's the best method to present your information. Tables are
    challenging for screen readers. For more information, see
    List or table.\n- Don't present new information in tables through images or symbols alone; always provide a
descriptive alt attribute for the image or symbol. For more information, see
Alt text.\n\nFor more information, see Tables.\n\n\n## Interactive elements\n\nIntroduce an interactive element (such as a button that expands and collapses) in the text
preceding the element.\n\nRecommended if practical: To see a list of
  requirements, expand the Requirements section.\n\nRecommended: To see a list of requirements,
  click the arrow_right expander arrow.\n\n\n## Forms\n\n- Label every input field by using a label element.\n- Place labels outside of fields.\n- When you're creating an error message for form validation, clearly state
what went wrong and how to fix it—for example: "Name is a required field."\n\n\n## Custom CSS and JavaScript\n\nTry to use your site's standard styles and standard JavaScript code as much
as possible. However, if you do use custom styles or code, then follow these guidelines:\n\n- Pick colors that respect
    accessible color contrast
ratios (4.5:1 for text).\n- Don't use visibility:hidden or display:none. Both
styles hide information from screen readers.\n- Avoid when possible using mouseover events. But if you do use them, then add alternate
focus and blur events for keyboard users.\n- Ensure that any ordering and positioning defined in styles reflects the
DOM and the reading order (such as left to right and top to bottom) of your page.\n\n\n## Document rendering\n\nMake sure that your document conveys all the information that you intended when you
view it in the following contexts:\n\n- Without sound\n- Using only sound\n- Without images, including animation\n- Without color\n- Using a keyboard\n- With screen magnification\n- Without punctuation\n\nDon't use color, size, location, or other visual cues as the primary way
  of communicating information.\n\n- If you're using color, an icon, or outline thickness to convey state,
then also provide a secondary cue, such as a change in the text label.\n- Refer to buttons and other elements by their label. For visual elements
       that have no text, don't try to describe the element. Instead, use the element's
       aria-label
       attribute if possible.
       For example:
Recommended: Click Save.
Recommended: Click Notifications.
Not recommended: Click the bell icon.\n- Don't use directional language to orient the reader, such as above, below,
      or right-hand side. This type of language doesn't work well for accessibility or for
      localization reasons. For example, what's on the right side for left-to-right languages
      appears on the left side for right-to-left languages.
Don't use directional language to refer to a position in a document. For example, the text
      isn't below if it's being read by a screen reader. Instead, use earlier,
  preceding, or following.
Recommended:
In the preceding diagram, clients run jobs on multi-team or single-team clusters.
Not recommended: In the diagram above,
clients run jobs on multi-team or single-team clusters.
If a UI element is hard to find,
provide a screenshot.
Recommended:
Click menu Menu.
Not recommended: In the left-side
panel, click the button with three lines.\n\nRefer to buttons and other elements by their label. For visual elements
       that have no text, don't try to describe the element. Instead, use the element's
       aria-label
       attribute if possible.
       For example:\n\nRecommended: Click Save.\n\nRecommended: Click Notifications.\n\nNot recommended: Click the bell icon.\n\nDon't use directional language to orient the reader, such as above, below,
      or right-hand side. This type of language doesn't work well for accessibility or for
      localization reasons. For example, what's on the right side for left-to-right languages
      appears on the left side for right-to-left languages.\n\nDon't use directional language to refer to a position in a document. For example, the text
      isn't below if it's being read by a screen reader. Instead, use earlier,
  preceding, or following.\n\nRecommended:
In the preceding diagram, clients run jobs on multi-team or single-team clusters.\n\nNot recommended: In the diagram above,
clients run jobs on multi-team or single-team clusters.\n\nIf a UI element is hard to find,
provide a screenshot.\n\nRecommended:
Click menu Menu.\n\nNot recommended: In the left-side
panel, click the button with three lines.\n\n\n## More resources\n\n- Google's main
    accessibility page\n- Web Content Accessibility
    Guidelines (WCAG) 2.0\n- Web Accessibility Initiative
    (WAI)\n- Using ARIA\n- Web Accessibility
    Tutorials\n