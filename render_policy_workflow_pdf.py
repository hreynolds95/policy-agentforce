from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/hreynolds/Documents/policy agentforce")
PDF_PATH = ROOT / "block_policy_lifecycle_workflow.pdf"
PNG_PATH = ROOT / "block_policy_lifecycle_workflow.png"

WIDTH = 3200
HEIGHT = 1900
MARGIN = 80
TITLE_Y = 55
LANE_GAP = 26
LANE_HEADER_W = 290
STAGE_GAP = 18
STAGE_W = 315
BOX_PAD_X = 18
BOX_PAD_Y = 16


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


FONT_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

TITLE_FONT = load_font(FONT_BOLD, 44)
SUBTITLE_FONT = load_font(FONT_REG, 23)
LANE_FONT = load_font(FONT_BOLD, 30)
BOX_TITLE_FONT = load_font(FONT_BOLD, 24)
BOX_BODY_FONT = load_font(FONT_REG, 19)
NOTE_FONT = load_font(FONT_REG, 18)


COLORS = {
    "bg": "#F7F7F5",
    "title": "#0F172A",
    "subtitle": "#334155",
    "border": "#CBD5E1",
    "arrow": "#475569",
    "owner_lane": "#E0F2FE",
    "owner_header": "#0284C7",
    "gov_lane": "#ECFCCB",
    "gov_header": "#4D7C0F",
    "agent_lane": "#FCE7F3",
    "agent_header": "#BE185D",
    "owner_box": "#F8FDFF",
    "gov_box": "#F9FFF0",
    "agent_box": "#FFF7FB",
    "box_outline": "#94A3B8",
    "footer": "#475569",
}


STAGES = [
    {
        "owner": ("Trigger", [
            "Net new document",
            "Annual review",
            "Off-cycle change",
            "Retirement, deferment, or exception",
        ]),
        "gov": ("Inventory context", [
            "LogicGate SOR holds current inventory",
            "Go/Policy and prior approvals available",
        ]),
        "agent": ("Review calendar monitor", [
            "Flags due reviews and change triggers",
        ]),
    },
    {
        "owner": ("Tollgate 1: Intake prep", [
            "Check Block and subsidiary documents",
            "Confirm domain, scope, owner or delegate",
            "Submit new document or change request",
        ]),
        "gov": ("Tollgate 1: Intake review", [
            "Policy Team confirms in-scope document type",
            "Conflict check and reuse before net new drafting",
            "Confirm template and lifecycle path",
        ]),
        "agent": ("Intake and conflict-check subagent", [
            "Searches for overlap and recommends policy vs standard",
        ]),
    },
    {
        "owner": ("Tollgate 2: Draft or revise", [
            "Use approved Go/Policy template",
            "Draft in English and link related documents",
            "Retain clean and redline versions",
        ]),
        "gov": ("Lifecycle controls", [
            "Set domain, tier, cadence, metadata, and ownership",
            "Record in LogicGate SOR tracking",
        ]),
        "agent": ("Drafting and template-QA subagent", [
            "Prefills required sections and checks style or hierarchy gaps",
        ]),
    },
    {
        "owner": ("Stakeholder review", [
            "Legal, SMEs, and stakeholder reviewers comment",
            "Owner or delegate resolves feedback and keeps audit trail",
        ]),
        "gov": ("Tollgate 3: QC review", [
            "Policy Team runs the PoP QC checklist",
            "Checks required sections, scope, retention, linked documents, approvals",
        ]),
        "agent": ("Review orchestrator and QC subagent", [
            "Summarizes comments, tracks redlines, and validates checklist readiness",
        ]),
    },
    {
        "owner": ("Owner attestation", [
            "Owner attests to content",
            "Provide clean copy, redline, and change summary for major rewrites",
        ]),
        "gov": ("Tollgate 4: Approval routing", [
            "Route by tier",
            "Tier 1 board or committee path",
            "Tier 2 committee or leadership path",
            "Tier 3 leadership path",
        ]),
        "agent": ("Approval-packet subagent", [
            "Builds routing package, summaries, and evidence set",
        ]),
    },
    {
        "owner": ("Implementation and awareness", [
            "Maintain implementation plan",
            "Drive stakeholder communications, training, and awareness",
        ]),
        "gov": ("Publication and storage", [
            "Publish to LogicGate SOR and Go/Policy",
            "Store approvals, redlines, and revision history",
        ]),
        "agent": ("Publication and audit-trail subagent", [
            "Verifies metadata, approvals, and upload readiness",
        ]),
    },
    {
        "owner": ("Ongoing maintenance", [
            "Annual review",
            "Off-cycle material or immaterial change",
            "Exceptions, deferments, and retirement requests",
        ]),
        "gov": ("Governance reporting and maintenance", [
            "Monthly reporting and CPC escalation as needed",
            "Track extensions, exceptions, renewals, archival, and retirement",
        ]),
        "agent": ("Exception and deferment tracker", [
            "Tracks approvals, renewal dates, and retention evidence",
        ]),
    },
]


