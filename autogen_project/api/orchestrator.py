"""Task orchestrator for managing agent execution."""

import time
import uuid
from typing import Dict, Any, Optional, Type, Union
from agents import BaseAgent, DataAnalystAgent, ContentWriterAgent, CodeReviewerAgent, FileDataAnalyst, TextProcessorAgent, CalculatorAgent, FormatterAgent, AgentFactory, ModelConfig
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
            "text_processor": TextProcessorAgent,
            "calculator": CalculatorAgent,
            "formatter": FormatterAgent,
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
    
    def run_data_pipeline_workflow(
        self,
        workflow: list[Dict[str, Any]],
        initial_data: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None,
        data_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Run a multi-agent workflow with enhanced data passing between agents.
        
        Args:
            workflow: List of agent tasks with data transformation specifications.
                     Each step can include:
                     - agent: Agent name to execute
                     - task_data: Initial task data
                     - input_mapping: Map previous step outputs to current step inputs
                     - output_key: Key to store this step's output for future steps
                     - transform: Optional function name to transform data
            initial_data: Initial data to seed the workflow.
            provider: LLM provider to use.
            data_mapping: Global mapping of data keys between steps.
            
        Returns:
            Dictionary containing workflow results with data flow tracking.
        """
        job_id = str(uuid.uuid4())
        start_time = time.time()
        
        orchestrator_logger.info(f"Starting data pipeline workflow {job_id} with {len(workflow)} steps")
        
        results = []
        shared_data = initial_data.copy() if initial_data else {}
        step_outputs = {}
        
        try:
            for i, step in enumerate(workflow):
                agent_name = step.get("agent")
                base_task_data = step.get("task_data", {})
                input_mapping = step.get("input_mapping", {})
                output_key = step.get("output_key", f"step_{i+1}_output")
                transform = step.get("transform")
                
                orchestrator_logger.info(f"Data Pipeline {job_id} - Step {i+1}: {agent_name}")
                
                # Build task data with mapped inputs from previous steps
                task_data = base_task_data.copy()
                
                # Apply input mapping from previous step outputs
                for target_key, source_key in input_mapping.items():
                    if source_key in step_outputs:
                        task_data[target_key] = step_outputs[source_key]
                    elif source_key in shared_data:
                        task_data[target_key] = shared_data[source_key]
                    else:
                        orchestrator_logger.warning(f"Data key '{source_key}' not found for mapping to '{target_key}'")
                
                # Add all shared data to task context
                task_data["shared_data"] = shared_data
                task_data["previous_outputs"] = step_outputs
                task_data["workflow_step"] = i + 1
                task_data["total_steps"] = len(workflow)
                
                # Execute the agent
                step_result = self.run_agent(agent_name, task_data, provider)
                results.append(step_result)
                
                if step_result.get("success"):
                    # Extract and store the output
                    agent_output = step_result.get("response", "")
                    
                    # Apply transformation if specified
                    if transform:
                        try:
                            agent_output = self._apply_transformation(agent_output, transform)
                        except Exception as e:
                            orchestrator_logger.warning(f"Transform '{transform}' failed: {e}")
                    
                    # Store output for future steps
                    step_outputs[output_key] = agent_output
                    
                    # Update shared data with step-specific data
                    step_data = step_result.get("data", {})
                    if isinstance(step_data, dict):
                        shared_data.update(step_data)
                    
                    # Apply global data mapping if provided
                    if data_mapping:
                        for target_key, source_key in data_mapping.items():
                            if source_key in step_result:
                                shared_data[target_key] = step_result[source_key]
                    
                    orchestrator_logger.info(f"Step {i+1} completed successfully, output stored as '{output_key}'")
                else:
                    # Handle failure
                    orchestrator_logger.error(f"Data Pipeline {job_id} failed at step {i+1}")
                    error_handling = step.get("on_error", "stop")
                    
                    if error_handling == "continue":
                        orchestrator_logger.info(f"Continuing pipeline despite step {i+1} failure")
                        step_outputs[output_key] = None
                        continue
                    else:
                        break
            
            workflow_success = all(result.get("success", False) for result in results)
            execution_time = time.time() - start_time
            
            # Create comprehensive result with data flow information
            workflow_result = {
                "success": workflow_success,
                "job_id": job_id,
                "execution_time": execution_time,
                "workflow_steps": len(workflow),
                "completed_steps": len(results),
                "results": results,
                "final_data": shared_data,
                "step_outputs": step_outputs,
                "data_flow": self._build_data_flow_summary(workflow, step_outputs),
                "orchestrator": "TaskOrchestrator"
            }
            
            orchestrator_logger.log_orchestrator_end(job_id, workflow_success, execution_time)
            
            return workflow_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            orchestrator_logger.error(f"Data pipeline workflow {job_id} failed", {"error": str(e)})
            
            return {
                "success": False,
                "error": str(e),
                "job_id": job_id,
                "execution_time": execution_time,
                "workflow_steps": len(workflow),
                "completed_steps": len(results),
                "results": results,
                "final_data": shared_data,
                "step_outputs": step_outputs,
                "orchestrator": "TaskOrchestrator"
            }
    
    def _apply_transformation(self, data: Any, transform: str) -> Any:
        """Apply a transformation to data.
        
        Args:
            data: Data to transform.
            transform: Transformation type.
            
        Returns:
            Transformed data.
        """
        transformations = {
            "uppercase": lambda x: str(x).upper(),
            "lowercase": lambda x: str(x).lower(),
            "strip": lambda x: str(x).strip(),
            "json_parse": lambda x: eval(x) if isinstance(x, str) else x,
            "to_list": lambda x: [x] if not isinstance(x, list) else x,
            "to_string": lambda x: str(x),
            "extract_numbers": lambda x: ''.join(filter(str.isdigit, str(x)))
        }
        
        if transform in transformations:
            return transformations[transform](data)
        else:
            orchestrator_logger.warning(f"Unknown transformation: {transform}")
            return data
    
    def _build_data_flow_summary(self, workflow: list[Dict[str, Any]], step_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Build a summary of data flow through the workflow.
        
        Args:
            workflow: The workflow configuration.
            step_outputs: Outputs from each step.
            
        Returns:
            Data flow summary.
        """
        flow_summary = {
            "steps": [],
            "data_keys": list(step_outputs.keys()),
            "transformations": []
        }
        
        for i, step in enumerate(workflow):
            step_summary = {
                "step": i + 1,
                "agent": step.get("agent"),
                "input_mapping": step.get("input_mapping", {}),
                "output_key": step.get("output_key", f"step_{i+1}_output"),
                "transform": step.get("transform"),
                "has_output": step.get("output_key", f"step_{i+1}_output") in step_outputs
            }
            flow_summary["steps"].append(step_summary)
            
            if step.get("transform"):
                flow_summary["transformations"].append({
                    "step": i + 1,
                    "transform": step.get("transform")
                })
        
        return flow_summary
