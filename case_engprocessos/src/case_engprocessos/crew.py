import os
from dotenv import load_dotenv

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from tools import GeradorJSONBacklogTool

_ = load_dotenv()
import agentops
agentops.init()

gerador_json_backlog_tool = GeradorJSONBacklogTool()

# =========================================================
# ENVIRONMENT CONFIGURATION
# =========================================================


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("MODEL", "gemini/gemini-2.5-flash")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY não encontrada. Verifique se a chave está configurada no arquivo .env."
    )

# =========================================================
# GEMINI LLM CONFIGURATION
# =========================================================
gemini_llm = LLM(
    model=GEMINI_MODEL,
    api_key=GEMINI_API_KEY,
    temperature=0.2,
    max_tokens=1200
)

print(f"Modelo em uso: {GEMINI_MODEL}")


@CrewBase
class CaseEngprocessos:
    """
    Crew multiagente para IA Generativa aplicada à Engenharia de Processos Bancários.
    """

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def intake_analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["intake_analyst_agent"],  # type: ignore[index]
            llm=gemini_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def process_diagnosis_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["process_diagnosis_agent"],  # type: ignore[index]
            llm=gemini_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def prioritization_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["prioritization_agent"],  # type: ignore[index]
            llm=gemini_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def solution_strategy_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["solution_strategy_agent"],  # type: ignore[index]
            llm=gemini_llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def governance_reporting_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["governance_reporting_agent"],  # type: ignore[index]
            llm=gemini_llm,
            tools=[gerador_json_backlog_tool],
            verbose=True,
            allow_delegation=False
        )

    @task
    def intake_structuring_task(self) -> Task:
        return Task(
            config=self.tasks_config["intake_structuring_task"],  # type: ignore[index]
        )

    @task
    def process_diagnosis_task(self) -> Task:
        return Task(
            config=self.tasks_config["process_diagnosis_task"],  # type: ignore[index]
        )

    @task
    def prioritization_task(self) -> Task:
        return Task(
            config=self.tasks_config["prioritization_task"],  # type: ignore[index]
        )

    @task
    def solution_strategy_task(self) -> Task:
        return Task(
            config=self.tasks_config["solution_strategy_task"],  # type: ignore[index]
        )

    @task
    def governance_reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config["governance_reporting_task"],  # type: ignore[index]
            output_file="solicitacao_final.md"
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            cache=True
        )