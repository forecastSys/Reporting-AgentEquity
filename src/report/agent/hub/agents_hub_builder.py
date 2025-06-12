from src.report.models import ReportTeamConfig, EvaluatorConfig
from textwrap import dedent

# sections = section['full_name'],
# description = desc.get('description', ''),
# input = desc.get('inputs', ''),
# deliverable = desc.get('deliverable', '')

class AgentsHubBuilder:

    @staticmethod
    def build_sup_hub(sections, instruction, prompt_template):
        def _get_acronym(phrase: str) -> str:
            def _is_title_case(phrase: str) -> bool:
                return all(word.istitle() for word in phrase.split() if word.isalpha())

            if not _is_title_case(phrase):
                raise ValueError(
                    f"[{AgentsHubBuilder.__name__}.build_sup_hub._get_acronym] Invalid section name: '{phrase}'. "
                    "Each word must start with a capital letter (e.g., 'Fair Value', 'Business Strategy')."
                )

            return ''.join(word[0] for word in phrase.split() if word[0].isupper())

        sup_hub = {}
        for key, section in sections.items():
            desc = section.section_description
            section_name = section.section_name
            short_section_name = _get_acronym(section_name)
            team_key = f"{key}_team"

            sup_hub[team_key] = ReportTeamConfig(
                supervisor_name=f"{short_section_name}_Team_Supervisor",
                section=section_name,
                team_name=f"{short_section_name}_Team",
                assistant_name=f"{short_section_name}_Assistant",
                evaluator_name=f"{short_section_name}_Evaluator",
                data_tools=section.tools,
                prompt_section_specific=desc.section_specific_desc,
                prompt_section_tools=", ".join(section.tools),
                prompt_section_deliverable=desc.section_deliverable,
                desc=dedent(prompt_template),
                assistant_instruction=dedent(instruction)
            )
        return sup_hub

    @staticmethod
    def build_eval_hub(prompt_template):
        name = "evaluator"
        eval2assit_instruction = ("\n\n **Please refine your written section base on the feedback, "
                                  "Please only refine your previous written section, DO NOT REMOVE ANY PART unless it is mentioned by the feedback provided.**")
        evaluation_hub = EvaluatorConfig(
            name=name,
            evaluator_instruction=dedent(prompt_template),
            evaluator2assistant_instruction=dedent(eval2assit_instruction)
        )
        return evaluation_hub