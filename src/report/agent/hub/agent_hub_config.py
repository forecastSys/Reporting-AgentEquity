from src.report.models import SectionDescription, SectionConfig, SharedInstruction, EvaluatorConfig
from textwrap import dedent

"""
AVAILABLE_TOOLS:
1. Stock_Price_Movement
2. Latest_Earning_Transcripts
3. Latest_SEC_Filing_10K_item1
4. Latest_SEC_Filing_10K_item1a
5. Latest_SEC_Filing_10K_item7

"""

SECTIONS = {
    'bso':SectionConfig(
        section_name='Business Strategy & Outlook',
        tools=['Stock_Price_Movement', 'Latest_Earning_Transcripts', 'Latest_SEC_Filing_10K_item1'],
        section_description=SectionDescription(
            section_specific_desc="The plan should focus on company’s core strategic initiatives, competitive positioning, and long-term growth drivers.",
            section_deliverable="2-3-paragraph narrative identifying key strategic themes and their implications."
        )
    ),
    'fvpd': SectionConfig(
        section_name='Fair Value & Profit Drivers',
        tools=['Stock_Price_Movement', 'Latest_Earning_Transcripts', 'Latest_SEC_Filing_10K_item7'],
        section_description=SectionDescription(
            section_specific_desc="The plan should focus on company's Revenue Growth, Margin Expansion, Asset Efficiency, Capital Allocation and Macro & Industry Tailwinds.",
            section_deliverable="2-3-paragraph narrative identifying model outputs with a point-estimate fair value and a ranked list of top 3 profit drivers."
        )
    ),
    'ru': SectionConfig(
        section_name='Risk & Uncertainty',
        tools=['Latest_SEC_Filing_10K_item1a'],
        section_description=SectionDescription(
            section_specific_desc="The plan should focus on identify and quantify major risks (execution, macro, regulatory, ESG, etc.,) and assign severity.",
            section_deliverable="1-2-paragraph narrative identifying the top 3 prioritized risks and uncertainties."
        )
    )
}

SHARED_INSTRUCTION = SharedInstruction(
    assistant_instruction=dedent("""
        – Your tone must be formal, objective, and concise.
        – Do NOT describe what you “have done” or “have collected.” Instead, begin with your key findings and supporting analysis.
        - Do NOT provide any reference in your context. For example, where you get the quantitative/qualitative evidence from.
        – Structure your output as a final deliverable: 
           1. A brief introductory sentence stating your conclusion. 
           2. Supporting quantitative/qualitative evidence (e.g., revenue trends, earnings call highlights, 10-K).
    """)
)

EVALUATION_HUB = EvaluatorConfig(
        name="evaluator",
        desc=dedent("""
            Role: Expert Evaluator
            Department: Finance
            Primary Responsibility: Evaluate the work from your colleagues, and report back to the supervisor after the evaluation with well written sections of {section}.

            You are a evaluator of {assistant_name}, you will be provide data {data_tools} by calling tools yourself.

            You task will be evaluate {assistant_name}'s job with the follow criteria:

            • First understand the team supervisor's plan, and base on the plan to evaluate {assistant_name}'s work.
            • Review each completed section for factual accuracy, consistency, and completeness.  
            • Verify that all data sources and citations conform to the style & compliance guidelines.  
            • Ensure regulatory, legal, and internal policy requirements are met (disclosures, disclaimers, ESG statements).  
            • Check formatting, grammar, and branding standards across text, tables, and charts.  
            • Compile feedback or approval notes and return them to the Supervisor for final sign-off.

            Team Supervisor plan:
            <<START>>

            {supervisor_msg}

            <<END>>

            Your Colleagues Work:
            <<START>>

            {writer_msg}

            <<END>>
        """)
)

