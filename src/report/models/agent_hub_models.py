from dataclasses import dataclass
from typing import List

## --- <START> Data Model - agent_hub_builder ---
@dataclass
class ReportTeamConfig:
    supervisor_name: str
    section: str
    team_name: str
    assistant_name: str
    evaluator_name: str
    data_tools: List[str]
    prompt_section_specific: str
    prompt_section_tools: str
    prompt_section_deliverable: str
    desc: str
    assistant_instruction: str
## --- <END> ---

## --- <START> Data Model - agent_hub_config ---
@dataclass
class SectionDescription:
    section_specific_desc: str
    section_deliverable: str

@dataclass
class SectionConfig:
    section_name: str
    tools: List[str]
    section_description: SectionDescription

@dataclass
class SharedInstruction:
    assistant_instruction: str

@dataclass
class EvaluatorConfig:
    name: str
    evaluator_instruction: str
    evaluator2assistant_instruction: str

## --- <END> ---