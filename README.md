# youtube-to-slides

Convert YouTube videos into infographic slides using Gemini AI. Extracts the transcript, segments it into sections, summarizes each, and generates stylized infographic images.

7 visual styles: **davinci**, **magazine**, **comic**, **geek**, **chalkboard**, **collage**, **newspaper**

![davinci](output/style_samples/sample_davinci.png)
![magazine](output/style_samples/sample_magazine.png)
![comic](output/style_samples/sample_comic.png)
![geek](output/style_samples/sample_geek.png)
![chalkboard](output/style_samples/sample_chalkboard.png)
![collage](output/style_samples/sample_collage.png)
![newspaper](output/style_samples/sample_newspaper.png)

## Compatibility

This is an [Agent Skill](https://agentskills.io/specification) — it works with any agent that supports the open Agent Skills standard:

- [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)
- [Cursor](https://cursor.com/docs/context/skills)
- [TRAE](https://trae.ai/)
- [VS Code (GitHub Copilot)](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
- And any other agent that supports [Agent Skills](https://skills.sh/)

## Install

```bash
npx skills add ambershen/youtube-to-slides
```

That's it. The [skills CLI](https://skills.sh/docs/cli) downloads the skill and configures it for your agent.

After installing, run the setup script to create the virtual environment and install Python dependencies:

```bash
bash skills/youtube-to-slides/scripts/setup.sh
```

## Get Your API Key

This skill requires one API key (free).

### Gemini API Key (for AI summarization and image generation)

The Gemini API free tier works without a credit card.

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click **Create API Key**
4. Copy the key

Video metadata is fetched via [yt-dlp](https://github.com/yt-dlp/yt-dlp) — no API key needed.

### Configure Your Key

Create a `.env` file in the skill directory:

```bash
cd skills/youtube-to-slides
cp .env.example .env
```

Edit `.env` and add your key:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

## Usage

### With Your Agent (Recommended)

Just ask naturally in any supported agent:

> Generate slides from https://youtu.be/VIDEO_ID in comic style

> Convert this YouTube video to slides: https://youtube.com/watch?v=VIDEO_ID

> Make magazine-style infographics from https://youtu.be/VIDEO_ID with 5 slides

The agent will run the pipeline and present the results.

### CLI (Direct)

```bash
cd skills/youtube-to-slides
source .venv/bin/activate

# Basic — davinci style
yt-slides "https://youtu.be/VIDEO_ID"

# Choose a style
yt-slides "https://youtu.be/VIDEO_ID" --style comic

# Limit number of slides
yt-slides "https://youtu.be/VIDEO_ID" --style magazine --max-sections 5

# Change aspect ratio (default: 16:9)
yt-slides "https://youtu.be/VIDEO_ID" --ar 1:1

# Dry run — preview prompts without generating images
yt-slides "https://youtu.be/VIDEO_ID" --dry-run
```

### All CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `--style` | `davinci` | Style preset: `davinci`, `magazine`, `comic`, `geek`, `chalkboard`, `collage`, `newspaper` |
| `--max-sections` | `0` (unlimited) | Maximum number of slides to generate |
| `--ar` | `16:9` | Aspect ratio: `16:9`, `4:3`, `1:1` |
| `--output`, `-o` | `./output` | Output directory |
| `--dry-run` | off | Preview prompts without generating images |
| `--gemini-key` | from `.env` | Gemini API key (overrides env) |

## Output

Slides are saved to `output/<video_id>/`:

```
output/
└── GcNu6wrLTJc/
    ├── metadata.json
    ├── 01_introduction_problem_statement.png
    ├── 02_todays_sponsor_daytona.png
    ├── 03_understanding_ai_context_hierarchy.png
    └── ...
```

`metadata.json` contains video info and a mapping of section titles to image files.

## Styles

### davinci (default)
Renaissance-era scientific manuscript. Hand-drawn ink on aged parchment with anatomical diagrams and cross-hatching. Best for educational, science, and history content.

### magazine
Fashion editorial magazine spread. Big dramatic headlines, asymmetrical layouts mixing photography and text, styled pull quotes, and drop caps. Inspired by Vogue and Harper's Bazaar. Best for business, interviews, and visually luxurious content.

### comic
Vibrant pop art. Bold outlines, Ben-Day dots, speech bubbles, and starburst shapes. Best for entertainment, tutorials, and casual content.

### geek
College bulletin board. Corkboard background with sticky notes, marker text, doodles, and red string connections. Best for study notes, brainstorming, and informal content.

### chalkboard
Real black classroom chalkboard. All text handwritten in chalk on matte black slate with a worn wooden frame, natural hand-pressure variation, and faint ghosting of erased content. Best for lectures, technical explanations, and academic topics.

### collage
Dreamcore ASCII collage. All text handwritten. Surreal mixed-media layering ASCII art, handwritten scrawls, cut-out imagery, and glitched pastel gradients on varied backgrounds. Best for tech/internet culture, creative essays, and experimental content.

### newspaper
Vintage newspaper broadsheet. Crisp black and white — bold serif headlines, multi-column layouts, and engraving-style illustrations on clean white newsprint. Best for history, journalism, and authoritative presentations.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `429 Too Many Requests` | Built-in retry handles this. If persistent, wait 60s or reduce `--max-sections` |
| No transcript available | Video needs captions enabled (auto-generated or manual) |
| Invalid URL | Use `youtu.be/ID` or `youtube.com/watch?v=ID` format |
| API key errors | Check your `.env` file has valid keys |
| `yt-slides` not found | Run `bash skills/youtube-to-slides/scripts/setup.sh` |

See [TROUBLESHOOTING.md](skills/youtube-to-slides/references/TROUBLESHOOTING.md) for more details.

## License

MIT
