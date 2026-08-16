Source: https://developers.google.com/style/cross-references\n\n# Cross-references and linking


      
      Stay organized with collections
    

      
      Save and categorize content based on your preferences.\n\n- Home\n- Products\n- Style\n\n\n## Page Summary\n\n- Prioritize providing context and help within the document itself instead of relying heavily on external links for supplementary information.\n- When linking to other documents or sections, use clear and descriptive link text that accurately reflects the content being linked.\n- Ensure links open in the same window unless absolutely necessary, and in such cases, explicitly inform the reader that the link will open in a new tab.\n- Maintain consistency by using site-root-relative URLs for internal links and avoid unnecessary link repetition.\n- When linking externally, use HTTPS if supported and clearly indicate when a link leads to a different domain or server within the link text if deemed important.\n\nPrioritize providing context and help within the document itself instead of relying heavily on external links for supplementary information.\n\nWhen linking to other documents or sections, use clear and descriptive link text that accurately reflects the content being linked.\n\nEnsure links open in the same window unless absolutely necessary, and in such cases, explicitly inform the reader that the link will open in a new tab.\n\nMaintain consistency by using site-root-relative URLs for internal links and avoid unnecessary link repetition.\n\nWhen linking externally, use HTTPS if supported and clearly indicate when a link leads to a different domain or server within the link text if deemed important.\n\nIn general, cross-references link to nonessential information that adds to
the reader's understanding.\n\nWhen used well, cross-references help readers navigate and understand
documentation. But cross-references can easily become disruptive. The guidelines
on this page help you to minimize disruption while providing cross-references
that help your readers.\n\n\n## Choose links selectively\n\nBe selective about which links you include on a page. Each link creates a
  decision for the reader, adding cognitive load. Each link is also a chance for
  the reader to leave the page and lose their place. When you include links,
  choose the most relevant destination.\n\n\n### Provide context on the page\n\nWhen possible, provide help in context rather than linking elsewhere. For
  example, in the following situations, consider providing information on the
  page instead of linking:\n\n- Define a term.\n- Briefly explain a concept.\n- Provide a couple of steps.\n\nAs a specific example, if you need readers to understand another product's
  software or standards, it's better to link to good documentation elsewhere
  than to try to thoroughly document another product's standards in our
  documentation. But if a few sentences of basic information is all your readers
  need, then it's better to provide that context and save your readers the trip
  outside of our documentation.\n\n\n### Avoid duplicate links\n\nGenerally, within a given page, don't provide duplicate links to the same
  destination. Provide the link once in the location where it's most useful to
  the reader.\n\nIt's OK to add a secondary link in situations such as the following:\n\n- You're linking to a particular section of another page.\n- Your page is very long and the duplicate links are far apart.\n- There are multiple entry points to the document that you're linking from.
        For example, if a page contains a procedure section and a troubleshooting
        section, then you might need to provide the same link in both of those
        sections.\n\n\n### Provide the most relevant link\n\nWhen you link, link to the most relevant page on a site. Link to the most
  relevant heading on a page. Avoid providing multiple links that do the same
  job.\n\n\n### Link to third-party sites\n\nOur documentation often relies on the reader knowing something about
  third-party standards or software. In such cases, it's better to provide a
  link rather than attempt to thoroughly document someone else's standards. But
  as with all links, when possible, provide brief information on the page
  instead of linking.\n\n\n## Write descriptive link text\n\nFor the link text itself, use short, unique, descriptive phrases that provide
  context for the material that you're linking to.\n\nEffective link text helps to improve accessibility and scannability. Different
  readers experience links differently. For example, users of screen reader
  software often jump from one link to the next without reading the words in
  between. Other readers visually scan a document to find relevant links.\n\nSometimes you have to rework a sentence to include a phrase that makes good
  link text.\n\n\n### Two options for effective link text\n\nFor your link text, use either the exact page title or a descriptive phrase, as
  described in the following sections.\n\n\n#### Page titles as link text\n\nOne option for effective link text is to match the link text to the page
  title or heading that you're referencing.\n\nFor more information about how to capitalize the page title in a
  cross-reference, see
  Capitalization in references to titles and headings.\n\nRecommended: For more
  information, see
  Load balancing and scaling.\n\n\n#### Descriptive phrases as link text\n\nAnother option for effective link text is to use a description of the
  destination page, capitalized as if it's part of the sentence.\n\nWhen you write a descriptive phrase as link text, help readers quickly
  determine whether the link is relevant to them:\n\n- Place important words at the beginning of the link text.\n- Don't use the same link text in the same document for different target
  pages.\n- Keep link text short where possible.
  Don't write lengthy link text such as a sentence or short paragraph.\n\nRecommended: You can use
  Cloud Scheduler and Cloud Functions to manage
  task scheduling on Compute Engine.\n\nNot recommended: See
  this blog post.\n\n\n### Avoid vague link text\n\nWrite link text that makes sense without the surrounding text.
  Don't use phrases such as this document, this article, or click here.\n\nRecommended:
  For more information, see
  Make headings into link targets.\n\nNot recommended:
  Want more? Click here!\n\nNot recommended:
  For more information,
  see this document.\n\n\n### Avoid URLs as link text\n\nIn general, don't use a URL as link text. Instead, use the page title or a
  description of the page.\n\nRecommended:\n\n```\nFor more information about protocols, see <a href="http://www.w3.org/Protocols/rfc2616/rfc2616.html">HTTP/1.1 RFC</a>.\n```\n\nNot recommended:\n\n```\nSee the HTTP/1.1 RFC at <a href="http://www.w3.org/Protocols/rfc2616/rfc2616.html">http://www.w3.org/Protocols/rfc2616/rfc2616.html</a>.\n```\n\nException: In some legal documents (such as some Terms of Service documents), it's
  okay to use URLs as link text.\n\n\n### Include abbreviations in link text\n\nIf the text includes an abbreviation in parentheses, include the long form
