from reportlab.lib import pagesizes, colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Frame, PageTemplate,
    Paragraph, Image, Table, TableStyle,
    Spacer, FrameBreak, NextPageTemplate, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.units import inch

class ReportLabStyles(object):
    """
    ReportLabUtils
    """

    STYLE = getSampleStyleSheet()
    CUSTOM_STYLE = ParagraphStyle(
        name="Custom",
        parent=STYLE["Normal"],
        fontName="Helvetica",
        fontSize=10,
        # leading=15,
        alignment=TA_JUSTIFY,
        backColor=colors.ghostwhite,
    )

    TITLE_STYLE = ParagraphStyle(
        name="TitleCustom",
        parent=STYLE["Title"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        alignment=TA_LEFT,
        spaceAfter=0,
        textColor=colors.blue,
    )

    SUBTITLE_STYLE = ParagraphStyle(
        name="Subtitle",
        parent=STYLE["Heading2"],
        fontName="Helvetica-Bold",
        # fontSize=14,
        # leading=12,
        alignment=TA_LEFT,
        spaceAfter=6,
        backColor=colors.lightblue,
    )

    TITLE_TABLE_STYLE = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
            ("FONT", (0, 0), (-1, -1), "Helvetica", 8),
            ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 12),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 1), (0, -1), "LEFT"),
            ("ALIGN", (1, 1), (1, -1), "RIGHT"),
            ("LINEBELOW", (0, 0), (-1, 0), 1, colors.deepskyblue),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.black),
            ("TEXTCOLOR", (1, 1), (-1, -1), colors.red),
            ("TEXTCOLOR", (1, 3), (-1, 3), colors.grey)
        ]
    )

    TABLE_STYLE = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
            ("FONT", (0, 0), (-1, -1), "Helvetica", 8),
            ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 12),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 1), (0, -1), "LEFT"),
            ("ALIGN", (1, 1), (1, -1), "RIGHT"),
            ("LINEBELOW", (0, 0), (-1, 0), 2, colors.deepskyblue),
        ]
    )
    STYLE_COMMAND = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        # ("BACKGROUND", (0, 1), (-1, 1), colors.lightskyblue),
        ("FONT", (0, 0), (-1, -1), "Helvetica", 7),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 14),
        ("FONT", (0, 1), (-1, 1), "Helvetica-Bold", 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, 0), 2, colors.black),
        ("LINEBELOW", (0, -1), (-1, -1), 2, colors.black),
    ]

    BG_TABLE_STYLE = TableStyle(
        STYLE_COMMAND
    )
