# English Coach

English Coach is a compact Hermes skill for practical English learning.

It handles:

- Translation: `en:` and `zh:`
- Word cards: `word:` and `words:`
- Pronunciation practice: `say:` and `shadow:`
- Correction and polishing: `fix:` and `polish:`
- Optional TTS audio and flashcard images when Hermes tools are available

**Author:** Rac 🦝

## Install

Clone this repository directly into a Hermes skills folder:

```bash
git clone <repo-url> ~/.hermes/skills/openclaw-imports/english-coach
```

Then use the skill by name:

```text
english-coach
```

## Quick examples

```text
word: plausible
words: paste an English paragraph here
say: how are you doing?
fix: I goed to store
en: 我想确认一下这个方案是否合理
zh: That sounds like a plausible explanation.
polish: Thanks for your help
```

## Files

```text
SKILL.md
references/cefr.md
references/EFLLex_NLP4J
```

## Notes

- Text output comes first.
- Audio/image generation is optional and tool-dependent.
- Sensitive/private text, credentials, legal/medical text, and personal data stay text-only by default.
