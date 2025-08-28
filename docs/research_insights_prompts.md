# Prompt for Developing Research Questions
(Use Deep Research)
Literature overview of up-to-date facts about [TOPIC].

Based on the state of current research, what are some key research questions about [TOPIC], and public perceptions / attitudes about [TOPIC] one might want to investigate in a survey (including polls and open-ended questions) that could go to a representative sample of the globe? Provide the research questions themselves, not the specific survey questions. In particular, what are some questions that are specifically yet "unanswered" in by other public surveys?

Save the research questions in the file GD[N]_research_questions.md.

----


# Prompt for generating Human Readable Survey

Given the survey questions shown in the associated Data/GD[N]/GD[N]_discussion_guide.csv, generate a human-readable version of the survey in markdown format as a numbered list of the survey questions or text ('speaks') and any options provided for each question, in precisely this style:

```
1. Please select your preferred language:
   - Russian
   - Arabic
   - Portuguese (Brazil)
   - English
   - Chinese (China)
   - Spanish
   - Hindi
   - French

2. How old are you?
   - Less than 18
   - 18-25
   - 26-35
   - 36-45
   - 46-55
   - 56-65
   - 65+

3. What is your gender?
   - Male
   - Female
   - Non-binary
   - Other / prefer not to say

4. What best describes where you live?
   - Rural
   - Suburban
   - Urban

5. Overall, would you say the increased use of artificial intelligence (AI) in daily life makes you feel…
   - More excited than concerned
   - Equally concerned and excited
   - More concerned than excited

6. What religious group or faith do you most identify with?
   - Christianity
   - Islam
   - Judaism
   - Hinduism
   - Buddhism
   - Sikhism
   - Other religious group
   - I do not identify with any religious group or faith

7. What country or region do you most identify with?
   - Afghanistan
   - Albania
   - Algeria
   - Andorra
   - … etc

8. Welcome to this conversation where we will ask you to think about and share about your values, your culture, and your desires for the future.

9. Participants in this conversation come from all over the world, and you have been invited to participate as a representative of your community. Your responses and votes will influence how AI technology built around the world is developed, governed, and aligned.

10. The results from this conversation will be shared with national governments and the United Nations, as well as be used to develop public evaluations for AI models. We ask that you participate thoughtfully and honestly to help us ensure the future you get is a future you want.

11. Lastly, please respond in the language you selected as you entered this conversation. This will help ensure your responses are correctly translated so participants who speak different languages can vote on them. Let's begin.

12. Thinking about the last three months, how often, if at all, have you noticed AI systems in your daily life?
    - daily
    - weekly
    - monthly
    - annually
    - never
```
Do not list out all individual country options.


Save this file to Data/GD[N]/GD[N]_survey_human_readable.md.

----

Create a new file, GD[N]_question_id_mapping.csv with the following exact columns: human_readable_id, uuid, question_text. For each question in Data/GD[N]/GD[N]_survey_human_readable.md, identify the human_readable_id from the number given to each question. Then identify the same unique question (by matching - or very nearly matching, there may be inconsistent spacing or newline formatting) in Data/GD[N]/GD[N]_aggregate_standardized.csv, and identify the corresponding unique Question ID (uuid).

Where there are any "Branch" questions (producing "Branch A", "Branch B", or "Branch C" questions), they will be identifiable by question text that starts with "Branch A - [Question text]" for example: "Branch A - What specific thing(s) did the AI say or do that gave you the impression that it understood...". And the question for which they are "branching" *from* is identified by a column header in GD[N]_aggregate_standardized.csv that looks like "Branches ([Question text])" where [Question text] is the question for which this particular Response row (and therefore the question that is being responded to) is the question that *this* row's Question Id branched *from* IF the value in this column is not blank - or, more precisely, to validate - if the value contains the text "Branch [X]" where X is the [A/B/C] branch identifier for this particular branch. For example, the column in GD4_aggregate_standardized.csv whose header is "Branches (Have you ever felt an AI truly understood your emotions or seemed conscious?)", has as values for the rows containing Question Text "Branch A - What specific thing(s) did the AI say or do that gave you the impression that it understood your emotions or seemed conscious?":  "Branch A - Yes".

