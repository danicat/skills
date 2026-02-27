Source: https://developers.google.com/style/api-reference-comments\n\n# API reference code comments


      
      Stay organized with collections
    

      
      Save and categorize content based on your preferences.\n\n- Home\n- Products\n- Style\n\n\n## Page Summary\n\n- API documentation must include descriptions for every class, constant, method, and parameter, with detailed explanations of their purpose, usage, and potential exceptions.\n- Descriptions should be concise and informative, prioritizing clarity and avoiding redundancy, using present tense and specific verbs for actions.\n- Parameter descriptions should clearly define their purpose and expected values, including behavior for booleans and defaults, while return values focus on the information provided.\n- Class descriptions should begin with a concise purpose statement and offer guidance on usage, features, and best practices, while member descriptions should link to relevant methods.\n- Deprecation notices must specify replacements and provide guidance for updating existing code to ensure compatibility.\n\nAPI documentation must include descriptions for every class, constant, method, and parameter, with detailed explanations of their purpose, usage, and potential exceptions.\n\nDescriptions should be concise and informative, prioritizing clarity and avoiding redundancy, using present tense and specific verbs for actions.\n\nParameter descriptions should clearly define their purpose and expected values, including behavior for booleans and defaults, while return values focus on the information provided.\n\nClass descriptions should begin with a concise purpose statement and offer guidance on usage, features, and best practices, while member descriptions should link to relevant methods.\n\nDeprecation notices must specify replacements and provide guidance for updating existing code to ensure compatibility.\n\n\n\nWhen you're documenting an API, provide a complete API reference, typically
generated from source code using document comments that describe all public
classes, methods, constants, and other members.\n\nUse the basic guidelines in this document as appropriate for a given programming
language. This document doesn't specify how to mark up document comments.\n\nFor more information, see the following resources:\n\n- AIP-192: Documentation
in Google's API standards\n- Inline API documentation
in the Google Cloud API design guide\n- The specific style guide for each programming language\n\n\n## Documentation basics\n\nThe API reference must provide a description for each of the following:\n\n- Every class, interface, struct, and any other similar member of the API (such
as union types in C++).\n- Every constant, field, enum, and typedef.\n- Every method, with a description for each parameter, the return value, and any
exceptions thrown.\n\nEvery class, interface, struct, and any other similar member of the API (such
as union types in C++).\n\nEvery constant, field, enum, and typedef.\n\nEvery method, with a description for each parameter, the return value, and any
exceptions thrown.\n\nThe following are extremely strong suggestions. In some cases, they don't
make sense for a particular API or in a specific language, but in general,
follow these guidelines:\n\n- On each unique page (for a class, interface, etc.), include a code sample
(~5-20 lines) at the top.\n- Put all API names, classes, methods, constants, and parameters in code font,
and link each name to the corresponding reference page. Most document
generators do this automatically for you.\n- Put string literals in code font, and enclose them in double quotation marks.
For example, XML attribute values might be "wrap_content" or "true".\n- Make sure that the spelling of a class name in documentation matches the
spelling in code, with capital letters and no spaces (for example,
ActionBar).

