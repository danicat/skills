Source: https://developers.google.com/style/procedures\n\n# Procedures


      
      Stay organized with collections
    

      
      Save and categorize content based on your preferences.\n\n- Home\n- Products\n- Style\n\n\n## Page Summary\n\n- Procedures should be written as numbered steps with clear and concise language, focusing on the action to be performed.\n- Sub-steps and multi-action steps have specific formatting guidelines to ensure clarity and readability, such as using letters and roman numerals for sub-steps and the > symbol for sequential actions within a single step.\n- Multiple procedures for the same task should be organized thoughtfully, prioritizing accessibility and clarity by using separate sections or tabs and favoring the shortest and simplest method.\n- Steps should provide context, clearly state the goal or purpose, and include any necessary justifications or results while avoiding redundancy and unnecessary information.\n- Optional steps are indicated with "Optional:", and repetitive procedures are referenced rather than repeated to maintain conciseness and avoid redundancy.\n\nProcedures should be written as numbered steps with clear and concise language, focusing on the action to be performed.\n\nSub-steps and multi-action steps have specific formatting guidelines to ensure clarity and readability, such as using letters and roman numerals for sub-steps and the > symbol for sequential actions within a single step.\n\nMultiple procedures for the same task should be organized thoughtfully, prioritizing accessibility and clarity by using separate sections or tabs and favoring the shortest and simplest method.\n\nSteps should provide context, clearly state the goal or purpose, and include any necessary justifications or results while avoiding redundancy and unnecessary information.\n\nOptional steps are indicated with "Optional:", and repetitive procedures are referenced rather than repeated to maintain conciseness and avoid redundancy.\n\nA procedure is a sequence of numbered steps for accomplishing a task. For information about
  lists of items that aren't part of a procedure, see the
  Lists page.\n\n\n## Introductory sentences\n\nIn most cases, introduce a procedure with an introductory sentence. This
introductory sentence should provide context to the reader that isn't part of
the section heading. Don't simply repeat the heading: if the heading explains
what the procedure is, and no additional context is needed, then don't
include an introductory statement.\n\nThe sentence can end with a colon or a period. Use a colon if it immediately
precedes the procedure. Use a period if there's more material (such as a
note paragraph) between the introduction and the procedure.\n\nYou can introduce a procedure with an imperative statement. Don't introduce a procedure with
a partial sentence that's completed by the numbered steps.\n\nRecommended: To customize the buttons,
follow these steps:\n\nAlso recommended: Customize the buttons:\n\nAlso recommended: To customize the buttons, do the following:\n\nNot recommended: To customize the
buttons:\n\nFor more information about introducing lists, see  Lists.\n\n\n## Single-step procedures\n\nWhen a procedure consists of only one step, write the step in one sentence and format it as a
  bulleted list.\n\nRecommended:\n\n- To clear (flush) the entire log, click Clear logcat.\n\nNot recommended:\n\nTo clear (flush) the entire log, follow this step:\n\n- Click Clear logcat.\n\nAlso not recommended:\n\nTo clear (flush) the entire log, follow this step:\n\n- Click Clear logcat.\n\n\n## Sub-steps in numbered procedures\n\nIn a numbered procedure, sub-steps are labeled with lowercase letters, and
sub-sub-steps get lowercase Roman numerals.\n\nWhen a step has sub-steps, treat the step like an introductory sentence: put a colon or a
period at the end of the step, as appropriate.\n\nFor more information about lists, see  Lists.\n\nRecommended:\n\n- To add a VM instance, do the following:
      
Click Create instance.
For Name, enter a name for the VM instance, and then do the following:
          
For Region, specify where you want to deploy the VM instance.
For Machine type, select an option.


Click Create.\n- Click Create instance.\n- For Name, enter a name for the VM instance, and then do the following:
          
For Region, specify where you want to deploy the VM instance.
For Machine type, select an option.\n- For Region, specify where you want to deploy the VM instance.\n- For Machine type, select an option.\n- Click Create.\n- To connect to the VM instance by using SSH, click SSH.\n\n- Click Create instance.\n- For Name, enter a name for the VM instance, and then do the following:
          
For Region, specify where you want to deploy the VM instance.
For Machine type, select an option.\n- For Region, specify where you want to deploy the VM instance.\n- For Machine type, select an option.\n- Click Create.\n\n- For Region, specify where you want to deploy the VM instance.\n- For Machine type, select an option.\n\n\n## Order of multiple components in a step\n\nTo document a complex procedural step, use the following order:\n\n- Describe the action to take.\n- List a command, if necessary.\n- Explain any placeholders that are used in the command.
For more information, see
      Formatting placeholders.\n- Explain the command in more detail, if necessary.\n- List the output of the command, if necessary.
