Source: https://developers.google.com/style/ui-elements\n\n# UI elements and interaction


      
      Stay organized with collections
    

      
      Save and categorize content based on your preferences.\n\n- Home\n- Products\n- Style\n\n\n## Page Summary\n\n- Instructions should focus on user goals and avoid UI specifics unless crucial for clarity.\n- UI elements like buttons and menus should be referred to by their labels in bold (e.g., File menu, Open command).\n- Prioritize feature functionality over UI element type, using specific terminology for clarity (e.g., "field" instead of "text box" in Google Cloud/Workspace).\n- Accessibility is important; ensure tooltips are present for icons and avoid directional language.\n- Keyboard keys should be formatted using <kbd> tags, with uppercase letters for letter keys and spelled-out modifier keys.\n\nInstructions should focus on user goals and avoid UI specifics unless crucial for clarity.\n\nUI elements like buttons and menus should be referred to by their labels in bold (e.g., File menu, Open command).\n\nPrioritize feature functionality over UI element type, using specific terminology for clarity (e.g., "field" instead of "text box" in Google Cloud/Workspace).\n\nAccessibility is important; ensure tooltips are present for icons and avoid directional language.\n\nKeyboard keys should be formatted using <kbd> tags, with uppercase letters for letter keys and spelled-out modifier keys.\n\n\n## Focus on the task\n\nWhen practical, state instructions in terms of what the reader
should accomplish, rather than focusing on the widgets and gestures.
By avoiding reference to UI elements, you help the reader understand
the purpose of an instruction, and it can help future-proof
procedures.\n\nRecommended: Refresh the page.\n\nRecommended: Expand the Advanced options
    section.\n\nHowever, know the audience and understand the context. In some cases, the point
of a procedure is to guide the reader through elements on the page. Or the UI might not be obvious,
and it's helpful to explain the gestures for completing a step. Provide the level of detail
that seems useful for the intended audience.\n\nRecommended: Click Refresh.\n\nRecommended: To expand the Advanced
    options section, click the
    arrow_rightexpander arrow.\n\nThe rest of this page focuses on scenarios where you've decided it's
useful to explicitly discuss UI elements.\n\nFor information about writing procedures, see Procedures.\n\n\n## Format names of UI elements\n\nWhen referring to any UI element by name, put its name in bold, using the
b element in HTML or ** in Markdown. This
includes names for buttons, menus, dialogs, windows, list items, or any other
feature on the page that has a visible name. Don't use code font for UI elements,
unless it's an element that meets the requirements for code font.
In that case, use both code font and bold.\n\nDon't make an official feature name or product name bold, except when it
directly refers to an element on the page that uses the name (such as a window
title or button name).\n\nRecommended:
    In the New project window, select the New activity
    checkbox, and then click Next.\n\nNot recommended:
    In the New Project window, select "New Activity", and then click the
    "Next" button.\n\n\n## Use appropriate capitalization\n\nIn most cases, follow the capitalization as it appears on the page. However,
if labels are inconsistent or they're all uppercase, use sentence case.\n\n\nGuidance | Recommended | Not recommended\nWhen a label is all uppercase, use sentence case. | Click refresh Refresh. | Click REFRESH.\nWhen referring to multiple labels that are inconsistently cased, use
    sentence case for all of the labels. | Click New project, and then click New activity. | Click NEW PROJECT, and then click New Activity.\n\n\n## Refer to UI elements\n\nDon't use UI elements as if they were English verbs or nouns.\n\n\nRecommended | Not recommended\nIn the Name field, enter an account name. | Name the account.\nTo save the settings, click Save. | Save the settings.\nIn the Service account ID field, enter a name.