def draw_wrapped_text(draw, text, font, fill, box, line_spacing=6, align="left"):
    x1, y1, x2, y2 = box
    width = x2 - x1
    avg_char_width = max(font.size * 0.52, 8)
    max_chars = max(int(width / avg_char_width), 8)
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        lines.extend(wrap(paragraph, width=max_chars))
    y = y1
    for line in lines:
        if y > y2:
            break
        if align == "center":
            bbox = draw.textbbox((0, 0), line, font=font)
            line_w = bbox[2] - bbox[0]
            tx = x1 + (width - line_w) / 2
        else:
            tx = x1
        draw.text((tx, y), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line or "Ag", font=font)
        y += (bbox[3] - bbox[1]) + line_spacing
    return y


def draw_box(draw, rect, title, bullets, fill, outline):
    x1, y1, x2, y2 = rect
    draw.rounded_rectangle(rect, radius=22, fill=fill, outline=outline, width=3)
    title_end = draw_wrapped_text(
        draw,
        title,
        BOX_TITLE_FONT,
        COLORS["title"],
        (x1 + BOX_PAD_X, y1 + BOX_PAD_Y, x2 - BOX_PAD_X, y1 + 80),
        line_spacing=4,
    )
    draw.line((x1 + 16, title_end + 4, x2 - 16, title_end + 4), fill=outline, width=2)
    text = "\n".join([f"- {item}" for item in bullets])
    draw_wrapped_text(
        draw,
        text,
        BOX_BODY_FONT,
        COLORS["subtitle"],
        (x1 + BOX_PAD_X, title_end + 18, x2 - BOX_PAD_X, y2 - BOX_PAD_Y),
        line_spacing=5,
    )


def draw_arrow(draw, start, end, color, width=5, head=16):
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    if x2 >= x1:
        pts = [(x2, y2), (x2 - head, y2 - head / 2), (x2 - head, y2 + head / 2)]
    else:
        pts = [(x2, y2), (x2 + head, y2 - head / 2), (x2 + head, y2 + head / 2)]
    draw.polygon(pts, fill=color)