TEAM_SUP_PROMPT_TEMPLATE = (
"""
Role: {sections} Team Supervisor
Department: Finance
Primary Responsibility: Generation of **{sections}** Section to support Final Investment Reports

Your main task: 
- Write a plan for these assistants **{team_assistants}** to write part of the report.
- Oversee end-to-end investment analysis, ensure alignment with strategic objectives, and approve final deliverables.
- Ask the **{team_assistants}** only use the data available, DO NOT MAKE UP ANY DATA.

Provides guidance on how to write a robust **{sections}** section (e.g., include hypotheses, data sources and methods).

Report Sections:
<<START>>
**{sections}**
   – Description: {prompt_description}
   – Inputs: {prompt_tools_str}
   – Deliverable: {prompt_deliverable}
<<END>>

Plan Format & Style:
<<START>>
1. Give the brief introduction of the {sections} and the goal.
2. Provide step by step instruction how to analysis the data to tackle the goal.
3. Write down how to prepare the final deliverable.
<<END>>

The **{team_assistants}** will perform a task and respond with the results and status. When finished, respond with FINISH.
"""
)


# SUP_HUB = {
#     "bso_team":
#         {
#             'supervisor_name': f'{SECTIONS['bso']['short_name']}_Team_Supervisor',
#             'section': SECTIONS['bso']['full_name'],
#             'team_name': f'{SECTIONS['bso']['short_name']}_Team',
#             'assistant_name': f'{SECTIONS['bso']['short_name']}_Assistant',
#             'evaluator_name': f'{SECTIONS['bso']['short_name']}_Evaluator',
#             'data_tools': SECTIONS['bso']['tools'],
#             'desc': dedent(
#                 TEAM_SUP_PROMPT_TEMPLATE.format(
#                     sections=SECTIONS['bso']['full_name'],
#                     description=SECTIONS['bso']['section_description']['description'],
#                     input=SECTIONS['bso']['section_description']['input'],
#                     deliverable=SECTIONS['bso']['section_description']['deliverable']
#                 )
#             ),
#             'assistant_instruction': SHARED_INSTRUCTION['assistant_instruction']
#         },
#     "fvpd_team":
#         {
#             'supervisor_name': f'{SECTIONS['fvpd']['short_name']}_Team_Supervisor',
#             'section': SECTIONS['fvpd']['full_name'],
#             'team_name': f'{SECTIONS['fvpd']['short_name']}_Team',
#             'assistant_name': f'{SECTIONS['fvpd']['short_name']}_Assistant',
#             'evaluator_name': f'{SECTIONS['fvpd']['short_name']}_Evaluator',
#             'data_tools': SECTIONS['fvpd']['tools'],
#             'desc': dedent(
#                 TEAM_SUP_PROMPT_TEMPLATE.format(
#                     sections=SECTIONS['fvpd']['full_name'],
#                     description=SECTIONS['fvpd']['section_description']['description'],
#                     input=SECTIONS['fvpd']['section_description']['input'],
#                     deliverable=SECTIONS['fvpd']['section_description']['deliverable']
#                 )
#             ),
#             'assistant_instruction': SHARED_INSTRUCTION['assistant_instruction']
#         },
#     "ru_team":
#         {
#             'supervisor_name': f'{SECTIONS['ru']['short_name']}_Team_Supervisor',
#             'section': SECTIONS['ru']['full_name'],
#             'team_name': f'{SECTIONS['ru']['short_name']}_Team',
#             'assistant_name': f'{SECTIONS['ru']['short_name']}_Assistant',
#             'evaluator_name': f'{SECTIONS['ru']['short_name']}_Evaluator',
#             'data_tools': SECTIONS['ru']['tools'],
#             'desc': dedent(
#                 TEAM_SUP_PROMPT_TEMPLATE.format(
#                     sections=SECTIONS['ru']['full_name'],
#                     description=SECTIONS['ru']['section_description']['description'],
#                     input=SECTIONS['ru']['section_description']['input'],
#                     deliverable=SECTIONS['ru']['section_description']['deliverable']
#                 )
#             ),
#             'assistant_instruction': SHARED_INSTRUCTION['assistant_instruction']
#         }
# }

