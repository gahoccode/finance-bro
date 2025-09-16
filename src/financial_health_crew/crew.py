from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from .tools.financial_analysis_tool import FinancialAnalysisTool


@CrewBase
class FinancialHealthCrew:
    """Financial Health Analysis Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def financial_data_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["financial_data_analyst"],
            tools=[FinancialAnalysisTool()],
            verbose=True,
        )

    @agent
    def risk_assessment_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["risk_assessment_specialist"],
            tools=[FinancialAnalysisTool()],
            verbose=True,
        )

    @agent
    def report_writer(self) -> Agent:
        return Agent(config=self.agents_config["report_writer"], verbose=True)

    @task
    def analyze_financial_data(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_financial_data"],
            agent=self.financial_data_analyst(),
        )

    @task
    def assess_financial_risks(self) -> Task:
        return Task(
            config=self.tasks_config["assess_financial_risks"],
            agent=self.risk_assessment_specialist(),
            context=[self.analyze_financial_data()],
        )

    @task
    def generate_health_report(self) -> Task:
        return Task(
            config=self.tasks_config["generate_health_report"],
            agent=self.report_writer(),
            context=[self.analyze_financial_data(), self.assess_financial_risks()],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Financial Health Analysis crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
