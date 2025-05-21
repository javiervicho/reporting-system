"""
Task generation functions for planning and execution.
"""

from typing import Dict, Any
from crewai import Task

def generate_planning_task(description: str, context: Dict[str, Any]) -> Task:
    """
    Generate a planning task for the Planner agent.
    
    Args:
        description: The description of what needs to be planned
        context: Additional context information
        
    Returns:
        A CrewAI Task object for planning
    """
    # Format context information
    context_str = "\n".join([f"{key}: {value}" for key, value in context.items()])
    
    # Build the task description with appropriate instructions
    task_description = f"""
    # Planning Task: {description}
    
    ## Context Information:
    {context_str if context else "No additional context provided."}
    
    ## Instructions:
    1. Analyze the request thoroughly and understand the requirements
    2. Break down the task into clear, manageable steps
    3. For each step, define:
       - What needs to be done
       - How it should be implemented
       - Success criteria to verify completion
    4. Consider potential challenges and include mitigation strategies
    5. Format your plan as a structured document with:
       - Background and motivation
       - Key challenges and analysis
       - High-level task breakdown with steps
       - Success criteria for each task
    
    ## Output Format:
    Your response should be a comprehensive plan document ready for implementation by the Executor agent.
    """
    
    # Create the Task object
    return Task(
        description=task_description,
        expected_output="A comprehensive implementation plan with clear steps, technical details, and success criteria."
    )

def generate_execution_task(plan: str, context: Dict[str, Any]) -> Task:
    """
    Generate an execution task for the Executor agent.
    
    Args:
        plan: The plan created by the Planner
        context: Additional context information
        
    Returns:
        A CrewAI Task object for execution
    """
    # Format context information
    context_str = "\n".join([f"{key}: {value}" for key, value in context.items()])
    
    # Build the task description with appropriate instructions
    task_description = f"""
    # Execution Task: Implement the following plan
    
    ## Plan Details:
    {plan}
    
    ## Additional Context:
    {context_str if context else "No additional context provided."}
    
    ## Instructions:
    1. Follow the plan step by step
    2. For each step:
       - Implement the required code or configuration
       - Test against the success criteria
       - Document any issues or challenges
    3. If a step is unclear or problematic:
       - Note the issue
       - Propose a solution or ask for clarification
    4. Track your progress through the plan
    5. Provide a summary of what was completed and any remaining items
    
    ## Output Format:
    Your response should include:
    - A summary of what was implemented
    - Code snippets or configuration changes made
    - Test results for each step
    - Any issues encountered and how they were resolved
    - Recommendations for improvements
    """
    
    # Create the Task object
    return Task(
        description=task_description,
        expected_output="A detailed execution report including implementation details, test results, challenges, and recommendations."
    ) 