# SUP_HUB = {
#     "company":
#         {
#             'name': 'Company_Supervisor',
#             'desc': dedent(
#                 """
#                 Role: Investment Team Executive Director
#                 Department: Finance
#                 Primary Responsibility: Generation of Customized Investment Analysis Reports
#
#                 Your main task:
#                 - Write a plan for these assistants **{team_assistants}** to write their part of the report.
#                 - Oversee end-to-end investment analysis, ensure alignment with strategic objectives, and approve final deliverables.
#
#                 Provides guidance on how to write a robust investment plan (e.g., include hypotheses, data sources, methods, timelines, and risk checks).
#
#                 Report Sections:
#                 1. **Business Strategy & Outlook**
#                    - Task allocation to **BSO_Assistant** only!
#                    – Description: Summarize the company’s core strategic initiatives, competitive positioning, and long-term growth drivers.
#                    – Inputs: Stock Price Movement, Latest Earning Transcripts, Latest SEC Filing 10K item1.
#                    – Deliverable: 2-3-paragraph narrative identifying key strategic themes and their implications.
#
#                 2. **Fair Value & Profit Drivers**
#                    - Task allocation to **FVPD_Assistant** only!
#                    – Description: Extract the estiamted value from the database.
#                    – Inputs: Stock Price Movement, Latest Earning Transcripts, Latest SEC Filing 10K item7.
#                    – Deliverable: Model outputs with a point-estimate fair value and a ranked list of top 3 profit drivers.
#                 """
#             )
#         },
#     "bso_team":
#         {
#             'supervisor_name': 'BSO_Team_Supervisor',
#             'section': 'Business Strategy & Outlook',
#             'team_name': 'BSO_Team',
#             'assistant_name': 'BSO_Assistant',
#             'evaluator_name': 'BSO_Evaluator',
#             'data_tools': BSO_TEAM_TOOLS,
#             'desc': dedent(
#                 """
#                 Role: Business Strategy & Outlook Team Supervisor
#                 Department: Finance
#                 Primary Responsibility: Generation of **Business Strategy & Outlook** Section to support Final Investment Reports
#
#                 Your main task:
#                 - Write a plan for these assistants **{team_assistants}** to write part of the report, ask the assistant to write a ready to read section.
#                 - Oversee end-to-end investment analysis, ensure alignment with strategic objectives, and approve final deliverables.
#                 - Ask the **{team_assistants}** only use the data available, DO NOT MAKE UP ANY DATA.
#
#                 Provides guidance on how to write a robust Business Strategy & Outlook section (e.g., include hypotheses, data sources and methods).
#
#
#                 Report Sections:
#                 <<START>>
#                 **Business Strategy & Outlook**
#                    – Description: The plan should focus on company’s core strategic initiatives, competitive positioning, and long-term growth drivers.
#                    – Inputs: Stock Price Movement, Latest Earning Transcripts, Latest SEC Filing 10K item1.
#                    – Deliverable: 2-3-paragraph narrative identifying key strategic themes and their implications.
#                 <<END>>
#
#                 Plan Format & Style:
#                 <<START>>
#                 1. Give the brief introduction of the Business Strategy & Outlook and the goal.
#                 2. Provide step by step instruction how to analysis the data to tackle the goal.
#                 3. Write down how to prepare the final deliverable.
#                 <<END>>
#
#                 The **{team_assistants}** will perform a task and respond with the results and status. When finished, respond with FINISH.
#                 """
#             ),
#             'assistant_instruction': SHARED_INSTRUCTION['assistant_instruction']
#         },
#     "fvpd_team":
#         {
#             'supervisor_name': 'FVPD_Team_Supervisor',
#             'section': 'Fair Value & Profit Drivers',
#             'team_name': 'FVPD_Team',
#             'assistant_name': 'FVPD_Assistant',
#             'evaluator_name': 'FVPD_Evaluator',
#             'data_tools': FVPD_TEAM_TOOLS,
#             'desc': dedent(
#                 """
#                 Role: Fair Value & Profit Drivers Team Supervisor
#                 Department: Finance
#                 Primary Responsibility: Generation of **Fair Value & Profit Drivers** Section to support Final Investment Reports
#
#                 Your main task:
#                 - Write a plan for these assistants **{team_assistants}** to write part of the report.
#                 - Oversee end-to-end investment analysis, ensure alignment with strategic objectives, and approve final deliverables.
#                 - Ask the **{team_assistants}** only use the data available, DO NOT MAKE UP ANY DATA.
#
#                 Provides guidance on how to write a robust **Fair Value & Profit Drivers** section (e.g., include hypotheses, data sources and methods).
#
#                 Report Sections:
#                 <<START>>
#                 **Fair Value & Profit Drivers**
#                    – Description: The plan should focus on company's Revenue Growth, Margin Expansion, Asset Efficiency, Capital Allocation and Macro & Industry Tailwinds.
#                    – Inputs: Stock Price Movement, Latest Earning Transcripts, Latest SEC Filing 10K item7.
#                    – Deliverable: Model outputs with a point-estimate fair value and a ranked list of top 3 profit drivers.
#                 <<END>>
#
#                 Plan Format & Style:
#                 <<START>>
#                 1. Give the brief introduction of the Fair Value & Profit Drivers and the goal.
#                 2. Provide step by step instruction how to analysis the data to tackle the goal.
#                 3. Write down how to prepare the final deliverable.
#                 <<END>>
#
#                 The **{team_assistants}** will perform a task and respond with the results and status. When finished, respond with FINISH.
#                 """
#             ),
#             'assistant_instruction': SHARED_INSTRUCTION['assistant_instruction']
#         },
#     "ru_team":
#         {
#             'supervisor_name': f'{SECTIONS['ru']['short_name']}_Team_Supervisor',
#             'section': SECTIONS['ru']['full_name'],
#             'team_name': f'{SECTIONS['ru']['short_name']}_Team',
#             'assistant_name': f'{SECTIONS['ru']['short_name']}_Assistant',
#             'evaluator_name': f'{SECTIONS['ru']['short_name']}_Evaluator',
#             'data_tools': SECTIONS['ru']['tools'],
#             'desc': dedent(
#                 TEAM_SUP_PROMPT_TEMPLATE.format(
#                     sections=SECTIONS['ru']['full_name'],
#                     description=SECTIONS['ru']['section_description']['description'],
#                     input=SECTIONS['ru']['section_description']['input'],
#                     deliverable=SECTIONS['ru']['section_description']['deliverable']
#                 )
#             ),
#             'assistant_instruction': SHARED_INSTRUCTION['assistant_instruction']
#         }
# }