For Service account ID, enter a name. | Specify a Service account ID.\n\nIn the Service account ID field, enter a name.\n\nFor Service account ID, enter a name.\n\n\n## Terminology and usage\n\nA user interface can contain a variety of UI elements. In general, focus on
the feature and its functionality, not the UI element. If you think it adds
clarity for the reader, use the name of the UI element. For example, both of the
following sentences are valid:\n\nRecommended:
    Go to File > Tools.\n\nRecommended:
    In the File menu, click Tools.\n\nDon't use slang terms for UI elements—for example,
  hamburger icon or zippy. For more information, see
  Buttons and icons.\n\nRecommended:
    To expand the Advanced options section, click the
    arrow_rightexpander arrow.\n\nRecommended:
    Expand Advanced options.\n\nNot recommended:
    To expand the Advanced options section, click the zippy.\n\nThe following sections define some terms to use when referring to UI
elements.\n\nFor prepositions to use with these elements, see the
  Prepositions table.\n\n\n### Windows, pages, dialogs, panes, and sections\n\nMost often, a window is the entire application window in a desktop
environment. However, it can also refer to modular application elements that you
can open and close. For example, in Android Studio, several windows are
available in the View > Tool Windows menu.\n\nRecommended:
    In the MyApp window, click Edit.\n\nNot recommended:
    In the MyApp page, click Edit.\n\nPage is the preferred term when referring to a web page in general and to a subpage
of a console in particular. For more information, see
console.\n\nRecommended:
    In the Google Cloud console, go to the Deployments page.\n\nNot recommended:
    In the Google Cloud console, go to the Deployments window.\n\nA dialog is a smaller window that is usually detached from the
main application window and appears in front of the window.\n\nRecommended:
    In the Welcome dialog, click OK.\n\nNot recommended:
    In the Welcome pop-up window, click OK.\n\nA pane (or panel) is typically a distinct rectangular region within a larger
browser or application window. A pane or panel can often be tightly coupled to surrounding UI
regions, whereas a window is distinctly separate and can be hidden. Do not use terms such as
window, section, area, or column to refer to a pane or panel.\n\nRecommended:
    In the Create service account pane, click New.\n\nNot recommended:
    In the Create service account section, click New.\n\nRecommended: In the Create metric pane, do the
      following:\n\n- In the Metric type section, select Counter.\n- In the Labels section, click Add label.\n\n\n### Menus and menu bars\n\nIn a desktop application, the menu bar appears at the top of the
window or at the top of the screen; it's a set of menus (such as
File or Edit), each of which is a set of related
commands and/or nested submenus.\n\nTo refer to an item in a menu, use the term command, not choice, menu item,
or option. Exception: if you're documenting how to build an interface,
you can use menu item.\n\nTo refer to a menu, use the form the LABEL_NAME menu.\n\nTo tell the reader where to find a command in a menu or submenu, use a phrase like
In the File menu, select Open.\n\nDon't use drop-down as a synonym for menu. See
drop-down.\n\n\n#### Use angle brackets\n\nAnother option is to use angle brackets (>). If you use angle brackets, follow these
  guidelines:\n\n- Put a nonbreaking space (&nbsp;) before each angle bracket.\n- Don't bold each menu name separately; instead, enclose the entire sequence in a single bold
tag (<b>...</b> or **...**).\n- Wrap the angle bracket with a span tag and add an aria-label attribute with
and then text
(for example, <span aria-label="and then">></span>).
Otherwise, some screen readers might read > as "greater than."\n\nIn the following example, the text renders as Select View >
      Tools > Developer Tools. A screen reader
  interprets this as Select View and then Tools and then Developer Tools.\n\n\n### HTML\n\n```\nSelect <b>View&ampnbsp<span aria-label="and then">></span> Tools&ampnbsp<span aria-label="and then">></span> Developer Tools</b>.\n```\n\n\n### Markdown\n\n```\nSelect **View&ampnbsp<span aria-label="and then">></span> Tools <span aria-label="and then">></span> Developer Tools**.\n```\n\nThis notation is useful for abbreviating a longer phrase like In the
