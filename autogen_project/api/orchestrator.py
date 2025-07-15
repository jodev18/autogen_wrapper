"""Task orchestrator for managing agent execution."""

import time
import uuid
from typing import Dict, Any, Optional, Type, Union
from agents import BaseAgent, DataAnalystAgent, ContentWriterAgent, CodeReviewerAgent, FileDataAnalyst, AgentFactory, ModelConfig
from core import orchestrator_logger


class TaskOrchestrator:
    """Orchestrates task execution across different agents."""
    
    def __init__(self) -> None:
        """Initialize the task orchestrator."""
        self.agents: Dict[str, Type[BaseAgent]] = {
            "data_analyst": DataAnalystAgent,
            "content_writer": ContentWriterAgent,
            "code_reviewer": CodeReviewerAgent,
            "file_data_analyst": FileDataAnalyst,
        }
        orchestrator_logger.info("TaskOrchestrator initialized")
    
    def register_agent(self, name: str, agent_class: Type[BaseAgent]) -> None:
        """Register a new agent type.
        
        Args:
            name: Agent identifier.
            agent_class: Agent class to register.
        """
        self.agents[name] = agent_class
        orchestrator_logger.info(f"Registered agent '{name}'")
    
    def create_agent_instance(
        self,
        agent_name: str,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        model_config: Optional[Union[ModelConfig, Dict[str, Any]]] = None,
        agent_config: Optional[Dict[str, Any]] = None
    ) -> BaseAgent:
        """Create an agent instance with custom configuration.
        
        Args:
            agent_name: Name of the agent type to create.
            provider: LLM provider.
            model_name: Specific model to use.
            model_config: Model configuration.
            agent_config: Additional agent configuration.
            
        Returns:
            Configured agent instance.
        """
        if agent_name not in self.agents:
            raise ValueError(f"Unknown agent: {agent_name}. Available: {list(self.agents.keys())}")
        
        # Use AgentFactory for enhanced creation if possible
        try:
            return AgentFactory.create_agent(
                agent_type=agent_name,
                provider=provider,
                model_name=model_name,
                model_config=model_config,
                agent_config=agent_config
            )
        except ValueError:
            # Fallback to direct instantiation for custom registered agents
            agent_class = self.agents[agent_name]
            return agent_class(provider=provider)
    
    def list_agents(self) -> Dict[str, str]:
        """List all available agents.
        
        Returns:
            Dictionary mapping agent names to class names.
        """
        return {name: cls.__name__ for name, cls in self.agents.items()}
    
    def run_agent(
        self, 
        agent_name: str, 
        task_data: Dict[str, Any],
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        model_config: Optional[Union[ModelConfig, Dict[str, Any]]] = None,
        agent_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run a specific agent with provided task data.
        
        Args:
            agent_name: Name of the agent to run.
            task_data: Data for the agent task.
            provider: LLM provider to use.
            model_name: Specific model to use.
            model_config: Model configuration.
            agent_config: Additional agent configuration.
            
        Returns:
            Dictionary containing execution results.
        """
        job_id = str(uuid.uuid4())
        start_time = time.time()
        
        orchestrator_logger.log_orchestrator_start(job_id, agent_name)
        
        try:
            # Create agent instance with custom configuration
            agent = self.create_agent_instance(
                agent_name=agent_name,
                provider=provider,
                model_name=model_name,
                model_config=model_config,
                agent_config=agent_config
            )
            result = agent.execute(task_data)
            
            # Add orchestrator metadata
            result.update({
                "job_id": job_id,
                "execution_time": time.time() - start_time,
                "orchestrator": "TaskOrchestrator"
            })
            
            orchestrator_logger.log_orchestrator_end(
                job_id, 
                result.get("success", False), 
                result["execution_time"]
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            orchestrator_logger.error(f"Orchestrator job {job_id} failed", {"error": str(e)})
            orchestrator_logger.log_orchestrator_end(job_id, False, execution_time)
            
            return {
                "success": False,
                "error": str(e),
                "job_id": job_id,
                "execution_time": execution_time,
                "orchestrator": "TaskOrchestrator"
            }
    
    def run_multi_agent_workflow(
        self, 
        workflow: list[Dict[str, Any]],
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run a multi-agent workflow.
        
        Args:
            workflow: List of agent tasks to execute in sequence.
            provider: LLM provider to use.
            
        Returns:
            Dictionary containing workflow results.
        """
        job_id = str(uuid.uuid4())
        start_time = time.time()
        
        orchestrator_logger.info(f"Starting multi-agent workflow {job_id} with {len(workflow)} steps")
        
        results = []
        context = {}
        
        try:
            for i, step in enumerate(workflow):
                agent_name = step.get("agent")
                task_data = step.get("task_data", {})
                
                # Add context from previous steps
                task_data["workflow_context"] = context
                
                orchestrator_logger.info(f"Workflow {job_id} - Step {i+1}: {agent_name}")
                
                step_result = self.run_agent(agent_name, task_data, provider)
                results.append(step_result)
                
                # Update context with result
                if step_result.get("success"):
                    context[f"step_{i+1}_{agent_name}"] = step_result.get("response", "")
                else:
                    # Stop workflow on failure
                    orchestrator_logger.error(f"Workflow {job_id} failed at step {i+1}")
                    break
            
            workflow_success = all(result.get("success", False) for result in results)
            execution_time = time.time() - start_time
            
            workflow_result = {
                "success": workflow_success,
                "job_id": job_id,
                "execution_time": execution_time,
                "workflow_steps": len(workflow),
                "completed_steps": len(results),
                "results": results,
                "orchestrator": "TaskOrchestrator"
            }
            
            orchestrator_logger.log_orchestrator_end(job_id, workflow_success, execution_time)
            
            return workflow_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            orchestrator_logger.error(f"Multi-agent workflow {job_id} failed", {"error": str(e)})
            
            return {
                "success": False,
                "error": str(e),
                "job_id": job_id,
                "execution_time": execution_time,
                "workflow_steps": len(workflow),
                "completed_steps": len(results),
                "results": results,
                "orchestrator": "TaskOrchestrator"
            }
