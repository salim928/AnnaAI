"""CrewAI 1.9 @CrewBase crew — 5 agents, sequential process, zero langchain."""
from __future__ import annotations

from dataclasses import dataclass

from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from agents.prompts import (
    ANALYSIS_TASK_DESCRIPTION,
    ANALYST_BACKSTORY,
    CREATE_TASK_DESCRIPTION,
    CREATOR_BACKSTORY,
    PUBLISH_TASK_DESCRIPTION,
    PUBLISHER_BACKSTORY,
    RESEARCH_TASK_DESCRIPTION,
    RESEARCHER_BACKSTORY,
    STRATEGIST_BACKSTORY,
    STRATEGY_TASK_DESCRIPTION,
)
from agents.tools import (
    ANALYST_TOOLS,
    CREATOR_TOOLS,
    PUBLISHER_TOOLS,
    RESEARCHER_TOOLS,
    STRATEGIST_TOOLS,
)
from config import settings


@dataclass(slots=True)
class AnnaCrewConfig:
    org_id: str
    brand_name: str
    industry: str = "technology"
    plan: str = "free"
    run_type: str = "daily"


@CrewBase
class AnnaCrew:
    """The daily marketing crew.

    Build one per run:
        crew = AnnaCrew(AnnaCrewConfig(org_id=..., brand_name=..., industry=...))
        result = crew.crew().kickoff()
    """

    def __init__(self, config: AnnaCrewConfig) -> None:
        self.config = config
        self.llm = LLM(
            model=f"anthropic/{settings.ANTHROPIC_MODEL}",
            api_key=settings.ANTHROPIC_API_KEY,
            temperature=0.7,
            max_tokens=settings.ANTHROPIC_MAX_TOKENS,
        )

    # --- Agents --------------------------------------------------------
    @agent
    def researcher(self) -> Agent:
        return Agent(
            role="Marketing Trend Researcher",
            goal=(
                f"Surface the top 3 trending topics in {self.config.industry} "
                "this week, backed by real sources."
            ),
            backstory=RESEARCHER_BACKSTORY,
            tools=RESEARCHER_TOOLS,
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def analyst(self) -> Agent:
        return Agent(
            role="Performance Analyst",
            goal=f"Summarise how {self.config.brand_name} is performing and highlight signal.",
            backstory=ANALYST_BACKSTORY,
            tools=ANALYST_TOOLS,
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def strategist(self) -> Agent:
        return Agent(
            role="Content Strategist",
            goal=(
                f"Pick one topic for {self.config.brand_name} and produce a tight "
                "content brief that matches the brand voice."
            ),
            backstory=STRATEGIST_BACKSTORY,
            tools=STRATEGIST_TOOLS,
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def creator(self) -> Agent:
        return Agent(
            role="Senior Content Creator",
            goal=f"Write a publish-ready piece for {self.config.brand_name} in the brand voice.",
            backstory=CREATOR_BACKSTORY,
            tools=CREATOR_TOOLS,
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def publisher(self) -> Agent:
        return Agent(
            role="Publisher",
            goal="Persist finished content, respecting the org plan and approval rules.",
            backstory=PUBLISHER_BACKSTORY,
            tools=PUBLISHER_TOOLS,
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
        )

    # --- Tasks ---------------------------------------------------------
    @task
    def research_task(self) -> Task:
        return Task(
            description=RESEARCH_TASK_DESCRIPTION.format(industry=self.config.industry),
            expected_output="A numbered list of 3 trending topics with one source URL each.",
            agent=self.researcher(),
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            description=ANALYSIS_TASK_DESCRIPTION.format(brand_name=self.config.brand_name),
            expected_output="A 3-sentence performance summary with page-level specifics.",
            agent=self.analyst(),
        )

    @task
    def strategy_task(self) -> Task:
        return Task(
            description=STRATEGY_TASK_DESCRIPTION.format(brand_name=self.config.brand_name),
            expected_output="A structured markdown content brief following the exact section template.",
            agent=self.strategist(),
            context=[self.research_task(), self.analysis_task()],
        )

    @task
    def create_task(self) -> Task:
        return Task(
            description=CREATE_TASK_DESCRIPTION.format(brand_name=self.config.brand_name),
            expected_output="A finished, publish-ready piece in the correct format for its content type.",
            agent=self.creator(),
            context=[self.strategy_task()],
        )

    @task
    def publish_task(self) -> Task:
        return Task(
            description=PUBLISH_TASK_DESCRIPTION,
            expected_output="A one-line summary of what was saved and where.",
            agent=self.publisher(),
            context=[self.create_task()],
        )

    # --- Crew ----------------------------------------------------------
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.researcher(),
                self.analyst(),
                self.strategist(),
                self.creator(),
                self.publisher(),
            ],
            tasks=[
                self.research_task(),
                self.analysis_task(),
                self.strategy_task(),
                self.create_task(),
                self.publish_task(),
            ],
            process=Process.sequential,
            verbose=True,
        )