and the abbreviation in the link text.\n\nRecommended: Google Kubernetes Engine (GKE)\n\nNot recommended: Google Kubernetes Engine (GKE)\n\n\n### Link to commands\n\nIf the text includes a command or another element usually conveyed with
  code font, include the description of the code element with the link text,
  unless doing so is awkward or redundant. For more information about elements
  that appear in code font, see Code in text.\n\nRecommended: To create an
  instance with a custom hostname, run the gcloud instances create
  command with the
  --hostname flag.\n\nNot recommended: To create
  an instance with a custom hostname, run the gcloud instances create
  command with the
  --hostname
  flag.\n\nRecommended: This service
  supports the GET, HEAD,
  and OPTIONS methods.\n\nNot recommended: This
  service supports the GET method,
  HEAD method, and
  OPTIONS method.\n\n\n## Write link introductions ("For more information")\n\nWhen you dedicate a separate sentence to a cross-reference, introduce the
cross-reference using consistent language—specifically, use the phrase "For more
information, see..." or "For more information about..., see... ."\n\nInclude the "about..." clause when the link text or surrounding context
  doesn't clearly indicate why you're referring the reader to this information.
  For more information, see the
  Clarify the purpose of a link
  section of this document.\n\nDon't use on instead of about.\n\nUse see to refer to links and cross-references. For more information, see
  see.\n\nRecommended: For more information, see
  Load balancing and scaling.\n\nRecommended: For more information about
  task scheduling, see
  Reliable task scheduling on Google Compute Engine.\n\nNot recommended: For more information on
  indexes, see Manage indexes.\n\n\n## Clarify the purpose of a link\n\nMake sure that the surrounding context or the link text itself clearly
  indicates why you're referring the reader to this information. Make the
  explanation specific, but don't repeat the link text.\n\nIf you're introducing a cross-reference with "For more information..."
  phrasing, then you can do this by adding an "about..." phrase. For more
  information, see the
  Write link introductions section
  of this document.\n\nRecommended: For more
  information about authentication and authorization, see
  Using OAuth 2.0 to access Google APIs.\n\nRecommended: If your
  sample dump file is in a CSV, Avro, or Parquet file format, then
  load the file to BigQuery and copy to Spanner using reverse ETL.\n\n\n## Explain unexpected link behavior\n\nIf a link goes to an unexpected destination or behaves in an unexpected way,
then provide that context. The following are a few such situations:\n\n- Links that download files and open emails. If a link
downloads a file or opens an email, then make that clear in the link text, and
mention the file type.
Recommended: For more
  information,
  download the security features PDF.
Recommended:

  <a href="mailto:support@example.com">send email to Technical Support</a>\n- Links to sections on the same page. When you're
linking to another section on the same page, let the reader know that the link
takes you to a different section of the same page. Use a standard phrase to clue
readers in if you use an on-page link.
Recommended: For more
  information, see the
  Write descriptive link text
  section of this document.
Links to sections on another page. When you're linking
  to a section heading on another page, use the same wording and formatting as you
  do in a regular cross-reference.
If the title of the section that you're linking to is identical to a
  title on the source page, add context to the cross-reference.
Recommended: For more information, see
  Create a table.
Recommended: For more information, see
  Install libraries
  in "Building new audiences based on existing customer lifetime value."
Links that open in a new tab. For more information, see the
  Open links in the current tab section of this
  document.
Links that go to a different domain or server. For more
  information, see the
  Don't use external link icons section
  of this document.\n- Links to sections on another page. When you're linking
  to a section heading on another page, use the same wording and formatting as you
  do in a regular cross-reference.
