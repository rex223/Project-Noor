from copy import deepcopy

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase

from .tools import (
    conversation_memory_tool as conversation_memory_tool_obj,
    email_parser_tool as email_parser_tool_obj,
    explanation_builder_tool as explanation_builder_tool_obj,
    gaming_ingest_tool as gaming_ingest_tool_obj,
    github_profile_tool as github_profile_tool_obj,
    music_ingest_tool as music_ingest_tool_obj,
    persona_vector_store_tool as persona_vector_store_tool_obj,
    rec_catalog_tool as rec_catalog_tool_obj,
    reinforcement_feedback_tool as reinforcement_feedback_tool_obj,
    safety_monitor_tool as safety_monitor_tool_obj,
    sentiment_classifier_tool as sentiment_classifier_tool_obj,
    survey_ingest_tool as survey_ingest_tool_obj,
    video_ingest_tool as video_ingest_tool_obj,
)


@CrewBase
class BondhuAICrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def crew(self) -> Crew:
        # Create a Gemini LLM instance for consistent provider usage
        gemini_llm = LLM(model="gemini/gemini-2.5-flash-preview-04-17")
        
        manager = self.orchestrator_agent()
        agents = [
            self.data_collection_agent(),
            self.personality_analysis_agent(),
            self.interaction_agent(),
            self.recommendation_agent(),
        ]

        name_to_agent = {
            "orchestrator_agent": manager,
            "data_collection_agent": agents[0],
            "personality_analysis_agent": agents[1],
            "interaction_agent": agents[2],
            "recommendation_agent": agents[3],
        }

        tasks = []
        for cfg in self.tasks_config.values():
            task_cfg = deepcopy(cfg)
            agent_entry = task_cfg.get("agent")
            if isinstance(agent_entry, Agent):
                task_cfg["agent"] = agent_entry
            elif isinstance(agent_entry, str):
                task_cfg["agent"] = name_to_agent[agent_entry]
            task_cfg.pop("depends_on", None)
            tasks.append(Task(**task_cfg))

        return Crew(
            agents=agents,
            tasks=tasks,
            process=Process.hierarchical,
            planning=True,
            verbose=True,
            manager_agent=manager,
            manager_llm=gemini_llm,  # Explicitly set manager LLM to Gemini
        )

    # -------- Agent factories -------------------------------------------------

    def _build_agent(self, agent_name: str) -> Agent:
        """Instantiate and cache an Agent from the YAML configuration."""
        if not hasattr(self, "_agent_cache"):
            self._agent_cache = {}

        if agent_name not in self._agent_cache:
            config = deepcopy(self.agents_config[agent_name])
            self._agent_cache[agent_name] = Agent(**config)

        return self._agent_cache[agent_name]

    def orchestrator_agent(self) -> Agent:
        return self._build_agent("orchestrator_agent")

    orchestrator_agent.is_agent = True

    def data_collection_agent(self) -> Agent:
        return self._build_agent("data_collection_agent")

    data_collection_agent.is_agent = True

    def personality_analysis_agent(self) -> Agent:
        return self._build_agent("personality_analysis_agent")

    personality_analysis_agent.is_agent = True

    def interaction_agent(self) -> Agent:
        return self._build_agent("interaction_agent")

    interaction_agent.is_agent = True

    def recommendation_agent(self) -> Agent:
        return self._build_agent("recommendation_agent")

    recommendation_agent.is_agent = True

    def music_ingest_tool(self):
        return music_ingest_tool_obj

    music_ingest_tool.is_tool = True

    def video_ingest_tool(self):
        return video_ingest_tool_obj

    video_ingest_tool.is_tool = True

    def gaming_ingest_tool(self):
        return gaming_ingest_tool_obj

    gaming_ingest_tool.is_tool = True

    def survey_ingest_tool(self):
        return survey_ingest_tool_obj

    survey_ingest_tool.is_tool = True

    def github_profile_tool(self):
        return github_profile_tool_obj

    github_profile_tool.is_tool = True

    def email_parser_tool(self):
        return email_parser_tool_obj

    email_parser_tool.is_tool = True

    def persona_vector_store_tool(self):
        return persona_vector_store_tool_obj

    persona_vector_store_tool.is_tool = True

    def conversation_memory_tool(self):
        return conversation_memory_tool_obj

    conversation_memory_tool.is_tool = True

    def safety_monitor_tool(self):
        return safety_monitor_tool_obj

    safety_monitor_tool.is_tool = True

    def sentiment_classifier_tool(self):
        return sentiment_classifier_tool_obj

    sentiment_classifier_tool.is_tool = True

    def rec_catalog_tool(self):
        return rec_catalog_tool_obj

    rec_catalog_tool.is_tool = True

    def reinforcement_feedback_tool(self):
        return reinforcement_feedback_tool_obj

    reinforcement_feedback_tool.is_tool = True

    def explanation_builder_tool(self):
        return explanation_builder_tool_obj

    explanation_builder_tool.is_tool = True