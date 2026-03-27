---
name: craft
description: Generate structured CRAFT prompts (Context, Role, Action, Format, Target audience) that produce high-quality LLM outputs. Use when creating prompts for ChatGPT, Claude, or other LLMs. Triggers on "craft", "craft prompt", "create a prompt", "prompt generation".
---

# Craft

> Generate structured prompts using the C.R.A.F.T. framework — Context, Role, Action, Format, Target audience — to produce LLM outputs that far exceed typical responses.

---

## When to use

- Creating a prompt for any LLM (ChatGPT, Claude, Gemini, etc.)
- User needs a detailed, structured prompt for a specific topic
- Turning a vague idea into a comprehensive prompt

## When NOT to use

- Simple one-line questions that don't need structure
- Tasks where the user already has a complete prompt

---

## Quick reference

<mark>**A CRAFT prompt is a prompt that creates a prompt.** You give it a topic; it produces a fully structured prompt with all five CRAFT sections that the user then pastes into a fresh LLM conversation to get exceptional output.</mark>

---

## The CRAFT framework

Each letter represents a section of the generated prompt:

| Section | Purpose | Key requirement |
|:--------|:--------|:----------------|
| **C** — Context | Frame the situation and what knowledge the LLM should reference | Comprehensive: goals, expertise areas, domain knowledge, references |
| **R** — Role | Define the LLM's persona, experience, and expertise level | Industry-leading expert with 20+ years of relevant experience |
| **A** — Action | Numbered sequential steps the LLM should follow | Ordered list that maximises success; include "fill in the blank" elements where the user hasn't provided specifics |
| **F** — Format | Structural arrangement of the output | Specify: essay, table, code, markdown, summary, list, etc. |
| **T** — Target audience | The ultimate consumer of the output | Demographics, geography, language, reading level, preferences |

---

## Process

1. **Receive the topic.** If the user doesn't provide a topic or theme, ask for it before proceeding
2. **Draft all five CRAFT sections** for the topic
3. **Add fill-in-the-blank elements** (in brackets) for any details the user hasn't specified
4. **Review the prompt** — ensure it is thorough, leaves nothing to question, and follows the example format below
5. **Present the complete CRAFT prompt** for the user to copy into a fresh LLM conversation
6. **Save the prompt** to `research/craft-prompts/YYYYMMDD-slugified-topic.md` in markdown format (headings per CRAFT section, emphasis hierarchy applied)

---

## Template

Paste this meta-prompt into a fresh LLM conversation, then provide your topic when asked:

```text
CONTEXT:
We are going to create one of the best LLM prompts ever
written. The best prompts include comprehensive details to fully
inform the Large Language Model of the prompt's: goals, required
areas of expertise, domain knowledge, preferred format, target
audience, references, examples, and the best approach to accomplish
the objective. Based on this and the following information, you
will be able write this exceptional prompt.

ROLE:
You are an LLM prompt generation expert. You are known for creating
extremely detailed prompts that result in LLM outputs far exceeding
typical LLM responses. The prompts you write leave nothing to
question because they are both highly thoughtful and extensive.

ACTION:
1) Before you begin writing this prompt, you will first look to
   receive the prompt topic or theme. If I don't provide the topic
   or theme for you, please request it.
2) Once you are clear about the topic or theme, please also review
   the Format and Example provided below.
3) If necessary, the prompt should include "fill in the blank"
   elements for the user to populate based on their needs.
4) Take a deep breath and take it one step at a time.
5) Once you've ingested all of the information, write the best
   prompt ever created.

FORMAT:
For organizational purposes, you will use an acronym called
"C.R.A.F.T." where each letter of the acronym CRAFT represents a
section of the prompt. Your format and section descriptions for
this prompt development are as follows:

- Context: This section describes the current context that outlines
  the situation for which the prompt is needed. It helps the LLM
  understand what knowledge and expertise it should reference when
  creating the prompt.
- Role: This section defines the type of experience the LLM has,
  its skill set, and its level of expertise relative to the prompt
  requested. In all cases, the role described will need to be an
  industry-leading expert with more than two decades of relevant
  experience and thought leadership.
- Action: This is the action that the prompt will ask the LLM to
  take. It should be a numbered list of sequential steps that will
  make the most sense for an LLM to follow in order to maximize
  success.
- Format: This refers to the structural arrangement or presentation
  style of the LLM's generated content. It determines how
  information is organized, displayed, or encoded to meet specific
  user preferences or requirements. Format types include: An essay,
  a table, a coding language, plain text, markdown, a summary, a
  list, etc.
- Target Audience: This will be the ultimate consumer of the output
  that your prompt creates. It can include demographic information,
  geographic information, language spoken, reading level,
  preferences, etc.

TARGET AUDIENCE:
The target audience for this prompt creation is Anthropic Claude
or any other suitable LLM (Google Gemini, ChatGPT, etc.). The
generated prompt may also serve as the starting point for a
deeper research process such as Google Gemini Deep Research.

Please reference the example I have just provided for your output.
Again, take a deep breath and take it one step at a time.
```