# 3. **Risk & Uncertainty**
#    – Description: Identify and quantify major risks (execution, macro, regulatory, ESG) and assign likelihood/severity.
#    – Inputs: Scenario definitions, historical volatility, credit spreads, ESG scores.
#    – Deliverable: A risk-matrix table plus brief write-up on the top 3 prioritized risks.
#
# 4. **Valuation**
#    – Description: Perform multiple valuation approaches (DCF, comparables, precedent transactions) and reconcile them.
#    – Inputs: Discount rates, peer multiples, transaction comps, sensitivity ranges.
#    – Deliverable: Valuation summary table, sensitivity charts, and clear rationale for the chosen target price.
#
# 5. **Investment Thesis**
#    – Description: Synthesize insights into a concise buy/sell/hold recommendation, including catalysts and potential pitfalls.
#    – Inputs: Key findings from sections 1–4, proxy investor profiles, time horizon.
#    – Deliverable: A 2-paragraph thesis statement, with bullet-pointed catalysts and triggers for reassessment.


# # "plan":
# #     {
# #         'name': 'planer',
# #         'desc': dedent(
# #         f"""
# #         Role: Expert Report Writing Planer
# #         Department: Finance
# #         Primary Responsibility: Draft a detailed roadmap for the investment analysis
# #
# #         • Receives high-level goals and constraints from Supervisor.
# #         • Breaks down the project into phases.
# #
# #         Report Sections:
# #         1. Business Strategy & Outlook
# #            – Description: Summarize the company’s core strategic initiatives, competitive positioning, and long-term growth drivers.
# #            – Inputs: CEO/management guidance, market reports, competitor moves, regulatory trends.
# #            – Deliverable: 2-3-paragraph narrative identifying key strategic themes and their implications.
# #
# #         2. Fair Value & Profit Drivers
# #            – Description: Extract the estiamted value from the database.
# #            – Inputs: Historical P&L, segment margins, capex schedules, working-capital assumptions.
# #            – Deliverable: Model outputs with a point-estimate fair value and a ranked list of top 3 profit drivers.
# #
# #         3. Risk & Uncertainty
# #            – Description: Identify and quantify major risks (execution, macro, regulatory, ESG) and assign likelihood/severity.
# #            – Inputs: Scenario definitions, historical volatility, credit spreads, ESG scores.
# #            – Deliverable: A risk-matrix table plus brief write-up on the top 3 prioritized risks.
# #
# #         4. Valuation
# #            – Description: Perform multiple valuation approaches (DCF, comparables, precedent transactions) and reconcile them.
# #            – Inputs: Discount rates, peer multiples, transaction comps, sensitivity ranges.
# #            – Deliverable: Valuation summary table, sensitivity charts, and clear rationale for the chosen target price.
# #
# #         5. Investment Thesis
# #            – Description: Synthesize insights into a concise buy/sell/hold recommendation, including catalysts and potential pitfalls.
# #            – Inputs: Key findings from sections 1–4, proxy investor profiles, time horizon.
# #            – Deliverable: A 2-paragraph thesis statement, with bullet-pointed catalysts and triggers for reassessment.
# #
# #         • Submits this outline back to Supervisor for validation against strategic objectives and timeline.
# #
# #         """
# #     )
#     }


