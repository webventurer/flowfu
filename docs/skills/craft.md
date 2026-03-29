# /craft — Structured prompt generation

A prompt that creates a prompt. Give it a topic; it produces a fully structured prompt using the C.R.A.F.T. framework that you then paste into a fresh LLM conversation to get exceptional output.

## The CRAFT framework

Each letter represents a section of the generated prompt:

| Section | Purpose | Key requirement |
|:--------|:--------|:----------------|
| **C** — Context | Frame the situation and what knowledge the LLM should reference | Comprehensive: goals, expertise areas, domain knowledge, references |
| **R** — Role | Define the LLM's persona, experience, and expertise level | Industry-leading expert with 20+ years of relevant experience |
| **A** — Action | Numbered sequential steps the LLM should follow | Ordered list that maximises success; include "fill in the blank" elements where the user hasn't provided specifics |
| **F** — Format | Structural arrangement of the output | Specify: essay, table, code, markdown, summary, list, etc. |
| **T** — Target audience | The ultimate consumer of the output | Demographics, geography, language, reading level, preferences |

## How it works

1. You give `/craft` a topic — "create a guide to setting monthly goals"
2. The skill drafts all five CRAFT sections for that topic
3. Placeholders (`[bracketed]`) are added where you haven't specified details
4. You get a complete prompt to paste into a fresh LLM conversation

The two-step workflow is deliberate — the CRAFT prompt *generates* the actual output in a clean context, free from conversation history.

## When to use

- Creating a prompt for any LLM (ChatGPT, Claude, Gemini, etc.)
- Turning a vague idea into a comprehensive, structured prompt
- `/linear:plan-work --craft` uses it automatically to sharpen issue descriptions before drafting

## Key principles

| Principle | What it means |
|:----------|:--------------|
| Comprehensive detail | The best prompts leave nothing to question — goals, expertise, domain knowledge, format, audience, references, examples |
| Fill in the blanks | When the user hasn't specified something, add `[bracketed placeholders]` they can populate |
| Two-step workflow | Step 1: topic → CRAFT prompt. Step 2: paste prompt into fresh conversation → actual output |
| Role elevation | Always make the role an industry-leading expert — this pushes the LLM past average responses |
| Sequential actions | The action section must be a numbered list of steps in the order that maximises success |

## Example

Topic: "Create a guide to setting and achieving monthly goals"

The skill produces a prompt with:
- **Context** framing the guide's purpose (breaking objectives into actionable monthly steps, SMART goals)
- **Role** as a productivity coach with 20+ years of experience
- **Action** as a 7-step sequence (introduction → breakdown → priorities → tracking → examples → obstacles → conclusion)
- **Format** specifying plain text with headings, numbered lists, and practical examples
- **Target audience** defining working professionals aged 25-55, 6th grade reading level

You paste this into a fresh conversation and get output that far exceeds a one-line "write me a guide about monthly goals" prompt.

## Source

Based on the C.R.A.F.T. prompt framework — a meta-prompting technique for generating structured, high-quality LLM prompts. See [The best ChatGPT Prompt I've ever created](https://www.youtube.com/watch?v=ABCqfaTjNd4) for the original source.
