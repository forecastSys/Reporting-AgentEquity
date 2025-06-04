from reportlab.lib import pagesizes, colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Frame, PageTemplate,
    Paragraph, Image, Table, TableStyle,
    Spacer, FrameBreak, NextPageTemplate, PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.units import inch
from reportlab.lib.units import mm
from datetime import datetime

class ReportLabStyles:
    """
    ReportLabUtils
    """
    GAP = 5 * mm

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

    # TITLE_STYLE = ParagraphStyle(
    #     name="TitleCustom",
    #     parent=STYLE["Title"],
    #     fontName="Helvetica-Bold",
    #     fontSize=16,
    #     leading=20,
    #     alignment=TA_LEFT,
    #     spaceAfter=0,
    #     textColor=colors.blue,
    #     lineColor=colors.black,
    # )
    TITLE_STYLE = ParagraphStyle(
        name="TitleCustom",
        parent=STYLE["Title"],
        fontName="Times-Roman",
        fontSize=9,
        leading=11,
        alignment=TA_LEFT,
        spaceAfter=5,
        textColor=colors.deepskyblue,
        underlineColor=colors.black,
        underlineWidth=2,
        underlineOffset=-1
    )
    DOWN_TITLE_STYLE = ParagraphStyle(
        name="TitleCustom",
        parent=STYLE["Title"],
        fontName="Times-Roman",
        fontSize=8,
        leading=5,
        alignment=TA_LEFT,
        spaceAfter=5,
        textColor=colors.black,
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

    DOWN_TITLE_TABLE_STYLE = TableStyle([
        # remove any default padding so the text really hugs the cell edges
        ("LEFTPADDING",   (0,0), (-1,-1), 0),
        ("RIGHTPADDING",  (0,0), (-1,-1), 0),
        ("TOPPADDING",    (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),

        # align first cell left, second cell right
        ("ALIGN", (0,0), (0,0), "LEFT"),
        ("ALIGN", (1,0), (1,0), "RIGHT"),

        # optionally vertically center
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ])

    STYLE_COMMAND = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightslategrey),
        # ("BACKGROUND", (0, 1), (-1, 1), colors.lightskyblue),
        ("FONT", (0, 0), (-1, -1), "Helvetica", 7),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 14),
        ("FONT", (0, 1), (-1, 1), "Helvetica-Bold", 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.black),
        ("LINEBELOW", (0, -1), (-1, -1), 1, colors.black),
    ]

    BG_TABLE_STYLE = TableStyle(
        STYLE_COMMAND
    )

