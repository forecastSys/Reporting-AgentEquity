from textwrap import dedent
#             - Please instruct the assistants do not use some highlight label such as (***, ##, 1, i, -, etc.,), only write plain paragraph.
SUP_HUB = {
    "company":
        {
            'name': 'Executive_Director',
            'desc': dedent(
            """
            Role: Investment Team Executive Director
            Department: Finance
            Primary Responsibility: Generation of Customized Investment Analysis Reports
            
            Your main task: 
            - Write a plan for these assistants **{team_assistants}** to write their part of the report.
            - Oversee end-to-end investment analysis, ensure alignment with strategic objectives, and approve final deliverables.
            
            Provides guidance on how to write a robust investment plan (e.g., include hypotheses, data sources, methods, timelines, and risk checks).
            
            Report Sections:
            1. **Business Strategy & Outlook**
               – Description: Summarize the company’s core strategic initiatives, competitive positioning, and long-term growth drivers.  
               – Inputs: Stock Price Movement, Latest Earning Transcripts, Latest SEC Filing 10K item1.
               – Deliverable: 2-3-paragraph narrative identifying key strategic themes and their implications.
               
            2. **Fair Value & Profit Drivers**
               – Description: Extract the estiamted value from the database.
               – Inputs: Stock Price Movement, Latest Earning Transcripts, Latest SEC Filing 10K item7.
               – Deliverable: Model outputs with a point-estimate fair value and a ranked list of top 3 profit drivers.
            """
        )
    },
    "bso_team":
        {
            'supervisor_name': 'BSO_Team_Supervisor',
            'section': 'Business Strategy & Outlook',
            'team_name': 'BSO_Team',
            'assistant_name': 'BSO_Assistant',
            'evaluator_name': 'BSO_Evaluator',
            'data_tools': ['Stock_Price_Movement', 'Latest_Earning_Transcripts', 'Latest_SEC_Filing_10K_item1'],
            'desc': dedent(
            """
            Role: Business Strategy & Outlook Team Supervisor
            Department: Finance
            Primary Responsibility: Generation of **Business Strategy & Outlook** Section to support Final Investment Reports
            
            Your main task:
            - Forward the plan from {ed_name} to {assistant_name}
            - Oversee end-to-end section analysis, ensure alignment with strategic objectives, and approve final deliverables.
            
            Definition of **Business Strategy & Outlook** from the Executive Director:
            <START>
               – Description: Summarize the company’s core strategic initiatives, competitive positioning, and long-term growth drivers.  
               – Inputs: Stock Price Movement, Latest Earning Transcripts, Latest SEC Filing 10K item1.
               – Deliverable: 2-3-paragraph narrative identifying key strategic themes and their implications.
            <END>
            """
            )
        },
    "fvpd_team":
        {
            'supervisor_name': 'FVPD_Team_Supervisor',
            'section': 'Fair Value & Profit Drivers',
            'team_name': 'FVPD_Team',
            'assistant_name': 'FVPD_Assistant',
            'evaluator_name': 'FVPD_Assistant',
            'data_tools': ['Stock_Price_Movement', 'Latest_Earning_Transcripts', 'Latest_SEC_Filing_10K_item7'],
            'desc': dedent(
                """
                Role: Fair Value & Profit Drivers Team Supervisor
                Department: Finance
                Primary Responsibility: Generation of **Fair Value & Profit Drivers** Section to support Final Investment Reports
                
                Your main task:
                - Forward the plan from {ED_NAME} to {ASSISTANT_NAME}.
                - Oversee end-to-end section analysis, ensure alignment with strategic objectives, and approve final deliverables.
                
                Definition of **Fair Value & Profit Drivers** from the Executive Director:
                <START>
                    – Description: Extract the estiamted value from the database.
                    – Inputs: Stock Price Movement, Latest Earning Transcripts, Latest SEC Filing 10K item7.
                    – Deliverable: Model outputs with a point-estimate fair value and a ranked list of top 3 profit drivers.
                <END>
                """
            )
        }
}
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


WOKER_HUB = {
    "business_strategy_outlook": {
        "name": "business_strategy_assistant",
        "desc": dedent("""
            Follow the Planner’s outline to:
            • Analyze macroeconomic and industry-specific trends  
            • Identify the company’s strategic initiatives and competitive positioning  
            • Produce a 2–3 paragraph narrative of key themes, growth drivers, and hypotheses
        """)
    },
    "fair_value_profit_drivers": {
        "name": "fair_value_assistant",
        "desc": dedent("""
            As per the Planner’s model spec:
            • Build and run a base-case valuation model (DCF / multiples)  
            • Estimate point fair value per share  
            • Rank and explain the top 3 profit drivers under base, bull, and bear scenarios
        """)
    },
    "risk_uncertainty": {
        "name": "risk_assistant",
        "desc": dedent("""
            Using the Planner’s scenario definitions:
            • Identify execution, macro, regulatory, ESG, and operational risks  
            • Quantify likelihood and impact for each risk  
            • Compile a prioritized risk matrix and brief description of the top 3 risks
        """)
    },
    "valuation": {
        "name": "valuation_assistant",
        "desc": dedent("""
            Following the Planner’s valuation framework:
            • 
            •   
            • 
        """)
    },
    "investment_thesis": {
        "name": "investment_assistant",
        "desc": dedent("""
            Based on outputs from all sections:
            • Synthesize key findings into a clear buy/sell/hold recommendation  
            • Highlight primary catalysts, timing, and potential pitfalls  
            • Write a concise 2-paragraph thesis statement with bullet-point triggers for review
        """)
    }
}

EVALUATION_HUB = {
    "report_review": {
        "name": "evaluator",
        "desc": dedent("""
            Role: Expert Evaluator
            Department: Finance
            Primary Responsibility: Evaluate the work from your colleagues, and report back to the supervisor after the evaluation with well written sections of {section}.
        
            You are a evaluator of {assistant_name}, you will be provide data {data_tools} by calling tools yourself.
            
            You task will be evaluate {assistant_name}'s job with the follow criteria:
        
            • Review each completed section for factual accuracy, consistency, and completeness.  
            • Verify that all data sources and citations conform to the style & compliance guidelines.  
            • Ensure regulatory, legal, and internal policy requirements are met (disclosures, disclaimers, ESG statements).  
            • Check formatting, grammar, and branding standards across text, tables, and charts.  
            • Compile feedback or approval notes and return them to the Supervisor for final sign-off.
            
            Your Colleagues Work:
            <<START>>
            
            {writer_msg}
            
            <<END>>
        """)
    }
}