Source: https://developers.google.com/style/code-in-text\n\n# Code in text


      
      Stay organized with collections
    

      
      Save and categorize content based on your preferences.\n\n- Home\n- Products\n- Style\n\n\n## Page Summary\n\n- Code font is used for verbatim text entry, boundary demarcation, and entity separation in technical documentation for clarity and readability.\n- Specific items to use code font for include attribute names, class names, command output, data types, database elements, filenames, and more, as detailed in the provided table.\n- Items to avoid using code font for are domain names, IP addresses, product or service names, and URLs for browser navigation.\n- Conditional code font usage applies to Boolean values, command-line utility names, and email addresses depending on context and usage.\n- Specific formatting and grammatical considerations exist for code font usage in technical documentation, including method names, HTTP status codes, and UI elements, to ensure consistency and clarity.\n\nCode font is used for verbatim text entry, boundary demarcation, and entity separation in technical documentation for clarity and readability.\n\nSpecific items to use code font for include attribute names, class names, command output, data types, database elements, filenames, and more, as detailed in the provided table.\n\nItems to avoid using code font for are domain names, IP addresses, product or service names, and URLs for browser navigation.\n\nConditional code font usage applies to Boolean values, command-line utility names, and email addresses depending on context and usage.\n\nSpecific formatting and grammatical considerations exist for code font usage in technical documentation, including method names, HTTP status codes, and UI elements, to ensure consistency and clarity.\n\nIn ordinary text sentences (as opposed to, say, code samples),
  use code font to mark up most things that have anything to do with code. Code
  font helps to clarify for your reader which text refers to an entity in these
  ways:\n\n- Signals to your reader that the text is meant to be entered
      verbatim.\n- Shows where the boundaries of the text to enter are.\n- Clearly separates the entity from surrounding text.\n\nTo mark text as code font, use the following:\n\n- In HTML, use the code element.\n- In Markdown, use backticks (`).\n\nFor information about choosing HTML or Markdown, see
  Markdown versus HTML.\n\nThis page explains how to format code in ordinary text sentences. For more information about
  formatting and explaining placeholders, command-line syntax, and code samples, see the following
  resources:\n\n- Formatting placeholders\n- Documenting command-line syntax\n- Code samples\n- Code style guides\n- Formatting a heading or title\n\n\n## Some specific items to put in code font\n\nThe following table includes items that should be in code font, but it's not an exhaustive
  list:\n\n\nItem | Recommended\nAttribute names and values | The imageURL attribute contains the path for the image file that you can open
        in a browser—for example,
        https://www.example.com/images/product.jpg.
You can create a VM instance using the e2-highcpu-16 machine type in the
        us-central1-a region.\nClass names | The SnapshotDiskOperator class includes the
        generate_snapshot_name method.\nCommand output | The output is similar to the following:

        Found sysprep-specialize-script-ps1 in metadata.
        ...
        Finished running specialize scripts.\nCommand-line utility names, such as gcloud,
        gsutil, kubectl, and bq | You can use the kubectl tool to define a network policy.\nData types | Nested data is represented as a STRUCT type.\nDatabase elements (such as row and column names) | The query extracts the month, julianday, and
        dayofweek values from the datetime and timestamp
        columns.\nDefined (constant) values for an element or attribute | The constant city has the value "San Francisco".\nDNS
        record types | Create a DNS AAAA record in your public DNS zone that points to
        the IP address of the load balancer.\nElement names (HTML and XML) | The script and df-messenger HTML elements
          should be in the body element of your page.
A C-CDA document contains a header and a body enclosed within a
          ClinicalDocument XML element.
When you refer to an element name, don't put angle brackets
          (<>) around the element name.\nEnum (enumerator) names | Generated from the protobuf enum BOOL = 1;.\nEnvironment variable names | Set the CHROME_REMOTE_DESKTOP_DEFAULT_DESKTOP_SIZES environment variable to
        include the resolution of your monitor.\nFilenames, filename extensions (if used),
        and paths | Open the pg_hba.conf file, which is typically in the
        /etc/postgresql/13/main directory.\nFolders and directories | The configuration information for the reader deployment is in the
        opentsdb-read.yaml.tpl file in the deployments folder of the guide
        repository.\nHTTP content-type
        values | The value of the Content-Type header value is required and must be set
        to application/fhir+json as defined in the FHIR specification.\nHTTP status codes | The HTTP 500 Internal Server Error status code indicates that the server
          encountered an unexpected condition that prevented it from fulfilling the
          request.\nHTTP verbs | To specify image content directly using a local image file, you can use a
        POST request.\nIAM role names | Grant the new service account the roles/cloudfunctions.invoker IAM role
        for the trace function.\nIP addresses | The other nodes of the cluster should contact this host on IP address
        10.10.10.10.\nLanguage keywords | The SQL statement contains the dataset table name after the FROM keyword in
        the format of
        PROJECT_NAME.DATASET.TABLE_NAME.\nMethod and function names | The ST_GEOPOINT function uses the longitude and latitude of
        the Colosseum in Rome.
To fetch the status of the job, call the get_job_status method.\nNamespace aliases | Use Config Sync to apply the package only to the default namespace.\nPlaceholder variables | Replace SUBNETWORK_NAME with the resource ID of the private subnet
        that you want the blueprint to use.\nPackage names | The Beautiful Soup library for parsing web pages is distributed as the
        beautifulsoup4 package.\nPort numbers | Each member Pod must have a container that's listening on TCP port
        50000.\nQuery parameter names and values | If you want to return all contents under a directory, use the
        recursive=true query parameter with your request.\nStrings (such as URLs or domain names) that are used in commands and code | In IAM, a condition can specify a page that only Human Resources admins can
        access—for example, https://hr.example.com.
The logID field includes the domain
          corpaudits.example.com.\nText input | In the Key name field, enter config-management.\nUI elements that are rendered based on previously
        entered text (such as a server or instance name) | From the Server name list, select my-sql-cluster1.
Click my-instance.
If a code-formatted element appears in UI, add bold as well. For more
        information, see
        Code in UI elements.\n\nThe imageURL attribute contains the path for the image file that you can open
        in a browser—for example,
        https://www.example.com/images/product.jpg.\n\nYou can create a VM instance using the e2-highcpu-16 machine type in the
        us-central1-a region.\n\nThe output is similar to the following:\n\n```\nFound sysprep-specialize-script-ps1 in metadata.
        ...
        Finished running specialize scripts.\n```\n\nThe script and df-messenger HTML elements
          should be in the body element of your page.\n\nA C-CDA document contains a header and a body enclosed within a
          ClinicalDocument XML element.\n\nWhen you refer to an element name, don't put angle brackets
          (<>) around the element name.\n\nGrant the new service account the roles/cloudfunctions.invoker IAM role
        for the trace function.\n\nThe ST_GEOPOINT function uses the longitude and latitude of
        the Colosseum in Rome.\n\nTo fetch the status of the job, call the get_job_status method.\n\nStrings (such as URLs or domain names) that are used in commands and code\n\nIn IAM, a condition can specify a page that only Human Resources admins can
        access—for example, https://hr.example.com.\n\nThe logID field includes the domain
          corpaudits.example.com.\n\nFrom the Server name list, select my-sql-cluster1.\n\nClick my-instance.\n\nIf a code-formatted element appears in UI, add bold as well. For more
        information, see
        Code in UI elements.\n\nGenerally, don't put quotation marks around code unless the quotation marks
are part of the code.\n\n\n## Items to put in ordinary (non-code) font\n\nThe following table includes items that should not be in code font, but it's
  not an exhaustive list. If you're referring to any of these items as computer input or output,
  or as a code entity like an attribute or value, then use code font.\n\n\nItem | Recommended\nDomain names | The test environment is designed only for standard application offerings from
        example.com.\nNames of products, services, and organizations | Example Organization has current and former employees who use Google products such as
        Google Docs and Google Sheets.\nURLs that the reader is supposed to follow in a browser | You can find support at https://support.example.com.
It's usually best to format a URL as a link and use descriptive link text
          instead of exposing the URL itself. For more information, see
          Avoid URLs as link text.\n\nYou can find support at https://support.example.com.\n\nIt's usually best to format a URL as a link and use descriptive link text
          instead of exposing the URL itself. For more information, see
          Avoid URLs as link text.\n\n\n## Code in UI elements\n\nIf a
UI element
meets the
requirements for code font,
then use both code font and bold for that element.\n\nRecommended: In the Network list, select
      my-net-2.\n\nRecommended: In the Query results pane,
      the Store column is displayed.\n\n\n## Items that are sometimes in code font\n\nThe following list includes items that are sometimes in code font, but it's not an exhaustive
  list.\n\n- Boolean values. If you refer directly to a Boolean data type value (such
    as true or false, or 1 or 0), then format
    the value as code. If you refer to the evaluation of a Boolean condition as true or
    false, then refer to the evaluation in non-code font.

Recommended:
        
If the update succeeds, returns true.
enableCertificateValidation: If true, validates the SSL certificate
            before proceeding. If false, trusts the certificate without validating it.\n- If the update succeeds, returns true.\n- enableCertificateValidation: If true, validates the SSL certificate
            before proceeding. If false, trusts the certificate without validating it.\n- Command-line utility names. Often, command-line utility names are spelled the same
    as the software project or product with which they are associated, with only differences in
    capitalization. In such cases, use code font for the command and ordinary font for the name of
    the project or product.

Recommended:

Invoke the GCC 8.3 compiler using gcc for C programs or
      g++ for C++ programs.
To send the file over FTP with IPv6, use ftp -6.
The options for the curl command are explained on the
              curl project website.
The apt program includes commands from the apt-get
            and apt-cache programs for working with APT packages.\n- Invoke the GCC 8.3 compiler using gcc for C programs or
      g++ for C++ programs.\n- To send the file over FTP with IPv6, use ftp -6.\n- The options for the curl command are explained on the
              curl project website.\n- The apt program includes commands from the apt-get
            and apt-cache programs for working with APT packages.\n- Email addresses as input or output. If you want the reader to use the email address
    as computer input or output, use code font. If you want the reader to treat the email address as
    a way to contact someone or a reference to someone, use non-code font and hyperlink the email
    address.

Recommended:
        
Enter the username, not the full email address. For example, enter alex,
            not alex@example.com.
For help, contact support@example.com.\n- Enter the username, not the full email address. For example, enter alex,
            not alex@example.com.\n- For help, contact support@example.com.\n\nBoolean values. If you refer directly to a Boolean data type value (such
    as true or false, or 1 or 0), then format
    the value as code. If you refer to the evaluation of a Boolean condition as true or
    false, then refer to the evaluation in non-code font.\n\nRecommended:
        
If the update succeeds, returns true.
enableCertificateValidation: If true, validates the SSL certificate
            before proceeding. If false, trusts the certificate without validating it.\n\n- If the update succeeds, returns true.\n- enableCertificateValidation: If true, validates the SSL certificate
            before proceeding. If false, trusts the certificate without validating it.\n\nCommand-line utility names. Often, command-line utility names are spelled the same
    as the software project or product with which they are associated, with only differences in
    capitalization. In such cases, use code font for the command and ordinary font for the name of
    the project or product.\n\nRecommended:\n\n- Invoke the GCC 8.3 compiler using gcc for C programs or
      g++ for C++ programs.\n- To send the file over FTP with IPv6, use ftp -6.\n- The options for the curl command are explained on the
              curl project website.\n- The apt program includes commands from the apt-get
            and apt-cache programs for working with APT packages.\n\nEmail addresses as input or output. If you want the reader to use the email address
    as computer input or output, use code font. If you want the reader to treat the email address as
    a way to contact someone or a reference to someone, use non-code font and hyperlink the email
    address.\n\nRecommended:
        
Enter the username, not the full email address. For example, enter alex,
            not alex@example.com.
For help, contact support@example.com.\n\n- Enter the username, not the full email address. For example, enter alex,
            not alex@example.com.\n- For help, contact support@example.com.\n\n\n## Method names\n\nWhen you refer to a method name in text, omit the class name except where
including it would prevent ambiguity.\n\nRecommended: To retrieve the zebra's
      metadata, call its get method.\n\nNot recommended: To retrieve the zebra's
      metadata, call its animal.get method.\n\n\n## HTTP status codes\n\nTo refer to a single status code, use the following formatting and
phrasing:\n\nan HTTP 400 Bad Request status code\n\nIn particular, call it a status code instead of a response
code or error code, and put the number and the name in code font.
If the HTTP is implicit from context, you can leave it out.\n\nTo refer to a range of codes, use the following form:\n\nan HTTP 2xx or 400 status code\n\nIn particular, use Nxx (with a specific digit in place of
N) to indicate anything in the N00-N99
range, and put the status code number in code font even if you're leaving
out the code's name.\n\nIf you prefer to specify an exact range, you can do so:\n\nan HTTP status code in the 200-299
range\n\nHere, too, put the numbers in code font.\n\n\n## Grammatical treatment of code elements\n\nIn general, don't use code elements such as keywords and filenames as if they were
English verbs or nouns. Don't inflect the name of a code element, such as to make it
plural or possessive. Instead, include a noun after the name of the code element, and
inflect that noun.\n\n\nRecommended | Not recommended\nThe ADDRESS constant's value is defined in the settings.h file. | ADDRESS's value is defined in settings.h.\nTo add the data, send a POST request. | POST the data.\nTo retrieve the data, send a GET request. | Retrieve information by GETting the data.\nYou can't close the file before opening it.
You can't call the close method for a file before you call
            open. | Closeing the file requires you to have opened it first.\nTakes an array of extended ASCII code points (an array of INT64 values)
        and returns BYTES values.
For STRING arguments, returns the original string with all alphabetic
            characters in uppercase. | Takes an array of extended ASCII code points (ARRAY of INT64) and returns BYTES.\n\nYou can't close the file before opening it.\n\nYou can't call the close method for a file before you call
            open.\n\nTakes an array of extended ASCII code points (an array of INT64 values)
        and returns BYTES values.\n\nFor STRING arguments, returns the original string with all alphabetic
            characters in uppercase.\n\n\n## Linking API terms in Android\n\nWhen you're writing code comments that you'll turn into generated reference
documentation, link to the first instance of each element of Android APIs, such as classes, methods,
constants, and XML attributes. Use code font and regular HTML
a elements to link to this reference material.
For later uses of the same API element in the same section, use code font
but do not link to the reference documentation.\n\nLink AndroidManifest.xml elements and attributes to the API
guide pages. Link the attribute for a particular widget or layout to its Javadoc
in the widget or layout's API reference entry.\n\nRecommended:\n\n```\n<a href="/guide/topics/manifest/data-element.html">data</a>\n```\n\nVery common classes such as Activity and Intent
don't need to be linked every time. If you use a term as a concept rather than a
class, then don't put it in code font and don't capitalize it. Here are some
objects that do not always require Javadoc links or capitalization:\n\n- activity, activities\n- service\n- fragment\n- view\n- loader\n- action bar\n- intent\n- content provider\n- broadcast receiver\n- app widget\n\nIf you use one of these terms in the context of referring to an actual
instance, use the formal class name and link to its reference page. Here are two
examples:\n\nRecommended: The Activity
class is an important part of an application's overall lifecycle...\n\nRecommended: The user interface for an
activity is provided by a hierarchy of views—objects derived from the

View class.\n\nTo link to a class or method:\n\n- To link to a class, use the class name as link text—for example:
<a href="/reference/android/widget/TextView">TextView</a>\n- To link to a method, use the method name as a fragment identifier. If
you're linking to a static method, also include the class name in the link
text. If you need to distinguish between overloaded versions of a particular
method, consider showing the full signature—for example:
<a href="/reference/android/app/Activity.html#onCreate(android.os.Bundle)">onCreate(Bundle)</a>\n- To link the attribute for a particular widget or layout to its Javadoc
in the widget or layout's API reference entry, use the URL for the page, and
then add the fragment identifier
#attr_android:ATTRIBUTE_NAME. For example, to link to
the XML attribute android:inputType for the TextView
widget, add the following:
<a href="/reference/android/widget/TextView.html#attr_android:inputType>inputType</a>\n\nTo link to a class, use the class name as link text—for example:\n\n```\n<a href="/reference/android/widget/TextView">TextView</a>\n```\n\nTo link to a method, use the method name as a fragment identifier. If
you're linking to a static method, also include the class name in the link
text. If you need to distinguish between overloaded versions of a particular
method, consider showing the full signature—for example:\n\n```\n<a href="/reference/android/app/Activity.html#onCreate(android.os.Bundle)">onCreate(Bundle)</a>\n```\n\nTo link the attribute for a particular widget or layout to its Javadoc
in the widget or layout's API reference entry, use the URL for the page, and
then add the fragment identifier
#attr_android:ATTRIBUTE_NAME. For example, to link to
the XML attribute android:inputType for the TextView
widget, add the following:\n\n```\n<a href="/reference/android/widget/TextView.html#attr_android:inputType>inputType</a>\n```\n