class ReportLabFrame:
    MARGIN=4
    PAGE_W, PAGE_H = pagesizes.A4
    TITLE_H = 30

    LEFT_W = PAGE_W * 2 / 3
    RIGHT_W = PAGE_W - LEFT_W

    USABLE_W = PAGE_W - 2 * MARGIN
    USABLE_H = PAGE_H - 2 * MARGIN
    CONTENT_H = USABLE_H - 2 * TITLE_H
    HALF_H = CONTENT_H / 2

    TOP_DOWN_LEFT_W = USABLE_W * 0.6
    TOP_DOWN_RIGHT_W = USABLE_W - TOP_DOWN_LEFT_W

    CAESARS_IMAGE_WIDTH=150

    def _get_single_frame(self):
        ## create page template with one coloumns
        single_frame = Frame(
            self.MARGIN,
            self.MARGIN,
            self.PAGE_W - self.MARGIN * 2,
            self.PAGE_H - self.MARGIN * 2,
            id='single')

        single_column_template = PageTemplate(
            id='OneCol',
            frames=[single_frame]
        )
        return single_column_template

    def _get_two_col_frame(self):
        ## define two columns frame
        frame_left = Frame(
            self.MARGIN,
            self.MARGIN,
            self.LEFT_W - self.MARGIN * 2,
            self.PAGE_H - self.MARGIN * 2,
            id="left",
        )
        frame_right = Frame(
            self.LEFT_W,
            self.MARGIN,
            self.RIGHT_W - self.MARGIN * 2,
            self.PAGE_H - self.MARGIN * 2,
            id="right",
        )
        two_cols_template = PageTemplate(
            id="TwoColumns",
            frames=[frame_left, frame_right]
        )
        return two_cols_template

    def _get_first_page_frame(self):
        ## Top down frame
        # usable_w = self.PAGE_W - 2 * self.MARGIN
        # usable_h = self.PAGE_H - 2 * self.MARGIN
        # content_h = usable_h - 2 * self.TITLE_H
        # half_h = content_h / 2

        frame_top_title = Frame(
            self.MARGIN,
            # put it at the top of the page, just inside the top margin:
            self.MARGIN + self.CONTENT_H + self.TITLE_H,
            self.USABLE_W,
            self.TITLE_H,
            id="top_title",
        )

        #  — Main content area (upper half)
        frame_content_top = Frame(
            self.MARGIN,
            # half down from the top title:
            self.MARGIN + self.HALF_H + self.TITLE_H,
            self.USABLE_W,
            self.HALF_H,
            id="content_top",
        )

        #  — Lower left content (bottom half, left 60%)
        frame_bottom_left = Frame(
            self.MARGIN,
            self.MARGIN + self.TITLE_H,
            self.USABLE_W * 0.6,
            self.HALF_H,
            id="bottom_left",
        )

        #  — Lower right content (bottom half, right 40%)
        frame_bottom_right = Frame(
            self.MARGIN + self.USABLE_W * 0.6,
            self.MARGIN + self.TITLE_H,
            self.USABLE_W * 0.4,
            self.HALF_H,
            id="bottom_right",
        )
        bottom_left_title_usable_w = self.USABLE_W * 0.8
        bottom_right_title_usable_w = self.USABLE_W - bottom_left_title_usable_w

        #  — Bottom title stripe
        frame_bottom_title = Frame(
            self.MARGIN,
            self.MARGIN,
            self.USABLE_W,
            self.TITLE_H,
            id="bottom_title",
        )

        # frame_bottom_left_title = Frame(
        #     self.MARGIN,
        #     self.MARGIN,
        #     bottom_left_title_usable_w,
        #     self.TITLE_H,
        #     id="bottom_title_left",
        # )
        # frame_bottom_right_title = Frame(
        #     self.MARGIN + bottom_left_title_usable_w,
        #     self.MARGIN,
        #     bottom_right_title_usable_w,
        #     self.TITLE_H,
        #     id="bottom_title_right",
        # )
        five_frame_template = PageTemplate(
            id="five_frames",
            frames=[frame_top_title,
                    frame_content_top,
                    frame_bottom_left,
                    frame_bottom_right,
                    frame_bottom_title,
                    # frame_bottom_left_title,
                    # frame_bottom_right_title
                    ])
        return five_frame_template

    def _get_second_page_frame(self):

        frame_top_title = Frame(
            self.MARGIN,
            # put it at the top of the page, just inside the top margin:
            self.MARGIN + self.CONTENT_H + self.TITLE_H,
            self.USABLE_W,
            self.TITLE_H,
            id="top_title",
        )



class ReportLabGeneralUtils:

    def _get_title_line(self):

        return HRFlowable(
            width="100%",  # full frame width
            thickness=0.5,  # line thickness
            color=colors.black,  # match your title color
            spaceBefore=2,  # gap above the line
            spaceAfter=2  # gap below before next paragraph
        )

class ContentUtils:

    def _get_top_title(self):
        para = Paragraph(
            f"AIDF Caesars Analyst Report  |  Report as of {datetime.today()}  |  Reporting Currency: USD  |  Exchange: NASDAQ",
            self.TITLE_STYLE)
        return para

    def _get_down_title(self, caesars_img_path):
        para = Paragraph(f'Copyright ©{datetime.today().year} Asian Institute of Digital Finance. All rights reserved.', style=self.DOWN_TITLE_STYLE)
        img = Image(caesars_img_path, width=self.CAESARS_IMAGE_WIDTH, height=self.TITLE_H)
        tbl = Table([[para, img]],
                    colWidths=[self.USABLE_W * 0.88, self.USABLE_W * 0.88],
                    style=self.DOWN_TITLE_TABLE_STYLE)
        return tbl