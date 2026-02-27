Source: https://developers.google.com/style/fonts\n\n# HTML and semantic tagging


      
      Stay organized with collections
    

      
      Save and categorize content based on your preferences.\n\n- Home\n- Products\n- Style\n\n\n## Page Summary\n\n- Utilize HTML elements for their intended semantic purposes, such as using the cite element for titles of standalone works and referring to MDN's Semantics in HTML for further guidance.\n- When specific visual effects are desired and no semantically appropriate HTML elements exist, leverage CSS or HTML elements with inherent visual styling but without semantic implications.\n- Structure content with CSS for layout purposes, employ heading elements (like h1, h2) exclusively for hierarchical headings and use CSS for visual styling, and utilize semantic elements like em, strong, i, b, and br according to their intended meanings, using CSS for spacing adjustments.\n\nUtilize HTML elements for their intended semantic purposes, such as using the cite element for titles of standalone works and referring to MDN's Semantics in HTML for further guidance.\n\nWhen specific visual effects are desired and no semantically appropriate HTML elements exist, leverage CSS or HTML elements with inherent visual styling but without semantic implications.\n\nStructure content with CSS for layout purposes, employ heading elements (like h1, h2) exclusively for hierarchical headings and use CSS for visual styling, and utilize semantic elements like em, strong, i, b, and br according to their intended meanings, using CSS for spacing adjustments.\n\nUse HTML elements for the purposes that they were designed for. For example, when
you give the title of a standalone work (such as a book or a movie), mark it
with a cite
element. For more information about semantic tagging, see Semantics in HTML
on the MDN web documents site.\n\nIn situations where there are no semantically relevant HTML elements, use CSS
or the few HTML elements that convey visual style without semantics.\n\n\n## Visual formatting\n\nIf you want to achieve specific visual results, don't use HTML elements that
convey different semantics.\n\nIn particular, follow these guidelines:\n\n- Don't use frames or tables for layout; instead, use your site's CSS to lay out the page.\n- Don't use the heading elements (such as h1 and
h2) to visually style text; instead, use those elements
only for hierarchically structured headings, and use CSS for visual style.\n- The em
element indicates emphasis, not italics as such. Don't use it to italicize
something that isn't meant to be emphasized; instead, use the i
element for non-emphasis italics.\n- The strong
element indicates strong importance, not bold as such. To bold a word that
doesn't merit strong importance, use the b
element.\n- The br
element is intended "only for line breaks that are actually part of the content,
as in poems or addresses." Don't use it to adjust the spacing between lines.
Instead, use elements like p to semantically mark the
text, and use CSS to adjust line spacing.\n\nThe em
element indicates emphasis, not italics as such. Don't use it to italicize
something that isn't meant to be emphasized; instead, use the i
element for non-emphasis italics.\n\n\n