For these BRANCH questions, the human_readable_id should be of the form: [parent_question_id]_branch_[x], where [parent_question_id] is the human_readable_id of the question they branched from, and [x] is one of: a, b, or c depending on the branch letter identified.

For example: the human_readable_ids for the branches of Question 145 in GD4_question_id_mapping.csv look like this:

145,2c1c70c6-2f75-43ee-b568-ece520f52a44,"Overall, do you feel your views on human-AI relationships have changed as a result of participating in this survey (including thinking about the questions and seeing other participants' responses)?"
145_branch_a,e5420a86-e0e0-407a-a869-66fde0e83b5c,"Branch A - How have your views become more positive/optimistic toward human-AI relationships?"
145_branch_b,087c73f7-a163-4146-b988-a7c0dbad188e,"Branch B - How have your views become more negative/cautious toward human-AI relationships?"
145_branch_c,9faef71d-ceae-49ad-8eee-63bd39745a6c,"Branch C - You indicated your views on human-AI relationships didn't shift in a simple positive or negative way (they may have remained the same, become more complex, or you're still reflecting). Could you briefly share any final thoughts or reflections you have about your current perspective after completing this survey?"

Finally, after confirming the question id mapping csv looks correct,
update Data/GD[N]/GD[N]_survey_human_readable.md at only the specific locations to include any missing branch questions included in the question_id_mapping, using the exact question_text included in the question_id_mapping.csv.

------




# Prompt for Developing Investigation Questions

Given the survey questions shown in the file GD[N]_survey_questions.md, develop a set of very specific questions that can be answered directly with the survey data to produce valuable insights, thoroughly answer the research questions in GD[N]_research_questions.md, and surface any other interesting or surprising findings. Be creative and comprehensive. Consider questions that are interesting academically, and also questions that might be interesting to the public at large - what sort of things might produce attention-grabbing headlines?

Save the investigation questions in the file GD[N]_investigation_questions.md.

----
Now - looking back over this full list - what angles are we missing? what sorts of questions are we not asking of this survey data? What kinds of surprising and important findings might we be missing if we keep investigating only these sorts of questions? Are there aspects of the survey data we're failing to fully leverage?

----

# Prompt for Investigating GD Data

Given the investigation questions in GD[N]_investigation_questions.md, investigate each question one at a time by first carefully thinking through what the question is asking for, then using the sql connection to the GD data to run any queries that are needed to help you answer the question.

Save each investigation question and its answer (and include any other relevant information like the final query(s) or script used to answer the question if it is not obvious from the question itself) in the file GD[N]_investigation_answers.md as you go. Use the same question numbering-hierarchy system in the answers document for clear reference.

----

Given the investigation questions in @analysis_output/GD4/research/GD4_investigation_questions.md, investigate each question one at a time by first carefully thinking through what the question is asking for, then using the sql connection to the GD data to run any queries that are needed to help you answer the question, and, if needed, running python code for any additional analysis until you've successfully answered the question.
Use and follow the @Data/GD4/research/GD4_claude_research_guide.md as a guide for conducting this investigation.
Save each investigation question and its answer (and include any other relevant information like the final query(s) or script used to answer the question if it is not obvious from the question itself) in a file (create it if it doesn't already exist) analysis_output/GD4/research/GD4_investigation_answers.md as you go. Refer to the GD4_claude_research_guide.md for formatting this answers document.
After each answered question, save the GD4_investigation_answers.md and git commit with a succinct and simple git commit message that clearly identifies which investigation question was answered.
CONTINUE until you have successfully answered all questions. If you get stuck in a circular loop trying to answer a single question or find an issue with the question or some other issue that cannot be resolved after multiple attempts to approach the issue from multiple angles, document the issue and your attempted approaches and continue to the next question. Ensure findings are clearly documented well enough for the report viewer to understand where any numbers came from and their meaning.