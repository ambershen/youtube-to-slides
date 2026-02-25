"""Build infographic generation prompts from section summaries."""

from __future__ import annotations

from yt_slides.models import SectionSummary

STYLE_PRESETS: dict[str, dict[str, str]] = {
    "davinci": {
        "description": (
            "Renaissance-era scientific manuscript style inspired by Leonardo da Vinci's notebooks. "
            "Hand-drawn ink illustrations on aged parchment paper with a warm sepia tone. "
            "Text is written in elegant serif calligraphy. Anatomical-style diagrams, "
            "mechanical sketches, and botanical-like illustrations annotate each concept. "
            "Faded ink washes, cross-hatching shading, and mirror-writing decorative flourishes in margins. "
            "The overall feel is a page torn from a genius inventor's private journal."
        ),
        "colors": (
            "Aged yellowed parchment background with dark brown and sepia ink. "
            "Occasional red-brown ink accents for emphasis. Subtle coffee-stain watermarks."
        ),
        "layout": (
            "Asymmetric hand-drawn layout. Title in large ornate calligraphy at top. "
            "Key points scattered with connecting arrows and sketch annotations around them. "
            "Small anatomical or mechanical diagrams interspersed between text blocks. "
            "Context text at bottom in smaller italic script with a decorative border."
        ),
        "visual_direction": (
            "Draw detailed pen-and-ink sketches: gears, pulleys, human figures in motion, "
            "botanical cross-sections, geometric constructions with compass and ruler marks. "
            "Include faint grid lines and measurement notations in the margins."
        ),
    },
    "magazine": {
        "description": (
            "High-end magazine editorial spread. Strictly black and white with dramatic contrast. "
            "Think Monocle magazine meets Swiss International Typographic Style. "
            "Bold Helvetica/Futura-style sans-serif typography with extreme size contrast between headline and body. "
            "Generous negative space. Razor-thin hairline rules separating sections. "
            "Photography-quality halftone dot texture accents. The design breathes sophistication and restraint."
        ),
        "colors": (
            "Pure black and white only. No gray tones except for subtle halftone textures. "
            "Solid black headline text on white, or reversed white text on black blocks. "
            "High contrast, no gradients."
        ),
        "layout": (
            "Grid-based editorial layout with strong vertical and horizontal alignment. "
            "Oversized bold headline dominates the top third. "
            "Key points set in a clean two-column or single-column layout with generous line spacing. "
            "Pull-quote style for the context text — large quotation marks, indented block. "
            "Thin black horizontal rules separate each section. Page number in bottom corner."
        ),
        "visual_direction": (
            "Use abstract geometric shapes — circles, lines, rectangles — as compositional elements, not decoration. "
            "No illustrations or icons. Let typography and whitespace do the work. "
            "If an image element is needed, use a high-contrast black silhouette or halftone dot pattern."
        ),
    },
    "comic": {
        "description": (
            "Vibrant comic book / pop art style infographic. Bold black outlines around everything. "
            "Ben-Day dots, halftone patterns, and explosive starburst shapes. "
            "Speech bubbles and thought clouds for key points. "
            "Dynamic diagonal compositions with action lines and motion effects. "
            "Colors are saturated primaries: red, blue, yellow with black and white. "
            "The feel is energetic, fun, and immediately eye-catching — like a page from a Marvel comic."
        ),
        "colors": (
            "Bright saturated primary colors: bold red, electric blue, sunshine yellow, vivid green. "
            "Thick black outlines and borders. White speech bubbles with black text. "
            "Ben-Day dot patterns fill backgrounds. Starburst shapes in contrasting colors for emphasis."
        ),
        "layout": (
            "Comic panel layout — the slide is divided into dynamic asymmetric panels with thick black borders. "
            "Headline in a large explosive starburst or banner at the top. "
            "Each key point gets its own panel with a small cartoon illustration and speech bubble. "
            "Context text in a narrator box at the bottom with a different background color. "
            "Slide number in a small circle badge."
        ),
        "visual_direction": (
            "Draw cartoon characters reacting to the content — pointing, thinking, excited. "
            "Use comic onomatopoeia (POW, ZAP, BOOM) as decorative elements where appropriate. "
            "Action lines radiate from important points. Include small comic-style icons for each concept."
        ),
    },
    "geek": {
        "description": (
            "College bulletin board / dorm room wall aesthetic. Kraft paper or corkboard background "
            "with content pinned using colorful pushpins and tape. "
            "Mix of handwritten marker text, typed index cards, printed photos, and sticky notes. "
            "Stickers, doodles, highlighter marks, and washi tape scattered around. "
            "The feel is authentic, nerdy, and lovingly chaotic — like a passionate student's study wall. "
            "Think Beautiful Mind meets college dorm meets tech startup whiteboard."
        ),
        "colors": (
            "Warm cork/kraft paper base. Neon sticky notes in pink, yellow, green, blue. "
            "Red and blue marker handwriting. Black Sharpie for headlines. "
            "Highlighter yellow streaks over important words. Colorful pushpin dots."
        ),
        "layout": (
            "Deliberately messy collage layout pinned to a corkboard or kraft paper wall. "
            "Headline scrawled in thick black marker, slightly tilted, at top center. "
            "Key points on individual sticky notes or index cards pinned at slight angles. "
            "Red string connecting related concepts (conspiracy-board style). "
            "Context text on a torn notebook page pinned at the bottom. "
            "Doodles, stars, and exclamation marks in margins."
        ),
        "visual_direction": (
            "Include hand-drawn doodles: stick figures, flowcharts, arrows, stars, lightbulbs, "
            "coffee cup rings, small printed memes or diagrams taped on. "
            "Some elements look like printouts taped to the board, others like handwritten notes. "
            "A pencil or marker casually placed on the board edge."
        ),
    },
}


def build_infographic_prompt(
    summary: SectionSummary,
    video_title: str,
    total_sections: int,
    style: str = "davinci",
) -> str:
    """Build a detailed image generation prompt for one infographic slide."""
    preset = STYLE_PRESETS.get(style, STYLE_PRESETS["davinci"])
    key_points_text = "\n".join(f"  {i+1}. {point}" for i, point in enumerate(summary.key_points))

    return f"""Generate an image of a single infographic slide. Slide {summary.section.index} of {total_sections} from "{video_title}".

=== ART DIRECTION ===
{preset["description"]}

=== COLOR PALETTE ===
{preset["colors"]}

=== COMPOSITION & LAYOUT ===
{preset["layout"]}

=== VISUAL ELEMENTS ===
{preset["visual_direction"]}
Additional visual context from the content: {summary.visual_suggestions}

=== TEXT CONTENT (render exactly as written) ===

TITLE:
"{summary.headline}"

KEY POINTS:
{key_points_text}

SUMMARY:
"{summary.summary}"

SLIDE: {summary.section.index}/{total_sections}

=== CRITICAL RULES ===
- Landscape 16:9 aspect ratio
- Every word of text must be spelled correctly and clearly readable
- The title must be the most prominent text element
- Do NOT add any text beyond what is specified above
- The image must look like a single cohesive infographic poster, not a photograph of a real scene
- Make it visually stunning and highly detailed"""
