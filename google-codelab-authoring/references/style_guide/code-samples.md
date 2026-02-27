Source: https://developers.google.com/style/code-samples\n\n# Code samples


      
      Stay organized with collections
    

      
      Save and categorize content based on your preferences.\n\n- Home\n- Products\n- Style\n\n\n## Page Summary\n\n- Code samples should follow indentation guidelines, typically using spaces instead of tabs and two spaces per indentation level.\n- Wrap code lines at 80 characters for better readability, especially in narrow browser windows or when printed.\n- Use <pre> element in HTML or four-space indentation in Markdown to format code blocks as preformatted text and indicate omissions with comments specific to the code's language.\n- Introduce code samples with a sentence or paragraph, ending with a colon if directly preceding the sample, or a period if there's intervening material.\n- Refer to the relevant code style guides, such as Google's or project-specific ones, for language-specific formatting conventions.\n\nCode samples should follow indentation guidelines, typically using spaces instead of tabs and two spaces per indentation level.\n\nWrap code lines at 80 characters for better readability, especially in narrow browser windows or when printed.\n\nUse <pre> element in HTML or four-space indentation in Markdown to format code blocks as preformatted text and indicate omissions with comments specific to the code's language.\n\nIntroduce code samples with a sentence or paragraph, ending with a colon if directly preceding the sample, or a period if there's intervening material.\n\nRefer to the relevant code style guides, such as Google's or project-specific ones, for language-specific formatting conventions.\n\nThis page explains how to format code samples. For more information about formatting and
  explaining code that appears in text, command-line syntax, and placeholders, see the following
  resources:\n\n- Code in text\n- Documenting command-line syntax\n- Formatting placeholders\n\n\n## Basic guidelines\n\nFollow these guidelines when formatting code samples:\n\n- Follow the indentation guidelines in the relevant
    code style guide. For most programming languages, this means using
    spaces instead of tabs and using two spaces for each indentation level. However, some contexts
    use four spaces for each indentation level, and some contexts use tabs. This guidance applies to
    formatting code samples, not to formatting commands.\n- Wrap lines at 80 characters. If you expect readers to have a relatively narrow
    browser window or to print out your document, consider wrapping at a smaller number of
    characters for readability.\n- Mark code blocks as preformatted text. In HTML, use a pre element;
    in Markdown, indent every line of the code block by four spaces.\n- Indicate omitted code by using a comment in the syntax of the language of your code
    sample. Don't use three dots or the ellipsis character (…). If a code
    block contains an omission, don't format the block as click-to-copy.\n\nFollow the indentation guidelines in the relevant
    code style guide. For most programming languages, this means using
    spaces instead of tabs and using two spaces for each indentation level. However, some contexts
    use four spaces for each indentation level, and some contexts use tabs. This guidance applies to
    formatting code samples, not to formatting commands.\n\nWrap lines at 80 characters. If you expect readers to have a relatively narrow
    browser window or to print out your document, consider wrapping at a smaller number of
    characters for readability.\n\nRecommended:\n\n```\n<pre>
function helloWorld() {
  alert('Hello, world! This sentence is so long that it wraps onto a second
    line.');
}
</pre>\n```\n\nThis renders the following code block:\n\n```\nfunction helloWorld() {
  alert('Hello, world! This sentence is so long that it wraps onto a second
    line.');
}\n```\n\nRecommended:\n\n```\napiVersion: serving.knative.dev/v1
kind: Service
# Several lines of code are omitted here.
spec:
  template:
    spec:
      containers:
      - image: IMAGE_URL
        ports:
        - name: h2c
          containerPort: 8080\n```\n\n\n## Introductory statements\n\nIn most cases, precede a code sample with an introductory sentence or
paragraph. The introduction can end with a colon or a period; usually a colon if it
immediately precedes the sample, usually a period if there's more material (such
as a note paragraph) between the introduction and the sample, or if the
introduction paragraph ends in a sentence that isn't directly related to the
sample.\n\nRecommended (ending with a period): The
following code sample shows how to use the get method. For
information about other methods, see [link]. [sample]\n\nAlso recommended: The following code
sample shows how to use the get method: [sample] For information about
other methods, see [link].\n\nNot recommended (ending with a colon): The
following code sample shows how to use the get method. For
information about other methods, see [link]: [sample]\n\nFor more information about how to introduce code samples, see
  Document command-line syntax.\n\n\n## Code style guides\n\nThe following public Google coding-style guides are available on GitHub:\n\n- C++ style guide.\n- HTML/CSS style guide.\n- Java style guide.\n- JavaScript style guide.\n- Python style guide\n- Full list of Google's programming style guides\n\nSome open source projects have their own overriding style guides. For
  example, Java code in the Android Open Source Project follows the AOSP Java Code
  Style for Contributors guide.\n