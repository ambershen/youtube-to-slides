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
            "Fashion editorial magazine spread — the kind of page you'd find in Vogue, Harper's Bazaar, or W Magazine. "
            "Big, dramatic headlines in bold condensed or elegant serif type with extreme size contrast. "
            "Asymmetrical layout that mixes photography, text blocks, and pull quotes in an artful, deliberately "
            "off-balance composition. Every element is placed with editorial intention. "
            "The overall feel is high-fashion, confident, and visually luxurious — a spread you'd tear out and pin on your wall."
        ),
        "colors": (
            "Sophisticated palette — either stark black and white with a single pop color (crimson red, electric pink, "
            "or gold), or a rich tonal palette (deep burgundy, cream, and charcoal). "
            "Large photographic or illustrated imagery dominates with text overlaid or wrapping around it. "
            "Generous use of white space as a design element. Accent color used for drop caps, pull quotes, or a single bold word."
        ),
        "layout": (
            "Asymmetrical editorial spread. An oversized headline — bold, condensed, and dramatic — anchors the page, "
            "potentially spanning the full width or set at an angle. "
            "Key points arranged in an elegant column alongside or overlapping a large feature image or illustration. "
            "A styled pull quote in large italic or serif type breaks the layout with quotation marks as design elements. "
            "Summary text set in a refined body font in a narrow column. "
            "Slide number styled as a small folio marker. Mixed type sizes and weights create visual rhythm."
        ),
        "visual_direction": (
            "Include a large editorial-style image or illustration as the visual anchor — a stylized portrait, "
            "an abstract fashion photograph, or a bold graphic composition that relates to the content. "
            "Text wraps around or overlays imagery with confidence. Use drop caps for the first letter of key sections. "
            "Pull quotes are set large and dramatic with thin rule lines above and below. "
            "The composition should feel like an actual magazine page — layered, intentional, and effortlessly stylish."
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
    "chalkboard": {
        "description": (
            "Photograph of a real black chalkboard in a classroom. The board is a true matte black surface "
            "with a worn wooden frame, mounted on a wall under fluorescent lighting. "
            "ALL text is handwritten in chalk — loose, natural, human handwriting with personality. "
            "Authentic hand pressure variation: thick downstrokes, thin upstrokes, chalk skipping on rough slate. "
            "The overall image should look like a photo you'd take of a lecture hall blackboard after "
            "an incredible class, not a digital illustration styled to look like chalk."
        ),
        "colors": (
            "True black chalkboard surface — not green, not dark gray, but the deep matte black of a "
            "well-used classroom blackboard. White chalk is the dominant writing color, with natural "
            "brightness variation where the chalk was pressed harder or lighter. "
            "Occasional use of yellow or pale blue chalk for underlines or circled terms, but sparingly — "
            "most real classrooms only have white chalk. Faint ghosting of previously erased content "
            "visible as gray smudges on the black surface."
        ),
        "layout": (
            "Organic lecture-notes layout that fills the board naturally. Title handwritten large across the "
            "top in firm chalk strokes, underlined once. "
            "Key points flow down the board in handwritten chalk — bullet dashes or numbered lists, slightly "
            "drifting from left to right as a real hand would. "
            "Arrows and lines connect related ideas. A boxed summary near the bottom, also handwritten. "
            "Slide number tucked into the bottom-right corner in casual handwriting. "
            "The wooden chalk tray at the bottom edge of the board is visible with a few chalk stubs "
            "and a felt eraser resting on it."
        ),
        "visual_direction": (
            "ALL text — title, bullet points, summary, labels — must be in handwritten chalk style. "
            "No typed, printed, or digital-looking fonts anywhere. Every letter looks written by a human hand "
            "holding a piece of chalk, with natural inconsistencies in size, spacing, and slant. "
            "Chalk lines have grain texture from the rough slate — not smooth vector strokes. "
            "Diagrams are simple and hand-drawn: boxes, arrows, circles, underlines, brackets. "
            "Some areas show eraser smudges where the board was wiped imperfectly. "
            "Fine chalk dust is visible near the tray. The board has subtle wear patterns and faint "
            "scratches from years of use. No digital effects, glow, or neon — just real chalk on real slate."
        ),
    },
    "collage": {
        "description": (
            "Digital collage with dreamcore and ASCII aesthetics. A surreal mixed-media composition that "
            "layers ASCII art text blocks, handwritten scrawls, cut-out imagery, and glitched gradients. "
            "ALL text is rendered in a loose handwritten style — scratchy, uneven, like someone writing "
            "with a marker on scraps of paper or directly onto the collage surface. "
            "The vibe is late-night internet, liminal spaces, and analog-digital fusion — "
            "like a zine made by an insomniac programmer in a half-dream state. "
            "The overall mood is hypnotic, slightly eerie, and deeply aesthetic."
        ),
        "colors": (
            "Background varies freely — can be light, dark, pastel, or mixed. Options include: washed-out "
            "cream with noise grain, soft pink-lavender gradient, deep navy, pale sky blue, or layered "
            "collage textures with no single dominant tone. "
            "Terminal green (#00FF00) and phosphor amber (#FFB000) appear as accent elements in ASCII art fragments. "
            "Soft pastel washes — lavender, baby pink, pale cyan — bleed through as dreamcore gradients. "
            "Harsh white or black for handwritten text overlays depending on background. "
            "Occasional glitch streaks of magenta or cyan."
        ),
        "layout": (
            "Deliberately fragmented collage layout. Title handwritten large and loose — scrawled in marker "
            "or pen style, placed off-center or at a slight angle. "
            "Key points appear as handwritten snippets on torn paper scraps, translucent overlays, or "
            "directly onto the collage surface at slight rotations. Some have ASCII box-drawing borders "
            "(using ┌─┐│└─┘ characters) around them for contrast. "
            "Summary text handwritten in a terminal-inspired block or on a scrap of lined paper. "
            "Elements overlap and layer at different depths. "
            "Slide number scrawled small in the margin."
        ),
        "visual_direction": (
            "ALL text must be in a handwritten style — messy, human, with natural variation in size and slant. "
            "No clean digital typography anywhere. The handwriting mixes with ASCII art patterns "
            "(box-drawing frames, simple ASCII illustrations, code-like text blocks). "
            "Layer dreamy photographic cutouts of empty hallways, clouds, windows, or geometric shapes. "
            "Apply subtle scanline or CRT screen texture over portions of the image. "
            "Include small visual fragments: a staircase going nowhere, a pixelated eye, a wireframe sphere. "
            "The composition should feel like a curated mood board from a parallel internet, "
            "assembled by hand with scissors and glue."
        ),
    },
    "newspaper": {
        "description": (
            "Vintage newspaper broadsheet from the early 20th century. Black and white print with the "
            "authoritative gravitas of The New York Times or The Times of London circa 1920s-1940s. "
            "Bold serif headlines in large point sizes, dense multi-column text layouts, and detailed "
            "engraving-style illustrations. The paper has a slightly aged, yellowed quality with visible "
            "print texture and ink density variation. "
            "The feel is historic, weighty, and credible — like front-page news from another era."
        ),
        "colors": (
            "Strictly black ink on clean white paper. No color, no yellowing, no sepia, no warm tint. "
            "Pure black and white like a freshly printed broadsheet newspaper. "
            "Rich dense blacks for headlines and engraving illustrations. Medium gray for body text. "
            "Clean white paper background — bright and crisp, not aged or yellowed. "
            "Variation in ink density gives depth: bold blacks for headlines, lighter grays for fine engraving detail."
        ),
        "layout": (
            "Traditional newspaper column layout. A bold, large serif headline spans the full width at top, "
            "possibly with a secondary deck headline in smaller type below it. "
            "Content arranged in 2-3 justified columns with thin vertical rules between them. "
            "Key points set as body text paragraphs or as indented sub-sections with bold lead-ins. "
            "An engraving-style illustration anchors one column or spans two. "
            "Summary set as a pull quote or boxed sidebar with a thin border rule. "
            "Slide number styled as a page/edition number in the header or footer alongside a date line."
        ),
        "visual_direction": (
            "Include detailed engraving-style illustrations — crosshatched portraits, technical diagrams, "
            "architectural views, or allegorical figures rendered in fine black ink lines. "
            "These should look like woodcut or steel-plate engravings reproduced on newsprint. "
            "Use bold serif typography throughout — thick/thin stroke contrast, classic Roman letterforms. "
            "Headlines are big, black, and commanding. Thin hairline rules separate sections. "
            "The overall page should feel like an actual broadsheet newspaper front page: dense with "
            "information, visually structured by typography and column grids, and illustrated with engravings."
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
