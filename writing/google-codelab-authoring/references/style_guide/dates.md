Source: https://developers.google.com/style/dates\n\n# Dates and times


      
      Stay organized with collections
    

      
      Save and categorize content based on your preferences.\n\n- Home\n- Products\n- Style\n\n\n## Page Summary\n\n- Express dates with the full month name, day, and four-digit year, for example, January 19, 2017.\n- Express time using the 12-hour clock with AM or PM, omitting minutes for round hours, for example, 3 PM.\n- Avoid using time zones unless necessary; if needed, use the full region name and UTC offset, such as US and Canadian Pacific Standard Time (UTC-8).\n- For numeric-only dates, adhere to the ISO 8601 standard (YYYY-MM-DD), like 2017-04-15.\n- Avoid using seasons; instead, specify months or quarters for clarity in global content.\n\nExpress dates with the full month name, day, and four-digit year, for example, January 19, 2017.\n\nExpress time using the 12-hour clock with AM or PM, omitting minutes for round hours, for example, 3 PM.\n\nAvoid using time zones unless necessary; if needed, use the full region name and UTC offset, such as US and Canadian Pacific Standard Time (UTC-8).\n\nFor numeric-only dates, adhere to the ISO 8601 standard (YYYY-MM-DD), like 2017-04-15.\n\nAvoid using seasons; instead, specify months or quarters for clarity in global content.\n\nExpressing dates and times in a clear and unambiguous way helps support
writing for a global audience and reduces
confusion.\n\n\n## Express times\n\nIn general, use the following guidelines to format expressions of time:\n\n- Use the 12-hour clock, except if required to use a 24-hour time, such as
   when documenting features that use 24-hour time. If the UI, a command, or a code sample uses the
   24-hour format, use that format throughout the page for consistency.\n- Use exact times when possible, but noon and midnight are OK.\n- Use hyphens in time ranges. Don't add spaces before or after the hyphens.
Recommended: 5-10 minutes ago.\n- Capitalize AM and PM, and leave one space between it and the time.
Recommended: 3:45 PM.\n- Remove the minutes from round hours.
Recommended: 3 PM.\n\nUse hyphens in time ranges. Don't add spaces before or after the hyphens.\n\nRecommended: 5-10 minutes ago.\n\nCapitalize AM and PM, and leave one space between it and the time.\n\nRecommended: 3:45 PM.\n\nRemove the minutes from round hours.\n\nRecommended: 3 PM.\n\n\n### Express time zones\n\nAvoid using time zones unless absolutely necessary. In cases where you need to use a time
  zone—such as describing real events at real times—use the following guidelines:\n\n- Let the reader know if the time is local to their time—for example, 10 AM your local
time.\n- If a time zone is necessary, use the timestamp format as seen in the user interface (if
available).\n- If using a specific time zone, spell out the region and include the
UTC or GMT label
as a parenthetical. For example:
  
US and Canadian Pacific Standard Time (UTC-8)
US and Canadian Pacific Daylight Time (UTC-7)\n- US and Canadian Pacific Standard Time (UTC-8)\n- US and Canadian Pacific Daylight Time (UTC-7)\n- Don't abbreviate the name of the time zone.\n- In the rare event where the time of an event doesn't change for daylight saving time, use the
specific time zone, without reference to UTC.\n\n- US and Canadian Pacific Standard Time (UTC-8)\n- US and Canadian Pacific Daylight Time (UTC-7)\n\n\n## Express dates\n\nIn general, spell out the names of months and days of the week in full. Give
the full four-digit year, not a two-digit abbreviation.\n\nRecommended: January 19, 2017\n\nIf including the day of the week, add it before the month as follows:
  DAY_OF_WEEK, MONTH DAY,
  YEAR.\n\nRecommended: Tuesday, April 27, 2021\n\n\n### Partial dates and abbreviations\n\nWhen giving only the month and year, don't use a comma.\n\nRecommended: She was hired in January
2017.\n\nIn most cases, don't abbreviate the day of the week or the month. However,
when conserving space, such as in a heading or table, it's okay to abbreviate
the month and the day of the week to their three-letter abbreviations.
Capitalize the first letter and do not add a period at the end of the abbreviation.\n\nIf you abbreviate, do so for the entire date. Don't mix written-out forms with
abbreviated forms in the same date.
Be consistent in where you apply abbreviations throughout your documentation. For
example, if you choose to abbreviate in table cells, do so in all table cells.
Recommended: Mon, Sep 3, 2018
Not recommended: Mon, September 3, 2018
Dates in the middle of a sentence
When a MONTH DAY, YEAR
  date appears in the middle of a sentence, add a comma after the year.
Recommended: The January 19, 2017,
release of ...
However, if the date in the middle of the sentence consists of the
month and year only, don't use a comma.
Recommended: The January 2017 release
of ...
Why we prefer dates written out
In general, don't express months as numbers unless you don't have the option
(in which case, see numeric-only date
format). Different regions of the world put parts of the date in a different
order for numeric dates. For example, a date written as 04/05/09 means different
things in different regions:

In the UK, 04/05/09 means May 4, 2009, where the order is usually day,
  month, and then year.
In the US, 04/05/09 means April 5, 2009, where the order is usually month,
  day, and then year.
In some other parts of the world, 04/05/09 means May 9, 2004. Some
  regions write the year first, followed by the month and day.

