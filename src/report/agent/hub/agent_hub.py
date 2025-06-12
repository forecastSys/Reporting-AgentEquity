from src.report.agent.hub.agents_hub_builder import AgentsHubBuilder
from src.report.agent.hub.agent_hub_config import SECTIONS
from src.report.prompts import TEAM_SUP_PROMPT_TEMPLATE, TEAM_EVAL_PROMPT_TEMPLATE, SHARED_INSTRUCTION_TEMPLATE

SUP_HUB = AgentsHubBuilder.build_sup_hub(SECTIONS, SHARED_INSTRUCTION_TEMPLATE, TEAM_SUP_PROMPT_TEMPLATE)
EVALUATION_HUB = AgentsHubBuilder.build_eval_hub(TEAM_EVAL_PROMPT_TEMPLATE)