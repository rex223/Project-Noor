"""
Base agent class for Bondhu AI multi-agent system.
All specialized agents inherit from this base class.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Type
from datetime import datetime, timedelta

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool

from ..core.config import get_config
from ..core.database.personality_service import get_personality_service
from ..core.database.models import PersonalityProfile, PersonalityContextResponse
from ..api.models.schemas import (
    DataSource, 
    AgentAnalysisResult, 
    AnalysisStatus, 
    PersonalityTrait,
    AgentMemory,
    MemoryItem
)

class BaseAgent(ABC):
    """
    Base class for all Bondhu AI agents.
    Provides common functionality for LangChain integration, memory management,
    error handling, and logging.
    """
    
    def __init__(
        self,
        agent_type: DataSource,
        user_id: str,
        tools: Optional[List[BaseTool]] = None,
        memory_size: int = 10,
        **kwargs
    ):
        """
        Initialize the base agent.
        
        Args:
            agent_type: Type of agent (music, video, gaming, etc.)
            user_id: User ID for this agent session
            tools: List of LangChain tools for this agent
            memory_size: Size of conversation memory window
            **kwargs: Additional arguments
        """
        self.config = get_config()
        self.agent_type = agent_type
        self.user_id = user_id
        self.memory_size = memory_size
        
        # Setup personality service
        self.personality_service = get_personality_service()
        self._personality_context: Optional[PersonalityContextResponse] = None
        self._personality_guidelines: Optional[Dict[str, Any]] = None
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Initialize LLM
        self.llm = self._initialize_llm()
        
        # Initialize memory
        self.memory = ConversationBufferWindowMemory(
            k=memory_size,
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize custom memory management
        self.agent_memory = AgentMemory(
            user_id=user_id,
            agent_type=agent_type
        )
        
        # Initialize tools
        self.tools = tools or []
        
        # Create agent executor
        self.agent_executor = self._create_agent_executor()
        
        # Performance tracking
        self.start_time: Optional[float] = None
        self.processing_times: List[float] = []
        
        self.logger.info(f"Initialized {agent_type.value} agent for user {user_id}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logger for this agent."""
        logger = logging.getLogger(f"bondhu.agents.{self.agent_type.value}")
        logger.setLevel(getattr(logging, self.config.logging.level))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(self.config.logging.format)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_llm(self) -> ChatGoogleGenerativeAI:
        """Initialize the language model."""
        return ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.7,
            google_api_key=self.config.gemini.api_key
        )
    
    def _create_agent_executor(self) -> AgentExecutor:
        """Create the LangChain agent executor."""
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent
        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create executor
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_execution_time=self.config.agents.timeout
        )
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Get the system prompt for this agent. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def collect_data(self, **kwargs) -> Dict[str, Any]:
        """Collect data from external sources. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def analyze_personality(self, data: Dict[str, Any]) -> Dict[PersonalityTrait, float]:
        """Analyze personality from collected data. Must be implemented by subclasses."""
        pass
    
    async def process_user_input(self, user_input: str) -> str:
        """Process natural language input through the agent."""
        try:
            self._start_timing()
            
            response = await asyncio.to_thread(
                self.agent_executor.invoke,
                {"input": user_input}
            )
            
            self._end_timing()
            
            # Store interaction in memory
            await self._store_memory_item(
                content={"input": user_input, "output": response["output"]},
                importance=0.7
            )
            
            return response["output"]
            
        except Exception as e:
            self.logger.error(f"Error processing user input: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    async def run_analysis(self, force_refresh: bool = False) -> AgentAnalysisResult:
        """
        Run complete analysis pipeline for this agent.
        
        Args:
            force_refresh: Whether to force refresh of cached data
            
        Returns:
            AgentAnalysisResult with personality insights
        """
        result = AgentAnalysisResult(
            agent_type=self.agent_type,
            user_id=self.user_id,
            status=AnalysisStatus.IN_PROGRESS
        )
        
        try:
            self._start_timing()
            self.logger.info(f"Starting analysis for {self.agent_type.value} agent")
            
            # Collect data
            data = await self.collect_data(force_refresh=force_refresh)
            result.raw_data = data
            
            if not data:
                result.status = AnalysisStatus.FAILED
                result.error_message = "No data collected"
                return result
            
            # Analyze personality
            personality_insights = await self.analyze_personality(data)
            result.personality_insights = personality_insights
            
            # Calculate confidence scores
            confidence_scores = await self._calculate_confidence_scores(data, personality_insights)
            result.confidence_scores = confidence_scores
            
            result.status = AnalysisStatus.COMPLETED
            result.processing_time = self._end_timing()
            
            # Store results in memory
            await self._store_memory_item(
                content={"analysis_result": result.dict()},
                importance=0.9
            )
            
            self.logger.info(f"Completed analysis for {self.agent_type.value} agent in {result.processing_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Error in analysis: {str(e)}")
            result.status = AnalysisStatus.FAILED
            result.error_message = str(e)
            result.processing_time = self._end_timing()
        
        return result
    
    async def _calculate_confidence_scores(
        self, 
        data: Dict[str, Any], 
        personality_insights: Dict[PersonalityTrait, float]
    ) -> Dict[PersonalityTrait, float]:
        """Calculate confidence scores for personality insights."""
        confidence_scores = {}
        
        # Base confidence calculation - can be overridden by subclasses
        data_quality = min(1.0, len(data) / 10)  # More data = higher confidence
        
        for trait in personality_insights.keys():
            # Base confidence from data quality
            confidence = data_quality * 0.7
            
            # Add trait-specific confidence adjustments
            trait_confidence = await self._get_trait_confidence(trait, data)
            confidence = min(1.0, confidence + trait_confidence)
            
            confidence_scores[trait] = confidence
        
        return confidence_scores
    
    async def _get_trait_confidence(self, trait: PersonalityTrait, data: Dict[str, Any]) -> float:
        """Get confidence adjustment for specific traits. Can be overridden by subclasses."""
        return 0.2  # Default modest confidence boost
    
    def _start_timing(self) -> None:
        """Start performance timing."""
        self.start_time = time.time()
    
    def _end_timing(self) -> float:
        """End performance timing and return duration."""
        if self.start_time is None:
            return 0.0
        
        duration = time.time() - self.start_time
        self.processing_times.append(duration)
        self.start_time = None
        return duration
    
    async def _store_memory_item(
        self, 
        content: Dict[str, Any], 
        importance: float = 0.5,
        memory_type: str = "short_term"
    ) -> None:
        """Store an item in agent memory."""
        memory_item = MemoryItem(
            user_id=self.user_id,
            agent_type=self.agent_type,
            content=content,
            importance=importance
        )
        
        if memory_type == "short_term":
            self.agent_memory.short_term.append(memory_item)
            # Maintain memory size limit
            if len(self.agent_memory.short_term) > self.agent_memory.max_short_term:
                # Remove least important items
                self.agent_memory.short_term.sort(key=lambda x: x.importance)
                self.agent_memory.short_term = self.agent_memory.short_term[-self.agent_memory.max_short_term:]
        
        elif memory_type == "long_term":
            self.agent_memory.long_term.append(memory_item)
            if len(self.agent_memory.long_term) > self.agent_memory.max_long_term:
                self.agent_memory.long_term.sort(key=lambda x: x.importance)
                self.agent_memory.long_term = self.agent_memory.long_term[-self.agent_memory.max_long_term:]
        
        elif memory_type == "episodic":
            self.agent_memory.episodic_memory.append(memory_item)
    
    async def get_memory_context(self, query: str = "") -> Dict[str, Any]:
        """Get relevant memory context for the current query."""
        context = {
            "recent_interactions": [],
            "relevant_long_term": [],
            "working_memory": self.agent_memory.working_memory
        }
        
        # Get recent short-term memories
        context["recent_interactions"] = [
            item.content for item in self.agent_memory.short_term[-5:]
        ]
        
        # Get relevant long-term memories (simple importance-based for now)
        relevant_long_term = sorted(
            self.agent_memory.long_term,
            key=lambda x: x.importance,
            reverse=True
        )[:3]
        
        context["relevant_long_term"] = [item.content for item in relevant_long_term]
        
        return context
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for this agent."""
        health_info = {
            "agent_type": self.agent_type.value,
            "user_id": self.user_id,
            "status": "healthy",
            "memory_items": {
                "short_term": len(self.agent_memory.short_term),
                "long_term": len(self.agent_memory.long_term),
                "episodic": len(self.agent_memory.episodic_memory)
            },
            "average_processing_time": sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0,
            "total_analyses": len(self.processing_times),
            "last_activity": datetime.utcnow().isoformat()
        }
        
        # Check if agent can access required resources
        try:
            # Test LLM connection
            await asyncio.to_thread(
                self.llm.invoke,
                "Health check test"
            )
            health_info["llm_accessible"] = True
        except Exception as e:
            health_info["llm_accessible"] = False
            health_info["llm_error"] = str(e)
            health_info["status"] = "degraded"
        
        return health_info
    
    async def get_personality_context(self) -> Optional[PersonalityContextResponse]:
        """
        Get or load personality context for this user.
        
        Returns:
            Personality context response or None if not available
        """
        if self._personality_context is None:
            try:
                self._personality_context = await self.personality_service.get_user_personality_context(
                    self.user_id,
                    include_analysis_history=True
                )
            except Exception as e:
                self.logger.error(f"Error loading personality context: {e}")
                return None
        
        return self._personality_context
    
    async def get_personality_guidelines(self) -> Dict[str, Any]:
        """
        Get personality-based guidelines for this agent.
        
        Returns:
            Dictionary of guidelines based on user's personality
        """
        if self._personality_guidelines is None:
            context = await self.get_personality_context()
            if context and context.personality_profile:
                self._personality_guidelines = self.personality_service.get_agent_guidelines(
                    context.personality_profile
                )
            else:
                # Default guidelines for users without personality assessment
                self._personality_guidelines = self._get_default_guidelines()
        
        return self._personality_guidelines
    
    def _get_default_guidelines(self) -> Dict[str, Any]:
        """Get default guidelines when personality assessment is not available."""
        return {
            "music_preferences": {
                "genres": "Mix familiar and new musical styles",
                "discovery": "Introduce new music gradually",
                "energy": "Balanced energy levels"
            },
            "video_preferences": {
                "content": "Mix of entertainment and educational content",
                "variety": "Moderate variety in topics",
                "length": "Medium-length content"
            },
            "gaming_preferences": {
                "multiplayer": "Both solo and social gaming options",
                "competition": "Mix of competitive and casual games",
                "complexity": "Moderate complexity games"
            },
            "conversation_style": {
                "energy": "Balanced energy and enthusiasm",
                "interaction": "Moderate interaction frequency",
                "tone": "Friendly and supportive",
                "support": "Standard emotional support"
            }
        }
    
    async def get_system_prompt_context(self) -> Optional[str]:
        """
        Get the user's LLM system prompt for personalized responses.
        
        Returns:
            System prompt string or None
        """
        context = await self.get_personality_context()
        if context and context.llm_context:
            return context.llm_context.system_prompt
        return None
    
    async def store_analysis_result(self, result_data: Dict[str, Any]) -> bool:
        """
        Store this agent's analysis result in the database.
        
        Args:
            result_data: Analysis result to store
            
        Returns:
            True if successful
        """
        try:
            return await self.personality_service.store_agent_result(
                self.user_id,
                self.agent_type.value,
                result_data
            )
        except Exception as e:
            self.logger.error(f"Error storing analysis result: {e}")
            return False
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get performance statistics for this agent."""
        return {
            "agent_type": self.agent_type.value,
            "total_processing_time": sum(self.processing_times),
            "average_processing_time": sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0,
            "max_processing_time": max(self.processing_times) if self.processing_times else 0,
            "min_processing_time": min(self.processing_times) if self.processing_times else 0,
            "total_analyses": len(self.processing_times),
            "memory_usage": {
                "short_term": len(self.agent_memory.short_term),
                "long_term": len(self.agent_memory.long_term),
                "episodic": len(self.agent_memory.episodic_memory)
            }
        }