For this reason, we recommend always using words to express dates. Expressing
dates in numbers only (using slashes, periods, or hyphens as separators) can be
confusing.
Recommended: February 12, 2017
Recommended: Sunday, February 12, 2017
Not recommended: 02.12.2017
Not recommended: 12/02/2017
Numeric-only date format
If you must express a date in numerical date format, use the format
YYYY-MM-DD, and separate the elements by using hyphens. This conforms
to ISO 8601 international
standards for numerical date format.
Additionally, if you have a choice of what date to write (such as in a
fictional example), then choose a calendar day greater than 12 to differentiate
it from the month.
Recommended: 2017-04-15
Not recommended: 04/06/2017
Express dates and times together
If you must express a date and a time together, then mention the date first and then the time.
    Recommended: 2017-04-15 at 3 PM
Recommended: May 4, 2009, at 6 PM\n\nBe consistent in where you apply abbreviations throughout your documentation. For
example, if you choose to abbreviate in table cells, do so in all table cells.
Recommended: Mon, Sep 3, 2018
Not recommended: Mon, September 3, 2018
Dates in the middle of a sentence
When a MONTH DAY, YEAR
  date appears in the middle of a sentence, add a comma after the year.
Recommended: The January 19, 2017,
release of ...
However, if the date in the middle of the sentence consists of the
month and year only, don't use a comma.
Recommended: The January 2017 release
of ...
Why we prefer dates written out
In general, don't express months as numbers unless you don't have the option
(in which case, see numeric-only date
format). Different regions of the world put parts of the date in a different
order for numeric dates. For example, a date written as 04/05/09 means different
things in different regions:

In the UK, 04/05/09 means May 4, 2009, where the order is usually day,
  month, and then year.
In the US, 04/05/09 means April 5, 2009, where the order is usually month,
  day, and then year.
In some other parts of the world, 04/05/09 means May 9, 2004. Some
  regions write the year first, followed by the month and day.

For this reason, we recommend always using words to express dates. Expressing
dates in numbers only (using slashes, periods, or hyphens as separators) can be
confusing.
Recommended: February 12, 2017
Recommended: Sunday, February 12, 2017
Not recommended: 02.12.2017
Not recommended: 12/02/2017
Numeric-only date format
If you must express a date in numerical date format, use the format
YYYY-MM-DD, and separate the elements by using hyphens. This conforms
to ISO 8601 international
standards for numerical date format.
Additionally, if you have a choice of what date to write (such as in a
fictional example), then choose a calendar day greater than 12 to differentiate
it from the month.
Recommended: 2017-04-15
Not recommended: 04/06/2017
Express dates and times together
If you must express a date and a time together, then mention the date first and then the time.
    Recommended: 2017-04-15 at 3 PM
Recommended: May 4, 2009, at 6 PM\n\nBe consistent in where you apply abbreviations throughout your documentation. For
example, if you choose to abbreviate in table cells, do so in all table cells.\n\nRecommended: Mon, Sep 3, 2018\n\nNot recommended: Mon, September 3, 2018\n\n\n### Dates in the middle of a sentence\n\nWhen a MONTH DAY, YEAR
  date appears in the middle of a sentence, add a comma after the year.\n\nRecommended: The January 19, 2017,
release of ...\n\nHowever, if the date in the middle of the sentence consists of the
month and year only, don't use a comma.\n\nRecommended: The January 2017 release
of ...\n\n\n### Why we prefer dates written out\n\nIn general, don't express months as numbers unless you don't have the option
(in which case, see numeric-only date
format). Different regions of the world put parts of the date in a different
order for numeric dates. For example, a date written as 04/05/09 means different
things in different regions:\n\n- In the UK, 04/05/09 means May 4, 2009, where the order is usually day,
  month, and then year.\n- In the US, 04/05/09 means April 5, 2009, where the order is usually month,
  day, and then year.\n- In some other parts of the world, 04/05/09 means May 9, 2004. Some
  regions write the year first, followed by the month and day.\n\nFor this reason, we recommend always using words to express dates. Expressing
dates in numbers only (using slashes, periods, or hyphens as separators) can be
confusing.\n\nRecommended: February 12, 2017\n\nRecommended: Sunday, February 12, 2017\n\nNot recommended: 02.12.2017\n\nNot recommended: 12/02/2017\n\n\n### Numeric-only date format\n\nIf you must express a date in numerical date format, use the format
YYYY-MM-DD, and separate the elements by using hyphens. This conforms
to ISO 8601 international
standards for numerical date format.\n\nAdditionally, if you have a choice of what date to write (such as in a
fictional example), then choose a calendar day greater than 12 to differentiate
it from the month.\n\nRecommended: 2017-04-15\n\nNot recommended: 04/06/2017\n\n\n### Express dates and times together\n\nIf you must express a date and a time together, then mention the date first and then the time.
    Recommended: 2017-04-15 at 3 PM
Recommended: May 4, 2009, at 6 PM\n\nRecommended: 2017-04-15 at 3 PM\n\nRecommended: May 4, 2009, at 6 PM\n\n\n## Express divisions of the year\n\nAvoid referring to seasons. Spring in the northern hemisphere is fall (autumn) in the
southern hemisphere. Instead, use the month, quarter, or temperature (if relevant).\n\n\nRecommended | Not recommended\nDuring warmer months, data centers face a higher risk of cooling failures. | During summer months, data centers face a higher risk of cooling failures.\nIn November and December, data centers experience higher traffic volume. | In winter, data centers experience higher traffic volume.\nChanges are released in October of each year. | Changes are released in the Fall of each year.\n