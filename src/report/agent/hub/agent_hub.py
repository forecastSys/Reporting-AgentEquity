from src.report.agent.hub.agents_hub_builder import AgentsHubBuilder
from src.report.agent.hub.agent_hub_config import SECTIONS, SHARED_INSTRUCTION, TEAM_SUP_PROMPT_TEMPLATE, EVALUATION_HUB

SUP_HUB = AgentsHubBuilder.build_sup_hub(SECTIONS, SHARED_INSTRUCTION, TEAM_SUP_PROMPT_TEMPLATE)