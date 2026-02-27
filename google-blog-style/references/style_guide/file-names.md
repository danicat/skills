Source: https://developers.google.com/style/file-names\n\n# Filenames and file types


      
      Stay organized with collections
    

      
      Save and categorize content based on your preferences.\n\n- Home\n- Products\n- Style\n\n\n## Page Summary\n\n- Use lowercase, hyphens, and standard ASCII characters for file and directory names for better search engine optimization and compatibility across operating systems.\n- Prioritize consistency with existing naming conventions within a directory when adding new files, even if it means deviating from the general guidelines.\n- When referencing files, use code font, include the word "file", and maintain the exact spelling of the filename.\n- When discussing file types, use their formal names instead of filename extensions (e.g., "PNG file" instead of ".png file").\n\nUse lowercase, hyphens, and standard ASCII characters for file and directory names for better search engine optimization and compatibility across operating systems.\n\nPrioritize consistency with existing naming conventions within a directory when adding new files, even if it means deviating from the general guidelines.\n\nWhen referencing files, use code font, include the word "file", and maintain the exact spelling of the filename.\n\nWhen discussing file types, use their formal names instead of filename extensions (e.g., "PNG file" instead of ".png file").\n\n\n## Guidelines for names\n\nMake file and directory names lowercase, with the occasional exception for consistency, to make file searches easier and search results more useful. For example, because most Unix-style operating systems are case sensitive, they can't find a file named Impersonate-Service-Accounts.html if you search for impersonate-service-accounts.html. Linux and macOS interpret these as two distinct files.\n\nUse hyphens, not underscores, to separate words—for example,
query-data.html. Search engines interpret hyphens in file and directory names as spaces between words. Underscores are generally not recognized, meaning that their presence can negatively affect SEO.\n\nUse only standard ASCII
  alphanumeric characters in file and directory names.\n\nDon't use generic page names such as document1.html.\n\n\n### Exceptions for consistency\n\nIf you're adding to a directory where everything else already uses
underscores, and it's not feasible to change everything to hyphens, it's okay to
use underscores to stay consistent.\n\nFor example, if the directory already has lesson_1.jd,
lesson_2.jd, and lesson_3.jd, it's okay to add your
new file as lesson_4.jd instead of lesson-4.jd.
However, in all other situations, use hyphens.\n\nRecommended: avoiding-cliches.jd\n\nSometimes OK: avoiding_cliches.jd\n\nNot recommended: avoidingcliches.jd\n\nNot recommended: avoidingCliches.jd\n\nNot recommended: avoiding-clichés.jd\n\n\n### Other exceptions\n\nIt's okay to have some inconsistency in filenames if it can't otherwise be
avoided. For example, sometimes tools that generate reference documentation
produce filenames based on different style requirements or based on the design
and naming conventions of the product or API itself. In those cases, it's okay
to make exceptions for those files.\n\n\n## Refer to files\n\nThe following sections discuss how to reference files.\n\n\n### Refer to filenames\n\nWhen referring to a specific file, do the following:\n\n- Use code font.\n- Include the word file after the filename. For more information, see
Grammatical treatment of code elements.\n- Use the exact spelling of the filename even if it doesn't follow
naming guidelines.\n- If a sample of the file is included on the page, follow the
code sample
guidelines and precede a code sample with an introductory sentence or paragraph that includes the
filename.\n\nRecommended: In the following
  build.sh file, modify the default values for all parameters:\n\n\n### Refer to file interactions\n\nWhen interacting with files and file types, don't use the file types as a verb.\n\nRecommended: Extract a zip file.\n\nNot recommended: Unzip a zip file.\n\n\n### Refer to file types\n\nWhen you're discussing a file type, use the formal name of the type, not the filename extension.
(The file type name is often in all caps because many file type names are acronyms
or initialisms.) Do not use the filename extension to refer generically to the
file type.\n\nRecommended: a PNG file\n\nNot recommended: a .png
file\n\nRecommended: a Bash file\n\nNot recommended: an .sh
file\n\nThe following table lists some examples of filename extensions and the
corresponding file type names to use.\n\n\nExtension | File type name\n.adoc | AsciiDoc file\n.csv | CSV file\n.exe | executable file\n.gif | GIF file\n.img | disk image file\n.ipynb | IPYNB file\n.jar | JAR file\n.jpg, .jpeg | JPEG file\n.json | JSON file\n.md | Markdown file\n.pdf | PDF file\n.png | PNG file\n.ps | PowerShell file\n.py | Python file\n.sh | Bash file\n.sql | SQL file\n.svg | SVG file\n.tar | tar file\n.tf | Terraform file\n.tiff | TIFF file\n.txt | text file\n.wasm | Wasm file\n.yaml | YAML file\n.zip | zip file\n