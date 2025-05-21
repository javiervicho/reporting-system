"""
Crew Manager for coordinating Planner and Executor roles using CrewAI.
"""

from typing import Dict, List, Optional, Any, Union
import os
from crewai import Agent, Task, Crew, Process
from langchain.llms import OpenAI

from app.coordinator.roles import planner_role_description, executor_role_description
from app.coordinator.tasks import generate_planning_task, generate_execution_task

class CrewManager:
    """
    Manager class to coordinate Planner and Executor agents using CrewAI.
    """
    
    def __init__(self, model_name: str = "gpt-4"):
        """
        Initialize the CrewManager with specified model.
        
        Args:
            model_name: The name of the model to use for agents
        """
        # Set up the language model
        self.llm = OpenAI(temperature=0.2, model_name=model_name)
        
        # Create agents
        self.planner_agent = self._create_planner_agent()
        self.executor_agent = self._create_executor_agent()
        
        # Initialize storage for task results
        self.results = {}
    
    def _create_planner_agent(self) -> Agent:
        """
        Create the Planner agent with appropriate role description.
        """
        return Agent(
            role="Planner",
            goal="Create comprehensive plans for software development projects, breaking down complex tasks into manageable steps",
            backstory=planner_role_description,
            verbose=True,
            llm=self.llm
        )
    
    def _create_executor_agent(self) -> Agent:
        """
        Create the Executor agent with appropriate role description.
        """
        return Agent(
            role="Executor",
            goal="Implement code and execute plans created by the Planner with precision and efficiency",
            backstory=executor_role_description,
            verbose=True,
            llm=self.llm
        )
    
    def plan_task(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Have the Planner agent create a plan for the given task.
        
        Args:
            task_description: Description of the task to plan
            context: Additional context information
            
        Returns:
            The planning results
        """
        # Create the planning task
        planning_task = generate_planning_task(
            description=task_description,
            context=context or {}
        )
        
        # Create a crew with just the planner
        planning_crew = Crew(
            agents=[self.planner_agent],
            tasks=[planning_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Execute the planning process
        result = planning_crew.kickoff()
        
        # Store the planning result
        self.results["plan"] = result
        
        return {"plan": result}
    
    def execute_task(self, plan: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Have the Executor agent execute the plan created by the Planner.
        
        Args:
            plan: The plan to execute
            context: Additional context information
            
        Returns:
            The execution results
        """
        # Create the execution task
        execution_task = generate_execution_task(
            plan=plan,
            context=context or {}
        )
        
        # Create a crew with just the executor
        execution_crew = Crew(
            agents=[self.executor_agent],
            tasks=[execution_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Execute the execution process
        result = execution_crew.kickoff()
        
        # Store the execution result
        self.results["execution"] = result
        
        return {"execution": result}
    
    def run_full_process(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run the full planning and execution process.
        
        Args:
            task_description: Description of the task to plan and execute
            context: Additional context information
            
        Returns:
            Combined results from planning and execution
        """
        # First, plan the task
        planning_result = self.plan_task(task_description, context)
        
        # Extract the plan from the result
        plan = planning_result["plan"]
        
        # Then, execute the plan
        execution_result = self.execute_task(plan, context)
        
        # Combine and return results
        return {
            "plan": planning_result["plan"],
            "execution": execution_result["execution"]
        } 