Don't make class names plural (Intents, Activities); instead, add a
plural noun (Intent objects, Activity instances). For more
information, see Plural product and feature
names.
However, if a class has a name that's a common term, you can refer to it
with the corresponding English word, in lowercase and not in code font
(activities, action bar).\n- Don't make class names plural (Intents, Activities); instead, add a
plural noun (Intent objects, Activity instances). For more
information, see Plural product and feature
names.\n- However, if a class has a name that's a common term, you can refer to it
with the corresponding English word, in lowercase and not in code font
(activities, action bar).\n\nOn each unique page (for a class, interface, etc.), include a code sample
(~5-20 lines) at the top.\n\nPut all API names, classes, methods, constants, and parameters in code font,
and link each name to the corresponding reference page. Most document
generators do this automatically for you.\n\nPut string literals in code font, and enclose them in double quotation marks.
For example, XML attribute values might be "wrap_content" or "true".\n\nMake sure that the spelling of a class name in documentation matches the
spelling in code, with capital letters and no spaces (for example,
ActionBar).\n\n- Don't make class names plural (Intents, Activities); instead, add a
plural noun (Intent objects, Activity instances). For more
information, see Plural product and feature
names.\n- However, if a class has a name that's a common term, you can refer to it
with the corresponding English word, in lowercase and not in code font
(activities, action bar).\n\nDon't make class names plural (Intents, Activities); instead, add a
plural noun (Intent objects, Activity instances). For more
information, see Plural product and feature
names.\n\nHowever, if a class has a name that's a common term, you can refer to it
with the corresponding English word, in lowercase and not in code font
(activities, action bar).\n\n\n## Classes, interfaces, structs\n\nIn the first sentence of a class description, briefly state the intended purpose
or function of the class or interface with information that can't be deduced
from the class name and signature. In additional documentation, elaborate on how
to use the API, including how to invoke or instantiate it, what some of the key
features are, and any best practices or pitfalls.\n\nMany documentation tools automatically extract the first sentence of each class
description for use in a list of all classes, so make the first sentence unique
and descriptive, yet short. Additionally:\n\n- Don't repeat the class name in the first sentence.\n- Don't say "this class will/does ..."\n- Don't use a period before the actual end of the sentence, because some
document generators naively terminate the "short description" at the first
period. For example, some generators terminate the sentence if they see
e.g., so use for example instead.\n\nDon't repeat the class name in the first sentence.\n\nDon't say "this class will/does ..."\n\nDon't use a period before the actual end of the sentence, because some
document generators naively terminate the "short description" at the first
period. For example, some generators terminate the sentence if they see
e.g., so use for example instead.\n\nThe following example is the first sentence of the description for Android's
ActionBar class:\n\n> A primary toolbar within the activity that may display the activity title,
application-level navigation affordances, and other interactive items.\n\nA primary toolbar within the activity that may display the activity title,
application-level navigation affordances, and other interactive items.\n\n\n## Members\n\nMake descriptions for members (constants and fields) as brief as possible. Be
sure to link to relevant methods that use the constant or field.\n\nFor example, here's the description for the ActionBar class's
DISPLAY_SHOW_HOME
constant:\n\n> Show 'home' elements in this action bar, leaving more space for other
navigation elements. This includes logo and icon.\n\nShow 'home' elements in this action bar, leaving more space for other
navigation elements. This includes logo and icon.\n\n> See also: setDisplayOptions(int), setDisplayOptions(int, int)\n\nSee also: setDisplayOptions(int), setDisplayOptions(int, int)\n\n\n## Methods\n\nIn the first sentence for a method description, briefly state what action the
method performs. In subsequent sentences, explain why and how to use the method,
state any prerequisites that must be met before calling it, give details about
exceptions that may occur, and specify any related APIs.\n\nDocument any dependencies (such as
Android permissions)
that are needed to call the method, and how the method behaves if such a
dependency is missing (for example, "the method throws a
SecurityException"
or "the method returns null").\n\nFor example, here's the description for Android's
Activity.isChangingConfigurations method:\n\n> Checks whether this activity is in the process of being destroyed in order to
be recreated with a new configuration. This is often used in onStop to
determine whether the state needs to be cleaned up or if it's passed on to the
next instance of the activity using onRetainNonConfigurationInstance.\n\nChecks whether this activity is in the process of being destroyed in order to
be recreated with a new configuration. This is often used in onStop to
determine whether the state needs to be cleaned up or if it's passed on to the
next instance of the activity using onRetainNonConfigurationInstance.\n\nUse present tense for all descriptions—for example:\n\n- Adds a new bird to the ornithology list.\n- Returns a bird.\n\nAdds a new bird to the ornithology list.\n\nReturns a bird.\n\n\n### Description\n\n- If a method performs an operation and returns some data, start the description
with a verb describing the operation—for example:

Adds a new bird to the ornithology list and returns the ID of the new
entry.\n- Adds a new bird to the ornithology list and returns the ID of the new
entry.\n- If it's a "getter" method and it returns a boolean, start with "Checks
whether ...."\n- If it's a "getter" method and it returns something other than a boolean,
start with "Gets the ...."\n- If it has no return value, start with a verb like one of the following:

