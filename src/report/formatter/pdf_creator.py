import os
from src.report.generator import InvestmentReportGenerator
from src.fdata_extractors.findata_extractor import YFinanceAnalyzer
from src.report.plotter import FinancialPlotter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

class CombinedReportPDF:
    """
    Generates a PDF report combining:
      1) LLM-generated sections: Investment Summary, Business Overview, Risk Assessment
      2) Financial charts: Close & MA(15,30,60,90), EPS vs. P/E Ratio
    """
    def __init__(self, ticker: str, year: int, quarter: int, output_path: str = "combined_report.pdf"):
        self.ticker = ticker
        self.year = year
        self.quarter = quarter
        self.output_path = output_path
        # Initialize LLM-based report generator
        self.generator = InvestmentReportGenerator()
        # Initialize financial data plotter
        self.plotter = FinancialPlotter(ticker)

    @staticmethod
    def _escape_dollars(s: str) -> str:
        return s.replace('$', r'\$')

    def create_pdf(self):
        # Generate text sections
        sections = self.generator.generate(self.ticker, self.year, self.quarter)
        summary = sections["investment_summary"]
        business = sections["business_overview"]
        risk     = sections["risk_assessment"]

        # Prepare PDF
        with PdfPages(self.output_path) as pdf:
            # Page 1: Text sections
            fig1, ax1 = plt.subplots(figsize=(8.27, 11.69))  # A4 size
            ax1.axis("off")
            full_text = (
                "=== Investment Summary ===\n" + self._escape_dollars(summary['summary']) + "\n\n" +
                "=== Business Overview ===\n" + self._escape_dollars(business['report']) + "\n\n" +
                "=== Risk Assessment ===\n" + self._escape_dollars(risk['report'])
            )
            ax1.text(0.02, 0.98, full_text, va="top", wrap=True)
            pdf.savefig(fig1, bbox_inches="tight")
            plt.close(fig1)

            # Page 2: Close price & Moving Averages
            df = self.plotter.analyzer.get_all_mas(
                price_period="1y", price_interval="1d",
                ma_windows=[15, 30, 60, 90]
            )
            fig2, ax2 = plt.subplots()
            ax2.plot(df.index, df["Close"], label="Close Price")
            for w in [15, 30, 60, 90]:
                ax2.plot(df.index, df[f"MA{w}"], label=f"MA{w}")
            ax2.set_title(f"{self.ticker}: Close & MA(15,30,60,90)")
            ax2.set_xlabel("Date")
            ax2.set_ylabel("Price")
            ax2.legend()
            fig2.tight_layout()
            pdf.savefig(fig2)
            plt.close(fig2)

            # Page 3: EPS (TTM) vs. P/E Ratio
            eps = self.plotter.analyzer.get_eps(n_quarters=4)
            pe  = self.plotter.analyzer.get_pe_ratio(
                price_period="1d", price_interval="1d", n_quarters=4
            )
            fig3, ax3 = plt.subplots()
            ax3.bar(["EPS (TTM)", "P/E Ratio"], [eps, pe])
            ax3.set_title(f"{self.ticker}: EPS (TTM) vs. P/E Ratio")
            ax3.set_ylabel("Value")
            fig3.tight_layout()
            pdf.savefig(fig3)
            plt.close(fig3)

        print(f"✅ Combined PDF report saved to {self.output_path}")

if __name__ == "__main__":
    # Example usage:
    report = CombinedReportPDF("AAPL", 2025, 1, output_path="AAPL_combined_report.pdf")
    report.create_pdf()