---

## Example output

Topic given: "Create a guide to setting and achieving monthly goals." The meta-prompt produces this CRAFT prompt:

```text
CONTEXT:
You are tasked with creating a detailed guide to help individuals
set, track, and achieve monthly goals. The purpose of this guide
is to break down larger objectives into manageable, actionable
steps that align with a person's overall vision for the year. The
focus should be on maintaining consistency, overcoming obstacles,
and celebrating progress while using proven techniques like SMART
goals (Specific, Measurable, Achievable, Relevant, Time-bound).

ROLE:
You are an expert productivity coach with over two decades of
experience in helping individuals optimize their time, define clear
goals, and achieve sustained success. You are highly skilled in
habit formation, motivational strategies, and practical planning
methods. Your writing style is clear, motivating, and actionable,
ensuring readers feel empowered and capable of following through
with your advice.

ACTION:
1. Begin with an engaging introduction that explains why setting
   monthly goals is effective for personal and professional growth.
   Highlight the benefits of short-term goal planning.
2. Provide a step-by-step guide to breaking down larger annual
   goals into focused monthly objectives.
3. Offer actionable strategies for identifying the most important
   priorities for each month.
4. Introduce techniques to maintain focus, track progress, and
   adjust plans if needed.
5. Include examples of monthly goals for common areas of life
   (e.g., health, career, finances, personal development).
6. Address potential obstacles, like procrastination or unexpected
   challenges, and how to overcome them.
7. End with a motivational conclusion that encourages reflection
   and continuous improvement.

FORMAT:
Write the guide in plain text, using clear headings and subheadings
for each section. Use numbered or bulleted lists for actionable
steps and include practical examples or case studies to illustrate
your points.

TARGET AUDIENCE:
The target audience includes working professionals and
entrepreneurs aged 25-55 who are seeking practical, straightforward
strategies to improve their productivity and achieve their goals.
They are self-motivated individuals who value structure and clarity
in their personal development journey. They prefer reading at a
6th grade level.

-End example-

Please reference the example I have just provided for your output.
Again, take a deep breath and take it one step at a time.
```

---

## Key principles

| Principle | What it means |
|:----------|:--------------|
| Comprehensive detail | The best prompts leave nothing to question — include goals, expertise, domain knowledge, format, audience, references, and examples |
| Fill in the blanks | When the user hasn't specified something, add `[bracketed placeholders]` they can populate before using the prompt |
| Two-step workflow | Step 1: user gives you a topic → you generate the CRAFT prompt. Step 2: user pastes that prompt into a fresh conversation to get the actual output |
| Role elevation | Always make the role an industry-leading expert — this pushes the LLM past average responses |
| Sequential actions | The action section must be a numbered list of steps in the order that maximises success |

---

## Cross-references

| Skill | Relationship |
|:------|:-------------|
| [prompt-generation](../prompt-generation/SKILL.md) | Related — OODA loop methodology for prompt creation |

---

## Source

Based on the C.R.A.F.T. prompt framework — a meta-prompting technique for generating structured, high-quality LLM prompts.

- [The best ChatGPT Prompt I've ever created](https://www.youtube.com/watch?v=ABCqfaTjNd4) — the original video (2 months of curation)

---

## The governing principle

> A prompt that creates a prompt: give it a topic, get back a fully structured CRAFT prompt that consistently produces exceptional LLM output.
