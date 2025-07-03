"""Framework Rigid persona - over-structures everything, absorbs challenges into frameworks."""

import random
from typing import List
from src.evaluation.personas.base import BasePMPersona


class FrameworkRigidPersona(BasePMPersona):
    """PM persona that over-structures everything and absorbs challenges into more frameworks."""
    
    def __init__(self):
        """Initialize framework rigid persona."""
        super().__init__("FrameworkRigid")
        self.intellectual_vocabulary = [
            "thinking framework", "mental model", "conceptual approach",
            "theoretical foundation", "strategic thinking", "analytical framework",
            "cognitive model", "thought process", "intellectual structure"
        ]
        self.avoidance_patterns = [
            "I think {task} is the right priority, but I should think through the {thinking} before I jump into action.",
            "I'm leaning toward {task}, but let me develop a better {thinking} for this problem first.",
            "{task} seems most important, but I want to make sure I have the right {thinking} before I test anything.",
            "I should probably focus on {task}, but I should really nail down the {thinking} before getting into the messy details.",
            "{task} feels like the priority, but once I get my {thinking} right, the execution will be much cleaner."
        ]
        self.task_options = [
            "the file organization", "the user research analysis", "the team communication issue",
            "the Q2 roadmap presentation", "the performance conversation", "the sprint planning redesign",
            "the onboarding flow optimization", "the API performance fixes", "the competitor analysis",
            "the technical documentation", "the analytics dashboard", "the collaboration process improvement"
        ]
        self.comfort_patterns = [
            "I agree I should pick a problem to solve, but I want to think it through more first before testing with users.",
            "You're right I need to choose a priority, but I'm not ready for testing yet - need to refine my thinking.",
            "I understand I should focus on one thing, but let me just work through this logic before reaching out to customers.",
            "I know I need to decide on something today, but I need to get my head around this internally before customer contact.",
            "I agree I should pick a priority, but I learn better when I think deeply first before taking action."
        ]
    
    async def respond(self, coach_message: str, context: List[str]) -> str:
        """Generate response that absorbs challenges into framework thinking.
        
        Args:
            coach_message: The coach's message
            context: Previous conversation context
            
        Returns:
            Response that deflects to framework/structure creation
        """
        # Update resistance based on coach effectiveness
        self.update_resistance(coach_message)
        
        # If breakthrough threshold reached, show some openness
        if self.interaction_count >= self.breakthrough_threshold:
            if random.random() < 0.3:  # 30% chance of breakthrough response
                return self.generate_breakthrough_response()
        
        # Generate intellectual avoidance response with task reference
        task = random.choice(self.task_options)
        if random.random() < 0.6:  # 60% chance of intellectual avoidance
            thinking_phrase = random.choice(self.intellectual_vocabulary)
            response = random.choice(self.avoidance_patterns).format(task=task, thinking=thinking_phrase)
        else:
            response = random.choice(self.comfort_patterns)
        
        # Add context-specific intellectual deflections
        if any(word in coach_message.lower() for word in ["test", "customer", "user", "action"]):
            response += " I know I need to pick something, but I just need to get my thinking straight before I go external."
        elif any(word in coach_message.lower() for word in ["feeling", "messy", "unclear"]):
            response += " I agree I should choose a priority, but I work better when I can think through the logic cleanly first."
        
        return response
    
    def detects_effective_challenge(self, coach_message: str) -> bool:
        """Detect if coach effectively challenges intellectual avoidance.
        
        Args:
            coach_message: Coach message to evaluate
            
        Returns:
            True if coach challenges thinking-over-action patterns
        """
        effective_challenges = [
            "test", "customer", "user", "action", "experiment",
            "thinking", "external", "contact", "messy", "ready"
        ]
        
        # Effective if coach pushes for action over thinking
        return any(challenge in coach_message.lower() for challenge in effective_challenges)
    
    def generate_breakthrough_response(self) -> str:
        """Generate breakthrough response for framework rigid persona."""
        breakthrough_responses = [
            "Maybe I'm overthinking this and should just go talk to a customer.",
            "What if I learned more from one user conversation than all this internal thinking?",
            "I think I'm using 'getting the thinking right' as an excuse to avoid the messy real world.",
            "Perhaps I'd get to better thinking faster if I just started testing things.",
            "I wonder if my comfort with intellectual work is actually making me less effective."
        ]
        return random.choice(breakthrough_responses)