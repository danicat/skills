Source: https://developers.google.com/style/placeholders\n\n# Format placeholders


      
      Stay organized with collections
    

      
      Save and categorize content based on your preferences.\n\n- Home\n- Products\n- Style\n\n\n## Page Summary\n\n- This page provides guidance on formatting placeholders within commands, code samples, and text strings for Google developer documentation.\n- Placeholders represent values that readers need to replace when using code samples or indicate variable values in example output.\n- Specific formatting rules are outlined for placeholders in inline text, code blocks, and general text, emphasizing clear and descriptive naming conventions.\n- The document also details how to effectively explain placeholders to readers, including providing context and descriptions for each placeholder used.\n- Guidelines for handling placeholders in output examples are provided, ensuring clarity and understanding of the presented information.\n\nThis page provides guidance on formatting placeholders within commands, code samples, and text strings for Google developer documentation.\n\nPlaceholders represent values that readers need to replace when using code samples or indicate variable values in example output.\n\nSpecific formatting rules are outlined for placeholders in inline text, code blocks, and general text, emphasizing clear and descriptive naming conventions.\n\nThe document also details how to effectively explain placeholders to readers, including providing context and descriptions for each placeholder used.\n\nGuidelines for handling placeholders in output examples are provided, ensuring clarity and understanding of the presented information.\n\nThis page explains how to format placeholders in commands, code samples, and text
strings. This page doesn't explain how to implement visual styling for placeholders, but it does
show examples of how Google developer documentation style renders placeholders as visually
distinct from other text.\n\nFor more information about formatting code, command-line syntax, and code samples, see the
following links:\n\n- Code in text\n- Documenting command-line syntax\n- Code samples\n\nPlaceholders in sample code and commands represent values that the reader must replace when they use
the sample input. Placeholders in example output can also represent other values that vary. In
general, a placeholder has a descriptive name as a default value.\n\nFor example, the placeholder PROJECT_ID represents a project ID in sample
code, commands, and example output.\n\nIn example output, the placeholder HTTP_RESPONSE_CODE represents an
  HTTP response code; the reader isn't expected to set this to a specific value.\n\n\n## Placeholders\n\nWhen you create placeholders follow this general guidance around using the letter
x:\n\n- In general, don't use a single x or a series of x's as placeholders; use a more
    informative placeholder.\n- In some contexts (such as HTTP status codes), a series of x's is the standard,
      so it's OK to use (for example) xx in those cases.\n\nThere are several ways to format placeholders, depending on whether you're
  working in HTML or Markdown, or whether the placeholder is inline, in a code block, or in a
  paragraph. For details, see the following sections.\n\n\n### Placeholders in inline text\n\nIf your sample code and command placeholders occur in a sentence, use the following formatting:\n\n- In HTML, wrap variable placeholders by using the var
     element, like this:
<code><var>PLACEHOLDER_NAME</var></code>\n- In Markdown, wrap inline placeholders in backticks (`), and use an
asterisk (*) before the first backtick and after the second one
(*`PLACEHOLDER_NAME`*).\n\nIn HTML, wrap variable placeholders by using the var
     element, like this:\n\n```\n<code><var>PLACEHOLDER_NAME</var></code>\n```\n\nIf your placeholder does not represent a code sample or command, use the following formatting:\n\n- In HTML, wrap placeholders by using the var
     element, like this:
<var>PLACEHOLDER_NAME</var>\n\nIn HTML, wrap placeholders by using the var
     element, like this:\n\n```\n<var>PLACEHOLDER_NAME</var>\n```\n\n\n### Placeholders in code blocks\n\nIf your placeholders are in a block of code, use the following formatting:\n\n- In HTML, wrap the code block in a pre element,
        and tag placeholders with var elements:

      <pre>
      gcloud compute forwarding-rules create <var>FORWARDING_RULE_NAME</var> \
          --global | --region=<var>REGION</var> \
          --load-balancing-scheme=<var>LOAD_BALANCING_SCHEME</var> \
          --network=<var>NETWORK</var> \
          ...
      </pre>\n- In Markdown, wrap the code block in a code fence (```). Inside a
code fence, you can't apply formatting like bold or italic.
      
```
PLACEHOLDER_NAME
```\n\nIn HTML, wrap the code block in a pre element,
        and tag placeholders with var elements:\n\n```\n<pre>
      gcloud compute forwarding-rules create <var>FORWARDING_RULE_NAME</var> \
          --global | --region=<var>REGION</var> \
          --load-balancing-scheme=<var>LOAD_BALANCING_SCHEME</var> \
          --network=<var>NETWORK</var> \
          ...
      </pre>\n```\n\n```\n```
PLACEHOLDER_NAME
```\n```\n\n\n### Placeholder text\n\nUse uppercase characters with underscore delimiters.\n\nFor example, in HTML:\n\nRecommended:\n\n- .../<var>API_NAME</var>\n- .../<var>METHOD_NAME</var>\n\nNot recommended:\n\n- .../<var>API-name</var>\n- .../<var>API_name</var>\n- .../<var>API name</var>\n- .../<var>api_name</var>\n- .../<var>api-name</var>\n- .../<var>apiName</var>\n\nIn Markdown:\n\nRecommended:
    
.../*API_NAME*
.../*METHOD_NAME*\n\n- .../*API_NAME*\n- .../*METHOD_NAME*\n\nIf the context in which your placeholders appear makes using
uppercase characters with underscore delimiters a bad idea, use something else
that makes sense to you, but be internally consistent.\n\nDon't include possessive adjectives in placeholders.\n\nNot recommended:\n\n- .../<var>MY_API_NAME</var>\n- .../<var>YOUR_API_NAME</var>\n\n\n## Explain placeholders\n\nWhen you use a placeholder in text or code, explain the placeholder the first time you use it.
It's not necessary to repeat the explanation in the document unless doing so might benefit the
reader—for example, in circumstances such as the following:\n\n- Your document is lengthy.\n- You've introduced several other placeholders in a long procedure.\n- Your document isn't intended to be read from beginning to end.\n\nThe following is an example of a command that uses a placeholder with an explanation of that
placeholder:\n\n```\n<pre class="devsite-click-to-copy">
gcloud compute instances create <var>INSTANCE_NAME</var> \
    --metadata enable-guest-attributes=TRUE
</pre>

<p>Replace <code><var>INSTANCE_NAME</var></code> with the name that
you want your new VM instance to have.</p>\n```\n\n\n### Single placeholder\n\nUse the following format for a single placeholder:\n\n- Replace PLACEHOLDER with a description of what
the placeholder represents.\n\nRecommended:\n\n- Stream the build logs to the Google Cloud console:
gcloud builds log --stream=BUILD_ID
Replace BUILD_ID with the ID of the WORKING build that
      you copied in the preceding step.\n\nStream the build logs to the Google Cloud console:\n\n```\ngcloud builds log --stream=BUILD_ID\n```\n\nReplace BUILD_ID with the ID of the WORKING build that
      you copied in the preceding step.\n\n\n### Two or more placeholders\n\nUse the following format for two or more placeholders:\n\n- Follow the command line with a descriptive list of the placeholders
    used in the command line. Explain what each placeholder represents
    even if the placeholder value is intuitive to you.\n- Introduce this list with Replace the following:\n- List the placeholders in the order in which they appear in the command line.\n- Tag each placeholder in a code sample or command with code and
    var elements, followed by a
    colon and a description that starts with a lowercase letter.
    For
    non-code samples, remove the code elements—for example:
<li><code><var>INSTANCE_NAME</var></code>: description</li>\n- If the description contains an example, introduce it with an em dash or
    such as—for example:
    <li><code><var>INSTANCE_NAME</var></code>: description&mdash;for example,...</li>
<li><code><var>INSTANCE_NAME</var></code>: description, such as...</li>\n- Each item in the list follows our list style.\n\nTag each placeholder in a code sample or command with code and
    var elements, followed by a
    colon and a description that starts with a lowercase letter.
    For
    non-code samples, remove the code elements—for example:\n\n```\n<li><code><var>INSTANCE_NAME</var></code>: description</li>\n```\n\n```\n<li><code><var>INSTANCE_NAME</var></code>: description&mdash;for example,...</li>\n```\n\n```\n<li><code><var>INSTANCE_NAME</var></code>: description, such as...</li>\n```\n\nRecommended:\n\n- Set the maximum concurrency target for a new reservation:

    bq mk \
        --project_id=ADMIN_PROJECT_ID \
        --location=LOCATION \
        --target_job_concurrency=CONCURRENCY \
        --reservation \
        RESERVATION_NAME
Replace the following:

ADMIN_PROJECT_ID: the project that owns the reservation
LOCATION: the location of the reservation
CONCURRENCY: the maximum concurrency target
RESERVATION_NAME: the name of the reservation\n- ADMIN_PROJECT_ID: the project that owns the reservation\n- LOCATION: the location of the reservation\n- CONCURRENCY: the maximum concurrency target\n- RESERVATION_NAME: the name of the reservation\n\nSet the maximum concurrency target for a new reservation:\n\n```\nbq mk \
        --project_id=ADMIN_PROJECT_ID \
        --location=LOCATION \
        --target_job_concurrency=CONCURRENCY \
        --reservation \
        RESERVATION_NAME\n```\n\nReplace the following:\n\n- ADMIN_PROJECT_ID: the project that owns the reservation\n- LOCATION: the location of the reservation\n- CONCURRENCY: the maximum concurrency target\n- RESERVATION_NAME: the name of the reservation\n\nRecommended:\n\n- In Cloud Shell, set the environment variables:
export ONPREM_PROJECT=ON_PREM_PROJECT_NAME \
    export ONPREM_ZONE=ZONE
Replace the following:

ON_PREM_PROJECT_NAME: the Google Cloud project
name for your on-premises project. You can find your project number on the
Dashboard
page of the Google Cloud console.
ZONE: a Google Cloud
zone that's close to your location—for example, us-east1.\n- ON_PREM_PROJECT_NAME: the Google Cloud project
name for your on-premises project. You can find your project number on the
Dashboard
page of the Google Cloud console.\n- ZONE: a Google Cloud
zone that's close to your location—for example, us-east1.\n\nIn Cloud Shell, set the environment variables:\n\n```\nexport ONPREM_PROJECT=ON_PREM_PROJECT_NAME \
    export ONPREM_ZONE=ZONE\n```\n\nReplace the following:\n\n- ON_PREM_PROJECT_NAME: the Google Cloud project
name for your on-premises project. You can find your project number on the
Dashboard
page of the Google Cloud console.\n- ZONE: a Google Cloud
zone that's close to your location—for example, us-east1.\n\n\n### Placeholders in output\n\nIf you provide a code output example, explain any placeholders that appear in
sample output:\n\n- Use var elements to identify the placeholder text in
the output.\n- Follow the example output with a list of the placeholders used in the
example.\n- Introduce the list of placeholders with This output includes the
    following values:\n- List the placeholders in the order in which they appear in the
example.\n- Tag each placeholder with a var element,
    followed by a colon and a description that starts with a lowercase letter—for example:
<li><code><var>INSTANCE_NAME</var></code>: description</li>\n- If the description contains an example, introduce it with an em dash or
    such as—for example:
    <li><code><var>INSTANCE_NAME</var></code>: description&mdash;for example,...</li>
<li><code><var>INSTANCE_NAME</var></code>: description, such as...</li>\n\nTag each placeholder with a var element,
    followed by a colon and a description that starts with a lowercase letter—for example:\n\n```\n<li><code><var>INSTANCE_NAME</var></code>: description</li>\n```\n\n```\n<li><code><var>INSTANCE_NAME</var></code>: description&mdash;for example,...</li>\n```\n\n```\n<li><code><var>INSTANCE_NAME</var></code>: description, such as...</li>\n```\n\nFor more information, see Output from commands.\n\nRecommended:\n\n\n#### Response\n\nThe output is similar to the following:\n\n```\n{
 "name": "operations/build/PROJECT_ID/OPERATION_ID",
 "metadata": {
  "@type": "type.googleapis.com/google.devtools.cloudbuild.v1.BuildOperationMetadata",
  "build": {
   "id": "BUILD_ID",
   "status": "QUEUED",
   "createTime": "2019-09-20T15:55:29.353258929Z",
   "steps": [
    {
     "name": "gcr.io/compute-image-tools/gce_vm_image_import:release",
     "env": [
      "BUILD_ID=BUILD_ID"
     ],
     "args": [
      "-timeout=7056s",
      "-image_name=IMAGE_NAME",
      "-client_id=api",
      "-data-disk",
      "-source_file=SOURCE_FILE"
     ]
    }
   ],
   "timeout": "7200s",
   "projectId": "PROJECT_ID",
   "logsBucket": "gs://PROJECT_NUMBER.cloudbuild-logs.googleusercontent.com",
   "options": {
    "logging": "LEGACY"
   },
   "logUrl": "https://console.cloud.google.com/gcr/builds/BUILD_ID?project=PROJECT_NUMBER"
  }
 }
}\n```\n\nThis output includes the following values:\n\n- PROJECT_ID: the project ID for the project that
  the image was imported into\n- OPERATION_ID: the ID of the import operation\n- BUILD_ID: the ID of the build for the import
  operation\n- IMAGE_NAME: the name of the image to be
  imported\n- SOURCE_FILE: the URI for the image in Cloud
  Storage—for example, gs://my-bucket/my-image.vmdk\n- PROJECT_NUMBER: the number for the import
  project\n