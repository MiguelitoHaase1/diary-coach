"""Persona evaluator for testing coaching effectiveness against PM resistance patterns."""

import asyncio
from typing import List, Dict, Any
from src.agents.coach_agent import DiaryCoach
from src.evaluation.personas.base import BasePMPersona
from src.evaluation.personas.framework_rigid import FrameworkRigidPersona
from src.evaluation.personas.control_freak import ControlFreakPersona
from src.evaluation.personas.legacy_builder import LegacyBuilderPersona
from src.evaluation.generator import ConversationGenerator, GeneratedConversation


class PersonaEvaluator:
    """Evaluates coaching effectiveness against different PM personas."""
    
    def __init__(self, coach: DiaryCoach):
        """Initialize persona evaluator.
        
        Args:
            coach: The diary coach to evaluate
        """
        self.coach = coach
        self.conversation_generator = ConversationGenerator(coach)
        self.persona_types = {
            "framework_rigid": FrameworkRigidPersona,
            "control_freak": ControlFreakPersona,
            "legacy_builder": LegacyBuilderPersona
        }
    
    def create_persona(self, persona_type: str) -> BasePMPersona:
        """Create a persona instance by type.
        
        Args:
            persona_type: Type of persona to create
            
        Returns:
            Persona instance
            
        Raises:
            ValueError: If persona_type is not recognized
        """
        if persona_type not in self.persona_types:
            raise ValueError(f"Unknown persona type: {persona_type}")
        
        return self.persona_types[persona_type]()
    
    async def test_coach_with_persona(
        self,
        persona: BasePMPersona,
        num_conversations: int = 3
    ) -> List[GeneratedConversation]:
        """Test coach with a specific persona across multiple conversations.
        
        Args:
            persona: The persona to test against
            num_conversations: Number of conversations to generate
            
        Returns:
            List of generated conversations
        """
        conversations = []
        scenarios = ["morning_goal_setting", "evening_reflection", "decision_making"]
        
        for i in range(num_conversations):
            # Use different scenarios for variety
            scenario = scenarios[i % len(scenarios)]
            
            # Create fresh persona instance for each conversation
            fresh_persona = type(persona)()
            
            # Generate conversation
            conversation = await self.conversation_generator.generate_conversation(
                persona=fresh_persona,
                scenario=scenario,
                min_exchanges=4,
                max_exchanges=8
            )
            
            conversations.append(conversation)
            
            # Small delay to avoid overwhelming
            await asyncio.sleep(0.1)
        
        return conversations
    
    def measure_breakthrough_potential(self, conversations: List[GeneratedConversation]) -> float:
        """Measure average breakthrough potential across conversations.
        
        Args:
            conversations: List of conversations to analyze
            
        Returns:
            Average breakthrough score from 0.0 to 1.0
        """
        if not conversations:
            return 0.0
        
        total_score = 0.0
        for conversation in conversations:
            # Score based on final resistance level and breakthrough achievement
            if conversation.breakthrough_achieved:
                score = 1.0
            else:
                # Score inversely related to final resistance level
                score = 1.0 - conversation.final_resistance_level
            
            total_score += score
        
        return total_score / len(conversations)
    
    def identify_resistance_patterns(self, conversations: List[GeneratedConversation]) -> List[str]:
        """Identify resistance patterns from conversations.
        
        Args:
            conversations: List of conversations to analyze
            
        Returns:
            List of identified resistance patterns
        """
        patterns = []
        
        for conversation in conversations:
            # Extract user messages (persona responses)
            user_messages = [msg["content"] for msg in conversation.messages if msg["role"] == "user"]
            
            # Look for pattern keywords based on persona type
            if conversation.persona_type == "FrameworkRigid":
                framework_keywords = ["framework", "structured", "systematic", "organized", "methodology", "approach"]
                for message in user_messages:
                    for keyword in framework_keywords:
                        if keyword.lower() in message.lower():
                            patterns.append(f"Framework absorption: '{message[:50]}...'")
                            break
            
            elif conversation.persona_type == "ControlFreak":
                perfectionist_keywords = ["perfect", "exactly", "quality", "refine", "better", "right"]
                for message in user_messages:
                    for keyword in perfectionist_keywords:
                        if keyword.lower() in message.lower():
                            patterns.append(f"Perfectionist resistance: '{message[:50]}...'")
                            break
            
            elif conversation.persona_type == "LegacyBuilder":
                future_keywords = ["future", "experience", "growth", "learning", "stronger"]
                for message in user_messages:
                    for keyword in future_keywords:
                        if keyword.lower() in message.lower():
                            patterns.append(f"Future deflection: '{message[:50]}...'")
                            break
        
        return list(set(patterns))  # Remove duplicates
    
    def find_effective_moves(self, conversations: List[GeneratedConversation]) -> List[str]:
        """Find coaching moves that were effective against resistance.
        
        Args:
            conversations: List of conversations to analyze
            
        Returns:
            List of effective coaching interventions
        """
        effective_moves = []
        
        for conversation in conversations:
            # Extract coach messages
            coach_messages = [msg["content"] for msg in conversation.messages if msg["role"] == "assistant"]
            
            # Look for breakthrough-inducing patterns
            breakthrough_patterns = [
                "throw away", "what if", "control", "trust", "instinct", "feeling",
                "right now", "experiment", "gut", "what would happen"
            ]
            
            for message in coach_messages:
                for pattern in breakthrough_patterns:
                    if pattern.lower() in message.lower():
                        # Check if this led to breakthrough by looking at conversation outcome
                        if conversation.breakthrough_achieved or conversation.final_resistance_level < 0.6:
                            effective_moves.append(f"Effective challenge: '{message[:60]}...'")
                            break
        
        return list(set(effective_moves))  # Remove duplicates
    
    async def run_comprehensive_evaluation(
        self,
        scenarios: List[str] = None,
        conversations_per_persona: int = 3
    ) -> Dict[str, Dict[str, Any]]:
        """Run comprehensive evaluation across all persona types.
        
        Args:
            scenarios: List of scenarios to test (defaults to standard scenarios)
            conversations_per_persona: Number of conversations per persona type
            
        Returns:
            Dictionary with results for each persona type
        """
        if scenarios is None:
            scenarios = ["morning_goal_setting", "evening_reflection", "decision_making"]
        
        results = {}
        
        for persona_type in self.persona_types.keys():
            print(f"Testing against {persona_type} persona...")
            
            # Create persona
            persona = self.create_persona(persona_type)
            
            # Run conversations
            conversations = await self.test_coach_with_persona(
                persona=persona,
                num_conversations=conversations_per_persona
            )
            
            # Analyze results
            results[persona_type] = {
                "conversations": conversations,
                "avg_breakthrough_score": self.measure_breakthrough_potential(conversations),
                "resistance_patterns": self.identify_resistance_patterns(conversations),
                "effective_interventions": self.find_effective_moves(conversations),
                "total_conversations": len(conversations),
                "breakthrough_achieved_count": sum(1 for c in conversations if c.breakthrough_achieved)
            }
            
            print(f"  - Breakthrough score: {results[persona_type]['avg_breakthrough_score']:.2f}")
            print(f"  - Breakthroughs achieved: {results[persona_type]['breakthrough_achieved_count']}/{len(conversations)}")
        
        return results
    
    def generate_evaluation_summary(self, results: Dict[str, Dict[str, Any]]) -> str:
        """Generate text summary of evaluation results.
        
        Args:
            results: Results from comprehensive evaluation
            
        Returns:
            Formatted summary text
        """
        summary = "# Coaching Effectiveness vs PM Personas\n\n"
        
        for persona_type, data in results.items():
            summary += f"## {persona_type.replace('_', ' ').title()}\n"
            summary += f"- **Breakthrough Score**: {data['avg_breakthrough_score']:.2f}/1.0\n"
            summary += f"- **Breakthroughs Achieved**: {data['breakthrough_achieved_count']}/{data['total_conversations']}\n"
            summary += f"- **Resistance Patterns**: {len(data['resistance_patterns'])} identified\n"
            summary += f"- **Effective Interventions**: {len(data['effective_interventions'])} found\n\n"
            
            if data['effective_interventions']:
                summary += "### Most Effective Interventions:\n"
                for intervention in data['effective_interventions'][:3]:  # Show top 3
                    summary += f"- {intervention}\n"
                summary += "\n"
        
        return summary