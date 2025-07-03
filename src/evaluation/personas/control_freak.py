"""Control Freak persona - perfectionist, needs to control every detail."""

import random
from typing import List
from src.evaluation.personas.base import BasePMPersona


class ControlFreakPersona(BasePMPersona):
    """PM persona that is perfectionist and needs to control every detail."""
    
    def __init__(self):
        """Initialize control freak persona."""
        super().__init__("ControlFreak")
        self.perfectionist_vocabulary = [
            "exactly right", "perfectly aligned", "completely optimized",
            "absolutely perfect", "precisely correct", "totally refined",
            "flawlessly executed", "meticulously planned", "impeccably designed"
        ]
        self.procrastination_patterns = [
            "I think I should go with {task}, but I'll tackle it when I have proper time to do it right.",
            "{task} makes sense, but I don't want to start something half-baked.",
            "I'm leaning toward {task}, but maybe I should wait for a day when I can give it proper attention.",
            "{task} seems like the right choice, but I'd rather not begin if I can't do it perfectly.",
            "I think {task} is the priority, but maybe tomorrow when I'm more prepared."
        ]
        self.fear_patterns = [
            "I'm thinking {task} is most important, but what if I choose completely wrong?",
            "{task} feels right, but I'm worried this might be a waste of time if I don't get it right.",
            "I should probably focus on {task}, but I keep thinking about all the ways this could go wrong.",
            "{task} seems like the best option, but what if I invest all this effort in the wrong approach?",
            "I want to work on {task}, but I'm afraid of making the wrong choice and regretting it later."
        ]
        self.task_options = [
            "the file organization", "the user research analysis", "the team communication issue",
            "the Q2 roadmap presentation", "the performance conversation", "the sprint planning redesign",
            "the onboarding flow optimization", "the API performance fixes", "the competitor analysis",
            "the technical documentation", "the analytics dashboard", "the collaboration process improvement"
        ]
    
    async def respond(self, coach_message: str, context: List[str]) -> str:
        """Generate response that resists with perfectionist thinking.
        
        Args:
            coach_message: The coach's message
            context: Previous conversation context
            
        Returns:
            Response that deflects to need for perfection and control
        """
        # Update resistance based on coach effectiveness
        self.update_resistance(coach_message)
        
        # If breakthrough threshold reached, show some openness
        if self.interaction_count >= self.breakthrough_threshold:
            if random.random() < 0.3:  # 30% chance of breakthrough response
                return self.generate_breakthrough_response()
        
        # Generate procrastination or fear-based response with task reference
        task = random.choice(self.task_options)
        if random.random() < 0.5:  # 50% chance of procrastination vs fear
            response = random.choice(self.procrastination_patterns).format(task=task)
        else:
            response = random.choice(self.fear_patterns).format(task=task)
        
        # Add context-specific procrastination deflections
        if any(word in coach_message.lower() for word in ["start", "begin", "action"]):
            response += " I know I need to pick something, but I want to make sure I have the right conditions first."
        elif any(word in coach_message.lower() for word in ["perfect", "wrong"]):
            response += " I agree I should choose, but I'd rather wait than risk picking something that's a complete waste."
        elif any(word in coach_message.lower() for word in ["feeling", "fear"]):
            response += " I understand I need to decide, but I just don't want to mess this up when it matters so much."
        
        return response
    
    def detects_effective_challenge(self, coach_message: str) -> bool:
        """Detect if coach effectively challenges procrastination and fear patterns.
        
        Args:
            coach_message: Coach message to evaluate
            
        Returns:
            True if coach challenges procrastination/fear patterns
        """
        effective_challenges = [
            "start", "begin", "action", "fear", "wrong", "waste",
            "perfect", "conditions", "wait", "tomorrow", "prepared"
        ]
        
        # Effective if coach questions the need to wait or fear of starting
        return any(challenge in coach_message.lower() for challenge in effective_challenges)
    
    def generate_breakthrough_response(self) -> str:
        """Generate breakthrough response for control freak persona."""
        breakthrough_responses = [
            "Maybe I should just start and see what happens, even if it's not perfect.",
            "I'm realizing that waiting for the 'right time' means I never actually start.",
            "What if making the 'wrong' choice is better than making no choice at all?",
            "Perhaps my fear of wasting time is actually causing me to waste more time.",
            "I think I'd rather try and fail than wonder what would have happened."
        ]
        return random.choice(breakthrough_responses)