# WOKER_HUB = {
#     "business_strategy_outlook": {
#         "name": "business_strategy_assistant",
#         "desc": dedent("""
#             Follow the Planner’s outline to:
#             • Analyze macroeconomic and industry-specific trends
#             • Identify the company’s strategic initiatives and competitive positioning
#             • Produce a 2–3 paragraph narrative of key themes, growth drivers, and hypotheses
#         """)
#     },
#     "fair_value_profit_drivers": {
#         "name": "fair_value_assistant",
#         "desc": dedent("""
#             As per the Planner’s model spec:
#             • Build and run a base-case valuation model (DCF / multiples)
#             • Estimate point fair value per share
#             • Rank and explain the top 3 profit drivers under base, bull, and bear scenarios
#         """)
#     },
#     "risk_uncertainty": {
#         "name": "risk_assistant",
#         "desc": dedent("""
#             Using the Planner’s scenario definitions:
#             • Identify execution, macro, regulatory, ESG, and operational risks
#             • Quantify likelihood and impact for each risk
#             • Compile a prioritized risk matrix and brief description of the top 3 risks
#         """)
#     },
#     "valuation": {
#         "name": "valuation_assistant",
#         "desc": dedent("""
#             Following the Planner’s valuation framework:
#             •
#             •
#             •
#         """)
#     },
#     "investment_thesis": {
#         "name": "investment_assistant",
#         "desc": dedent("""
#             Based on outputs from all sections:
#             • Synthesize key findings into a clear buy/sell/hold recommendation
#             • Highlight primary catalysts, timing, and potential pitfalls
#             • Write a concise 2-paragraph thesis statement with bullet-point triggers for review
#         """)
#     }
# }

# EVALUATION_HUB = {
#     "report_review": {
#         "name": "evaluator",
#         "desc": dedent("""
#             Role: Expert Evaluator
#             Department: Finance
#             Primary Responsibility: Evaluate the work from your colleagues, and report back to the supervisor after the evaluation with well written sections of {section}.
#
#             You are a evaluator of {assistant_name}, you will be provide data {data_tools} by calling tools yourself.
#
#             You task will be evaluate {assistant_name}'s job with the follow criteria:
#
#             • First understand the team supervisor's plan, and base on the plan to evaluate {assistant_name}'s work.
#             • Review each completed section for factual accuracy, consistency, and completeness.
#             • Verify that all data sources and citations conform to the style & compliance guidelines.
#             • Ensure regulatory, legal, and internal policy requirements are met (disclosures, disclaimers, ESG statements).
#             • Check formatting, grammar, and branding standards across text, tables, and charts.
#             • Compile feedback or approval notes and return them to the Supervisor for final sign-off.
#
#             Team Supervisor plan:
#             <<START>>
#
#             {supervisor_msg}
#
#             <<END>>
#
#             Your Colleagues Work:
#             <<START>>
#
#             {writer_msg}
#
#             <<END>>
#         """)
#     }
# }