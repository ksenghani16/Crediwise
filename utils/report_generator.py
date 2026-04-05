"""
utils/report_generator.py

Crediwise — Full PDF Report Generator using ReportLab.
Includes: Risk Deep-Dive, Stress Timeline, Plan Suggestions, Plan Comparison, Key Insights.

Install:  pip install reportlab
"""

from __future__ import annotations
import io
import math
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, String, Circle, Line
from reportlab.graphics import renderPDF

# ── Brand colours ─────────────────────────────────────────────────────────────
NAVY   = colors.HexColor("#003399")
DARK   = colors.HexColor("#1a2540")
SLATE  = colors.HexColor("#475569")
LIGHT  = colors.HexColor("#f0f5ff")
GREEN  = colors.HexColor("#15803d")
GREEN_BG = colors.HexColor("#f0fdf4")
AMBER  = colors.HexColor("#b45309")
AMBER_BG = colors.HexColor("#fffbeb")
RED    = colors.HexColor("#dc2626")
RED_BG = colors.HexColor("#fff1f2")
BLUE   = colors.HexColor("#1d4ed8")
BLUE_BG = colors.HexColor("#eff6ff")
WHITE  = colors.white
BORDER = colors.HexColor("#c7d7ff")
GRID   = colors.HexColor("#e2e8f0")

PAGE_W, PAGE_H = A4
MARGIN = 18 * mm


def _fmt(n: float) -> str:
    try:
        return f"\u20b9{float(n):,.0f}"
    except Exception:
        return str(n)


def _risk_color(score: int) -> colors.Color:
    if score < 35:
        return GREEN
    elif score < 60:
        return AMBER
    return RED


def _risk_bg(score: int) -> colors.Color:
    if score < 35:
        return GREEN_BG
    elif score < 60:
        return AMBER_BG
    return RED_BG


def _risk_label(score: int) -> str:
    if score < 35:
        return "Low Risk"
    elif score < 60:
        return "Moderate Risk"
    return "High Risk"


def _rc_hex(score: int) -> str:
    if score < 35:
        return "#15803d"
    elif score < 60:
        return "#b45309"
    return "#dc2626"


def _section_header(title: str, W: float) -> Table:
    """Creates a navy section header bar."""
    tbl = Table(
        [[Paragraph(title, ParagraphStyle("sh", fontSize=11, fontName="Helvetica-Bold",
                                          textColor=WHITE, leading=14))]],
        colWidths=[W],
    )
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return tbl


def _calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    if annual_rate == 0:
        return principal / tenure_months
    r = annual_rate / (12 * 100)
    return principal * r * (1 + r) ** tenure_months / ((1 + r) ** tenure_months - 1)


def _build_gauge_drawing(score: int, width: float = 160, height: float = 90) -> Drawing:
    """Draw a simple semicircular risk gauge."""
    d = Drawing(width, height)
    cx, cy = width / 2, height - 10
    r_outer, r_inner = height * 0.85, height * 0.5

    # Background arc segments (simplified as rectangles)
    segments = [
        (0, 35, "#22c55e"),
        (35, 60, "#f59e0b"),
        (60, 100, "#ef4444"),
    ]
    for seg_start, seg_end, hex_col in segments:
        # Draw arc approximation using multiple small lines
        start_angle = 180 - (seg_start / 100) * 180
        end_angle   = 180 - (seg_end / 100) * 180
        steps = max(1, int(abs(end_angle - start_angle)))
        col = colors.HexColor(hex_col)
        for i in range(steps):
            a1 = math.radians(start_angle - i * (start_angle - end_angle) / steps)
            a2 = math.radians(start_angle - (i + 1) * (start_angle - end_angle) / steps)
            x1o, y1o = cx + r_outer * math.cos(a1), cy + r_outer * math.sin(a1)
            x2o, y2o = cx + r_outer * math.cos(a2), cy + r_outer * math.sin(a2)
            x1i, y1i = cx + r_inner * math.cos(a1), cy + r_inner * math.sin(a1)
            x2i, y2i = cx + r_inner * math.cos(a2), cy + r_inner * math.sin(a2)
            from reportlab.graphics.shapes import Polygon
            d.add(Polygon([x1o, y1o, x2o, y2o, x2i, y2i, x1i, y1i],
                          fillColor=col, strokeColor=col, strokeWidth=0.3))

    # Needle
    needle_angle = math.radians(180 - (score / 100) * 180)
    needle_len = r_inner - 5
    nx = cx + needle_len * math.cos(needle_angle)
    ny = cy + needle_len * math.sin(needle_angle)
    rc = _risk_color(score)
    d.add(Line(cx, cy, nx, ny, strokeColor=rc, strokeWidth=2.5))
    d.add(Circle(cx, cy, 5, fillColor=rc, strokeColor=WHITE, strokeWidth=1))

    # Score text
    d.add(String(cx, cy - 22, f"{score}/100",
                 fontSize=13, fontName="Helvetica-Bold",
                 fillColor=_risk_color(score), textAnchor="middle"))
    return d


