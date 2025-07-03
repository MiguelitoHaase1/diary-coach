"""Legacy Builder persona - deflects to future impact, avoids present feelings."""

import random
from typing import List
from src.evaluation.personas.base import BasePMPersona


class LegacyBuilderPersona(BasePMPersona):
    """PM persona that deflects to future impact and avoids present feelings."""
    
    def __init__(self):
        """Initialize legacy builder persona."""
        super().__init__("LegacyBuilder")
        self.vision_vocabulary = [
            "ideal case study", "vision for this", "big picture impact",
            "strategic transformation", "long-term vision", "game-changing approach",
            "revolutionary solution", "industry-defining work", "legacy-building opportunity"
        ]
        self.vision_patterns = [
            "I think {task} is the right priority, but I'm excited about the {vision} this could become.",
            "{task} makes sense to work on, but the {vision} here is really compelling - imagine if we could...",
            "I should probably focus on {task}, but this has the potential to be a {vision} that changes everything.",
            "{task} seems like the priority, but I keep thinking about the {vision} and how transformative it could be.",
            "I'm leaning toward {task}, but the {vision} is so inspiring - this could be the thing that defines my career."
        ]
        self.task_options = [
            "the file organization", "the user research analysis", "the team communication issue",
            "the Q2 roadmap presentation", "the performance conversation", "the sprint planning redesign",
            "the onboarding flow optimization", "the API performance fixes", "the competitor analysis",
            "the technical documentation", "the analytics dashboard", "the collaboration process improvement"
        ]
        self.avoidance_patterns = [
            "I know I should pick a problem to solve today, but I don't want to suboptimize by just solving the immediate issue.",
            "You're right I need to choose a priority, but sure, we could fix this now, but what about the bigger transformation?",
            "I understand I should focus on one thing, but I worry that focusing on daily execution means missing the big opportunity.",
            "I agree I need to decide on something, but the tactical stuff is fine, but I'm thinking about the strategic impact.",
            "I know I should pick a priority today, but I'd rather invest time in the vision than just optimize the current state."
        ]
    
    async def respond(self, coach_message: str, context: List[str]) -> str:
        """Generate response that deflects to future thinking.
        
        Args:
            coach_message: The coach's message
            context: Previous conversation context
            
        Returns:
            Response that avoids present feelings and redirects to future impact
        """
        # Update resistance based on coach effectiveness
        self.update_resistance(coach_message)
        
        # If breakthrough threshold reached, show some openness
        if self.interaction_count >= self.breakthrough_threshold:
            if random.random() < 0.3:  # 30% chance of breakthrough response
                return self.generate_breakthrough_response()
        
        # Generate vision-focused or avoidance response with task reference
        task = random.choice(self.task_options)
        if random.random() < 0.6:  # 60% chance of vision focus
            vision_phrase = random.choice(self.vision_vocabulary)
            response = random.choice(self.vision_patterns).format(task=task, vision=vision_phrase)
        else:
            response = random.choice(self.avoidance_patterns)
        
        # Add context-specific vision deflections
        if any(word in coach_message.lower() for word in ["daily", "immediate", "now", "today"]):
            response += " I know I need to pick something today, but I'm worried about losing sight of the transformational opportunity."
        elif any(word in coach_message.lower() for word in ["problem", "issue", "fix"]):
            response += " I understand I should choose a priority, but I don't want to spend all my energy on tactics when the strategy is so exciting."
        elif any(word in coach_message.lower() for word in ["energy", "time", "focus"]):
            response += " I agree I should decide on something, but I'd rather invest that energy in something that could be game-changing."
        
        return response
    
    def detects_effective_challenge(self, coach_message: str) -> bool:
        """Detect if coach effectively challenges vision-avoidance patterns.
        
        Args:
            coach_message: Coach message to evaluate
            
        Returns:
            True if coach challenges vision-deflection and brings attention to immediate execution
        """
        effective_challenges = [
            "daily", "immediate", "now", "today", "energy", "time",
            "focus", "execution", "problem", "grind", "tactics"
        ]
        
        # Effective if coach brings attention to immediate execution over vision
        return any(challenge in coach_message.lower() for challenge in effective_challenges)
    
    def generate_breakthrough_response(self) -> str:
        """Generate breakthrough response for legacy builder persona."""
        breakthrough_responses = [
            "Maybe I'm using the vision as an excuse to avoid the hard work right in front of me.",
            "What if solving this immediate problem with full energy is actually the strategic move?",
            "I think I'm so focused on the case study that I'm not actually creating anything worth studying.",
            "Perhaps the daily grind is where the real transformation happens.",
            "I wonder if my obsession with the big picture is preventing me from making any real progress."
        ]
        return random.choice(breakthrough_responses)