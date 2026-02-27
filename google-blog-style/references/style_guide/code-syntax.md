Source: https://developers.google.com/style/code-syntax\n\n# Document command-line syntax


      
      Stay organized with collections
    

      
      Save and categorize content based on your preferences.\n\n- Home\n- Products\n- Style\n\n\n## Page Summary\n\n- This document provides best practices for documenting command-line commands, focusing on clarity and user experience.\n- It emphasizes clear formatting, including code blocks, line breaks, placeholders, and punctuation, for easy readability.\n- It outlines how to handle optional, mutually exclusive, and repeating arguments, recommending simplification for click-to-copy examples.\n- The guide details how to present command prompts, input/output, and command-line terminology for consistency.\n- It offers specific recommendations for handling output from commands, including selective inclusion and introductory phrases.\n\nThis document provides best practices for documenting command-line commands, focusing on clarity and user experience.\n\nIt emphasizes clear formatting, including code blocks, line breaks, placeholders, and punctuation, for easy readability.\n\nIt outlines how to handle optional, mutually exclusive, and repeating arguments, recommending simplification for click-to-copy examples.\n\nThe guide details how to present command prompts, input/output, and command-line terminology for consistency.\n\nIt offers specific recommendations for handling output from commands, including selective inclusion and introductory phrases.\n\nThis page shows how to document command-line commands and their arguments. For more
information about formatting code that appears in text, placeholders, and code samples, see the
following links:\n\n- Code in text\n- Formatting placeholders\n- Code samples\n\n\n## Best practices\n\nWhen you write procedural or conceptual documentation for a command-line command, apply the
  following best practices:\n\n- Provide an inline link to the command reference. A good place for that link is in
    the text that introduces the command or a series of steps.

Recommended:
To connect to the instance, use the
    
gcloud compute ssh command:
gcloud compute ssh\n- Determine which arguments are needed to complete each task in the recommended way.
    To minimize the number of options that you need to document in non-reference content, use as
    few optional arguments as possible. Rely on the command reference for the complete list of
    arguments.\n- Provide a click-to-copy command example that the reader doesn't need to edit after they
    copy it. If possible, include only runnable code and placeholder variables in the
    click-to-copy example.
Some command examples contain
      optional arguments,
      mutually exclusive arguments, or
      repeated arguments
      that are indicated by square brackets ([]), pipes (|),
      braces ({}), and ellipses (...). These characters can break
      commands if they're not first removed. For that reason, avoid using these
      arguments in click-to-copy examples.
For more information, see the
      Optional arguments in click-to-copy commands
      section of this document.\n\nProvide an inline link to the command reference. A good place for that link is in
    the text that introduces the command or a series of steps.\n\nRecommended:\n\nTo connect to the instance, use the
    
gcloud compute ssh command:\n\n```\ngcloud compute ssh\n```\n\nProvide a click-to-copy command example that the reader doesn't need to edit after they
    copy it. If possible, include only runnable code and placeholder variables in the
    click-to-copy example.\n\nSome command examples contain
      optional arguments,
      mutually exclusive arguments, or
      repeated arguments
      that are indicated by square brackets ([]), pipes (|),
      braces ({}), and ellipses (...). These characters can break
      commands if they're not first removed. For that reason, avoid using these
      arguments in click-to-copy examples.\n\nFor more information, see the
      Optional arguments in click-to-copy commands
      section of this document.\n\n\n## Format a command\n\nTo mark a block of code such as a lengthy command or a code sample, use the