File menu, select Open. However, this notation applies only to
menu items. Don't use it to describe a combination of different UI elements.\n\nRecommended: Select
    MyApp > Preferences, and then select the
    Languages preference pane.\n\nNot recommended:
    Select MyApp > Preferences > Languages >
    + > CSS.\n\n\n### Navigation menu\n\nA navigation menu is a control—usually a pane or window—that contains a list of items
that the user can click to go to pages in an application or website. Don't use the terms
navigation bar, navigation pane, navigation panel, or
navigation window for such a control.\n\nRecommended:
    In the BigQuery navigation menu, click Scheduled queries.\n\n\n### Toolbar\n\nA toolbar is a set of buttons for common user actions. A toolbar
button that includes a menu is called a menu button. Refer to the
toolbar by name if you think that the user needs help finding a button.\n\nRecommended:
    On the Google Cloud console toolbar, click
    notifications_none Notifications.\n\nRecommended: Click
    notifications_none Notifications.\n\n\n### Buttons and icons\n\nA button initiates an action when clicked (or tapped, in the case
  of a touchscreen). To refer to a button, use the button's label.\n\nRecommended: Click OK.\n\nNot recommended: Click the "OK"
    button.\n\nAn icon is a symbol or image that represents an object or a function. An icon
can be a button as well. If the button includes an icon, write the name of the
button as shown in the tooltip, and add the button icon before the
name. If you need to use a space between the icon and the name for readability,
use a nonbreaking space.\n\nRecommended: Click
  more_vert Settings and utilities.\n\nNot recommended: Click
  more_vert.\n\nIf the icon tooltip is identical to the name of the icon, use an
empty alt attribute.\n\nIf you're unsure of the name of the icon, inspect the element using browser
tools. In many cases, a visual element like an icon has an ARIA attribute
that provides a textual description of the element for use by screen readers.
To inspect an element, right-click the element and select
Inspect or Inspect element, depending on your browser. Look for one of the following
types of labels: aria-labelledby, aria-label,
aria-describedby, label, placeholder, or title.
For more information, see
Using aria-label
and
Accessible Name and Description calculation.\n\nIf a button with an icon doesn't include a tooltip, submit a bug report
requesting that a tooltip be added. Tooltips are crucial for accessibility, and
for documentation and discoverability in general.\n\nRecommended: Click  Add.\n\nNot recommended: Click the  icon.\n\nIf a UI element name ends with an ellipsis (...), leave out the ellipsis.\n\nRecommended: Click Browse.\n\nNot recommended: Click
    Browse ....\n\nDon't use directional language to orient the reader, such as above,
below, or right-hand side. Phrases like those don't work well for
accessibility or for localization. If a UI element is hard to find, provide a
screenshot.\n\nRecommended: Click menu Menu.\n\nNot recommended: In the left-side panel,
    click the button with three lines.\n\n\n#### Difficult-to-find UI elements\n\nIf you have UI elements that are difficult to find, consider one of the following options
  as an alternative to using directional language, which can be problematic for
  accessibility and localization reasons.\n\n- Use the button icon along with its name as shown in the button tooltip.

      
Recommended: Click
          refresh Refresh.\n- Add context to help the user find the element.

      
Recommended: On the Cloud Run toolbar, click
          refresh Refresh.\n- Use a screenshot.

Recommended: In the list of services, click
          view_column Column display options.


For more information about when and how to use screenshots, see
      Diagrams, figures, and other images.\n\nRecommended: Click
          refresh Refresh.\n\nRecommended: On the Cloud Run toolbar, click
          refresh Refresh.\n\nUse a screenshot.\n\nRecommended: In the list of services, click
          view_column Column display options.\n\nFor more information about when and how to use screenshots, see
      Diagrams, figures, and other images.\n\n\n### Tab\n\nA tab is a navigation element that looks like a file tab. To refer
