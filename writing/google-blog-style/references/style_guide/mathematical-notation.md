Source: https://developers.google.com/style/mathematical-notation\n\n# Mathematical notation


      
      Stay organized with collections
    

      
      Save and categorize content based on your preferences.\n\n- Home\n- Products\n- Style\n\nThis page describes how to format common mathematical notation such as
exponents, expressions, equations, operators, and variables in
documentation. Formatting best practices can help ensure that your
documentation is compatible with assistive technologies and
renders accurately.\n\nFor general information about using and formatting numbers, see
Numbers.\n\nNote: This page includes examples of formatting in HTML
and Markdown in standard text. If you're using a third-party tool to display
complex math, follow that tool's formatting guidance to ensure that your
mathematical markup displays correct.\n\n\n## Use HTML entities for mathematical symbols\n\nIn general, use HTML entities for mathematical symbols instead of keyboard
symbols. The following table lists entities for symbols that are common in
arithmetic and algebra. For the plus sign (+), equals sign
(=), and division sign (/), you can use
their keyboard equivalents.\n\n\nSymbol | Markup | Description\n+ | Use the keyboard symbol. | Plus sign\n− | &minus; | Minus sign\n× | &times; | Multiplication sign
Alternatively, you can use the dot operator ∙
        (&#8729;) or asterisk operator *
        (&#42;) to match the UI. Don't use an asterisk
        (*) to indicate multiplication in text.
You can indicate multiplication by omitting the multiplication
        symbol if doing so doesn't create ambiguity—for example,
        instead of a × b, you can write
        ab.\n/ | Use the keyboard symbol. | Division sign\n= | Use the keyboard symbol. | Equals sign\n≠ | &ne; | Not equal to\n± | &plusmn; | Plus-minus sign\n∓ | &mnplus; | Minus-plus sign\n< | &lt; | Less than sign\n> | &gt; | Greater than sign\n≈ | &asymp; | Approximately equal to\n≉ | &nap; | Not approximately equal to\n≅ | &cong; | Congruent to\n≤ | &le; | Less than or equal to\n≥ | &ge; | Greater than or equal to\n≡ | &equiv; | Identical to\n≢ | &nequiv; | Not identical to\n√ | &radic; | Square root\n∑ | &sum; | N-ary summation\n\nMultiplication sign\n\nAlternatively, you can use the dot operator ∙
        (&#8729;) or asterisk operator *
        (&#42;) to match the UI. Don't use an asterisk
        (*) to indicate multiplication in text.\n\nYou can indicate multiplication by omitting the multiplication
        symbol if doing so doesn't create ambiguity—for example,
        instead of a × b, you can write
        ab.\n\n\n## Format mathematical notation\n\nThe following sections provide formatting for common math-related notation.\n\n\n### Operators\n\nTo ensure accessibility and accurate HTML syntax, use
HTML entities
instead of keyboard symbols for operators. For example, use
&minus; instead of a hyphen (-).\n\nInclude a non-breaking space (&nbsp;) on both sides
of operators within a single expression, equation, or
statement.\n\nDon't italicize operators.\n\nRecommended: a − b\n\nTo render a − b, use the following markup:\n\n- HTML: <i>a</i>&nbsp;&minus;&nbsp;<i>b</i>\n- Markdown: _a_&nbsp;&minus;&nbsp;_b_\n\n\n### Variables\n\nItalicize variables.\n\nRecommended: x ≠ y\n\nRecommended: xy\n\nRecommended: yi\n\nTo render x ≠ y, use the following markup:\n\n- HTML: <i>x</i>&nbsp;&ne;&nbsp;<i>y</i>\n- Markdown: _x_&nbsp;&ne;&nbsp;_y_\n\n\n### Expressions and equations\n\nInclude short expressions and equations inline with your text.\n\nInclude a non-breaking space (&nbsp;) between components
such as operators and variables so that the expression or equation renders on
the same line.\n\nWhen an expression or equation creates an awkward line break, consider
placing it on its own line.\n\nRecommended: The equation
that describes a linear trend line is
y = a + bx.\n\nRecommended: The equation
that describes a polynomial trend line, where the order is o, is the
following:
y = a + b × x + ... + k × xo\n\nTo render y = a + bx, use the
following markup:\n\n- HTML: <i>y</i>&nbsp;&=&nbsp;<i>a</i>&nbsp;+&nbsp;<i>bx</i>\n- Markdown: _y_&nbsp;&=&nbsp;_a_&nbsp;+&nbsp;_bx_\n\n\n### Fractions\n\nExpress fractions as decimal numbers, when possible.
If you must express fractions as words, connect the numerator and
denominator with a hyphen unless one of them is already hyphenated.\n\nExpress fractions as decimal numbers, when possible.\n\nIf you must express fractions as words, connect the numerator and
denominator with a hyphen unless one of them is already hyphenated.\n\nRecommended: 0.02\n\nRecommended: one and one-half\n\nRecommended: three-sevenths\n\nRecommended: three seventy-fourths\n\n\n### Exponents and subscripts\n\nUse
  standard mathematical notation.
  Don't put a space between the base and the exponent.\n\nTo render exponents, use the HTML <sup> tag. Don't use the
keyboard caret symbol (^) to indicate an exponent.\n\nTo render subscripts, use the HTML <sub> tag.\n\nRecommended: 23\n\nRecommended: xy\n\nRecommended: yi\n\nNot recommended: 2^3\n\nTo render 23, use the following markup in HTML and Markdown:
2<sup>3</sup>\n\n\n## Notation as words\n\nIn general, you can use mathematical notation in place of words in running
text. For example, in a sentence, you might use the statement
x ≠ y instead of writing "x is not equal to
y." If the use of notation instead of words creates ambiguous, grammatically
incorrect, or difficult-to-read text, then use words to convey the
mathematical concept.\n\nRecommended: Check
whether a > b.\n\nRecommended: The area
is calculated by multiplying the length by the width.\n\nNot recommended: Check
whether a is greater than b.\n\nNot recommended: The
area is calculated by multiplying l × w.\n\n\n## Provide visuals for math concepts\n\nAccompany math concepts and numerals with
diagrams or other images
to support comprehension. For example, if comparing statistics, consider illustrating percentages in
a pie chart or a bar graph.\n\n\n## More resources\n\n- Numbers\n- Units of measure\n- Text-formatting summary\n