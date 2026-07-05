---
name: xuexi2
description: Use when the user asks to learn, digest, de-noise, simplify, or turn an article, course note, transcript, tutorial, Feishu document, or pasted text into a beginner-friendly learning note that is readable, actionable, memorable, and transferable.
---

# xuexi2

## Core Standard

Create a pure-beginner learning note that helps the reader understand, act, remember, and transfer the source material.

The final output must be at least as good as the validated reference standard:

- clear enough for a zero-background reader
- preserves all original teaching points, examples, cases, tool names, and caveats
- adds transfer examples only when clearly marked as non-original
- gives a concrete action template plus a filled example
- includes self-check questions with qualified answers
- passes validation before delivery

## Hard Rules

- Do the cleaning step silently. Do not show a cleaning report or artificial confirmation block unless the user explicitly asks for it.
- Do not expose internal workflow labels such as "stage one", "stage two", or "phase". The reader-facing output must read like a polished article.
- Never delete original cases or examples. Keep original examples first, then add transfer examples.
- Mark generated examples as `迁移示例，不是原文案例`.
- If a correction is inferred from context and not certain, add `（？）` after the corrected term.
- Do not invent facts, software behavior, prices, data, or real-world outcomes. If unsure, say it is an analogy or a transfer example.
- Do not promise results such as guaranteed revenue, guaranteed mastery, or instant success.
- Explain English terms, acronyms, and tool names in plain Chinese the first time they matter to understanding.
- Prefer short mobile-friendly paragraphs. Aim for each paragraph under 120 Chinese characters.

## Hidden Workflow

### 1. Silent De-noising

Before writing the learning note:

- remove ads, comments, UI residue, duplicated navigation, scrape leftovers, and irrelevant metadata
- merge broken paragraphs and flattened tables into readable structure
- fix obvious typos only when context is clear; mark uncertain fixes with `（？）`
- preserve every teaching point, original example, case, tool name, boundary, and caveat

This step is internal. Do not output it.

### 2. Reader-Facing Learning Note

Use this order unless the source strongly requires another order:

1. Title
2. `先记住一句话`
   - Put the core conclusion and AI-generated plain-language restatement here.
   - Do not create a separate "AI 代复述" section.
3. `🧭 本文的认知边界`
   - State what this article can and cannot help the reader do.
4. Core concept map
   - Break the source into the main concepts.
   - Use life analogies: `像……一样`.
   - Keep original definitions and tool names, but explain them in beginner language.
5. Original cases and examples
   - Preserve original cases first.
   - Preserve small examples under each concept, not only big project cases.
6. Transfer examples
   - Add 1-3 transfer examples only after original examples.
   - Label each as `迁移示例，不是原文案例`.
7. Beginner confusion points
   - Identify where a beginner may misunderstand.
   - Use `错法` and `对法` pairs.
8. Concrete action
   - Include a task that can be done in about 10 minutes.
   - It must include concrete time, concrete object, and concrete action.
9. Filled example
   - Show one completed example using the action template.
10. Self-check
   - Add 3 questions and qualified answers.
11. Memory card
   - Add a one-minute recap and a short口诀/formula.

### 3. Internal Reading-Experience Pass

Before delivery, optimize the reading experience silently:

- remove visible workflow scaffolding
- move the cognitive boundary near the top
- merge duplicate AI restatement into the core conclusion
- move action and self-check after explanation and examples
- keep paragraphs short
- reduce jargon
- make headings scannable on mobile
- ensure every added example supports learning rather than decoration

Do not write a visible "reading optimization" section.

## Required Output Quality Gates

Before delivering, verify every applicable item. If any item fails, revise before responding.

- No visible internal stage/phase labels.
- Original teaching points are preserved.
- Original cases and examples are preserved.
- Original tool names and caveats are preserved.
- Generated examples are clearly marked as transfer examples, not source facts.
- The note has a core conclusion and cognitive boundary near the top.
- Every important abstract concept has a beginner analogy.
- There is at least one `错法` / `对法` pair for common misunderstanding.
- There is a concrete 10-minute action template.
- There is one filled example.
- There are 3 self-check questions with qualified answers.
- There is a one-minute recap or口诀.
- No paragraph is unnecessarily long; target under 120 Chinese characters.
- No exaggerated promise appears.
- If writing to a document, read back the document and verify the rendered content exists.

Report the validation result briefly in the final response.

## Handling Source Types

- If the user provides pasted text, process it directly.
- If the user provides a Feishu/Lark document or wiki target, use the available Feishu/Lark document skills to read and, when requested, write the result.
- If the content is too long to process safely, ask for a chunk or process one document/section at a time.
- If source logic contradicts itself, add a plain-language warning near the relevant section.

## Quality Floor

If the generated output would score below this floor, keep improving before delivery:

- Understandable by a pure beginner: 85/100 or higher
- Immediate actionability: 85/100 or higher
- Transferability: 85/100 or higher
- Retention/self-check quality: 85/100 or higher
- Mobile reading experience: 90/100 or higher

When in doubt, improve the output rather than explaining why the source is hard.
