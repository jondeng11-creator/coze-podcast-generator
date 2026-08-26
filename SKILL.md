---
name: coze-podcast-generator
description: "Convert written text, articles, or notes into a dual-host (male + female) conversational podcast audio using the Coze voice-podcast plugin. This skill should be used when a user wants to turn any text into a spoken podcast, generate a 双主播播客, 文字转播客, 把文章做成播客, or 文字生成播客音频. It calls the Coze workflow run API, parses the returned audio URL, and downloads the MP3 locally with no background music by design."
agent_created: true
---

# Coze Podcast Generator

Turn any text into a one-man-one-woman conversational podcast MP3 via the
Coze voice-podcast plugin. The output is the raw generated episode only —
no background music, no intro music, no fixed opening/closing lines (those are
intentionally excluded; see "Known Limitations").

## When to use

- User says "把这段文字生成播客", "文字转播客", "生成双主播播客", "把文章做成播客音频",
  or hands over an article / markdown and asks to voice it as a podcast.
- User wants a podcast-style audio from written content using Coze.

## Prerequisites (one-time setup)

1. Build a Coze "语音播客" workflow and obtain three values:
   `workflow_id`, `space_id`, and a personal access token (`pat_...`).
   Full steps and pitfalls are in `references/coze_setup.md`.
2. Provide credentials to the script via ONE of:
   - Environment variables: `COZE_PAT`, `COZE_WORKFLOW_ID`, `COZE_SPACE_ID`
   - A `config.json` next to the script (copy `config.json.example`):
     ```json
     {"pat": "...", "workflow_id": "...", "space_id": "..."}
     ```
   Do NOT hardcode credentials into the script — they are user-private.

## How to use

Run the bundled script `scripts/generate_podcast.py`:

```bash
# From a string
python scripts/generate_podcast.py --text "今天咱们聊一聊……" --out episode.mp3

# From a file / stdin
cat article.md | python scripts/generate_podcast.py --out episode.mp3

# Interactive paste
python scripts/generate_podcast.py --out episode.mp3
```

The script is pure standard library (no `pip install`). It:

1. Reads text from `--text`, stdin, or interactive input.
2. Calls `POST https://api.coze.cn/v1/workflow/run` with `parameters.input = text`.
3. Parses `podcast_url` from the returned `data` JSON.
4. Downloads the MP3 to `--out` (default `podcast.mp3`).

## Known limitations (important)

- The Coze plugin only does **long-text → full episode**. Feeding it a short
  fixed opening/closing line makes it treat that as a topic and expand into a
  rambling off-topic episode. Therefore this skill deliberately generates only
  the body episode; do not try to prepend/append canned opening/closing text.
- `input_text` limit is ~15000 chars per call.
- The audio URL expires in ~3 days — always download and save locally (the
  script does this automatically).
- No BGM by design. For BGM, mix locally with ffmpeg separately.
- Generation is slow; a single call can take up to ~10 minutes. Be patient.

## Reference

- `references/coze_setup.md` — how to build the Coze workflow, get the PAT,
  and troubleshoot (empty data, "input content can not be empty", etc.).