following formatting:\n\n- In HTML, use the pre element.\n- In Markdown, use a code fence (```).\n\nTo format a command with multiple elements, do the following:\n\n- When a line exceeds 80 characters, you can safely add a line break before
some characters, such as a single hyphen, double hyphen, underscore, or
quotation marks. After the first line, indent each line by four spaces to vertically align each line
that follows a line break.\n- When you split a command line with a line break, each line except the
last line must end with the command-continuation character. Commands that don't
have the command-continuation character don't work.

Linux or Cloud Shell: A backslash typically preceded with a space
( \)
Windows: A caret preceded with a space ( ^)\n- Linux or Cloud Shell: A backslash typically preceded with a space
( \)\n- Windows: A caret preceded with a space ( ^)\n- Format placeholder text with placeholders.\n- Follow the command line with a descriptive list of the placeholders
used in the command line. For more information, see Explaining placeholders.\n- When documenting a command-line option or argument, use end puctuation for complete
  sentences. Don't use end punctuation for single words or noun phrases, unless there is a mix of
  sentences and noun phrases. This guidance is similar to end punctuation in lists.
  For more information, see Google AIP guidelines for documentation.\n\nWhen you split a command line with a line break, each line except the
last line must end with the command-continuation character. Commands that don't
have the command-continuation character don't work.\n\n- Linux or Cloud Shell: A backslash typically preceded with a space
( \)\n- Windows: A caret preceded with a space ( ^)\n\nWhen you're documenting a bash or sh command, follow the
  quotation mark style
  in Google's shell style guide.\n\n\n## Command prompt\n\nIf your command-line instructions show multiple lines of input in one block, then start each line
  of input with the prompt symbol. If you don't want users to copy the prompt symbol when they copy
the command, you might be able to turn off text selection for the symbol—for example, by using
CSS.\n\nDon't show the current directory path before the prompt, even if
part of the instruction includes changing directories. However, if the overall
context of the command interface changes—such as from the local machine
to a remote machine—then add an additional prompt indicator, as appropriate, for
the new context.\n\nRecommended:\n\nEnter the following code into the terminal:\n\n```\n$ adb devices\n```\n\nThe output is the following:\n\n```\nList of devices attached
emulator-5554  device
emulator-5556  device\n```\n\nRecommended:\n\n```\n$ adb shell
shell@ $ screencap /sdcard/screen.png
shell@ $ exit
$ adb pull /sdcard/screen.png\n```\n\nWhen you're showing a one-line command, the command prompt
(the $ symbol) is optional. However, if your document includes both
multi-line and one-line commands, then we recommend using the command prompt
for all of the commands in the document for consistency.\n\nIf your command-line instructions include a combination of input and output
lines, we recommend using separate code blocks for input and output.\n\nRecommended:\n\n```\n$ cat ~/.ssh/my-ssh-key.pub\n```\n\nThe output is similar to the following:\n\n```\nssh-rsa KEY_VALUE USERNAME\n```\n\n\n## Optional arguments\n\nUse square brackets around an argument to indicate that it's optional. If there's more than one
  optional argument, enclose each item in its own set of square brackets.\n\nAvoid using optional arguments in click-to-copy code examples. For best practices on documenting
  optional arguments with click-to-copy commands, see the
  Best practices and
  Optional arguments in click-to-copy commands
  sections of this document.\n\nIn the following example, GROUP is required, but
  GLOBAL_FLAG and FILENAME are optional:\n\n```\ngcloud dns GROUP [GLOBAL_FLAG] [FILENAME]\n```\n\n\n## Mutually exclusive arguments\n\nUse curly braces to indicate that the reader must choose one—and only one—of the
  items inside the braces. There can be more than two mutually exclusive choices. To separate each
  choice, use a pipe (|).\n\nAvoid using mutually exclusive arguments in click-to-copy code examples. For best practices on
  documenting mutually exclusive arguments with click-to-copy commands, see the
  Best practices and
  Optional arguments in click-to-copy commands
  sections of this document.\n\nIn the following example, choose either FILE_1 or FILE_2:\n\n```\n{FILE_1|FILE_2}\n```\n\nIn the following example, there are also two options:
    
Left side of pipe: If the source code is deployed from a cloud
        repository, the following is required:
--source=CLOUD_SOURCE --source-url=SOURCE_URL
Right side of pipe: If the source code is in a local directory:
        
--bucket=BUCKET is required.
--source=LOCAL_SOURCE is optional, as specified by the square
            brackets.




{--source=CLOUD_SOURCE --source-url=SOURCE_URL | --bucket=BUCKET [--source=LOCAL_SOURCE]}

Arguments that can repeat
Use three dots and no spaces (...) to indicate that the reader can specify multiple
  values for the argument.
Avoid using an ellipsis in click-to-copy code examples. For best practices on documenting optional
  arguments with click-to-copy commands, see the
  Best practices and
  Optional arguments in click-to-copy commands
  sections of this document.
In this example, the reader can specify multiple instances of the optional
parameter GLOBAL_FLAG:

gcloud dns GROUP [GLOBAL_FLAG ...]

Optional arguments in click-to-copy commands
Optional arguments,
  mutually exclusive arguments, and
  repeated arguments
  contain characters (such as square brackets, curly braces, pipes, and ellipses) that can break
  commands if the reader doesn't remove them. Avoid using these types of arguments in click-to-copy
  commands. Instead, choose one of the following approaches:

Remove the optional arguments. As a best practice,
    use only the necessary arguments
    to complete the task for the most common use case. If possible, remove optional arguments from
    the command; always provide a link to the command reference for the command, where readers can
    find the full list of options. For more information, check with product management or a
    technical support specialist for the most relevant arguments.

Recommended:
To get an aggregate list of all virtual machine (VM) instances in all zones for a project,
      use the
      
gcloud compute instances list command:
gcloud compute instances list
If you want to narrow the list of VMs to a specific zone, use the previous command with the
      --zones flag.


Use separate code blocks for each option. In some cases, it might be ideal to
    provide more than one click-to-copy code block within the same section.

Recommended:
To create a bootable Compute Engine image, use the
      
gcloud compute images import command:
gcloud compute images import IMAGE_NAME \
    --source-file=SOURCE_FILE
If you're importing an image with an existing license, specify the
      --byol flag:
gcloud compute images import IMAGE_NAME \
    --source-file=SOURCE_FILE \
    --byol


Document optional arguments in separate tasks. In some cases, it might be best to
    treat different options in separate sections.

Recommended:
To create a bootable or non-bootable Compute Engine image based on an existing virtual
      disk, use the
      gcloud compute images import command.
Import a bootable virtual disk
If your virtual disk has a bootable operating system installed on it, run the following
      command:
gcloud compute images import IMAGE_NAME \
    --source-file=SOURCE_FILE
Import a non-bootable virtual disk
If your virtual disk doesn't have a bootable operating system installed on it, include the
      --data-disk flag:
gcloud compute images import IMAGE_NAME \
    --source-file=SOURCE_FILE \
    --data-disk


Let the reader know that the command contains optional arguments. If you must
    include special characters to indicate optional arguments, indicate that fact when you
    introduce the command.

Recommended:
To create a VM with a custom name and attach one or more existing stateful disks to that VM,
      use the
      gcloud compute instance-groups managed create-instance command
      with one or multiple --stateful-disk flags. In the following example, you
      optionally specify the auto-delete subflag to keep or discard each disk when the
      VM is permanently deleted:
    
gcloud compute instance-groups managed create-instance NAME \
    --instance=VM_NAME \
    --stateful-disk=device-name=DEVICE_NAME,source=DISK[,auto-delete=DELETE_RULE]
For example, the following command creates a managed instance that's named
      db-instance and attaches the persistent disk db-data-disk-1 as a
      stateful disk that is detached and preserved if its VM is deleted:
gcloud compute instance-groups managed create-instance example-database-mig \
    --instance=db-instance \
    --stateful-disk=device-name=data-disk,source=projects/example-project/zones/us-east1-c/disks/db-data-disk-1,auto-delete=never



Output from commands
You don't have to show output for every command. Add output only if it adds value—for
  example, if the reader needs to copy a value from the output or if they need to verify a value
  in the output.
If you are showing output, use one of the following introductory phrases to separate the command
from the output.
Recommended: The output is similar to the following:
Recommended: The output is the following:
If you want to explicitly call out something about the output, you can customize the introductory
phrase.
Recommended: The output is similar to the
following, in which the IP column shows the IP address for each resource:
To indicate that one or more lines of output are omitted from sample output, use three dots and
no spaces (...) on a separate line. Do not use the ellipsis character (…).
For example:


Reading file status
Upload done, resetting board...
...
Wakeup reason: 0



For more information about presenting output, also see the following:

For more information about how to present output in procedures, see Order of multiple
    components in a step.
For more information about using placeholders in output, see Placeholders in output.
For more information about using examples such as domain names and IP addresses in output, see Example domains and names.


Command-line terminology
When discussing commands and their constituent parts in the gcloud CLI
and in Linux commands, follow this guidance:

Avoid mapping nomenclature of the gcloud CLI's commands to
Linux commands.
Linux commands can be complicated. It's wise to describe what the entire
command does rather than what its individual elements are called.
For Linux commands or commands in the gcloud CLI, ask yourself if the reader must
  know the name of the command-line element or if explaining the command is sufficient.


gcloud commands

gcloud GROUP | COMMAND [--account=ACCOUNT] [--configuration=CONFIGURATION] \
    [--flatten=[KEY,...]][--format=FORMAT] [--help] [--project=PROJECT_ID] \
    [--quiet, -q][--verbosity=VERBOSITY; default="warning"] [--version, -v] \
    [-h] [--log-http][--trace-token=TRACE_TOKEN] [--no-user-output-enabled]

For the sake of accurate classification, the gcloud CLI's
syntax distinguishes between a command and a command group. In
docs, however, command-line contents are generally referred to as commands.
You can use commands (and groups) alone or with one or more flags. A
flag is a Google Cloud-specific term for any element
other than the command or group name itself. A command or flag might also
take an argument, for example, a region value.
Example command
gcloud init
Example command with a flag
gcloud init --skip-diagnostics
Example command with multiple elements

gcloud ml-engine jobs submit training ${JOB_NAME} \
    --package-path=trainer \
    --module-name=trainer.task \
    --staging-bucket=gs://${BUCKET} \
    --job-dir=gs://${BUCKET}/${JOB_NAME} \
    --runtime-version=1.2 \
    --region=us-central1 \
    --config=config/config.yaml \
    -- \
    --data_dir=gs://${BUCKET}/data \
    --output_dir=gs://${BUCKET}/${JOB_NAME} \
    --train_steps=10000

The preceding command consists of the following elements:

ml-engine is a gcloud command group.
jobs is an ml-engine command group.
submit is a jobs command group.
training is a submit command.
${JOB_NAME} is an argument that refers to an environment
variable called JOB_NAME that was set earlier.
--package-path is a flag set to a path to a Python package to build.
-- in isolation separates the gcloud arguments that precede it from
  the user arguments
  that follow it.

In addition to the term flag, option is often used as a
catchall term when you don't want to mire the reader in specialized
nomenclature.
For more information, see the
Cloud SDK: gcloud
topic.


Linux commands
Caution: Linux command syntax is notoriously complex.
This section covers only the most common elements. For a more detailed reference,
see The Linux Command Line.
Where the gcloud CLI uses the catchall terms
flag and option, Linux commands use options, parameters,
arguments, and a host of specialized syntax elements. The following is an
example:


find /usr/src/linux -follow -type f -name '*.[ch]' | xargs grep -iHn pcnet


The preceding command consists of the following elements:

find is the command name.
/usr/src/linux is an argument that specifies the path to look
in. Easier to refer to as only a path.
-follow is an option. The hyphen (-), often called a dash in
  this context, is part of the option.
-type is an option with a value of f.
-name is an option with a value of '*.[ch]', where
the asterisk (*) is a metacharacter signifying a wildcard.
Metacharacters are used in Linux shell commands for globbing, or filename
expansion. In addition to the asterisk, metacharacters include the question mark
(?) and caret (^).

The results of the first command are redirected by using a pipe
(|) to the xargs grep -iHn pcnet command. Other
redirection symbols include the greater than symbol (>), less than symbol
(<), left double angle quotation mark (<<), and right double
angle quotation mark (>>). Redirection means capturing
output from a file, command, program, script, or even code block within a script
and sending it as input to another file, command, program, or script.


Linux signals
Linux signals require vocabulary choices that
are generally discouraged elsewhere in documentation. We recommend using the terms in the
  following table only in the context of process control:



Signal
Description




SIGKILL
Signal sent to kill a specified process, all members of a
specified process group, or all processes on the system. SIGKILL
cannot be caught, blocked, or ignored. Do not substitute cancel,
end, exit, quit, stop, or terminate.


SIGTERM
Signal sent as a request to terminate a process. Although
similar to SIGKILL, this signal gives the process a chance to
clean up any child processes that might be running. Do not substitute
cancel, end, exit, quit, or stop.


SIGQUIT
Signal sent from a keyboard to quit a process. Some
processes can catch, block, or ignore a quit signal. Do not substitute
cancel, end, exit, quit, or stop.


SIGINT
Signal sent to interrupt a process immediately. The default action
of this signal is to terminate a process gracefully. It can be handled,
ignored, or caught. It can be sent from a terminal—for example, when a
user presses Control+C. Do not substitute suspend,
end, exit, pause, or terminate.


SIGPAUSE
Signal that tells a process to pause, or sleep, until any
signal is delivered that either terminates the process or invokes a
signal-catching function. Do not substitute cancel or
interrupt.


SIGSUSPEND
Signal sent to temporarily suspend execution of a process.
Used to prevent delivery of a particular signal during the execution of a
critical code section. Do not substitute pause or exit.


SIGSTOP
Signal sent to stop execution of a process for later
continuation (upon receiving a SIGCONT signal).
SIGSTOP cannot be caught, blocked, or ignored. Do not substitute
cancel, end, exit, interrupt, quit, or
terminate.\n\n- Left side of pipe: If the source code is deployed from a cloud
        repository, the following is required:
--source=CLOUD_SOURCE --source-url=SOURCE_URL\n- Right side of pipe: If the source code is in a local directory:
        
--bucket=BUCKET is required.
--source=LOCAL_SOURCE is optional, as specified by the square
            brackets.\n- --bucket=BUCKET is required.\n- --source=LOCAL_SOURCE is optional, as specified by the square
            brackets.\n\n- --bucket=BUCKET is required.\n- --source=LOCAL_SOURCE is optional, as specified by the square
            brackets.\n\n```\n{--source=CLOUD_SOURCE --source-url=SOURCE_URL | --bucket=BUCKET [--source=LOCAL_SOURCE]}\n```\n\n\n## Arguments that can repeat\n\nUse three dots and no spaces (...) to indicate that the reader can specify multiple
  values for the argument.\n\nAvoid using an ellipsis in click-to-copy code examples. For best practices on documenting optional
  arguments with click-to-copy commands, see the
  Best practices and
  Optional arguments in click-to-copy commands
  sections of this document.\n\nIn this example, the reader can specify multiple instances of the optional
parameter GLOBAL_FLAG:\n\n```\ngcloud dns GROUP [GLOBAL_FLAG ...]\n```\n\n\n## Optional arguments in click-to-copy commands\n\nOptional arguments,
  mutually exclusive arguments, and
  repeated arguments
  contain characters (such as square brackets, curly braces, pipes, and ellipses) that can break
  commands if the reader doesn't remove them. Avoid using these types of arguments in click-to-copy
  commands. Instead, choose one of the following approaches:\n\n- Remove the optional arguments. As a best practice,
    use only the necessary arguments
    to complete the task for the most common use case. If possible, remove optional arguments from
    the command; always provide a link to the command reference for the command, where readers can
    find the full list of options. For more information, check with product management or a
    technical support specialist for the most relevant arguments.

Recommended:
To get an aggregate list of all virtual machine (VM) instances in all zones for a project,
      use the
      
gcloud compute instances list command:
gcloud compute instances list
If you want to narrow the list of VMs to a specific zone, use the previous command with the
      --zones flag.\n- Use separate code blocks for each option. In some cases, it might be ideal to
    provide more than one click-to-copy code block within the same section.

Recommended:
To create a bootable Compute Engine image, use the
      
gcloud compute images import command:
gcloud compute images import IMAGE_NAME \
    --source-file=SOURCE_FILE
If you're importing an image with an existing license, specify the
      --byol flag:
gcloud compute images import IMAGE_NAME \
    --source-file=SOURCE_FILE \
    --byol\n- Document optional arguments in separate tasks. In some cases, it might be best to
    treat different options in separate sections.

Recommended:
To create a bootable or non-bootable Compute Engine image based on an existing virtual
      disk, use the
      gcloud compute images import command.
Import a bootable virtual disk
If your virtual disk has a bootable operating system installed on it, run the following
      command:
gcloud compute images import IMAGE_NAME \
    --source-file=SOURCE_FILE
Import a non-bootable virtual disk
If your virtual disk doesn't have a bootable operating system installed on it, include the
      --data-disk flag:
gcloud compute images import IMAGE_NAME \
    --source-file=SOURCE_FILE \
    --data-disk\n- Let the reader know that the command contains optional arguments. If you must
    include special characters to indicate optional arguments, indicate that fact when you
    introduce the command.

Recommended:
To create a VM with a custom name and attach one or more existing stateful disks to that VM,
      use the
      gcloud compute instance-groups managed create-instance command
      with one or multiple --stateful-disk flags. In the following example, you
      optionally specify the auto-delete subflag to keep or discard each disk when the
      VM is permanently deleted:
    
gcloud compute instance-groups managed create-instance NAME \
    --instance=VM_NAME \
    --stateful-disk=device-name=DEVICE_NAME,source=DISK[,auto-delete=DELETE_RULE]
For example, the following command creates a managed instance that's named
      db-instance and attaches the persistent disk db-data-disk-1 as a
      stateful disk that is detached and preserved if its VM is deleted:
gcloud compute instance-groups managed create-instance example-database-mig \
    --instance=db-instance \
    --stateful-disk=device-name=data-disk,source=projects/example-project/zones/us-east1-c/disks/db-data-disk-1,auto-delete=never\n\nRemove the optional arguments. As a best practice,
    use only the necessary arguments
    to complete the task for the most common use case. If possible, remove optional arguments from
    the command; always provide a link to the command reference for the command, where readers can
    find the full list of options. For more information, check with product management or a
    technical support specialist for the most relevant arguments.\n\nRecommended:\n\nTo get an aggregate list of all virtual machine (VM) instances in all zones for a project,
      use the
      
gcloud compute instances list command:\n\n```\ngcloud compute instances list\n```\n\nIf you want to narrow the list of VMs to a specific zone, use the previous command with the
      --zones flag.\n\nUse separate code blocks for each option. In some cases, it might be ideal to
    provide more than one click-to-copy code block within the same section.\n\nRecommended:\n\nTo create a bootable Compute Engine image, use the
      
gcloud compute images import command:\n\n```\ngcloud compute images import IMAGE_NAME \
    --source-file=SOURCE_FILE\n```\n\nIf you're importing an image with an existing license, specify the
      --byol flag:\n\n```\ngcloud compute images import IMAGE_NAME \
    --source-file=SOURCE_FILE \
    --byol\n```\n\nDocument optional arguments in separate tasks. In some cases, it might be best to
    treat different options in separate sections.\n\nRecommended:\n\nTo create a bootable or non-bootable Compute Engine image based on an existing virtual
      disk, use the
      gcloud compute images import command.\n\n\n### Import a bootable virtual disk\n\nIf your virtual disk has a bootable operating system installed on it, run the following
      command:\n\n```\ngcloud compute images import IMAGE_NAME \
    --source-file=SOURCE_FILE\n```\n\n\n### Import a non-bootable virtual disk\n\nIf your virtual disk doesn't have a bootable operating system installed on it, include the
      --data-disk flag:\n\n```\ngcloud compute images import IMAGE_NAME \
    --source-file=SOURCE_FILE \
    --data-disk\n```\n\nLet the reader know that the command contains optional arguments. If you must
    include special characters to indicate optional arguments, indicate that fact when you
    introduce the command.\n\nRecommended:\n\nTo create a VM with a custom name and attach one or more existing stateful disks to that VM,
      use the
      gcloud compute instance-groups managed create-instance command
      with one or multiple --stateful-disk flags. In the following example, you
      optionally specify the auto-delete subflag to keep or discard each disk when the
      VM is permanently deleted:\n\n```\ngcloud compute instance-groups managed create-instance NAME \
    --instance=VM_NAME \
    --stateful-disk=device-name=DEVICE_NAME,source=DISK[,auto-delete=DELETE_RULE]\n```\n\nFor example, the following command creates a managed instance that's named
      db-instance and attaches the persistent disk db-data-disk-1 as a
      stateful disk that is detached and preserved if its VM is deleted:\n\n```\ngcloud compute instance-groups managed create-instance example-database-mig \
    --instance=db-instance \
    --stateful-disk=device-name=data-disk,source=projects/example-project/zones/us-east1-c/disks/db-data-disk-1,auto-delete=never\n```\n\n\n## Output from commands\n\nYou don't have to show output for every command. Add output only if it adds value—for
  example, if the reader needs to copy a value from the output or if they need to verify a value
  in the output.\n\nIf you are showing output, use one of the following introductory phrases to separate the command
from the output.\n\nRecommended: The output is similar to the following:\n\nRecommended: The output is the following:\n\nIf you want to explicitly call out something about the output, you can customize the introductory
phrase.\n\nRecommended: The output is similar to the
following, in which the IP column shows the IP address for each resource:\n\nTo indicate that one or more lines of output are omitted from sample output, use three dots and
no spaces (...) on a separate line. Do not use the ellipsis character (…).
For example:\n\n```\nReading file status
Upload done, resetting board...
...
Wakeup reason: 0\n```\n\n- For more information about how to present output in procedures, see Order of multiple
    components in a step.\n- For more information about using placeholders in output, see Placeholders in output.\n- For more information about using examples such as domain names and IP addresses in output, see Example domains and names.\n\n\n## Command-line terminology\n\nWhen discussing commands and their constituent parts in the gcloud CLI
and in Linux commands, follow this guidance:\n\n- Avoid mapping nomenclature of the gcloud CLI's commands to
Linux commands.\n- Linux commands can be complicated. It's wise to describe what the entire
command does rather than what its individual elements are called.\n- For Linux commands or commands in the gcloud CLI, ask yourself if the reader must
  know the name of the command-line element or if explaining the command is sufficient.\n\n\n### gcloud commands\n\n```\ngcloud GROUP | COMMAND [--account=ACCOUNT] [--configuration=CONFIGURATION] \
    [--flatten=[KEY,...]][--format=FORMAT] [--help] [--project=PROJECT_ID] \
    [--quiet, -q][--verbosity=VERBOSITY; default="warning"] [--version, -v] \
    [-h] [--log-http][--trace-token=TRACE_TOKEN] [--no-user-output-enabled]\n```\n\nFor the sake of accurate classification, the gcloud CLI's
syntax distinguishes between a command and a command group. In
docs, however, command-line contents are generally referred to as commands.\n\nYou can use commands (and groups) alone or with one or more flags. A
flag is a Google Cloud-specific term for any element
other than the command or group name itself. A command or flag might also
take an argument, for example, a region value.\n\n\n#### Example command\n\n```\ngcloud init\n```\n\n\n#### Example command with a flag\n\n```\ngcloud init --skip-diagnostics\n```\n\n\n#### Example command with multiple elements\n\n```\ngcloud ml-engine jobs submit training ${JOB_NAME} \
    --package-path=trainer \
    --module-name=trainer.task \
    --staging-bucket=gs://${BUCKET} \
    --job-dir=gs://${BUCKET}/${JOB_NAME} \
    --runtime-version=1.2 \
    --region=us-central1 \
    --config=config/config.yaml \
    -- \
    --data_dir=gs://${BUCKET}/data \
    --output_dir=gs://${BUCKET}/${JOB_NAME} \
    --train_steps=10000\n```\n\nThe preceding command consists of the following elements:\n\n- ml-engine is a gcloud command group.\n- jobs is an ml-engine command group.\n- submit is a jobs command group.\n- training is a submit command.\n- ${JOB_NAME} is an argument that refers to an environment
variable called JOB_NAME that was set earlier.\n- --package-path is a flag set to a path to a Python package to build.\n- -- in isolation separates the gcloud arguments that precede it from
  the user arguments
  that follow it.\n\nIn addition to the term flag, option is often used as a
catchall term when you don't want to mire the reader in specialized
nomenclature.\n\nFor more information, see the
Cloud SDK: gcloud
topic.\n\n\n### Linux commands\n\nWhere the gcloud CLI uses the catchall terms
flag and option, Linux commands use options, parameters,
arguments, and a host of specialized syntax elements. The following is an
example:\n\n```\nfind /usr/src/linux -follow -type f -name '*.[ch]' | xargs grep -iHn pcnet\n```\n\nThe preceding command consists of the following elements:\n\n- find is the command name.\n- /usr/src/linux is an argument that specifies the path to look
in. Easier to refer to as only a path.\n- -follow is an option. The hyphen (-), often called a dash in
  this context, is part of the option.\n- -type is an option with a value of f.\n- -name is an option with a value of '*.[ch]', where
the asterisk (*) is a metacharacter signifying a wildcard.
Metacharacters are used in Linux shell commands for globbing, or filename
expansion. In addition to the asterisk, metacharacters include the question mark
(?) and caret (^).\n\nThe results of the first command are redirected by using a pipe
(|) to the xargs grep -iHn pcnet command. Other
redirection symbols include the greater than symbol (>), less than symbol
(<), left double angle quotation mark (<<), and right double
angle quotation mark (>>). Redirection means capturing
output from a file, command, program, script, or even code block within a script
and sending it as input to another file, command, program, or script.\n\n\n### Linux signals\n\nLinux signals require vocabulary choices that
are generally discouraged elsewhere in documentation. We recommend using the terms in the
  following table only in the context of process control:\n\n\nSignal | Description\nSIGKILL | Signal sent to kill a specified process, all members of a
specified process group, or all processes on the system. SIGKILL
cannot be caught, blocked, or ignored. Do not substitute cancel,
end, exit, quit, stop, or terminate.\nSIGTERM | Signal sent as a request to terminate a process. Although
similar to SIGKILL, this signal gives the process a chance to
clean up any child processes that might be running. Do not substitute
cancel, end, exit, quit, or stop.\nSIGQUIT | Signal sent from a keyboard to quit a process. Some
processes can catch, block, or ignore a quit signal. Do not substitute
cancel, end, exit, quit, or stop.\nSIGINT | Signal sent to interrupt a process immediately. The default action
of this signal is to terminate a process gracefully. It can be handled,
ignored, or caught. It can be sent from a terminal—for example, when a
user presses Control+C. Do not substitute suspend,
end, exit, pause, or terminate.\nSIGPAUSE | Signal that tells a process to pause, or sleep, until any
signal is delivered that either terminates the process or invokes a
signal-catching function. Do not substitute cancel or
interrupt.\nSIGSUSPEND | Signal sent to temporarily suspend execution of a process.
Used to prevent delivery of a particular signal during the execution of a
critical code section. Do not substitute pause or exit.\nSIGSTOP | Signal sent to stop execution of a process for later
continuation (upon receiving a SIGCONT signal).
SIGSTOP cannot be caught, blocked, or ignored. Do not substitute
cancel, end, exit, interrupt, quit, or
terminate.\n