For more information, see
    Output from commands.\n- In a separate paragraph, explain
    the result of an
      action, or any output, if necessary.\n\nExplain any placeholders that are used in the command.\n\nFor more information, see
      Formatting placeholders.\n\nList the output of the command, if necessary.\n\nFor more information, see
    Output from commands.\n\nThe following example demonstrates the preceding order:\n\n- Plan the Terraform deployment:
terraform plan -out=NAME
Replace NAME with the name of your Terraform plan.
The terraform plan command does the following:

Parses the Terraform configuration, building a list of resources to provision.
Refreshes the current state of resources already provisioned in Google Cloud.
Creates a plan to make the currently provisioned resources match the parsed
    configuration.

The output is similar to the following:

  Plan: 26 to add, 0 to change, 0 to destroy.
  ------------------------------------------------------------
  This plan was saved to: NAME
The output shows what resources to add, change, or destroy.\n- Parses the Terraform configuration, building a list of resources to provision.\n- Refreshes the current state of resources already provisioned in Google Cloud.\n- Creates a plan to make the currently provisioned resources match the parsed
    configuration.\n\nPlan the Terraform deployment:\n\n```\nterraform plan -out=NAME\n```\n\nReplace NAME with the name of your Terraform plan.\n\nThe terraform plan command does the following:\n\n- Parses the Terraform configuration, building a list of resources to provision.\n- Refreshes the current state of resources already provisioned in Google Cloud.\n- Creates a plan to make the currently provisioned resources match the parsed
    configuration.\n\nThe output is similar to the following:\n\n```\nPlan: 26 to add, 0 to change, 0 to destroy.
  ------------------------------------------------------------
  This plan was saved to: NAME\n```\n\nThe output shows what resources to add, change, or destroy.\n\n\n## Multi-action procedures\n\nIn general, use one step for each action. However, you can combine small actions
into one step by using
angle brackets (>) for sequential menu selections.\n\nRecommended:\n\n- Click Next > Finish.\n\nAlso recommended:\n\n- Click
File > New > Document.\n\nDon't make the steps too long. If they feel too long, consider splitting them
into multiple steps.\n\n\n## Multiple procedures for the same task\n\nIn general, if there's more than one way to complete a task, then document
one procedure that's accessible for all readers. If all methods are accessible, pick the shortest
and simplest approach if possible. If you need to document multiple ways to complete a
task, then separate them in different pages, headings, or tabs.\n\nThe following guidelines can help you choose which procedure to document:\n\n- Choose a procedure that lets readers do all the steps by using only a keyboard.\n- Choose the shortest procedure.\n- Choose a procedure that uses a programming language that most of your
    audience is familiar with.\n\n\n## Repetitive procedures\n\nAvoid repeating procedures. Instead, reference those procedures and link to
them.\n\nRecommended:\n\n- Create a user as you did in the previous step.\n\nAlso recommended:\n\n- Create a user as you did in the previous step.\n\n\n## Optional steps\n\nFor an optional step, at the beginning of the step, type Optional
    followed by a colon.\n\nRecommended:\n\n- Optional: Type an arbitrary string ...\n\nNot recommended:\n\n- (Optional) Type an arbitrary string ...\n\n\n## Steps that say where to complete a task\n\nTell the reader where to complete an action—for example, in a
  particular tool or UI field—before you state the action.\n\nRecommended:\n\n- In Google Docs, click
      File > New > Document.\n- In the Google Cloud console, go to the Monitoring page.\n\nNot recommended:\n\n- Click File >
      New > Document in Google
      Docs.\n- Go to the Monitoring page in the Google Cloud console.\n\nIf a set of procedures is split across multiple headings, then in each
  procedure, restate where the reader completes the action. For example, if two
  procedures in a document take place in the console, then start both
  procedures with "In the console ..."\n\n\n## Steps with goals\n\nFor some steps, it's useful to state the goal
    that the step accomplishes.\n\nWhen a step includes a goal, state the goal before the action. This
    structure helps readers understand and complete the step more easily.\n\n- To start a new document, click
        File >
        New > Document.\n\n- Click File >
        New > Document to start a
        new document.\n\nSometimes, the preceding format can imply that the required step is
    optional. In such cases, use the following format:\n\nRecommended:\n\n- Start a new document: click
      File >
        New > Document.\n\nIt's usually clear within the context of a procedure whether a step is
    required. In such cases, the "To ..." format is more natural than the colon
    format.\n\nTo determine whether you need to use the colon format, consider how the
    goal of the step relates to the goal of the procedure. For example, in a
    procedure for creating a bar chart, a step with the goal "To create the
    chart" is clearly required. A step with the goal "To enhance the chart" is
    also unlikely to create confusion. But a step with the goal "To sort the
    data by date" might or might not be necessary. To clarify that the step
    isn't optional, use "Sort the data by date:" instead.\n\n\n## Steps with results or justifications\n\nSome steps consist of an action along with a resulting reaction that helps
    the reader navigate to the next step. State the action first and the result
    second. Keep the result in the same paragraph as the action. But also consider whether you
    can avoid repetitiveness and overwhelming the reader with too much bolding of UI elements.\n\n- Click Run. The query results appear after the query runs.\n\n- Click Enter.\n- In the New file dialog that appears, click Next.\n\n- Click Enter. The New file dialog appears.\n- In the New file dialog, click Next.\n\nFor information about describing output, see
  Output from commands.\n\nOther steps benefit from including a justification for why the step is
    important. State the action first and the justification second.\n\n- Store the private key in a secure location. You need it later.\n\n\n## Summary of guidelines for writing procedures\n\n\nGuidance | Recommended | Not recommended\nMake sure that the first sentence in a procedural step includes an imperative verb. | Clone the repository that contains the sample data. | You need the project ID later in this document. Retrieve the project ID.\nUse complete sentences. |  | \nUse parallel structure and consistent verb form. | Download the service account key to
        your local machine. Click More, and then click Download. | Download the service account key to your
  local machine by clicking More and then clicking Download file.\nFor an optional step, type Optional: as the first word of the step. | Optional: Type an arbitrary string... | (Optional) Type an arbitrary string...\nSet the context (such as a tool or an environment) in which the reader performs a
          procedure.
If there are multiple headings associated with a set of procedures, restate the context
          of the procedure in the first step, even if the context is the same as in the previous
          procedure. | In Cloud Shell, connect to the development cluster.
In the Google Cloud console, go to the BigQuery page. | \nWrite in the order that the reader needs to follow. State the location of the action
        before stating the action. | In Google Docs, click File >
        New > Document.
In the Google Cloud console, go to the Monitoring page. | Click File >
            New > Document in Google Docs.
Go to the Monitoring page in the Google Cloud console.\nState the purpose or goal of the action before stating the action. | To start a new document, click File >
            New > Document. | Click File >
            New > Document
            to start a new document.\nDon't use directional language to orient the reader, such as above, below,
        or right-hand side. This type of language doesn't work well for accessibility or for
        localization. If a UI element is hard to find, provide a screenshot.
For information about documenting icons, see
          Buttons and icons. | Click menuMenu.
In the preceding diagram,...
In the following diagram,... | Click the button with three lines.
In the above diagram, ...
In the diagram below, ...\nDon't use please. | To open a document, click File > Open. | To open a document, please click
            File > Open.\nAvoid using run the following command to introduce code. Instead, focus on what
        the command does. | In Cloud Shell, deploy the load generator:...
Define a firewall rule to allow internal traffic:... | In Cloud Shell, deploy the load generator by running the following command:...
Run the following command:...\nIf the reader must press Enter after a step, then include that instruction as part
        of the step. | Click the search box, type custom function, and then press Enter. | Click the search box and type custom function.
Press Enter.\nDon't include keyboard shortcuts. | Copy the command, and then paste it... | Press Ctrl+C, and then press Ctrl+V...\nWhen there's more than one way to do something, give only the best way. Giving alternate
        ways can confuse readers. |  | \nIf your procedure includes code samples, see how to format  code samples. |  | \nIf your procedure includes commands, see how to format  commands. |  | \nEnsure that the reader has the information that they need in order to prepare for the
        task ahead of time. Having information in advance supports task management, executive
        functioning, memory, and emotional regulation. | The following hardware and software are required:... | \nInclude as few steps as possible to complete the task. Limit interruptions in the path. |  | \nFocus on one reader decision at a time. Separate each instruction by making each
        instruction a separate list item. |  | \n\nSet the context (such as a tool or an environment) in which the reader performs a
          procedure.\n\nIf there are multiple headings associated with a set of procedures, restate the context
          of the procedure in the first step, even if the context is the same as in the previous
          procedure.\n\nIn Cloud Shell, connect to the development cluster.\n\nIn the Google Cloud console, go to the BigQuery page.\n\nIn Google Docs, click File >
        New > Document.\n\nIn the Google Cloud console, go to the Monitoring page.\n\nClick File >
            New > Document in Google Docs.\n\nGo to the Monitoring page in the Google Cloud console.\n\nDon't use directional language to orient the reader, such as above, below,
        or right-hand side. This type of language doesn't work well for accessibility or for
        localization. If a UI element is hard to find, provide a screenshot.\n\nFor information about documenting icons, see
          Buttons and icons.\n\nClick menuMenu.\n\nIn the preceding diagram,...\n\nIn the following diagram,...\n\nClick the button with three lines.\n\nIn the above diagram, ...\n\nIn the diagram below, ...\n\nAvoid using run the following command to introduce code. Instead, focus on what
        the command does.\n\nIn Cloud Shell, deploy the load generator:...\n\nDefine a firewall rule to allow internal traffic:...\n\nIn Cloud Shell, deploy the load generator by running the following command:...\n\nRun the following command:...\n\n- Click the search box and type custom function.\n- Press Enter.\n