If the title of the section that you're linking to is identical to a
  title on the source page, add context to the cross-reference.
Recommended: For more information, see
  Create a table.
Recommended: For more information, see
  Install libraries
  in "Building new audiences based on existing customer lifetime value."\n- Links that open in a new tab. For more information, see the
  Open links in the current tab section of this
  document.\n- Links that go to a different domain or server. For more
  information, see the
  Don't use external link icons section
  of this document.\n\nLinks that download files and open emails. If a link
downloads a file or opens an email, then make that clear in the link text, and
mention the file type.\n\nRecommended: For more
  information,
  download the security features PDF.\n\nRecommended:\n\n```\n<a href="mailto:support@example.com">send email to Technical Support</a>\n```\n\nLinks to sections on the same page. When you're
linking to another section on the same page, let the reader know that the link
takes you to a different section of the same page. Use a standard phrase to clue
readers in if you use an on-page link.\n\nRecommended: For more
  information, see the
  Write descriptive link text
  section of this document.\n\nLinks to sections on another page. When you're linking
  to a section heading on another page, use the same wording and formatting as you
  do in a regular cross-reference.\n\nIf the title of the section that you're linking to is identical to a
  title on the source page, add context to the cross-reference.\n\nRecommended: For more information, see
  Create a table.\n\nRecommended: For more information, see
  Install libraries
  in "Building new audiences based on existing customer lifetime value."\n\n\n## Open links in the current tab\n\nDon't force links to open in a new tab or window. Let the reader decide how
  to open links.\n\nIn the rare situation that a link needs to open in a new tab or window, let
  the reader know that the link opens differently than expected.\n\nRecommended:\n\n```\n<a href="/style/accessibility">Accessible content</a>\n```\n\nRecommended:\n\n```\n<a href="/style/accessibility" target="_blank">Accessible content (opens in a new tab)</a>\n```\n\nNot recommended:\n\n```\n<a href="/style/accessibility" target="_blank">Accessible content</a>\n```\n\n\n## Don't use external link icons\n\nDon't use an external link icon to indicate that the link goes to a different
  domain or server. If you think it's important to inform the reader that they're
  leaving a Google domain, mention it in the text and don't rely on an icon.\n\nRecommended: For
  more information, see
  OS-level virtualization.\n\nSometimes OK:
  For more information, see the Wikipedia page about
  OS-level virtualization.\n\nNot recommended:
  For more information, see
  OS-level virtualization.\n\n\n## Punctuation around link text\n\nIf you have punctuation immediately before or after a link, put the
  punctuation outside of the link tags where possible.\n\nRecommended:\n\n```\nFor more information, see <a href="#Test">Test your code</a>.\n```\n\nNot recommended:\n\n```\nFor more information, see <a href="#Test">Test your code.</a>\n```\n\n\n## Quotation marks and italics\n\nWhen a cross-reference is a link, don't put the link text in quotation marks.\n\nRecommended: For more
  information, see
  Meet Android Studio.\n\nRecommended: Learn
  about
  what's new in Android Wear 2.0.\n\nNot recommended: For
  more information, see
  "Meet Android Studio".\n\nIn the rare case when a cross-reference isn't a link, use italics or
  quotation marks as appropriate.\n\n- For an unlinked reference to a document section, short work, or part
  of a series—such as an episode in a web series—use quotation marks.\n- For an unlinked reference to the title of a full-length work—such as a
book, movie, or web series—use italics.
Recommended: ...see
  The Chicago Manual of Style.\n\nFor an unlinked reference to a document section, short work, or part
  of a series—such as an episode in a web series—use quotation marks.\n\nRecommended: For more
  information, see "Describing system versions" in the following section.\n\nFor an unlinked reference to the title of a full-length work—such as a
book, movie, or web series—use italics.\n\nRecommended: ...see
  The Chicago Manual of Style.\n\n\n## Avoid external links in your documentation navigation\n\nIn a documentation set's navigation, such as a table of contents, we
  recommend against linking outside of the documentation set. Instead, include the
  link in a page within the documentation.\n\nIf you need to link outside of your documentation set from your navigation,
  then make sure it's clear to the reader that they'll be leaving that document
  set.\n\n\n## Style link text\n\nIf you write sitewide CSS for your website, apply standard styling to link
  text. This helps readers find links in your content.\n\n- Contrast link text color and regular text color. To
  help readers see links, link text should be distinguishable from the rest of the
  text on the page.\n- Underline link text, and don't underline non-link text.
  When readers scan a page, a horizontal line cuts through the vertical line of
  scanning and helps readers find links.\n- Make visited links change color. Use color-blind-friendly
  color changes to help readers differentiate links that they've followed against
  links that they haven't followed. This helps readers navigate your site
  effectively without revisiting content that they've already read.\n