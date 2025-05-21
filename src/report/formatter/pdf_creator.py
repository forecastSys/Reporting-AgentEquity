from src.report.generator import InvestmentReportGenerator
from src.fdata_extractors.findata_extractor import YFinanceAnalyzer
from src.report.plotter import FinancialPlotter
from src.report.formatter import ReportLabStyles

from reportlab.lib import pagesizes, colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Frame, PageTemplate,
    Paragraph, Image, Table, TableStyle,
    Spacer, FrameBreak, NextPageTemplate, PageBreak
)

import json
import textwrap3
import pandas as pd
import random
from pathlib import Path
import os
from datetime import date
import numpy as np
from typing import Union
import copy

class CombinedReportPDF:
    """
    Generates a multi-page PDF combining:
      - Text sections (Summary, Business, Risk)
      - Financial charts (Close & MA15/30/60/90, EPS vs. P/E)
      - Annual metrics table for previous 5 years
    """
    P = Path(__file__).resolve()
    PROJECT_DIR = P.parents[3]
    IMAGE_DIR = PROJECT_DIR / 'data' / 'images'
    STATIC_IMAGE_DIR = PROJECT_DIR / '_static' / 'images'
    FDATA_DIR = PROJECT_DIR / 'data' / 'fdata'
    OUTPUT_DIR = PROJECT_DIR / 'data' / 'reports'

    for d in (IMAGE_DIR, FDATA_DIR, OUTPUT_DIR):
        d.mkdir(parents=True, exist_ok=True)

    def __init__(self, ticker: str, year: int, quarter: int, output_name: str = "combined_report.pdf"):
        self.ticker = ticker
        self.year = year
        self.quarter = quarter
        self.output_path = self.OUTPUT_DIR / output_name
        # Initialize LLM-based report generator
        self.generator = InvestmentReportGenerator()
        self.plotter = FinancialPlotter(ticker)
        self.analyzer = YFinanceAnalyzer(ticker)
        self.oil_analyzer = YFinanceAnalyzer('CL=F')

    @staticmethod
    def _escape_dollars(s: str) -> str:
        return s.replace('$', r'\$')

    @staticmethod
    def _escape_and_wrap(s: str, width: int = 80) -> str:
        # Escape dollar signs and wrap long lines
        escaped = s.replace('$', r'\$')
        lines = []
        for paragraph in escaped.split('\n'):
            if paragraph.strip() == '':
                lines.append('')
            else:
                lines.extend(textwrap3.wrap(paragraph, width=width))
        return '\n'.join(lines)

    def _get_text(self) -> str:
        """Fetch and wrap LLM text sections"""
        filename = self.FDATA_DIR / f"report_sections_{self.ticker}_{self.year}_{self.quarter}.json"
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                result = json.load(f)
            buy_sell_sign = result["investment_summary"]['signal'] if isinstance(result["investment_summary"], dict) else result["investment_summary"]
            summary = result["investment_summary"]["summary"] if isinstance(result["investment_summary"], dict) else result["investment_summary"]
            business = result["business_overview"]["report"] if isinstance(result["business_overview"], dict) else result["business_overview"]
            risk     = result["risk_assessment"]["report"] if isinstance(result["risk_assessment"], dict) else result["risk_assessment"]
        else:
            # Generate text sections
            result = self.generator.generate(self.ticker, self.year, self.quarter)
            buy_sell_sign = result["investment_summary"]['signal'] if isinstance(result["investment_summary"], dict) else result["investment_summary"]
            summary = result["investment_summary"]["summary"] if isinstance(result["investment_summary"], dict) else result["investment_summary"]
            business = result["business_overview"]["report"] if isinstance(result["business_overview"], dict) else result["business_overview"]
            risk     = result["risk_assessment"]["report"] if isinstance(result["risk_assessment"], dict) else result["risk_assessment"]
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)

        results = {
            "signal": buy_sell_sign,
            "investment_summary": summary,
            "business_overview": business,
            "risk_assessment": risk
        }
        # full = (
        #     '<b>Investment Summary</b><br/>' + summary.replace('\n', '<br/>') + '<br/><br/>' +
        #     '<b>Business Overview</b><br/>'   + business.replace('\n', '<br/>') + '<br/><br/>' +
        #     '<b>Risk Assessment</b><br/>'     + risk.replace('\n', '<br/>')
        # )
        return results

    def _save_charts(self):
        """Generate and save chart images via matplotlib"""
        # MA chart
        df_ma = self.analyzer.get_all_mas(price_period='1y', price_interval='1d', ma_windows=[15,30,60,90])
        ma_path = self.IMAGE_DIR / f"{self.ticker}_{self.year}_{self.quarter}_ma.png"
        plt_ma = self.plotter.plot_moving_averages_to_fig(df_ma)
        plt_ma.savefig(ma_path, bbox_inches='tight')

        # EPS/PER chart
        eps = self.analyzer.get_eps(n_quarters=4)
        pe  = self.analyzer.get_pe_ratio(price_period='1d', price_interval='1d', n_quarters=4)
        pe_path = self.IMAGE_DIR / f"{self.ticker}_{self.year}_{self.quarter}_eps_pe.png"
        plt_pe = self.plotter.plot_eps_pe_to_fig(eps, pe)
        plt_pe.savefig(pe_path, bbox_inches='tight')

        df_oil = self.oil_analyzer.ticker.history(period='6mo', interval='1d')
        oil_path = self.IMAGE_DIR / f"{self.ticker}_{self.year}_{self.quarter}_oil.png"
        plt_oil = self.plotter.plot_oil_price(df_oil, period='6mo', interval='1d')
        plt_oil.savefig(oil_path, bbox_inches='tight')
        return str(ma_path), str(pe_path), str(oil_path)

    def _get_table_data(self, period: str='5y'):

        year_count = int(period[0])
        def _get_div_sorted_desc(a: pd.DataFrame, b: pd.DataFrame, return_type: str = 'array') -> Union[
            np.array, pd.DataFrame]:
            """
            values_list = a / b
            """
            out_div = a.div(b).sort_index(ascending=False)
            if return_type == 'array':
                return out_div.values
            else:
                return out_div

        def _extend_year(df: pd.DataFrame, years_dt: list) -> pd.DataFrame:
            """

            """
            df = df.reindex(years_dt).sort_index(ascending=False)
            return df

        filename = self.FDATA_DIR / f"{self.ticker}_{self.year}_{self.quarter}_table_df.csv"
        if not os.path.exists(filename):
            # # Prepare annual metrics table
            # # Use yfinance annual financials and balance sheet
            annual_fs = self.analyzer.get_past_financial()  # annual metrics
            bal_sheet = self.analyzer.get_past_balance_sheet()  # quarterly; approximate use first column per year
            fiscal_month = int(bal_sheet.columns[0].month)
            fiscal_day = int(bal_sheet.columns[0].day)

            ## append years if less than 5
            idx = pd.to_datetime(annual_fs.columns)
            last_date = idx.max()
            years_dt = pd.date_range(end=last_date, periods=year_count, freq='YE')
            years = [str(d.year) for d in years_dt]
            years = sorted(years, key=int, reverse=True)
            # years = [str(int(y.year)) for y in annual_fs.columns[:year_count]]

            rev = annual_fs.loc['Total Revenue', :]
            net = annual_fs.loc['Net Income', :]
            ebitda = annual_fs.loc['EBITDA', :]

            rev = _extend_year(rev, years_dt)
            net = _extend_year(net, years_dt)
            ebitda = _extend_year(ebitda, years_dt)

            # Compute ROE: Net Income / Shareholder Equity
            eq = bal_sheet.loc['Stockholders Equity', :]
            eq = _extend_year(eq, years_dt)
            # balance_sheet quarterly; take first column of each year-end quarter
            roe_vals = _get_div_sorted_desc(net, eq)
            # roe_vals = net.values / eq.values

            # Compute P/E per year: year-end close / (Net Income/Shares)

            price_hist = self.analyzer.get_past_fiscal_year_end_stock_price(
                period_end_month=fiscal_month,
                period_end_day=fiscal_day,
                period='5y')

            shares_hist = self.analyzer.get_past_fiscal_year_end_shares(period='5y')
            shares_hist = _extend_year(shares_hist, years_dt)

            eps_year = _get_div_sorted_desc(net, shares_hist, return_type='df')
            pe_vals = _get_div_sorted_desc(price_hist, eps_year)
            # eps_year = net.values / shares_hist.values
            # pe_vals = price_hist.values / eps_year

            # Compute P/B per year: year-end close / (Equity/Shares)
            book_val = _get_div_sorted_desc(eq, shares_hist, return_type='df')
            pb_vals = _get_div_sorted_desc(price_hist, book_val)
            # book_val = eq.values / shares_hist.values
            # pb_vals = price_hist.values / book_val

            table_df = pd.DataFrame(
                {
                    'Total Revenue':  rev.values,
                    'Net Profit':     net.values,
                    'EBITDA':         ebitda.values,
                    'ROE':            roe_vals,
                    'P/E Ratio':      pe_vals,
                    'P/B Ratio':      pb_vals
                },
                index=years,
                dtype=float
            )

            table_df.to_csv(filename, index=True)
        else:
            table_df = pd.read_csv(filename).set_index('Unnamed: 0')

        table_df = table_df.dropna(axis=0, how='all')
        cols = ['ROE', 'P/E Ratio', 'P/B Ratio']
        table_df[cols] = table_df[cols].round(2)
        cols = list(table_df.index)


        data = [
            ['Total Revenue (in mil)']  + list(table_df['Total Revenue'] / 1000000),
            ['Net Profit (in mil)']     + list(table_df['Net Profit'] / 1000000),
            ['EBITDA (in mil)']         + list(table_df['EBITDA'] / 1000000),
            ['ROE']            + list(table_df['ROE']),
            ['P/E Ratio']      + list(table_df['P/E Ratio']),
            ['P/B Ratio']      + list(table_df['P/B Ratio'])
        ]
        # header row inserted by Table
        return [['FY'] + cols], data, table_df.shape

    def create_pdf(self):
        # filename = f"report_sections_{self.ticker}_{self.year}_{self.quarter}.json"
        # with open(filename, "r", encoding="utf-8") as f:
        #     result = json.load(f)
        # summary = result["investment_summary"]["summary"] if isinstance(result["investment_summary"], dict) else result[
        #     "investment_summary"]
        # business = result["business_overview"]["report"] if isinstance(result["business_overview"], dict) else result[
        #     "business_overview"]
        # risk = result["risk_assessment"]["report"] if isinstance(result["risk_assessment"], dict) else result[
        #     "risk_assessment"]

        ## ---------------------------------------------- <START> Define reportlab styles ----------------------------------------------- ##

        CUSTOM_STYLE, TITLE_STYLE, SUBTITLE_STYLE,\
            TITLE_TABLE_STYLE, TABLE_STYLE, STYLE_COMMAND= (
            ReportLabStyles.CUSTOM_STYLE, ReportLabStyles.TITLE_STYLE, ReportLabStyles.SUBTITLE_STYLE,
            ReportLabStyles.TITLE_TABLE_STYLE, ReportLabStyles.TABLE_STYLE, ReportLabStyles.STYLE_COMMAND)
        ## ------------------------------------------------ <END> Define reportlab styles------------------------------------------------ ##
        # Setting paths
        caesars_path = str(self.STATIC_IMAGE_DIR / 'nus_avatar.png')

        # Get statements
        result = self._get_text()

        buy_sell_sign, summary, business, risk = (result['signal'],
                                                  result['investment_summary'],
                                                  result['business_overview'],
                                                  result['risk_assessment'])
        # get image path
        ma_path, pe_path, oil_path = self._save_charts()

        # get table data
        header, fm_metrics_table, df_shape = self._get_table_data()

        page_w, page_h = pagesizes.A4
        margin = 4
        left_w = page_w * 2 / 3
        right_w = page_w - left_w

        doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=A4
        )

        ## create page template with one coloumns
        single_frame = Frame(
            margin,
            margin,
            page_w - margin * 2,
            page_h - margin * 2,
            id='single')
        single_column_layout = PageTemplate(id='OneCol', frames=[single_frame])

        ## define two columns frame
        frame_left = Frame(
            margin,
            margin,
            left_w - margin * 2,
            page_h - margin * 2,
            id="left",
        )
        frame_right = Frame(
            left_w,
            margin,
            right_w - margin * 2,
            page_h - margin * 2,
            id="right",
        )

        left_column_width_p2 = (page_w - margin * 3) // 2
        right_column_width_p2 = left_column_width_p2
        frame_left_p2 = Frame(
            margin,
            margin,
            left_column_width_p2 - margin * 2,
            page_h - margin * 2,
            id="left",
        )
        frame_right_p2 = Frame(
            left_column_width_p2,
            margin,
            right_column_width_p2 - margin * 2,
            page_h - margin * 2,
            id="right",
        )

        ## create 2-pages template with two coloumns
        page_template = PageTemplate(
            id="TwoColumns", frames=[frame_left, frame_right]
        )
        page_template_p2 = PageTemplate(
            id="TwoColumns_p2", frames=[frame_left_p2, frame_right_p2]
        )

        doc.addPageTemplates([page_template, single_column_layout, page_template_p2])

        content = []
        width = right_w
        height = width // 4
        content.append(Image(caesars_path, width=width, height=height, hAlign='LEFT'))
        # caesars_title = "AIDF - CAESARS"
        # content.append(Paragraph(caesars_title, title_style))

        content.append(
            Paragraph(
                f"Investment Report: {self.ticker}",
                TITLE_STYLE,
            )
        )
        creation_date = f"Report Creation Date: {date.today()}"
        content.append(Paragraph(creation_date, TITLE_STYLE))

        content.append(Paragraph("Summary Investment Thesis & Valuation", SUBTITLE_STYLE))
        content.append(Paragraph(summary, CUSTOM_STYLE))

        content.append(Paragraph("Business Overview", SUBTITLE_STYLE))
        content.append(Paragraph(business, CUSTOM_STYLE))

        ## Predicted Key Metrics
        col_widths = [(left_w - margin * 4) * 1.2 / df_shape[1]] * df_shape[1]
        pred_header = [[(i + 4 if isinstance(i, int) else i) for i in header[0]]]
        style_commands_km = copy.deepcopy(STYLE_COMMAND)
        for col in range(df_shape[1]):
            bg = colors.lightgrey if (col % 2) == 0 else colors.white
            style_commands_km.append(
                ("BACKGROUND", (col, 1), (col, -1), bg)
            )
        table = ([["Predicted Key Metrics"]]
                 + pred_header +
                 [['Total Revenue (in mil)', 'TBD', 'TBD', 'TBD', 'TBD'],
                  ['EBITDA (in mil)', 'TBD', 'TBD', 'TBD', 'TBD'],
                  ['Others (in mil)', 'TBD', 'TBD', 'TBD', 'TBD'],
                  ['Others (in mil)', 'TBD', 'TBD', 'TBD', 'TBD'],
                  ['Others (in mil)', 'TBD', 'TBD', 'TBD', 'TBD'],
                  ['Others (in mil)', 'TBD', 'TBD', 'TBD', 'TBD']
                  ])
        table_input = Table(table, colWidths=col_widths, hAlign="LEFT")
        table_input.setStyle(TableStyle(style_commands_km))
        content.append(table_input)

        # move to the right column
        content.append(FrameBreak())
        stock_df = self.analyzer.get_price()
        stock_cur_date = stock_df.index[-1]
        stock_cur_price = stock_df[stock_cur_date]
        current_price = round(float(stock_cur_price), 2)
        target_price = round(current_price * random.uniform(1, 1.5))
        prior_target_price = round(target_price * random.uniform(1, 1.5), 2)
        up_down = round(((target_price - current_price) / current_price) * 100, 2)
        if up_down > 0:
            str_up_down = "+" + str(up_down) + '%'
        else:
            str_up_down = "-" + str(up_down) + '%'
        mkt_cap = self.analyzer.ticker.info.get('marketCap') / 1000000
        data = (
            [
            ['Suggestions & Predictions'] + [''],
            ["Suggestions"] + [buy_sell_sign],
            ['Target Price'] + [target_price],
            ['Prior Target Price'] + [prior_target_price],
            [f'Share Price ({str(stock_cur_date.date())})'] + [current_price],
            ['Upside / Downsides'] + [str_up_down],
            ['MKT CAP (in mil)'] + [mkt_cap],
            ]
        )
        # ['Target Price over the year'] + ['TBD'],
        # ['Total Revenue'] + ['TBD'],
        # ['EBITDA'] + ['TBD'],
        # ['Others'] + ['TBD']]

        full_length = right_w - 2 * margin
        col_widths = [full_length // 3 * 2, full_length // 3]
        table = Table(data, colWidths=col_widths)
        table.setStyle(TITLE_TABLE_STYLE)
        content.append(table)

        # ## Adding plots - EPS VS PE
        data = [["PE and EPS"]]
        col_widths = [full_length]
        table = Table(data, colWidths=col_widths)
        table.setStyle(TABLE_STYLE)
        content.append(table)

        width = right_w
        height = width // 2
        content.append(Image(pe_path, width=width, height=height))

        ## Adding plots - MA
        data = [["Moving Average"]]
        col_widths = [full_length]
        table = Table(data, colWidths=col_widths)
        table.setStyle(TABLE_STYLE)
        content.append(table)

        width = right_w
        height = width // 2
        content.append(Image(ma_path, width=width, height=height))

        ## Adding plot - Oil price
        data = [["Oil Price"]]
        col_widths = [full_length]
        table = Table(data, colWidths=col_widths)
        table.setStyle(TABLE_STYLE)
        content.append(table)

        width = right_w
        height = width // 2
        content.append(Image(oil_path, width=width, height=height))

        data = [["Highlights"]] + [['TBD']]
        col_widths = [full_length]
        table = Table(data, colWidths=col_widths, hAlign='LEFT')
        table.setStyle(TITLE_TABLE_STYLE)
        content.append(table)

        # content.append(Paragraph("Highlights", subtitle_style))
        # content.append(Paragraph("TBD", custom_style))

        # # Start another page
        content.append(NextPageTemplate("OneCol"))
        content.append(PageBreak())

        ## Key Metrics
        col_widths = [(left_w - margin * 4) * 1.2 / df_shape[1]] * df_shape[1]
        style_commands_km = copy.deepcopy(STYLE_COMMAND)
        for col in range(df_shape[1]):
            bg = colors.lightgrey if (col % 2) == 0 else colors.white
            style_commands_km.append(
                ("BACKGROUND", (col, 1), (col, -1), bg)
            )

        table = [["Key Metrics"]] + header + fm_metrics_table
        table_input = Table(table, colWidths=col_widths, hAlign="LEFT")
        table_input.setStyle(TableStyle(style_commands_km))
        content.append(table_input)

        ## Todo: Adding some dummy PNG
        ### Peer comparison ratios
        # data = [["Price Earning History"]]
        # col_widths = [right_w]
        # table = Table(data, colWidths=col_widths, hAlign="LEFT")
        # table.setStyle(table_style)
        # content.append(table)

        content.append(Paragraph("Price Earning History", SUBTITLE_STYLE))

        width = right_w * 2
        height = width // 2 * 1.5
        content.append(
            Image(str(self.STATIC_IMAGE_DIR / 'price_earning_history.png'), width=width,height=height, hAlign="LEFT"))

        content.append(Paragraph("Risk Assessment", SUBTITLE_STYLE))
        content.append(Paragraph(risk, CUSTOM_STYLE))

        content.append(NextPageTemplate("OneCol"))
        content.append(PageBreak())

        content.append(Paragraph("Industry Analysis", SUBTITLE_STYLE))
        content.append(Paragraph("TBD \n \n \n", CUSTOM_STYLE))

        width = right_w * 3
        height = width // 2
        content.append(Image(str(self.STATIC_IMAGE_DIR / 'industry_comparison.png'),
                             width=width, height=height, hAlign="LEFT"))

        ## Todo: Adding some dummy PNG

        # content.append(Paragraph("Peer Comparison", subtitle_style))
        # content.append(Paragraph("TBD", custom_style))

        ### Peer comparison ratios
        # data = [["Company to Industry Comparison"]]
        # col_widths = [full_length*1.2]
        # table = Table(data, colWidths=col_widths, hAlign="LEFT")
        # table.setStyle(table_style)
        # content.append(table)
        content.append(Paragraph("Company to Industry Comparison", SUBTITLE_STYLE))

        width = right_w * 3
        height = width // 2
        content.append(Image(str(self.STATIC_IMAGE_DIR / 'company_to_industry_comparison.png'),
                             width=width, height=height, hAlign="LEFT"))

        content.append(NextPageTemplate("OneCol"))
        content.append(PageBreak())

        ### Peer comparison ratios
        # data = [["Peer Comparison Ratios"]]
        # col_widths = [full_length*0.8]
        # table = Table(data, colWidths=col_widths, hAlign="LEFT")
        # table.setStyle(table_style)
        # content.append(table)

        content.append(Paragraph("Peer Comparison Ratios", SUBTITLE_STYLE))
        width = right_w * 3
        height = width // 2
        content.append(Image(str(self.STATIC_IMAGE_DIR / 'peer_comparison_ratios.png'),
                             width=width, height=height, hAlign="LEFT"))

        doc.build(content)
        print(f"✅ PDF saved to {self.output_path}")

    # def create_pdf(self):
    #     filename = f"report_sections_{self.ticker}_{self.year}_{self.quarter}.json"
    #     if os.path.exists(filename):
    #         with open(filename, "r", encoding="utf-8") as f:
    #             result = json.load(f)
    #         summary = result["investment_summary"]["summary"] if isinstance(result["investment_summary"], dict) else result["investment_summary"]
    #         business = result["business_overview"]["report"] if isinstance(result["business_overview"], dict) else result["business_overview"]
    #         risk     = result["risk_assessment"]["report"] if isinstance(result["risk_assessment"], dict) else result["risk_assessment"]
    #     else:
    #         # Generate text sections
    #         result = self.generator.generate(self.ticker, self.year, self.quarter)
    #         summary = result["investment_summary"]["summary"] if isinstance(result["investment_summary"], dict) else result["investment_summary"]
    #         business = result["business_overview"]["report"] if isinstance(result["business_overview"], dict) else result["business_overview"]
    #         risk     = result["risk_assessment"]["report"] if isinstance(result["risk_assessment"], dict) else result["risk_assessment"]
    #         # build the result dict
    #         result = {
    #             "investment_summary": summary,
    #             "business_overview": business,
    #             "risk_assessment": risk
    #         }
    #         # write to a file
    #         with open(filename, "w", encoding="utf-8") as f:
    #             json.dump(result, f, ensure_ascii=False, indent=4)
    #
    #     full_text = (
    #         "=== Investment Summary ===\n" + self._escape_dollars(summary) + "\n\n" +
    #         "=== Business Overview ===\n"   + self._escape_dollars(business) + "\n\n" +
    #         "=== Risk Assessment ===\n"     + self._escape_dollars(risk)
    #     )
    #     text_for_pdf = self._escape_and_wrap(full_text, width=80)
    #
    #     # Split into lines and paginate
    #     lines = text_for_pdf.split('\n')
    #     max_lines_per_page = 60
    #     chunks = [lines[i:i + max_lines_per_page] for i in range(0, len(lines), max_lines_per_page)]
    #
    #     # Prepare financial data
    #     df = self.analyzer.get_all_mas(price_period="1y", price_interval="1d", ma_windows=[15, 30, 60, 90])
    #     eps = self.analyzer.get_eps(n_quarters=4)
    #     pe = self.analyzer.get_pe_ratio(price_period="1d", price_interval="1d", n_quarters=4)
    #
    #     # Prepare annual metrics table
    #     # Use yfinance annual financials and balance sheet
    #     annual_fs = self.analyzer.get_past_financial()  # annual metrics
    #     bal_sheet = self.analyzer.get_past_balance_sheet() # quarterly; approximate use first column per year
    #     fiscal_month = int(bal_sheet.columns[0].month)
    #     fiscal_day = int(bal_sheet.columns[0].day)
    #
    #     shares    = self.analyzer.ticker.info.get('sharesOutstanding', 1)
    #     years     = [str(int(y.year)) for y in annual_fs.columns[:5]]
    #
    #     rev   = annual_fs.loc['Total Revenue', :]
    #     net   = annual_fs.loc['Net Income', :]
    #     ebitda = annual_fs.loc['EBITDA', :]
    #
    #     # Compute ROE: Net Income / Shareholder Equity
    #     eq = bal_sheet.loc['Stockholders Equity', :]
    #     # balance_sheet quarterly; take first column of each year-end quarter
    #     roe_vals = net.values / eq.values
    #
    #     # Compute P/E per year: year-end close / (Net Income/Shares)
    #
    #     price_hist = self.analyzer.get_past_fiscal_year_end_stock_price(
    #         period_end_month=fiscal_month,
    #         period_end_day=fiscal_day,
    #         period='5y')
    #
    #     shares_hist = self.analyzer.get_past_fiscal_year_end_shares(period='5y')
    #
    #     eps_year = net.values / shares_hist.values
    #     pe_vals = price_hist.values / eps_year
    #
    #     # Compute P/B per year: year-end close / (Equity/Shares)
    #     book_val = eq.values / shares_hist.values
    #     pb_vals = price_hist.values / book_val
    #
    #     table_df = pd.DataFrame(
    #         {
    #             'Total Revenue': rev.values,
    #             'Net Profit':     net.values,
    #             'EBITDA':         ebitda.values,
    #             'ROE':            roe_vals,
    #             'P/E Ratio':      pe_vals,
    #             'P/B Ratio':      pb_vals
    #         },
    #         index=years
    #     ).T
    #     table_df = table_df.dropna(axis=1, how='all')
    #     # Create PDF
    #     with PdfPages(self.output_path) as pdf:
    #         # Page 1: first chunk + charts
    #         fig = plt.figure(figsize=(11.69, 8.27))  # A4 landscape
    #         fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    #
    #         # Text region (35% width)
    #         ax_text = fig.add_axes([0.02, 0.02, 0.35, 0.96])
    #         ax_text.axis('off')
    #         ax_text.text(0, 1, '\n'.join(chunks[0]), va='top', wrap=True, fontsize=8)
    #
    #         # MA plot (right top)
    #         ax_ma = fig.add_axes([0.55, 0.65, 0.35, 0.25])
    #         ax_ma.plot(df.index, df['Close'], label='Close')
    #         for w in [15, 30, 60, 90]:
    #             ax_ma.plot(df.index, df[f'MA{w}'], label=f'MA{w}')
    #         ax_ma.set_title(f"{self.ticker}: Close & MA15/30/60/90", fontsize=10)
    #         ax_ma.set_xlabel('Date', fontsize=8)
    #         ax_ma.set_ylabel('Price', fontsize=8)
    #         ax_ma.legend(fontsize=7)
    #
    #         # EPS vs P/E plot (right bottom)
    #         ax_epspe = fig.add_axes([0.55, 0.25, 0.35, 0.25])
    #         ax_epspe.bar(['EPS (TTM)', 'P/E Ratio'], [eps, pe])
    #         ax_epspe.set_title(f"{self.ticker}: EPS vs. P/E", fontsize=10)
    #         ax_epspe.set_ylabel('Value', fontsize=8)
    #
    #         pdf.savefig(fig)
    #         plt.close(fig)
    #
    #         # Additional pages for overflow text
    #         for chunk in chunks[1:]:
    #             fig = plt.figure(figsize=(11.69, 8.27))
    #             fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    #             ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    #             ax.axis('off')
    #             ax.text(0, 1, '\n'.join(chunk), va='top', wrap=True, fontsize=8)
    #             pdf.savefig(fig)
    #             plt.close(fig)
    #
    #         # Annual metrics table page
    #         fig, ax = plt.subplots(figsize=(11.69, 8.27))
    #         ax.axis('off')
    #         # Add title
    #         ax.set_title("Financial Metrics", fontsize=16, pad=20, weight='bold', loc='left')
    #
    #         # Create table
    #         table = ax.table(
    #             cellText=table_df.values,
    #             rowLabels=table_df.index,
    #             colLabels=table_df.columns,
    #             cellLoc='center',
    #             loc='upper center'
    #         )
    #         table.auto_set_font_size(False)
    #         table.set_fontsize(10)
    #         table.scale(1, 1.5)
    #
    #         # Draw top and bottom lines
    #         # Coordinates are in axis fraction
    #         ax.plot([0.05, 0.95], [0.88, 0.88], color='black', linewidth=1)
    #         ax.plot([0.05, 0.95], [0.10, 0.10], color='black', linewidth=1)
    #
    #         pdf.savefig(fig)
    #         plt.close(fig)
    #
    #     print(f"✅ Combined PDF saved to {self.output_path}")

if __name__ == "__main__":
    # Example usage:
    ticker = "UAL"
    year = 2025
    quarter = 1
    output_name = f'{ticker}_{year}_{quarter}_report.pdf'
    report = CombinedReportPDF(ticker, year, quarter, output_name=output_name)
    report.create_pdf()