def generate_report(data: dict) -> bytes:
    """
    Generate a comprehensive PDF report and return raw bytes.
    Expects the full report_data dict from dashboard.py.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN,  bottomMargin=MARGIN,
    )

    story = []
    W = PAGE_W - 2 * MARGIN

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 1 — HEADER + RISK BANNER + KPIs + FINANCIAL PROFILE
    # ══════════════════════════════════════════════════════════════════════════

    # ── HEADER ────────────────────────────────────────────────────────────────
    header_data = [[
        Paragraph(
            '<font color="#003399"><b>Credi</b></font>'
            '<font color="#e53e3e"><b>wise</b></font>',
            ParagraphStyle("logo", fontSize=22, leading=26, fontName="Helvetica-Bold"),
        ),
        Paragraph(
            f'<font color="#64748b" size="9">AI Loan Intelligence \u00b7 India<br/>'
            f'Generated: {datetime.now().strftime("%d %b %Y, %I:%M %p")}</font>',
            ParagraphStyle("meta", fontSize=9, leading=13, alignment=TA_RIGHT),
        ),
    ]]
    hdr_tbl = Table(header_data, colWidths=[W * 0.5, W * 0.5])
    hdr_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(hdr_tbl)
    story.append(HRFlowable(width="100%", thickness=2, color=NAVY, spaceAfter=10))

    # ── TITLE ─────────────────────────────────────────────────────────────────
    username = data.get("username", "")
    greeting = f"Loan Analysis Report — {username}" if username else "Loan Analysis Report"
    story.append(Paragraph(greeting,
        ParagraphStyle("title", fontSize=18, fontName="Helvetica-Bold",
                       textColor=DARK, spaceAfter=3)))
    story.append(Paragraph(
        f"{data.get('loan_type','Personal Loan')} \u00b7 {data.get('employment','Salaried')} \u00b7 "
        f"{_fmt(data['loan_amount'])} over {data['tenure']} months @ {data['interest_rate']}% p.a.",
        ParagraphStyle("sub", fontSize=10, textColor=SLATE, spaceAfter=12),
    ))

    # ── RISK BANNER ───────────────────────────────────────────────────────────
    rs = int(data["risk_score"])
    rc = _risk_color(rs)
    rl = _risk_label(rs)
    rch = _rc_hex(rs)

    risk_desc = {
        "Low Risk":      "Your financial profile looks healthy. You are well-positioned to service this loan comfortably.",
        "Moderate Risk": "Some concerns exist in your profile. Consider adjusting loan terms for a safer outcome.",
        "High Risk":     "Significant stress indicators detected. This loan may be difficult to service without financial strain.",
    }.get(rl, "")

    risk_data = [[
        Paragraph(
            f'<b><font size="28" color="{rch}">{rs}</font></b>'
            f'<br/><font size="9" color="{rch}">out of 100</font>',
            ParagraphStyle("rscore", alignment=TA_CENTER, leading=32)),
        Paragraph(
            f'<b><font size="14" color="{rch}">{rl}</font></b><br/><br/>'
            f'<font size="9" color="#334155">{risk_desc}</font>',
            ParagraphStyle("rdesc", leading=13)),
    ]]
    risk_tbl = Table(risk_data, colWidths=[38 * mm, W - 38 * mm])
    risk_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), _risk_bg(rs)),
        ("BOX",           (0, 0), (-1, -1), 1.5, rc),
        ("LINEAFTER",     (0, 0), (0, -1), 1, BORDER),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(risk_tbl)
    story.append(Spacer(1, 10))

    # ── KPI STRIP ─────────────────────────────────────────────────────────────
    def _kpi_cell(label, val, sub, top_color):
        return Paragraph(
            f'<font size="7.5" color="#64748b"><b>{label.upper()}</b></font><br/>'
            f'<font size="12" color="#1a2540"><b>{val}</b></font><br/>'
            f'<font size="7.5" color="#64748b">{sub}</font>',
            ParagraphStyle("kpi", leading=14),
        )

    kpi_items = [
        ("Monthly EMI",         _fmt(data["emi"]),            f"{data['emi_ratio']:.1f}% of income",         "#3b82f6"),
        ("Safe EMI Capacity",   _fmt(data["safe_emi"]),       "40% of disposable income",                    "#22c55e"),
        ("Max Affordable Loan", _fmt(data["max_loan"]),       f"At {data['interest_rate']}% for {data['tenure']}m", "#f59e0b"),
        ("Total Interest",      _fmt(data["total_interest"]), f"Over {data['tenure']} months",                "#ef4444"),
    ]
    kpi_data = [[_kpi_cell(l, v, s, c) for l, v, s, c in kpi_items]]
    kpi_tbl  = Table(kpi_data, colWidths=[W / 4] * 4)
    top_borders = [(f"LINEABOVE", (i, 0), (i, 0), 3, colors.HexColor(kpi_items[i][3])) for i in range(4)]
    kpi_tbl.setStyle(TableStyle([
        ("BOX",          (i, 0), (i, 0), 0.5, BORDER) for i in range(4)
    ] + top_borders + [
        ("BACKGROUND",    (0, 0), (-1, -1), WHITE),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(kpi_tbl)
    story.append(Spacer(1, 12))

    # ── FINANCIAL PROFILE ─────────────────────────────────────────────────────
    story.append(_section_header("📋  Financial Profile", W))
    story.append(Spacer(1, 4))

    disposable = data["income"] - data["expenses"] - data["existing_emi"]
    profile_rows = [
        ["Parameter",       "Value",                     "Parameter",        "Value"],
        ["Monthly Income",  _fmt(data["income"]),         "Monthly Expenses", _fmt(data["expenses"])],
        ["Existing EMIs",   _fmt(data["existing_emi"]),   "Monthly Savings",  _fmt(data.get("savings", 0))],
        ["Credit Score",    str(data["credit_score"]),    "Credit History",   f"{data['credit_history']} years"],
        ["Debt-to-Income",  f"{data['debt_ratio']:.1f}%", "Disposable",       _fmt(disposable)],
        ["Employment",      data.get("employment", ""),   "Loan Type",        data.get("loan_type", "")],
    ]
    col_w = W / 4
    profile_tbl = Table(profile_rows, colWidths=[col_w * 1.3, col_w * 0.7] * 2)
    profile_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#f8faff"), WHITE]),
        ("GRID",          (0, 0), (-1, -1), 0.4, BORDER),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("FONTNAME",      (1, 1), (1, -1), "Helvetica-Bold"),
        ("FONTNAME",      (3, 1), (3, -1), "Helvetica-Bold"),
    ]))
    story.append(profile_tbl)
    story.append(Spacer(1, 14))

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION — RISK DEEP-DIVE
    # ══════════════════════════════════════════════════════════════════════════
    story.append(_section_header("🔍  Risk Deep-Dive", W))
    story.append(Spacer(1, 6))

    # Score factors table
    income       = float(data["income"])
    existing_emi = float(data["existing_emi"])
    emi          = float(data["emi"])
    debt_ratio   = float(data["debt_ratio"])
    credit_score = int(data["credit_score"])
    savings      = float(data.get("savings", 0))

    sav_rate_pct = (savings / income * 100) if income > 0 else 0
    disp_pct     = (disposable / income * 100) if income > 0 else 0

    def _bar_cell(pct: float, hex_color: str, label: str) -> Paragraph:
        pct = max(0, min(pct, 100))
        bar  = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        return Paragraph(
            f'<font color="{hex_color}"><b>{label}</b></font><br/>'
            f'<font size="7" color="{hex_color}">{bar}</font>',
            ParagraphStyle("bar", fontSize=8, leading=12),
        )

    dr_col = "#ef4444" if debt_ratio > 50 else "#f59e0b" if debt_ratio > 30 else "#22c55e"
    cs_col = "#22c55e" if credit_score >= 700 else "#f59e0b" if credit_score >= 650 else "#ef4444"
    sr_col = "#22c55e" if sav_rate_pct > 15 else "#f59e0b" if sav_rate_pct > 5 else "#ef4444"
    db_col = "#3b82f6"

    factors_data = [
        ["Score Factor", "Your Value", "Visual (0–100%)", "Status"],
        ["Debt-to-Income Ratio",
         f"{debt_ratio:.1f}%",
         _bar_cell(min(debt_ratio, 100), dr_col, f"{debt_ratio:.0f}%"),
         Paragraph(f'<font color="{dr_col}"><b>{"⚠ High" if debt_ratio > 50 else "⚡ Moderate" if debt_ratio > 30 else "✓ Good"}</b></font>',
                   ParagraphStyle("st", fontSize=9))],
        ["Credit Score",
         str(credit_score),
         _bar_cell((credit_score - 300) / 6, cs_col, f"{credit_score}"),
         Paragraph(f'<font color="{cs_col}"><b>{"✓ Good" if credit_score >= 700 else "⚡ Fair" if credit_score >= 650 else "⚠ Poor"}</b></font>',
                   ParagraphStyle("st", fontSize=9))],
        ["Savings Rate",
         f"{sav_rate_pct:.1f}%",
         _bar_cell(min(sav_rate_pct * 3, 100), sr_col, f"{sav_rate_pct:.0f}%"),
         Paragraph(f'<font color="{sr_col}"><b>{"✓ Good" if sav_rate_pct > 15 else "⚡ Low" if sav_rate_pct > 5 else "⚠ Very Low"}</b></font>',
                   ParagraphStyle("st", fontSize=9))],
        ["Disposable Buffer",
         _fmt(disposable),
         _bar_cell(min(disp_pct * 2, 100), db_col, f"{disp_pct:.0f}%"),
         Paragraph(f'<font color="{db_col}"><b>{"✓ Good" if disposable > 0 else "⚠ Negative"}</b></font>',
                   ParagraphStyle("st", fontSize=9))],
    ]
    factors_tbl = Table(factors_data, colWidths=[W * 0.28, W * 0.15, W * 0.37, W * 0.20])
    factors_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#f8faff"), WHITE]),
        ("GRID",          (0, 0), (-1, -1), 0.4, BORDER),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(factors_tbl)
    story.append(Spacer(1, 10))

    # Risk Insights (explain_risk equivalent)
    story.append(Paragraph("Why This Risk Score?",
        ParagraphStyle("subsec", fontSize=10, fontName="Helvetica-Bold", textColor=DARK, spaceAfter=5)))

    insights = _build_risk_insights(data, debt_ratio, disposable, emi, income, savings, credit_score)
    for icon, text, bg_hex, border_hex in insights:
        cell = Table(
            [[Paragraph(f"{icon}  {text}",
               ParagraphStyle("ins", fontSize=8.5, leading=13, textColor=DARK))]],
            colWidths=[W],
        )
        cell.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(bg_hex)),
            ("BOX",           (0, 0), (-1, -1), 0.8, colors.HexColor(border_hex)),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(cell)
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 12))

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION — STRESS TIMELINE
    # ══════════════════════════════════════════════════════════════════════════
    story.append(_section_header("📈  Stress Timeline — Savings Trajectory", W))
    story.append(Spacer(1, 6))

    tenure       = int(data["tenure"])
    interest_rate = float(data["interest_rate"])
    monthly_sav  = disposable - emi
    loan_amount  = float(data["loan_amount"])

    # Build table for key milestones
    milestones = []
    for m in [0, tenure // 4, tenure // 2, 3 * tenure // 4, tenure]:
        with_loan    = monthly_sav * m + savings
        without_loan = disposable * m + savings
        emi_cumul    = emi * m
        opportunity  = without_loan - with_loan
        milestones.append([
            f"Month {m}",
            _fmt(max(0, with_loan)),
            _fmt(without_loan),
            _fmt(emi_cumul),
            _fmt(opportunity),
        ])

    timeline_rows = [["Month", "Savings (with loan)", "Savings (no loan)", "Cumul. EMI Paid", "Opportunity Cost"]] + milestones
    tl_tbl = Table(timeline_rows, colWidths=[W * 0.12, W * 0.22, W * 0.22, W * 0.22, W * 0.22])
    tl_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#f8faff"), WHITE]),
        ("GRID",          (0, 0), (-1, -1), 0.4, BORDER),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME",      (0, 1), (0, -1), "Helvetica-Bold"),
    ]))
    story.append(tl_tbl)
    story.append(Spacer(1, 8))

    # Stress notes
    breakeven = None
    for m in range(tenure + 1):
        with_loan_m    = monthly_sav * m + savings
        without_loan_m = disposable * m + savings
        if without_loan_m - with_loan_m > loan_amount:
            breakeven = m
            break

    if breakeven:
        stress_note = (f"The opportunity cost of this loan exceeds the loan principal around "
                       f"Month {breakeven}. Plan your finances accordingly.")
        note_bg, note_border = "#eff6ff", "#3b82f6"
    elif monthly_sav < 0:
        stress_note = ("Your monthly savings will be NEGATIVE with this loan. "
                       "You may be drawing down existing savings each month to cover the EMI.")
        note_bg, note_border = "#fff1f2", "#ef4444"
    else:
        months_to_break_even = loan_amount / (disposable - monthly_sav) if (disposable - monthly_sav) > 0 else None
        stress_note = (f"Disposable after EMI: {_fmt(monthly_sav)}/month. "
                       f"You maintain positive monthly savings throughout the loan tenure.")
        note_bg, note_border = "#f0fdf4", "#22c55e"

    note_cell = Table(
        [[Paragraph(f"📊  {stress_note}",
           ParagraphStyle("note", fontSize=8.5, leading=13, textColor=DARK))]],
        colWidths=[W],
    )
    note_cell.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(note_bg)),
        ("BOX",           (0, 0), (-1, -1), 0.8, colors.HexColor(note_border)),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(note_cell)
    story.append(Spacer(1, 14))

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION — PLAN SUGGESTIONS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(_section_header("💡  Plan Suggestions", W))
    story.append(Spacer(1, 6))

    plan_label    = data.get("plan_label", "Suggested Plan")
    plan_amount   = float(data.get("plan_amount", loan_amount))
    plan_tenure   = int(data.get("plan_tenure", tenure))
    plan_emi      = float(data.get("plan_emi", emi))
    plan_interest = float(data.get("plan_interest", data["total_interest"]))
    plan_risk     = int(data.get("plan_risk", rs))

    plan_rc    = _risk_color(plan_risk)
    plan_rch   = _rc_hex(plan_risk)
    plan_rl    = _risk_label(plan_risk)

    risk_drop  = rs - plan_risk
    int_diff   = data["total_interest"] - plan_interest
    emi_diff   = emi - plan_emi
    same_plan  = (plan_tenure == tenure and abs(plan_emi - emi) < 1)

    # Two plan cards side by side
    def _plan_card(title, badge, amt, ten, m_emi, tot_int, risk_s, risk_l, rch, highlight=False):
        bg = "#f0fdf4" if highlight else "#f8faff"
        border_note = " ★ Recommended" if highlight else ""
        rows = [
            [Paragraph(f'<b><font size="10" color="#003399">{title}</font></b>'
                       f'<font size="8" color="#64748b">{border_note}</font>',
                       ParagraphStyle("ph", leading=14)), ""],
            ["Loan Amount",      _fmt(amt)],
            ["Tenure",           f"{ten} months"],
            ["Monthly EMI",      _fmt(m_emi)],
            ["Total Interest",   _fmt(tot_int)],
            ["Risk Score",       f'{risk_s}/100'],
            ["Risk Level",       risk_l],
        ]
        half = (W - 12) / 2
        t = Table(rows, colWidths=[half * 0.55, half * 0.45])
        styles = [
            ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#003399" if highlight else "#1e3a8a")),
            ("SPAN",          (0, 0), (1, 0)),
            ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
            ("BACKGROUND",    (0, 1), (-1, -1), colors.HexColor(bg)),
            ("GRID",          (0, 0), (-1, -1), 0.4, BORDER),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("FONTNAME",      (1, 1), (1, -1), "Helvetica-Bold"),
            ("TEXTCOLOR",     (1, 5), (1, 5), colors.HexColor(rch)),
            ("TEXTCOLOR",     (1, 6), (1, 6), colors.HexColor(rch)),
        ]
        t.setStyle(TableStyle(styles))
        return t

    plan_row = Table(
        [[_plan_card(plan_label, "★ Suggested",
                     plan_amount, plan_tenure, plan_emi, plan_interest,
                     plan_risk, plan_rl, plan_rch, highlight=True),
          Spacer(12, 1),
          _plan_card("Your Plan", "",
                     loan_amount, tenure, emi, data["total_interest"],
                     rs, rl, rch, highlight=False)]],
        colWidths=[(W - 12) / 2, 12, (W - 12) / 2],
    )
    plan_row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(plan_row)
    story.append(Spacer(1, 10))

    # Impact summary
    if not same_plan:
        if risk_drop > 0:
            imp_icon, imp_text, imp_bg, imp_border = "📉", f"Risk drops by {risk_drop} points ({rs} → {plan_risk}) by choosing {plan_label}.", "#f0fdf4", "#22c55e"
        elif risk_drop == 0:
            imp_icon, imp_text, imp_bg, imp_border = "↔", f"Same risk level ({rs}/100) — no change in risk profile.", "#fffbeb", "#f59e0b"
        else:
            imp_icon, imp_text, imp_bg, imp_border = "📈", f"Risk increases by {abs(risk_drop)} points. Review carefully before choosing {plan_label}.", "#fff1f2", "#ef4444"

        imp_cell = Table(
            [[Paragraph(f"{imp_icon}  <b>Risk Impact:</b>  {imp_text}",
               ParagraphStyle("imp", fontSize=9, leading=13))]],
            colWidths=[W],
        )
        imp_cell.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(imp_bg)),
            ("BOX",           (0, 0), (-1, -1), 0.8, colors.HexColor(imp_border)),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(imp_cell)
        story.append(Spacer(1, 4))

        if int_diff > 0:
            sav_cell = Table(
                [[Paragraph(f"💰  <b>Interest Savings:</b>  Switching to {plan_label} saves {_fmt(int_diff)} in total interest. "
                             f"EMI {'decreases' if emi_diff > 0 else 'increases'} by {_fmt(abs(emi_diff))}/month.",
                   ParagraphStyle("sav", fontSize=9, leading=13))]],
                colWidths=[W],
            )
            sav_cell.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), GREEN_BG),
                ("BOX",           (0, 0), (-1, -1), 0.8, colors.HexColor("#22c55e")),
                ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(sav_cell)
        elif int_diff < 0:
            cost_cell = Table(
                [[Paragraph(f"⚖️  <b>Tradeoff:</b>  {plan_label} costs {_fmt(abs(int_diff))} more in total interest "
                             f"but {'reduces' if risk_drop > 0 else 'does not change'} your risk score.",
                   ParagraphStyle("cost", fontSize=9, leading=13))]],
                colWidths=[W],
            )
            cost_cell.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), AMBER_BG),
                ("BOX",           (0, 0), (-1, -1), 0.8, colors.HexColor("#f59e0b")),
                ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(cost_cell)
    else:
        story.append(Table(
            [[Paragraph("✅  Your current plan is already optimal — no better tenure or amount found.",
               ParagraphStyle("opt", fontSize=9, leading=13))]],
            colWidths=[W],
        ))

    story.append(Spacer(1, 14))

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION — PLAN COMPARISON TABLE
    # ══════════════════════════════════════════════════════════════════════════
    story.append(_section_header("📊  Plan Comparison", W))
    story.append(Spacer(1, 6))

    cmp_rows = [
        ["Metric",         "Your Plan",                              plan_label,                          "Difference"],
        ["Loan Amount",    _fmt(loan_amount),                        _fmt(plan_amount),                   _fmt(loan_amount - plan_amount)],
        ["Monthly EMI",    _fmt(emi),                                _fmt(plan_emi),                      f"{_fmt(abs(emi_diff))} {'lower' if emi_diff > 0 else 'higher'}"],
        ["Tenure",         f"{tenure} months",                       f"{plan_tenure} months",             f"{abs(tenure - plan_tenure)} months {'shorter' if tenure > plan_tenure else 'longer'}"],
        ["Risk Score",     f"{rs}/100 — {rl}",                       f"{plan_risk}/100 — {plan_rl}",      f"{abs(risk_drop)} pts {'better' if risk_drop > 0 else 'same' if risk_drop == 0 else 'worse'}"],
        ["Total Interest", _fmt(data["total_interest"]),             _fmt(plan_interest),                 f"{_fmt(abs(int_diff))} {'saved' if int_diff > 0 else 'extra'}"],
    ]
    diff_colors = [None, None, None,
                   "#15803d" if emi_diff > 0 else "#dc2626" if emi_diff < 0 else "#475569",
                   "#15803d" if risk_drop > 0 else "#dc2626" if risk_drop < 0 else "#475569",
                   "#15803d" if int_diff > 0 else "#dc2626" if int_diff < 0 else "#475569"]

    cmp_tbl = Table(cmp_rows, colWidths=[W * 0.25, W * 0.25, W * 0.25, W * 0.25])
    cmp_style = [
        ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#f8faff"), WHITE]),
        ("GRID",          (0, 0), (-1, -1), 0.4, BORDER),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("FONTNAME",      (0, 1), (0, -1), "Helvetica-Bold"),
        ("BACKGROUND",    (2, 1), (2, -1), colors.HexColor("#f0fff4")),
    ]
    for i, dc in enumerate(diff_colors):
        if dc and i > 0:
            cmp_style.append(("TEXTCOLOR", (3, i), (3, i), colors.HexColor(dc)))
            cmp_style.append(("FONTNAME",  (3, i), (3, i), "Helvetica-Bold"))
    cmp_tbl.setStyle(TableStyle(cmp_style))
    story.append(cmp_tbl)
    story.append(Spacer(1, 10))

    # Savings callout
    if int_diff > 0:
        callout = Table(
            [[Paragraph(f"💰  Switching to {plan_label} saves you {_fmt(int_diff)} in total interest "
                        f"over the loan period.",
               ParagraphStyle("callout", fontSize=10, fontName="Helvetica-Bold", textColor=GREEN, leading=14))]],
            colWidths=[W],
        )
        callout.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), GREEN_BG),
            ("BOX",           (0, 0), (-1, -1), 1.5, GREEN),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
            ("TOPPADDING",    (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(callout)
        story.append(Spacer(1, 10))

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION — KEY INSIGHTS & RECOMMENDATIONS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(_section_header("✅  Key Insights & Recommendations", W))
    story.append(Spacer(1, 6))

    for icon, text, bg_hex in _build_key_insights(data):
        cell = Table(
            [[Paragraph(f"{icon}  {text}",
               ParagraphStyle("ins", fontSize=9, leading=14, textColor=DARK))]],
            colWidths=[W],
        )
        cell.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(bg_hex)),
            ("BOX",           (0, 0), (-1, -1), 0.5, BORDER),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
            ("TOPPADDING",    (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(cell)
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 14))

    # ── AMORTISATION SNAPSHOT (first 6 months) ────────────────────────────────
    story.append(_section_header("📅  Amortisation Snapshot (First 6 Months)", W))
    story.append(Spacer(1, 6))

    amort_rows = [["Month", "Scheduled EMI", "Principal", "Interest", "Closing Balance"]]
    r_rate   = interest_rate / (12 * 100)
    balance  = loan_amount
    sched_emi = _calculate_emi(loan_amount, interest_rate, tenure)
    for m in range(1, min(7, tenure + 1)):
        int_c  = balance * r_rate
        prin_c = sched_emi - int_c
        balance = max(0, balance - prin_c)
        amort_rows.append([str(m), _fmt(sched_emi), _fmt(prin_c), _fmt(int_c), _fmt(balance)])

    amort_tbl = Table(amort_rows, colWidths=[W * 0.1, W * 0.22, W * 0.22, W * 0.22, W * 0.24])
    amort_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#f8faff"), WHITE]),
        ("GRID",          (0, 0), (-1, -1), 0.4, BORDER),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME",      (4, 1), (4, -1), "Helvetica-Bold"),
    ]))
    story.append(amort_tbl)
    story.append(Paragraph(
        f"• Showing first {min(6, tenure)} of {tenure} months  •  Full schedule available in the Repayment Tracker on your dashboard.",
        ParagraphStyle("note2", fontSize=7.5, textColor=SLATE, spaceBefore=4)
    ))
    story.append(Spacer(1, 14))

    # ── FOOTER ────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.8, color=BORDER, spaceBefore=8))
    story.append(Paragraph(
        "This report is generated by Crediwise AI and is for informational purposes only. "
        "It does not constitute financial, legal, or credit advice. Please consult a certified "
        "financial planner before making borrowing decisions.\u00a0\u00b7\u00a0crediwise.in"
        "\u00a0\u00b7\u00a0support@crediwise.in",
        ParagraphStyle("footer", fontSize=7.5, textColor=SLATE,
                       alignment=TA_CENTER, leading=11, spaceBefore=4),
    ))

    doc.build(story)
    return buf.getvalue()


def _build_risk_insights(data, debt_ratio, disposable, emi, income, savings, credit_score):
    """Returns list of (icon, text, bg_hex, border_hex) for risk factors."""
    out = []
    rs = int(data["risk_score"])
    safe_emi = float(data["safe_emi"])
    credit_history = int(data.get("credit_history", 0))

    if debt_ratio > 50:
        out.append(("🔴", f"Debt-to-income ratio is {debt_ratio:.1f}% — well above the safe 30% threshold. Lenders may reject this application.", "#fff1f2", "#ef4444"))
    elif debt_ratio > 30:
        out.append(("🟡", f"Debt-to-income ratio of {debt_ratio:.1f}% is elevated. Try to pay down existing EMIs before adding a new loan.", "#fffbeb", "#f59e0b"))
    else:
        out.append(("🟢", f"Debt-to-income ratio of {debt_ratio:.1f}% is healthy (below 30% threshold).", "#f0fdf4", "#22c55e"))

    if credit_score >= 750:
        out.append(("🟢", f"Excellent credit score of {credit_score}. You qualify for the best interest rates from most lenders.", "#f0fdf4", "#22c55e"))
    elif credit_score >= 700:
        out.append(("🟡", f"Good credit score of {credit_score}. You should qualify, but may not get the lowest rates. Aim for 750+.", "#fffbeb", "#f59e0b"))
    else:
        out.append(("🔴", f"Credit score of {credit_score} is below the preferred threshold. Work on improving it before applying.", "#fff1f2", "#ef4444"))

    sav_pct = (savings / income * 100) if income > 0 else 0
    if sav_pct < 5:
        out.append(("🟡", f"Savings rate of {sav_pct:.1f}% is low. Build an emergency fund of 3–6 months of expenses before borrowing.", "#fffbeb", "#f59e0b"))
    else:
        out.append(("🟢", f"Savings rate of {sav_pct:.1f}% is healthy. Good buffer for emergencies.", "#f0fdf4", "#22c55e"))

    if emi > safe_emi:
        out.append(("🔴", f"Requested EMI ({_fmt(emi)}) exceeds your safe EMI capacity ({_fmt(safe_emi)}). Consider a smaller loan or longer tenure.", "#fff1f2", "#ef4444"))
    else:
        out.append(("🟢", f"EMI of {_fmt(emi)} is within your safe capacity of {_fmt(safe_emi)}. Good affordability signal.", "#f0fdf4", "#22c55e"))

    if credit_history < 2:
        out.append(("🟡", f"Short credit history of {credit_history} year(s). A longer track record helps lenders assess your reliability.", "#fffbeb", "#f59e0b"))

    return out


def _build_key_insights(data: dict) -> list[tuple[str, str, str]]:
    insights = []
    rs = int(data["risk_score"])
    dr = float(data["debt_ratio"])
    em = float(data["emi"])
    se = float(data["safe_emi"])
    cs = int(data["credit_score"])

    if rs >= 60:
        insights.append(("🔴", "High risk detected. Consider reducing loan amount or extending tenure to lower EMI burden.", "#fff1f2"))
    elif rs >= 35:
        insights.append(("🟡", "Moderate risk profile. Review your debt-to-income ratio and consider building savings before borrowing.", "#fffbeb"))
    else:
        insights.append(("🟢", "Strong financial profile. You are well-positioned to service this loan comfortably.", "#f0fdf4"))

    if dr > 50:
        insights.append(("🔴", f"Debt-to-income ratio is {dr:.1f}% — well above the safe 30% threshold. Lenders may reject this application.", "#fff1f2"))
    elif dr > 30:
        insights.append(("🟡", f"Debt-to-income ratio of {dr:.1f}% is elevated. Pay down existing EMIs before adding a new loan.", "#fffbeb"))

    if em > se:
        insights.append(("🔴", f"Requested EMI ({_fmt(em)}) exceeds your safe EMI capacity ({_fmt(se)}). Consider a smaller loan or longer tenure.", "#fff1f2"))
    else:
        insights.append(("🟢", f"EMI of {_fmt(em)} is within your safe capacity of {_fmt(se)}. Good affordability signal.", "#f0fdf4"))

    if cs >= 750:
        insights.append(("🟢", f"Excellent credit score of {cs}. You qualify for the best interest rates from most lenders.", "#f0fdf4"))
    elif cs >= 700:
        insights.append(("🟡", f"Good credit score of {cs}. You should qualify, but may not get the lowest rates. Aim for 750+.", "#fffbeb"))
    else:
        insights.append(("🔴", f"Credit score of {cs} is below the preferred threshold. Work on improving it before applying.", "#fff1f2"))

    sav = data.get("savings", 0)
    inc = data.get("income", 1)
    sav_pct = (float(sav) / float(inc) * 100) if inc else 0
    if sav_pct < 5:
        insights.append(("🟡", f"Savings rate of {sav_pct:.1f}% is low. Build an emergency fund of 3–6 months expenses before borrowing.", "#fffbeb"))

    return insights