Turning on an ability or setting: "Sets the ...."
Updating a property: "Updates the ...."
Deleting something: "Deletes the ...."
Registering a callback or other element for later reference:
"Registers ...."
For a callback: "Called by ...." (Usually for a method that's named
starting with "on", such as onBufferingUpdate.) For example, "Called by
Android when ...." Then, later in the description: "Subclasses implement this
method to ...."\n- Turning on an ability or setting: "Sets the ...."\n- Updating a property: "Updates the ...."\n- Deleting something: "Deletes the ...."\n- Registering a callback or other element for later reference:
"Registers ...."\n- For a callback: "Called by ...." (Usually for a method that's named
starting with "on", such as onBufferingUpdate.) For example, "Called by
Android when ...." Then, later in the description: "Subclasses implement this
method to ...."\n- If it's a convenience method that constructs the class object, start with
"Creates a ...."\n\nIf a method performs an operation and returns some data, start the description
with a verb describing the operation—for example:\n\n- Adds a new bird to the ornithology list and returns the ID of the new
entry.\n\nIf it's a "getter" method and it returns a boolean, start with "Checks
whether ...."\n\nIf it's a "getter" method and it returns something other than a boolean,
start with "Gets the ...."\n\nIf it has no return value, start with a verb like one of the following:\n\n- Turning on an ability or setting: "Sets the ...."\n- Updating a property: "Updates the ...."\n- Deleting something: "Deletes the ...."\n- Registering a callback or other element for later reference:
"Registers ...."\n- For a callback: "Called by ...." (Usually for a method that's named
starting with "on", such as onBufferingUpdate.) For example, "Called by
Android when ...." Then, later in the description: "Subclasses implement this
method to ...."\n\nTurning on an ability or setting: "Sets the ...."\n\nUpdating a property: "Updates the ...."\n\nDeleting something: "Deletes the ...."\n\nRegistering a callback or other element for later reference:
"Registers ...."\n\nFor a callback: "Called by ...." (Usually for a method that's named
starting with "on", such as onBufferingUpdate.) For example, "Called by
Android when ...." Then, later in the description: "Subclasses implement this
method to ...."\n\nIf it's a convenience method that constructs the class object, start with
"Creates a ...."\n\n\n### Parameters\n\nFor parameter descriptions, follow these guidelines:\n\n- Capitalize the first word, and end the sentence or phrase with a period.\n- Begin descriptions of non-boolean parameters with "The" or "A" if possible:

The ID of the bird you want to get.
A description of the bird.\n- The ID of the bird you want to get.\n- A description of the bird.\n- For boolean parameters that tell the API to do or not do something, state
what the API does if the parameter is true and if it's false. For example:

enableCertificateValidation: If true, validates the SSL certificate
before proceeding. If false, trusts the certificate without validating it.\n- enableCertificateValidation: If true, validates the SSL certificate
before proceeding. If false, trusts the certificate without validating it.\n- For boolean parameters that declare the already-established state of something
(rather than telling the API to do something), use the format "True if ...;
false otherwise." For example:

True if the zoom is set; false otherwise.\n- True if the zoom is set; false otherwise.\n- In this context, don't put the words "true" and "false" in code font or
quotation marks.\n- For parameters with default behavior, explain what the behavior is for each
value or range of values, and then say what the default value is. Use the
format Default: to explain the default value.\n\nCapitalize the first word, and end the sentence or phrase with a period.\n\nBegin descriptions of non-boolean parameters with "The" or "A" if possible:\n\n- The ID of the bird you want to get.\n- A description of the bird.\n\nThe ID of the bird you want to get.\n\nA description of the bird.\n\nFor boolean parameters that tell the API to do or not do something, state
what the API does if the parameter is true and if it's false. For example:\n\n- enableCertificateValidation: If true, validates the SSL certificate
before proceeding. If false, trusts the certificate without validating it.\n\nFor boolean parameters that declare the already-established state of something
(rather than telling the API to do something), use the format "True if ...;
false otherwise." For example:\n\n- True if the zoom is set; false otherwise.\n\nIn this context, don't put the words "true" and "false" in code font or
quotation marks.\n\nFor parameters with default behavior, explain what the behavior is for each
value or range of values, and then say what the default value is. Use the
format Default: to explain the default value.\n\n\n### Return values\n\nBe as brief as possible in the return value's description; put any detailed
information in the class description.\n\n- If the return value is anything other than a boolean, start with "The ..."—for
example:

The bird specified by the given ID.\n- The bird specified by the given ID.\n- If the return value is a boolean, use the format "True if ...; false
otherwise."—for example:

True if the bird is in the sanctuary; false otherwise.\n- True if the bird is in the sanctuary; false otherwise.\n\nIf the return value is anything other than a boolean, start with "The ..."—for
example:\n\n- The bird specified by the given ID.\n\nIf the return value is a boolean, use the format "True if ...; false
otherwise."—for example:\n\n- True if the bird is in the sanctuary; false otherwise.\n\n\n### Exceptions\n\nIn languages where the reference generator automatically inserts the word
"Throws", begin your description with "If ...":\n\n- If no key is assigned.\n\nOtherwise, begin with "Thrown when ...":\n\n- Thrown when no key is assigned.\n\n\n### Deprecations\n\nWhen something is deprecated, tell the user what to use as a replacement. (If
you track your API with version numbers, mention which version it was first
deprecated in.)\n\nOnly the first sentence of a description appears in the summary section and
index, so put the most important information there. Subsequent sentences can
explain why it was deprecated, along with any other information that's useful
for a developer using your API.\n\nIf a method is deprecated, tell the reader what to do to make their code work.\n\n\n#### Examples\n\n> Deprecated. Use #CameraPose instead.\n\nDeprecated. Use #CameraPose instead.\n\n> Deprecated. Access this field using the getField method.\n\nDeprecated. Access this field using the getField method.\n