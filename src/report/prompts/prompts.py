# SUMMARY_SECTION_PROMPT="""
# You are expert **financial analyst** that able to write a summary if a {company_name}'stock is worth to buy or sell.
#
# ### **Task:**
# Generate a forward looking **investment suggestion summary** for the investor base on the provided data in the list [Most recent Earning Conference Call, Last Fiscal Year's SEC 10K Filing - Item7 Management’s Discussion and Analysis of Financial Condition and Results of Operations, rencent Stock Price & Moving Average movement, Last 4 Quarter's income statement information]
# We will focus on one year prediction from ** Year {year} Quarter {quarter}** to ** Next Year {next_year} Quarter {quarter}**
#
# 1. Generate a signal whether to buy or sell
# 2. Generate a report summary why the investor should buy or sell
#
# Please remember DO NOT GENERATED SOME RANDOM NUMBER THAT YOU NEVER SEE
#
# ### **Data Provided:**
# 1. Earning Conference Call. Date: ** {year} Quarter {quarter} **
#     - {ecc_transcripts}
#
# 2. SEC 10K Filing - Item7 Management’s Discussion and Analysis of Financial Condition and Results of Operations. Date: ** fiscal year {fiscal_year} **
#     - {item7}
#
# 3. 1 Month Stock Price in a Dict Format: ** Date: Stock Price ** Today's Date: ** {today_date} **. Data provided below:
#     - {stock_price}
#
# 4. 1 Month Stock Price Moving Average in a Dict Format: ** Date: Stock Price Moving Average ** Today's Date: ** {today_date} **. Data provided below:
#     - MA15: {stock_price_ma_15}
#     - MA30: {stock_price_ma_30}
#     - MA60: {stock_price_ma_60}
#     - MA90: {stock_price_ma_90}
#     - MA120: {stock_price_ma_120}
#
# 5. 1 Year Income Statement Information in a Dict Format: ** Date: Value ** Today's Date: ** {today_date} **. Data provided below:
#     - EPS: {eps}
#     - Total_revenues: {total_revenues}
#     - EBITDA: {ebitda}
#
# Please organize the output into one paragraph, and keep it to about 300–400 words.
#
# ### **Output Format:**
# {format_instructions}
# """
#
# BUSINESS_SECTION_PROMPT = """
# You are a financial research assistant. I will provide you with two inputs:
# 1. The “Item 1. Business” section from the company’s latest SEC 10-K filing.
#     - {item1}
# 2. The transcript of the company’s most recent earnings conference call.
#     - {ecc_transcripts}
# Your task is to draft a clear, concise “Business Overview” section that:
# • Summarizes the company’s core operations, business segments, and key products/services.
# • Highlights the geographic markets in which the company competes.
# • Describes any major strategic initiatives, recent developments, or competitive advantages mentioned in the call.
# • Uses language suitable for inclusion in an investment research report.
#
# Please organize the output into one paragraph, and keep it to about 300–400 words.
#
# ### **Output Format:**
# {format_instructions}
# """
#
# RISK_ASSESSMENT_SECTION_PROMPT = """
# You are a financial research assistant. I will provide you with one input:
# 1. The “Item 1A. Risk Factors” section from the company’s latest SEC 10-K filing.
#     - {item1a}
#
# Your task is to produce a structured risk assessment that:
# • Identifies and summarizes the top 5–7 material risks facing the company.
# • Categorizes each risk (e.g., market, operational, regulatory, technological, geopolitical).
# • Explains the potential impact of each risk on the company’s business, operations, and financial performance.
# • Notes any recent changes or trends in these risk factors compared to prior filings.
# • Suggests possible mitigation strategies or management responses, if discussed in the filing.
#
# Please organize the output into one paragraph. Aim for approximately 400–500 words.
#
# ### **Output Format:**
# {format_instructions}
# """
