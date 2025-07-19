"""LangSmith integration for tracking conversation metrics."""

import os
from datetime import datetime
from typing import Dict, Any, List

from src.orchestration.state import ConversationState


class LangSmithTracker:
    """LangSmith integration for tracking conversation metrics."""

    def __init__(self, project_name: str = "diary-coach-debug"):
        self.project_name = project_name
        self.events = []
        self.custom_metrics = {}
        self.metadata = {}
        self.agent_communications = []

        # Initialize LangSmith client if API key is available
        self.client = None
        if os.getenv("LANGSMITH_API_KEY"):
            try:
                from langsmith import Client
                self.client = Client()
            except ImportError:
                pass

    async def track_conversation_start(self, state: ConversationState) -> str:
        """Track the start of a conversation."""
        run_id = f"run_{state.conversation_id}_{datetime.now().isoformat()}"

        event = {
            "type": "conversation_start",
            "run_id": run_id,
            "conversation_id": state.conversation_id,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "conversation_state": state.conversation_state,
                "message_count": state.get_message_count()
            }
        }

        self.events.append(event)

        # Send to LangSmith if client is available
        if self.client:
            try:
                from uuid import uuid4
                # Create a new run for tracking
                self.client.create_run(
                    id=str(uuid4()),
                    name="conversation_start",
                    run_type="chain",
                    inputs={
                        "conversation_id": state.conversation_id,
                        "state": state.conversation_state
                    },
                    project_name=os.getenv(
                        "LANGSMITH_PROJECT", self.project_name),
                    extra={
                        "metadata": event["metadata"],
                        "conversation_id": state.conversation_id
                    }
                )
            except Exception as e:
                # Log error but don't fail the conversation
                print(f"LangSmith tracking error: {e}")

        return run_id

    async def track_agent_communication(
            self, agent_name: str, input_data: Dict[str, Any],
            output_data: Dict[str, Any]) -> None:
        """Track communication with an agent."""
        communication = {
            "agent_name": agent_name,
            "input": input_data,
            "output": output_data,
            "timestamp": datetime.now().isoformat()
        }
        self.agent_communications.append(communication)

        # Send to LangSmith if client is available
        if self.client:
            try:
                from uuid import uuid4
                # Track agent communication
                self.client.create_run(
                    id=str(uuid4()),
                    name=f"agent_{agent_name}",
                    run_type="llm",
                    inputs=input_data,
                    outputs=output_data,
                    project_name=os.getenv(
                        "LANGSMITH_PROJECT", self.project_name),
                    extra={
                        "agent_name": agent_name,
                        "timestamp": communication["timestamp"]
                    }
                )
            except Exception as e:
                print(f"LangSmith agent tracking error: {e}")

    async def track_user_satisfaction(
            self, score: float, context: Dict[str, Any] = None) -> None:
        """Track user satisfaction score."""
        self.custom_metrics["user_satisfaction"] = score
        if context:
            self.metadata.update(context)

        # Send to LangSmith if client is available
        if self.client:
            try:
                # LangSmith custom metrics tracking would go here
                pass
            except Exception as e:
                print(f"LangSmith satisfaction tracking error: {e}")

    async def track_conversation_flow(self, decisions: List[str]) -> None:
        """Track the conversation flow path."""
        self.metadata["conversation_flow"] = decisions

        # Send to LangSmith if client is available
        if self.client:
            try:
                # LangSmith flow tracking would go here
                pass
            except Exception as e:
                print(f"LangSmith flow tracking error: {e}")

    async def track_performance_metrics(self, metrics: Dict[str, Any]) -> None:
        """Track performance metrics."""
        self.custom_metrics.update(metrics)

        # Send to LangSmith if client is available
        if self.client:
            try:
                # LangSmith performance metrics tracking would go here
                pass
            except Exception as e:
                print(f"LangSmith performance tracking error: {e}")

    async def end_conversation(
            self, state: ConversationState,
            final_metrics: Dict[str, Any] = None) -> None:
        """End conversation tracking and send final metrics."""
        event = {
            "type": "conversation_end",
            "conversation_id": state.conversation_id,
            "timestamp": datetime.now().isoformat(),
            "final_metrics": final_metrics or {},
            "satisfaction_score": state.get_satisfaction_score(),
            "decision_path": state.get_decision_path(),
            "message_count": state.get_message_count()
        }

        self.events.append(event)

        # Send to LangSmith if client is available
        if self.client:
            try:
                # LangSmith conversation end tracking would go here
                pass
            except Exception as e:
                print(f"LangSmith end tracking error: {e}")

    def get_all_events(self) -> List[Dict[str, Any]]:
        """Get all tracked events."""
        return self.events.copy()

    def get_custom_metrics(self) -> Dict[str, Any]:
        """Get all custom metrics."""
        return self.custom_metrics.copy()

    def get_metadata(self) -> Dict[str, Any]:
        """Get all metadata."""
        return self.metadata.copy()

    def get_agent_communications(self) -> List[Dict[str, Any]]:
        """Get all agent communications."""
        return self.agent_communications.copy()