to a tab, use the form the LABEL_NAME tab.\n\nRecommended: Select
Tools > Options, and then click the Edit
tab.\n\n\n### Text box\n\nA text box is a box that the user can type in. Use
  box and the form the LABEL_NAME box. Format the text
  that the user types by using the code element in HTML, or by using code
  formatting (monospace) in other markup.\n\nRecommended: In the Owner box,
    enter your name.\n\nRecommended: In the Name box,
    enter wsfc-1.\n\nIn Google Cloud, use
field instead of box.\n\nIn Google Workspace documentation, use
field instead of box.\n\nRecommended: In the Instance field,
    specify a value less than 64 characters long.\n\n\n### List box, combo box, and spin box\n\nA list box is a box that offers the user a list of items. To refer to a list box, use
the form the LABEL_NAME list or
the LABEL_NAME box, whichever is clearer.\n\nRecommended: In the Item list, select
Desktop.\n\nA combo box is a combination of a text box and a list box. To
refer to a combo box, use the form the LABEL_NAME box. To refer to
entering a value into a combo box, use the verbs type or select or enter.\n\nRecommended: In the Font box, type
or select the font that you want to use.\n\nA spin box is a box that lets the user choose a value by clicking
arrows or by typing. To refer to a spin box, use the form the
LABEL_NAME box. To refer to entering a value into a spin
box, use the verb enter.\n\nRecommended: In the Font Size box,
enter a font size.\n\n\n### Checkbox\n\nA checkbox is a small box that indicates whether an option is
on or off. To refer to a checkbox, use the form the
LABEL_NAME checkbox.\n\nBe wary of using the verbs check and uncheck, which can be ambiguous; it's often
  best to use select and clear instead.\n\nRecommended: Select the Automatically
check for updates checkbox.\n\nRecommended: Clear the
Bookmarks checkbox.\n\nIf you need to refer to the state of the checkbox, it's often best to refer to it as
  selected or not selected.
Recommended: Make sure that the
Bookmarks checkbox is selected.
Recommended: Make sure that the
Bookmarks checkbox isn't selected.
Radio button
A radio button is a small button used to choose one item from a
group of mutually exclusive options. To refer to a radio button, use the radio
button's label, or refer to the group of buttons by its label.
Recommended: Select Do not remember
passwords.
Recommended: For Startup mode,
select an option.
Expander arrow
An expander arrow is the UI element used to expand or collapse a section of
  navigation or content. Avoid referring to these explicitly in documentation, but when you do, use
  the terms expander arrow and expandable section rather than terms like
  expando or zippy.
Recommended: To expand the
  Advanced options section, click the
  arrow_rightexpander arrow.
Not recommended: To expand
  the Advanced options section, click the zippy.
Toggle
A toggle is the UI element that switches back and forth between on and off
states. Don't use the word toggle as a verb. Describe the action that you want the
user to take.
Recommended: To turn on the setting, click
  the Wi-Fi toggle.
In some cases, you might not know what state the toggle is in before the user interacts with it
  so be clear what position the toggle should be in.
Recommended: In Settings, click
    the Magic mode toggle to the on position.\n\nRecommended: Make sure that the
Bookmarks checkbox is selected.\n\nRecommended: Make sure that the
Bookmarks checkbox isn't selected.\n\n\n### Radio button\n\nA radio button is a small button used to choose one item from a
group of mutually exclusive options. To refer to a radio button, use the radio
button's label, or refer to the group of buttons by its label.\n\nRecommended: Select Do not remember
passwords.\n\nRecommended: For Startup mode,
select an option.\n\n\n### Expander arrow\n\nAn expander arrow is the UI element used to expand or collapse a section of
  navigation or content. Avoid referring to these explicitly in documentation, but when you do, use
  the terms expander arrow and expandable section rather than terms like
  expando or zippy.\n\nRecommended: To expand the
  Advanced options section, click the
  arrow_rightexpander arrow.\n\nNot recommended: To expand
  the Advanced options section, click the zippy.\n\n\n### Toggle\n\nA toggle is the UI element that switches back and forth between on and off
