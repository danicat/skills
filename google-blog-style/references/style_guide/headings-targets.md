Source: https://developers.google.com/style/headings-targets\n\n# Make headings into link targets


      
      Stay organized with collections
    

      
      Save and categorize content based on your preferences.\n\n- Home\n- Products\n- Style\n\n\n## Page Summary\n\n- Turn a heading into a link target by adding an id attribute within a <section> element or directly to the heading tag in HTML.\n- When creating custom anchors, use lowercase letters, hyphens between words, and ensure they are descriptive yet concise.\n- Consider adding custom anchors for frequently linked content or when revising headings to prevent broken links.\n- If revising a heading with an existing anchor, create a new custom anchor using the older ID to maintain link functionality, or update existing links if changing the anchor.\n\nTurn a heading into a link target by adding an id attribute within a <section> element or directly to the heading tag in HTML.\n\nWhen creating custom anchors, use lowercase letters, hyphens between words, and ensure they are descriptive yet concise.\n\nConsider adding custom anchors for frequently linked content or when revising headings to prevent broken links.\n\nIf revising a heading with an existing anchor, create a new custom anchor using the older ID to maintain link functionality, or update existing links if changing the anchor.\n\nThis page discusses how to turn a heading into a link target by using an
    id attribute. For more information about how to format headings, see
    Headings and titles.\n\nIn some content management systems, anchors are automatically created for headings. However, you
  might want to add a custom anchor to a heading for several reasons:\n\n- You want to use an anchor that's shorter than the automatically generated anchor.\n- You want to use an anchor for content that might be frequently linked to. Adding a custom
  anchor reduces the likelihood of breaking existing links if the heading text changes later.\n- You want to revise a heading. If the
      anchor for the heading is generated automatically, then the anchor changes when you revise
      the heading, breaking existing links.\n\nAdd a custom anchor


HTML
To add an anchor to a heading in HTML, add a section element
    with an id attribute. Don't use an a element with
    a name attribute. For anchor text, use lowercase letters, and
    put hyphens between words. In the following, replace
    ID_OF_ANCHOR with your anchor text—for example,
    introduction-to-everything.

    <section id="ID_OF_ANCHOR"></section>
  

Recommended:

  <section id="introduction-to-everything">
  <h2>Introduction to everything</h2>
  ...
  </section>
  
Acceptable:

  <h2 id="introduction-to-everything">Introduction to everything</h2>
  
Not recommended:

  <h2><a name="Introduction_To_Everything">Introduction to everything</a></h2>
  
Not recommended:

  <a name="Introduction_To_Everything"></a>
  <h2>Introduction to everything</h2>
  



Markdown
To add an anchor to a heading in Markdown, add the following code to the
    end of the line that the heading is on. For anchor text, use lowercase
    letters, and put hyphens between words. In the following, replace
    ID_OF_ANCHOR with your anchor text—for example,
    conserve-habitat.
{: #ID_OF_ANCHOR }

Recommended:
## Help conserve habitat for pollinators {: #help-conserve-habitat-for-pollinators }
Also recommended:
## Help conserve habitat for pollinators {: #conserve-habitat }
Acceptable:
## Help conserve habitat for pollinators {: id='conserve-habitat' }
Acceptable:
## Help conserve habitat for pollinators {: id="conserve-habitat" }





Revise a heading
If you revise a heading in a content management system where anchors are automatically created,
  you can create a custom anchor to avoid breaking existing links. If the heading already has a
  custom anchor, don't change the anchor unless it contains a term that you want to remove (such as
  a disrespectful term).
To create the custom anchor, use the older ID string for the heading. You can find the ID
  string by inspecting the heading on the published page. For example, if you change a heading from
  Introduction to some things to Introduction to everything, then add a custom anchor
  that uses the older ID string and formatting.


HTML

<section id="introduction-to-some-things">
<h2>Introduction to everything</h2>
...
</section>



Markdown

## Introduction to everything {: #introduction-to-some-things }



If you need to change an existing custom anchor, you should check your content management
  system to update any links that use the old anchor. Inbound links that use the old anchor still
  reach the page but not the specific section or heading.\n\n\n## Add a custom anchor\n\n\n### HTML\n\nTo add an anchor to a heading in HTML, add a section element
    with an id attribute. Don't use an a element with
    a name attribute. For anchor text, use lowercase letters, and
    put hyphens between words. In the following, replace
    ID_OF_ANCHOR with your anchor text—for example,
    introduction-to-everything.\n\n```\n<section id="ID_OF_ANCHOR"></section>\n```\n\nRecommended:\n\n```\n<section id="introduction-to-everything">
  <h2>Introduction to everything</h2>
  ...
  </section>\n```\n\nAcceptable:\n\n```\n<h2 id="introduction-to-everything">Introduction to everything</h2>\n```\n\nNot recommended:\n\n```\n<h2><a name="Introduction_To_Everything">Introduction to everything</a></h2>\n```\n\nNot recommended:\n\n```\n<a name="Introduction_To_Everything"></a>
  <h2>Introduction to everything</h2>\n```\n\n\n### Markdown\n\nTo add an anchor to a heading in Markdown, add the following code to the
    end of the line that the heading is on. For anchor text, use lowercase
    letters, and put hyphens between words. In the following, replace
    ID_OF_ANCHOR with your anchor text—for example,
    conserve-habitat.\n\n```\n{: #ID_OF_ANCHOR }\n```\n\nRecommended:\n\n```\n## Help conserve habitat for pollinators {: #help-conserve-habitat-for-pollinators }\n```\n\nAlso recommended:\n\n```\n## Help conserve habitat for pollinators {: #conserve-habitat }\n```\n\nAcceptable:\n\n```\n## Help conserve habitat for pollinators {: id='conserve-habitat' }\n```\n\nAcceptable:\n\n```\n## Help conserve habitat for pollinators {: id="conserve-habitat" }\n```\n\n\n## Revise a heading\n\nIf you revise a heading in a content management system where anchors are automatically created,
  you can create a custom anchor to avoid breaking existing links. If the heading already has a
  custom anchor, don't change the anchor unless it contains a term that you want to remove (such as
  a disrespectful term).\n\nTo create the custom anchor, use the older ID string for the heading. You can find the ID
  string by inspecting the heading on the published page. For example, if you change a heading from
  Introduction to some things to Introduction to everything, then add a custom anchor
  that uses the older ID string and formatting.\n\n\n### HTML\n\n```\n<section id="introduction-to-some-things">
<h2>Introduction to everything</h2>
...
</section>\n```\n\n\n### Markdown\n\n```\n## Introduction to everything {: #introduction-to-some-things }\n```\n\nIf you need to change an existing custom anchor, you should check your content management
  system to update any links that use the old anchor. Inbound links that use the old anchor still
  reach the page but not the specific section or heading.\n