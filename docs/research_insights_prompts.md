# Prompt for Developing Research Questions
(Use Deep Research)
Literature overview of up-to-date facts about [TOPIC].

Based on the state of current research, what are some key research questions about [TOPIC], and public perceptions / attitudes about [TOPIC] one might want to investigate in a survey (including polls and open-ended questions) that could go to a representative sample of the globe? Provide the research questions themselves, not the specific survey questions. In particular, what are some questions that are specifically yet "unanswered" in by other public surveys?

Save the research questions in the file GD[N]_research_questions.md.

----


# Prompt for generating Human Readable Survey

Given the survey questions shown in the attached GD[N]_discussion_guide.csv, generate a human-readable version of the survey in markdown format as a numbered list of the survey questions or text ('speaks') and any options provided for each question, in precisely this style:

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


Save this file to GD[N]_survey_questions.md.

----

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