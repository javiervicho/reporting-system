"""
Command-line interface for running the CrewAI coordination.
"""

import argparse
import os
import json
from typing import Dict, Any, Optional
import logging

from app.coordinator.crew_manager import CrewManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("crew-cli")

def setup_parser() -> argparse.ArgumentParser:
    """
    Set up the argument parser for the CLI tool.
    """
    parser = argparse.ArgumentParser(
        description="Run the CrewAI coordination for planning and execution tasks."
    )
    
    # Add arguments
    parser.add_argument(
        "--mode",
        type=str,
        choices=["plan", "execute", "full"],
        default="full",
        help="The mode to run the crew in (plan, execute, or full process)"
    )
    
    parser.add_argument(
        "--task",
        type=str,
        required=True,
        help="The task description to plan or execute"
    )
    
    parser.add_argument(
        "--context-file",
        type=str,
        help="Path to a JSON file containing context information"
    )
    
    parser.add_argument(
        "--plan-file",
        type=str,
        help="Path to a text file containing the plan (required for execute mode)"
    )
    
    parser.add_argument(
        "--output-file",
        type=str,
        help="Path to write the output to (if not specified, prints to console)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4",
        help="The model to use for the agents"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser

def load_context(context_file: Optional[str]) -> Dict[str, Any]:
    """
    Load context information from a JSON file.
    
    Args:
        context_file: Path to the context file
        
    Returns:
        Context dictionary
    """
    if not context_file:
        return {}
    
    try:
        with open(context_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading context file: {e}")
        return {}

def load_plan(plan_file: Optional[str]) -> str:
    """
    Load a plan from a text file.
    
    Args:
        plan_file: Path to the plan file
        
    Returns:
        Plan text
    """
    if not plan_file:
        return ""
    
    try:
        with open(plan_file, 'r') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading plan file: {e}")
        return ""

def save_output(output: Dict[str, Any], output_file: Optional[str]) -> None:
    """
    Save the output to a file or print to console.
    
    Args:
        output: The output data
        output_file: Path to the output file
    """
    if output_file:
        try:
            with open(output_file, 'w') as f:
                json.dump(output, f, indent=2)
            logger.info(f"Output saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving output: {e}")
            print(json.dumps(output, indent=2))
    else:
        print(json.dumps(output, indent=2))

def main():
    """
    Main entry point for the CLI tool.
    """
    parser = setup_parser()
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Initialize the crew manager
    logger.info(f"Initializing CrewManager with model: {args.model}")
    crew_manager = CrewManager(model_name=args.model)
    
    # Load context if provided
    context = load_context(args.context_file)
    
    # Run in the appropriate mode
    if args.mode == "plan":
        logger.info(f"Planning task: {args.task}")
        result = crew_manager.plan_task(args.task, context)
    elif args.mode == "execute":
        # Load the plan
        plan = load_plan(args.plan_file)
        if not plan:
            logger.error("No plan provided for execution mode. Use --plan-file to specify a plan.")
            return
        
        logger.info("Executing plan")
        result = crew_manager.execute_task(plan, context)
    else:  # Full process
        logger.info(f"Running full process for task: {args.task}")
        result = crew_manager.run_full_process(args.task, context)
    
    # Save or print the output
    save_output(result, args.output_file)

if __name__ == "__main__":
    main() 