states. Don't use the word toggle as a verb. Describe the action that you want the
user to take.\n\nRecommended: To turn on the setting, click
  the Wi-Fi toggle.\n\nIn some cases, you might not know what state the toggle is in before the user interacts with it
  so be clear what position the toggle should be in.\n\nRecommended: In Settings, click
    the Magic mode toggle to the on position.\n\n\n## Press and type keyboard keys\n\nTo indicate that the user should press a given keyboard key or
  combination, use the kbd element.\n\nRecommended:
  Press <kbd>Control+C</kbd>.\n\nWhen rendered, the text appears as follows:\n\nRecommended: Press Control+C.\n\nIf you're working with non-HTML markup, use monospace formatting, which is how the
kbd element renders.\n\nTo refer to a letter key, use uppercase instead of lowercase.\n\nRecommended: To save, press
  Control+S.\n\nNot recommended: To save, press
  Control+s.\n\nTo refer to a key that the user types to enter that key's value as text input,
  use the code element, not the kbd element.
  For more information, see Code font.\n\nTo refer to a keyboard key, use the key's name. If that's ambiguous, use the
form the KEY_NAME key.\n\nRecommended: Press Esc.\n\nRecommended: Press the Esc key.\n\nSpell out the names of modifier keys such as Command, Control, Option, and
Shift. Don't use symbols for those keys. To refer to a key combination, use the
form MODIFIER+KEY_NAME.\n\nRecommended: Press
Control+V.\n\nWhen you provide shortcuts for multiple operating systems, put the macOS shortcut in
parentheses after the Windows and Linux shortcut.\n\nRecommended: To copy, press
Control+C (or Command+C on macOS).\n\nNot recommended: To copy, press
Ctrl+C (⌘+C).\n\nTo refer to a key or combination that uses the Shift key, use the form
  MODIFIER+Shift+KEY_NAME.\n\nRecommended: Press
Control+Shift+?.\n\nSpell out the names of characters that could be confusing in a keyboard
shortcut, such as comma, hyphen, period, and plus.\n\nTo refer to a keyboard shortcut, use either keyboard shortcut or key
combination.\n\nTo refer to pressing a key or combination to cause an action to occur, use
the verb press. To refer to typing a key or combination as part of text, use
the verbs enter or type.\n\n\n## Prepositions\n\nWhen documenting the UI, use the following prepositions.\n\n\nPreposition | UI element | Recommended\nin | dialogs
fields
lists
menus
panes
windows | In the Alert dialog, click OK.
In the Name field, enter wsfc-1.
In the Item list, select Desktop.
In the File menu, click Tools.
In the Metrics pane, click New.
In the Task window, click Start.\non | pages
tabs
toolbars | On the Create an instance page, click Add.
On the Edit tab, click Save.
On the Dashboard toolbar, click Edit.\n\ndialogs\n\nfields\n\nlists\n\nmenus\n\npanes\n\nwindows\n\nIn the Alert dialog, click OK.\n\nIn the Name field, enter wsfc-1.\n\nIn the Item list, select Desktop.\n\nIn the File menu, click Tools.\n\nIn the Metrics pane, click New.\n\nIn the Task window, click Start.\n\npages\n\ntabs\n\ntoolbars\n\nOn the Create an instance page, click Add.\n\nOn the Edit tab, click Save.\n\nOn the Dashboard toolbar, click Edit.\n\n\n## Verbs in procedures\n\nTo describe an action on the page, use the following verbs. For more
  information about each verb, see its corresponding entry on the
  word list.\n\n- Click\n- Choose\n- Drag\n- Enable\n- Enter, type\n- Go to (see scroll)\n- Hold the pointer over\n- Press\n- Select\n- Tap\n- Turn on, turn off\n\nFor information about writing procedures, see Procedures.\n