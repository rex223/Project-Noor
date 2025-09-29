from crewai import Crew, Process
from crewai.project import CrewBase

from .tools import (  # noqa: F401
    conversation_memory_tool,
    email_parser_tool,
    explanation_builder_tool,
    gaming_ingest_tool,
    github_profile_tool,
    music_ingest_tool,
    persona_vector_store_tool,
    rec_catalog_tool,
    reinforcement_feedback_tool,
    safety_monitor_tool,
    sentiment_classifier_tool,
    survey_ingest_tool,
    video_ingest_tool,
)


@CrewBase
class BondhuAICrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            planning=True,
            verbose=2,
        )