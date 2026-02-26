# Troubleshooting

Common errors when running youtube-to-slides and how to fix them.

## API Key Issues

### Missing or invalid GEMINI_API_KEY

**Symptom:** Error mentioning Gemini authentication or missing API key.

**Fix:**
1. Get a Gemini API key at https://aistudio.google.com/apikey
2. Add it to your `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_actual_key_here
   ```

### Video metadata extraction fails (yt-dlp)

**Symptom:** Error fetching video metadata or "Video not found".

**Possible causes:**
- The video is private, age-restricted, or region-locked
- yt-dlp is outdated and YouTube changed its format

**Fix:**
1. Verify the video is publicly accessible in a browser
2. Update yt-dlp to the latest version:
   ```bash
   skills/youtube-to-slides/.venv/bin/pip install --upgrade yt-dlp
   ```

## Rate Limits

### 429 Too Many Requests (Gemini)

**Symptom:** `429` or "Resource exhausted" error during image generation.

**What happens:** The tool has built-in retry logic with exponential backoff for rate limits. It will automatically retry several times.

**If it still fails:**
- Wait 60 seconds and retry the command
- If persistent, you may be hitting the free-tier Gemini rate limit. Consider upgrading your API plan or reducing `--max-sections`

## Transcript Issues

### No transcript available

**Symptom:** Error about missing transcript or captions.

**Cause:** The video doesn't have captions (auto-generated or manual).

**Workarounds:**
- Try a different video that has captions enabled
- Check if the video has captions by looking for the "CC" button on YouTube

## URL Issues

### Invalid YouTube URL

**Symptom:** Error parsing URL or "invalid video ID".

**Supported URL formats:**
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtube.com/watch?v=VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`

**Not supported:**
- Playlist URLs (use a specific video URL instead)
- Channel URLs
- YouTube Shorts URLs (may work but not guaranteed)

## Installation Issues

### yt-slides command not found

**Fix:** Run the setup script:
```bash
bash .claude/skills/youtube-to-slides/scripts/setup.sh
```

### Python version too old

**Symptom:** Setup script reports "Python 3.9+ is required".

**Fix:** Install Python 3.9 or newer from https://www.python.org/downloads/

## Output Issues

### Slides look different than expected

- Each generation produces unique images — Gemini's output is non-deterministic
- Try a different `--style` for a different look
- Use `--dry-run` to preview the prompts before generating
