Source: https://developers.google.com/style/html-formatting\n\n# HTML formatting


      
      Stay organized with collections
    

      
      Save and categorize content based on your preferences.\n\n- Home\n- Products\n- Style\n\n\n## Page Summary\n\n- Adhere to Google's HTML/CSS Style Guide, ensuring optional elements are included and utilizing spaces for indentation instead of tabs.\n- Maintain consistent indentation with two spaces per level, employ lowercase for elements and attributes, and avoid trailing spaces unless necessary for Markdown.\n- Observe an 80-character line length limit, with exceptions for meta elements, long URLs, and specific legacy file formatting.\n- Break code snippets within <pre> blocks at 80 characters while ensuring the code's meaning remains intact and considering exceptions for existing file consistency.\n\nAdhere to Google's HTML/CSS Style Guide, ensuring optional elements are included and utilizing spaces for indentation instead of tabs.\n\nMaintain consistent indentation with two spaces per level, employ lowercase for elements and attributes, and avoid trailing spaces unless necessary for Markdown.\n\nObserve an 80-character line length limit, with exceptions for meta elements, long URLs, and specific legacy file formatting.\n\nBreak code snippets within <pre> blocks at 80 characters while ensuring the code's meaning remains intact and considering exceptions for existing file consistency.\n\nFollow Google's HTML/CSS
Style Guide. Exception: don't leave out optional elements.\n\nIn particular, following are some basic guidelines from that style guide,
which generally apply to other documentation source files, too (such as YAML and Markdown):\n\n- Don't use tabs to indent text; use spaces only. Different text
editors interpret tabs differently, and some Markdown features expect spaces
and not tabs.\n- Indent by two spaces per indentation level.\n- Use all-lowercase for elements and attributes.\n- Don't leave trailing spaces at the end of a line (except as
needed for Markdown).\n\n\n## Line length\n\nBreak lines at 80 characters except in the following cases:\n\n- Information in a meta element at the beginning of a file must be on a single line,
  so those lines can be as long as needed.\n- If a URL in a link has a line break, the link won't work.
If a URL is longer than 80 characters (quite common), you're stuck with it. In that case,
put the URL on its own line with the href attribute to make it
easier to review the text before and after, as the following example shows:\n\n```\nYou can find more information in
<a href="https://example.com/long-url/johan-gambolputty-de-von-ausfern-…-von-hautkopf-of-ulm.html"
>his biography.</a>\n```\n\nBreak code snippets (in <pre> blocks) at 80 characters:\n\n- Older files might use different line lengths. If you're making small changes to a file that
    has a consistent line length other than 80 characters, then make your changes conform to that
    file's line length rather than reformatting the whole file.\n- When adding line breaks, make sure that you don't change the meaning of the code! If you're
    not familiar with the programming language, ask for help from someone who is. But sometimes you
    just can't avoid a long line.\n