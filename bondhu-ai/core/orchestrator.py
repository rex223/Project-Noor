"""
LangGraph Orchestrator for managing multi-agent personality analysis workflows.
Coordinates all agents and manages complex state transitions and error recovery.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, TypedDict, Literal
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from agents import (
    MusicIntelligenceAgent,
    VideoIntelligenceAgent, 
    GamingIntelligenceAgent,
    PersonalityAnalysisAgent
)
from core.config import get_config
from api.models.schemas import (
    DataSource,
    AnalysisRequest,
    AnalysisResponse,
    AnalysisStatus,
    AgentAnalysisResult,
    PersonalityProfile
)

class WorkflowState(TypedDict):
    """State object for the personality analysis workflow."""
    # Input
    user_id: str
    analysis_request: AnalysisRequest
    
    # Agent data
    music_data: Optional[Dict[str, Any]]
    video_data: Optional[Dict[str, Any]]
    gaming_data: Optional[Dict[str, Any]]
    survey_data: Optional[Dict[str, Any]]
    conversation_data: Optional[List[Dict[str, Any]]]
    
    # Agent results
    music_result: Optional[AgentAnalysisResult]
    video_result: Optional[AgentAnalysisResult]
    gaming_result: Optional[AgentAnalysisResult]
    
    # Final results
    personality_profile: Optional[PersonalityProfile]
    analysis_response: Optional[AnalysisResponse]
    
    # Workflow metadata
    current_step: str
    errors: List[str]
    warnings: List[str]
    start_time: float
    processing_time: float
    
    # Agent instances
    agents: Dict[str, Any]

class PersonalityOrchestrator:
    """
    LangGraph-based orchestrator for multi-agent personality analysis.
    Manages the complete workflow from data collection to final personality profile generation.
    """
    
    def __init__(self):
        """Initialize the orchestrator with workflow configuration."""
        self.config = get_config()
        self.logger = logging.getLogger("bondhu.orchestrator")
        
        # Create workflow graph
        self.workflow = self._create_workflow()
        
        # Initialize memory for checkpointing
        self.memory = MemorySaver()
        
        # Compile the graph with memory
        self.app = self.workflow.compile(checkpointer=self.memory)
        
        self.logger.info("Personality Orchestrator initialized")
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for personality analysis."""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes for each step
        workflow.add_node("initialize", self._initialize_workflow)
        workflow.add_node("collect_music_data", self._collect_music_data)
        workflow.add_node("collect_video_data", self._collect_video_data)
        workflow.add_node("collect_gaming_data", self._collect_gaming_data)
        workflow.add_node("analyze_music", self._analyze_music)
        workflow.add_node("analyze_video", self._analyze_video)
        workflow.add_node("analyze_gaming", self._analyze_gaming)
        workflow.add_node("synthesize_personality", self._synthesize_personality)
        workflow.add_node("finalize_response", self._finalize_response)
        workflow.add_node("handle_error", self._handle_error)
        
        # Set entry point
        workflow.set_entry_point("initialize")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "initialize",
            self._route_after_initialization,
            {
                "collect_data": "collect_music_data",
                "error": "handle_error"
            }
        )
        
        # Data collection flow
        workflow.add_edge("collect_music_data", "collect_video_data")
        workflow.add_edge("collect_video_data", "collect_gaming_data")
        
        # Analysis flow
        workflow.add_conditional_edges(
            "collect_gaming_data",
            self._route_to_analysis,
            {
                "analyze": "analyze_music",
                "error": "handle_error"
            }
        )
        
        # Parallel analysis (simulated with sequential calls)
        workflow.add_edge("analyze_music", "analyze_video")
        workflow.add_edge("analyze_video", "analyze_gaming")
        
        # Synthesis
        workflow.add_conditional_edges(
            "analyze_gaming",
            self._route_to_synthesis,
            {
                "synthesize": "synthesize_personality",
                "error": "handle_error"
            }
        )
        
        # Finalization
        workflow.add_edge("synthesize_personality", "finalize_response")
        workflow.add_edge("finalize_response", END)
        workflow.add_edge("handle_error", END)
        
        return workflow
    
    async def analyze_personality(self, request: AnalysisRequest, **kwargs) -> AnalysisResponse:
        """
        Run the complete personality analysis workflow.
        
        Args:
            request: Analysis request with user ID and parameters
            **kwargs: Additional data (survey responses, conversation history, etc.)
            
        Returns:
            Complete analysis response with personality profile
        """
        start_time = asyncio.get_event_loop().time()
        
        # Create initial state
        initial_state = WorkflowState(
            user_id=request.user_id,
            analysis_request=request,
            music_data=None,
            video_data=None,
            gaming_data=None,
            survey_data=kwargs.get("survey_data"),
            conversation_data=kwargs.get("conversation_data"),
            music_result=None,
            video_result=None,
            gaming_result=None,
            personality_profile=None,
            analysis_response=None,
            current_step="initialize",
            errors=[],
            warnings=[],
            start_time=start_time,
            processing_time=0.0,
            agents={}
        )
        
        try:
            # Run the workflow
            config = {"configurable": {"thread_id": f"user_{request.user_id}_{int(start_time)}"}}
            final_state = await self.app.ainvoke(initial_state, config=config)
            
            # Return the analysis response
            if final_state.get("analysis_response"):
                return final_state["analysis_response"]
            else:
                # Create error response
                return AnalysisResponse(
                    user_id=request.user_id,
                    status=AnalysisStatus.FAILED,
                    error_message="Workflow completed but no response generated",
                    processing_time=asyncio.get_event_loop().time() - start_time
                )
                
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            return AnalysisResponse(
                user_id=request.user_id,
                status=AnalysisStatus.FAILED,
                error_message=str(e),
                processing_time=asyncio.get_event_loop().time() - start_time
            )
    
    async def _initialize_workflow(self, state: WorkflowState) -> WorkflowState:
        """Initialize the workflow and create agent instances."""
        self.logger.info(f"Initializing personality analysis for user {state['user_id']}")
        
        try:
            # Create agent instances
            agents = {}
            
            # Only create agents that are requested
            requested_agents = state["analysis_request"].requested_agents
            
            if DataSource.MUSIC in requested_agents:
                agents["music"] = MusicIntelligenceAgent(user_id=state["user_id"])
            
            if DataSource.VIDEO in requested_agents:
                agents["video"] = VideoIntelligenceAgent(user_id=state["user_id"])
            
            if DataSource.GAMING in requested_agents:
                agents["gaming"] = GamingIntelligenceAgent(user_id=state["user_id"])
            
            # Always create personality agent for synthesis
            agents["personality"] = PersonalityAnalysisAgent(user_id=state["user_id"])
            
            state["agents"] = agents
            state["current_step"] = "data_collection"
            
            self.logger.info(f"Initialized {len(agents)} agents")
            
        except Exception as e:
            self.logger.error(f"Error initializing workflow: {e}")
            state["errors"].append(f"Initialization failed: {str(e)}")
        
        return state
    
    async def _collect_music_data(self, state: WorkflowState) -> WorkflowState:
        """Collect music data if music agent is available."""
        if "music" not in state["agents"]:
            self.logger.info("Skipping music data collection - agent not requested")
            return state
        
        try:
            music_agent = state["agents"]["music"]
            
            # Collect music data with error handling
            state["music_data"] = await music_agent.collect_data(
                force_refresh=state["analysis_request"].force_refresh
            )
            
            if not state["music_data"]:
                state["warnings"].append("No music data collected")
            else:
                self.logger.info("Music data collected successfully")
                
        except Exception as e:
            error_msg = f"Music data collection failed: {str(e)}"
            self.logger.error(error_msg)
            state["errors"].append(error_msg)
            state["music_data"] = {}
        
        return state
    
    async def _collect_video_data(self, state: WorkflowState) -> WorkflowState:
        """Collect video data if video agent is available."""
        if "video" not in state["agents"]:
            self.logger.info("Skipping video data collection - agent not requested")
            return state
        
        try:
            video_agent = state["agents"]["video"]
            
            # Collect video data with error handling
            state["video_data"] = await video_agent.collect_data(
                force_refresh=state["analysis_request"].force_refresh
            )
            
            if not state["video_data"]:
                state["warnings"].append("No video data collected")
            else:
                self.logger.info("Video data collected successfully")
                
        except Exception as e:
            error_msg = f"Video data collection failed: {str(e)}"
            self.logger.error(error_msg)
            state["errors"].append(error_msg)
            state["video_data"] = {}
        
        return state
    
    async def _collect_gaming_data(self, state: WorkflowState) -> WorkflowState:
        """Collect gaming data if gaming agent is available."""
        if "gaming" not in state["agents"]:
            self.logger.info("Skipping gaming data collection - agent not requested")
            return state
        
        try:
            gaming_agent = state["agents"]["gaming"]
            
            # Collect gaming data with error handling
            state["gaming_data"] = await gaming_agent.collect_data(
                force_refresh=state["analysis_request"].force_refresh
            )
            
            if not state["gaming_data"]:
                state["warnings"].append("No gaming data collected")
            else:
                self.logger.info("Gaming data collected successfully")
                
        except Exception as e:
            error_msg = f"Gaming data collection failed: {str(e)}"
            self.logger.error(error_msg)
            state["errors"].append(error_msg)
            state["gaming_data"] = {}
        
        state["current_step"] = "analysis"
        return state
    
    async def _analyze_music(self, state: WorkflowState) -> WorkflowState:
        """Analyze music data for personality insights."""
        if "music" not in state["agents"] or not state["music_data"]:
            self.logger.info("Skipping music analysis - no data or agent available")
            return state
        
        try:
            music_agent = state["agents"]["music"]
            
            # Run music analysis
            state["music_result"] = await music_agent.run_analysis(
                force_refresh=state["analysis_request"].force_refresh
            )
            
            self.logger.info("Music analysis completed")
            
        except Exception as e:
            error_msg = f"Music analysis failed: {str(e)}"
            self.logger.error(error_msg)
            state["errors"].append(error_msg)
        
        return state
    
    async def _analyze_video(self, state: WorkflowState) -> WorkflowState:
        """Analyze video data for personality insights."""
        if "video" not in state["agents"] or not state["video_data"]:
            self.logger.info("Skipping video analysis - no data or agent available")
            return state
        
        try:
            video_agent = state["agents"]["video"]
            
            # Run video analysis
            state["video_result"] = await video_agent.run_analysis(
                force_refresh=state["analysis_request"].force_refresh
            )
            
            self.logger.info("Video analysis completed")
            
        except Exception as e:
            error_msg = f"Video analysis failed: {str(e)}"
            self.logger.error(error_msg)
            state["errors"].append(error_msg)
        
        return state
    
    async def _analyze_gaming(self, state: WorkflowState) -> WorkflowState:
        """Analyze gaming data for personality insights."""
        if "gaming" not in state["agents"] or not state["gaming_data"]:
            self.logger.info("Skipping gaming analysis - no data or agent available")
            return state
        
        try:
            gaming_agent = state["agents"]["gaming"]
            
            # Run gaming analysis
            state["gaming_result"] = await gaming_agent.run_analysis(
                force_refresh=state["analysis_request"].force_refresh
            )
            
            self.logger.info("Gaming analysis completed")
            
        except Exception as e:
            error_msg = f"Gaming analysis failed: {str(e)}"
            self.logger.error(error_msg)
            state["errors"].append(error_msg)
        
        state["current_step"] = "synthesis"
        return state
    
    async def _synthesize_personality(self, state: WorkflowState) -> WorkflowState:
        """Synthesize personality profile from all agent results."""
        try:
            personality_agent = state["agents"]["personality"]
            
            # Collect all agent results
            agent_results = []
            if state["music_result"]:
                agent_results.append(state["music_result"])
            if state["video_result"]:
                agent_results.append(state["video_result"])
            if state["gaming_result"]:
                agent_results.append(state["gaming_result"])
            
            # Prepare data for personality synthesis
            synthesis_data = {
                "agent_results": agent_results,
                "survey_responses": state["survey_data"] or {},
                "conversation_history": state["conversation_data"] or []
            }
            
            # Create personality profile
            state["personality_profile"] = await personality_agent.create_personality_profile(synthesis_data)
            
            self.logger.info("Personality synthesis completed")
            
        except Exception as e:
            error_msg = f"Personality synthesis failed: {str(e)}"
            self.logger.error(error_msg)
            state["errors"].append(error_msg)
        
        state["current_step"] = "finalization"
        return state
    
    async def _finalize_response(self, state: WorkflowState) -> WorkflowState:
        """Finalize the analysis response."""
        try:
            # Calculate processing time
            current_time = asyncio.get_event_loop().time()
            processing_time = current_time - state["start_time"]
            
            # Collect all agent results
            agent_results = []
            if state["music_result"]:
                agent_results.append(state["music_result"])
            if state["video_result"]:
                agent_results.append(state["video_result"])
            if state["gaming_result"]:
                agent_results.append(state["gaming_result"])
            
            # Determine overall status
            if state["errors"]:
                if state["personality_profile"]:
                    status = AnalysisStatus.PARTIAL
                else:
                    status = AnalysisStatus.FAILED
            else:
                status = AnalysisStatus.COMPLETED
            
            # Create final response
            state["analysis_response"] = AnalysisResponse(
                user_id=state["user_id"],
                status=status,
                personality_profile=state["personality_profile"],
                agent_results=agent_results,
                processing_time=processing_time,
                error_message="; ".join(state["errors"]) if state["errors"] else None,
                warnings=state["warnings"]
            )
            
            self.logger.info(f"Analysis completed in {processing_time:.2f}s with status: {status.value}")
            
        except Exception as e:
            error_msg = f"Response finalization failed: {str(e)}"
            self.logger.error(error_msg)
            state["errors"].append(error_msg)
            
            # Create error response
            state["analysis_response"] = AnalysisResponse(
                user_id=state["user_id"],
                status=AnalysisStatus.FAILED,
                error_message=error_msg,
                processing_time=asyncio.get_event_loop().time() - state["start_time"]
            )
        
        return state
    
    async def _handle_error(self, state: WorkflowState) -> WorkflowState:
        """Handle workflow errors and create error response."""
        self.logger.error(f"Workflow error handler triggered. Errors: {state['errors']}")
        
        # Create error response
        state["analysis_response"] = AnalysisResponse(
            user_id=state["user_id"],
            status=AnalysisStatus.FAILED,
            error_message="; ".join(state["errors"]) if state["errors"] else "Unknown error occurred",
            processing_time=asyncio.get_event_loop().time() - state["start_time"],
            warnings=state["warnings"]
        )
        
        return state
    
    def _route_after_initialization(self, state: WorkflowState) -> Literal["collect_data", "error"]:
        """Route after initialization based on success/failure."""
        if state["errors"]:
            return "error"
        return "collect_data"
    
    def _route_to_analysis(self, state: WorkflowState) -> Literal["analyze", "error"]:
        """Route to analysis phase or error handling."""
        # Check if we have at least some data to analyze
        has_data = bool(state["music_data"] or state["video_data"] or state["gaming_data"] or state["survey_data"])
        
        if not has_data and not state["errors"]:
            state["errors"].append("No data collected from any source")
        
        if state["errors"] and not has_data:
            return "error"
        return "analyze"
    
    def _route_to_synthesis(self, state: WorkflowState) -> Literal["synthesize", "error"]:
        """Route to synthesis phase or error handling."""
        # Check if we have at least one successful analysis result
        has_results = bool(state["music_result"] or state["video_result"] or state["gaming_result"] or state["survey_data"])
        
        if not has_results and not state["errors"]:
            state["errors"].append("No analysis results available for synthesis")
        
        if state["errors"] and not has_results:
            return "error"
        return "synthesize"
    
    async def get_workflow_status(self, user_id: str, thread_id: str) -> Dict[str, Any]:
        """Get the current status of a running workflow."""
        try:
            # Get state from memory
            config = {"configurable": {"thread_id": thread_id}}
            current_state = await self.app.aget_state(config)
            
            if current_state and current_state.values:
                state = current_state.values
                return {
                    "user_id": user_id,
                    "current_step": state.get("current_step", "unknown"),
                    "status": "in_progress" if state.get("current_step") != "completed" else "completed",
                    "errors": state.get("errors", []),
                    "warnings": state.get("warnings", []),
                    "processing_time": asyncio.get_event_loop().time() - state.get("start_time", 0)
                }
            else:
                return {"user_id": user_id, "status": "not_found"}
                
        except Exception as e:
            self.logger.error(f"Error getting workflow status: {e}")
            return {"user_id": user_id, "status": "error", "error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the orchestrator."""
        try:
            # Test workflow compilation
            test_state = WorkflowState(
                user_id="health_check",
                analysis_request=AnalysisRequest(user_id="health_check"),
                music_data=None,
                video_data=None,
                gaming_data=None,
                survey_data=None,
                conversation_data=None,
                music_result=None,
                video_result=None,
                gaming_result=None,
                personality_profile=None,
                analysis_response=None,
                current_step="test",
                errors=[],
                warnings=[],
                start_time=0.0,
                processing_time=0.0,
                agents={}
            )
            
            # Simple validation that workflow is accessible
            nodes = list(self.workflow.nodes.keys())
            
            return {
                "status": "healthy",
                "workflow_nodes": len(nodes),
                "memory_enabled": self.memory is not None,
                "app_compiled": self.app is not None,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }