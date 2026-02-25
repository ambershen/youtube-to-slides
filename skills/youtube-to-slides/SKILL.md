---
name: youtube-to-slides
description: >
  Convert a YouTube video into infographic slides. Extracts transcript, segments
  into sections, summarizes, and generates stylized infographic images using Gemini AI.
  4 styles: davinci, magazine, comic, geek. Use when user wants slide summaries from YouTube.
argument-hint: "<youtube-url> [--style davinci|magazine|comic|geek] [--max-sections N]"
allowed-tools: Bash, Read, Write, Glob
context: fork
---

# youtube-to-slides

Convert YouTube videos into beautiful infographic slide decks.

## Argument Parsing

Parse `$ARGUMENTS` to extract:

- **url** (required) — YouTube video URL. Supports formats: `https://youtu.be/ID`, `https://www.youtube.com/watch?v=ID`, `https://youtube.com/watch?v=ID`
- **--style** (optional, default: `davinci`) — One of: `davinci`, `magazine`, `comic`, `geek`
- **--max-sections** (optional, default: `8`) — Maximum number of slide sections to generate. Use `0` for unlimited.
- **--dry-run** (optional) — Show prompts without generating images
- **--ar** (optional, default: `16:9`) — Aspect ratio: `16:9`, `4:3`, or `1:1`

If no URL is provided, ask the user for one. If the URL looks invalid (not a YouTube URL), tell the user and ask for a valid one.

For style guidance, read `references/STYLES.md` in this skill directory.

## Execution Steps

### Step 1: Pre-flight Check

Run the environment check script:

```bash
bash "$SKILL_DIR/scripts/check-env.sh"
```

- If it exits 0, proceed to Step 2.
- If it exits non-zero, read its output for diagnostics:
  - If the virtual environment or package is missing, run the setup script:
    ```bash
    bash "$SKILL_DIR/scripts/setup.sh"
    ```
  - If API keys are missing, tell the user they need to configure their `.env` file in the project root with `GEMINI_API_KEY` and `YOUTUBE_API_KEY`. Link them to `references/TROUBLESHOOTING.md` for setup instructions.
  - After fixing, re-run `check-env.sh` to confirm.

### Step 2: Run the Pipeline

Build the command from parsed arguments and run:

```bash
bash "$SKILL_DIR/scripts/run.sh" "<url>" --style <style> --max-sections <max_sections> --ar <ar>
```

Add `--dry-run` flag if requested.

**This takes 3-5 minutes for a full run.** Inform the user that generation is in progress.

### Step 3: Present Results

After successful completion:

1. Determine the video ID from the URL (the 11-character ID, e.g. `twzLDx9iers` from `https://youtu.be/twzLDx9iers`)
2. Read `output/<video_id>/metadata.json` to get the list of generated slides
3. Present a summary to the user:
   - Video title and channel
   - Style used
   - Number of slides generated
   - List each slide with its title and file path
4. Tell the user they can view the slides:
   ```bash
   open output/<video_id>/
   ```

### Error Handling

If the pipeline fails, check output for common errors and consult `references/TROUBLESHOOTING.md`:

- **429 Rate Limit** — Gemini rate limit hit. The tool has built-in retry logic. If it still fails, suggest waiting 60 seconds and retrying.
- **No transcript available** — The video may not have captions. Inform the user.
- **Invalid URL** — Ask the user for a valid YouTube URL.
- **API key errors** — Guide user to set up their `.env` file.

## Variable Reference

- `$SKILL_DIR` — Absolute path to this skill's directory (`.claude/skills/youtube-to-slides/`)
- `$ARGUMENTS` — Raw argument string passed by the user after `/youtube-to-slides`