def main():
    image = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg"])
    draw = ImageDraw.Draw(image)

    draw.text((MARGIN, TITLE_Y), "Block Compliance Policy on Policies", font=TITLE_FONT, fill=COLORS["title"])
    draw.text(
        (MARGIN, TITLE_Y + 58),
        "Policy lifecycle workflow aligned to February 18, 2026 PoP, separated by Document Owner and Compliance Governance interfaces.",
        font=SUBTITLE_FONT,
        fill=COLORS["subtitle"],
    )

    lane_top = 165
    lane_h = 430
    agent_lane_h = 300

    lanes = [
        ("Document Owner UI", lane_top, lane_h, COLORS["owner_lane"], COLORS["owner_header"], COLORS["owner_box"]),
        ("Compliance Governance / Policy Team UI (LogicGate SOR)", lane_top + lane_h + LANE_GAP, lane_h, COLORS["gov_lane"], COLORS["gov_header"], COLORS["gov_box"]),
        ("Supporting Subagents", lane_top + 2 * (lane_h + LANE_GAP), agent_lane_h, COLORS["agent_lane"], COLORS["agent_header"], COLORS["agent_box"]),
    ]

    stage_x0 = MARGIN + LANE_HEADER_W + 24
    y_map = {}

    for idx, (label, y, h, lane_fill, header_fill, box_fill) in enumerate(lanes):
        draw.rounded_rectangle((MARGIN, y, WIDTH - MARGIN, y + h), radius=28, fill=lane_fill, outline=COLORS["border"], width=3)
        draw.rounded_rectangle((MARGIN + 10, y + 10, MARGIN + LANE_HEADER_W, y + h - 10), radius=24, fill=header_fill)
        draw_wrapped_text(
            draw,
            label,
            LANE_FONT,
            "white",
            (MARGIN + 32, y + 34, MARGIN + LANE_HEADER_W - 20, y + h - 20),
            line_spacing=6,
        )

        box_y1 = y + 26
        box_y2 = y + h - 26
        if idx == 2:
            box_y1 = y + 38
            box_y2 = y + h - 32

        lane_key = "owner" if idx == 0 else "gov" if idx == 1 else "agent"
        y_map[lane_key] = (box_y1, box_y2, box_fill)

    for i, stage in enumerate(STAGES):
        x1 = stage_x0 + i * (STAGE_W + STAGE_GAP)
        x2 = x1 + STAGE_W

        owner_y1, owner_y2, owner_fill = y_map["owner"]
        gov_y1, gov_y2, gov_fill = y_map["gov"]
        agent_y1, agent_y2, agent_fill = y_map["agent"]

        draw_box(draw, (x1, owner_y1, x2, owner_y2), stage["owner"][0], stage["owner"][1], owner_fill, COLORS["box_outline"])
        draw_box(draw, (x1, gov_y1, x2, gov_y2), stage["gov"][0], stage["gov"][1], gov_fill, COLORS["box_outline"])
        draw_box(draw, (x1, agent_y1, x2, agent_y2), stage["agent"][0], stage["agent"][1], agent_fill, COLORS["box_outline"])

        if i < len(STAGES) - 1:
            nx1 = stage_x0 + (i + 1) * (STAGE_W + STAGE_GAP)
            for mid_y in (
                (owner_y1 + owner_y2) / 2,
                (gov_y1 + gov_y2) / 2,
                (agent_y1 + agent_y2) / 2,
            ):
                draw_arrow(draw, (x2 + 6, mid_y), (nx1 - 8, mid_y), COLORS["arrow"], width=4, head=15)

    loop_start_x = stage_x0 + (len(STAGES) - 1) * (STAGE_W + STAGE_GAP) + STAGE_W / 2
    loop_end_x = stage_x0 + STAGE_W / 2
    loop_y = HEIGHT - 125
    owner_mid_y = (y_map["owner"][0] + y_map["owner"][1]) / 2
    draw.line((loop_start_x, y_map["gov"][1] + 8, loop_start_x, loop_y), fill=COLORS["arrow"], width=4)
    draw.line((loop_start_x, loop_y, loop_end_x, loop_y), fill=COLORS["arrow"], width=4)
    draw.line((loop_end_x, loop_y, loop_end_x, owner_mid_y), fill=COLORS["arrow"], width=4)
    draw.polygon(
        [(loop_end_x, owner_mid_y), (loop_end_x - 10, owner_mid_y + 18), (loop_end_x + 10, owner_mid_y + 18)],
        fill=COLORS["arrow"],
    )
    draw.text(
        (loop_end_x + 20, loop_y - 40),
        "Annual review, off-cycle change, or retirement restarts the lifecycle",
        font=NOTE_FONT,
        fill=COLORS["footer"],
    )

    footer = (
        "Source: Block 'Compliance Policy on Policies' (Last Approval Date: February 18, 2026). "
        "Subagents prepare, validate, route, and monitor, but final approvals remain with Owners, "
        "Compliance Leadership, CPC, and Boards per the PoP."
    )
    draw_wrapped_text(
        draw,
        footer,
        NOTE_FONT,
        COLORS["footer"],
        (MARGIN, HEIGHT - 85, WIDTH - MARGIN, HEIGHT - 20),
        line_spacing=4,
    )

    image.save(PNG_PATH, "PNG")
    image.save(PDF_PATH, "PDF", resolution=300.0)
    print(PDF_PATH)
    print(PNG_PATH)


if __name__ == "__main__":
    main()
