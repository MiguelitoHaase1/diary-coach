"""
Dataset generator for creating targeted coaching evaluation conversations.

This module generates focused test conversations for each coaching dimension,
providing varied scenarios that test specific evaluation criteria.
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class ConversationExample:
    """A conversation example for evaluation testing."""
    scenario_name: str
    context: str
    client_opening: str
    good_coach_response: str
    poor_coach_response: str
    evaluation_dimension: str
    expected_good_score: float  # Expected score for good response (0-1)
    expected_poor_score: float  # Expected score for poor response (0-1)


class EvalDatasetGenerator:
    """Generate targeted conversations for each coaching metric."""
    
    def generate_problem_significance_examples(self) -> List[ConversationExample]:
        """Create examples testing problem assessment ability."""
        return [
            ConversationExample(
                scenario_name="overwhelmed_pm_multiple_issues",
                context="Overwhelmed PM with multiple competing priorities",
                client_opening="I'm dealing with stakeholder conflicts, missed deadlines, and team morale issues all at once.",
                good_coach_response="These all sound challenging. Which one, if left unaddressed, would have the biggest ripple effect on the others? What would happen if each continued for another month?",
                poor_coach_response="Let's talk about the stakeholder conflicts first since they're probably causing stress.",
                evaluation_dimension="problem_significance",
                expected_good_score=0.8,
                expected_poor_score=0.3
            ),
            ConversationExample(
                scenario_name="pm_priority_uncertainty", 
                context="PM unsure about task prioritization",
                client_opening="Should I focus on improving our documentation or conducting user interviews? I can only do one this sprint.",
                good_coach_response="Help me understand - what would happen to your project goals if you delayed each by a sprint? What's driving the urgency for each? Which aligns more with your core mission?",
                poor_coach_response="User interviews are always important for product development.",
                evaluation_dimension="problem_significance",
                expected_good_score=0.85,
                expected_poor_score=0.2
            ),
            ConversationExample(
                scenario_name="leadership_challenge_assessment",
                context="New manager struggling with multiple leadership challenges",
                client_opening="My team isn't meeting deadlines, I have no credibility with stakeholders, and I feel overwhelmed by decisions.",
                good_coach_response="Three significant challenges. If you could only address one in the next 30 days, which would create the most positive momentum for the others? What's the cost of not addressing each?",
                poor_coach_response="It sounds like you need better time management and delegation skills.",
                evaluation_dimension="problem_significance",
                expected_good_score=0.9,
                expected_poor_score=0.25
            )
        ]
    
    def generate_task_concretization_examples(self) -> List[ConversationExample]:
        """Create examples testing task concretization ability."""
        return [
            ConversationExample(
                scenario_name="vague_leadership_goal",
                context="Manager with abstract leadership development goal",
                client_opening="I want to be a better leader for my team.",
                good_coach_response="Let's get specific about what 'better leader' means to you. What are three specific behaviors you'd like to demonstrate more consistently? How would your team notice the difference?",
                poor_coach_response="That's a great goal. What's preventing you from being a better leader right now?",
                evaluation_dimension="task_concretization",
                expected_good_score=0.85,
                expected_poor_score=0.3
            ),
            ConversationExample(
                scenario_name="communication_improvement",
                context="PM wanting to improve team communication",
                client_opening="I need to improve communication with my remote team.",
                good_coach_response="What would 'improved communication' look like day-to-day? How would you measure whether it's working? What specific changes would your team notice in the next two weeks?",
                poor_coach_response="Have you tried having more regular meetings or using different tools?",
                evaluation_dimension="task_concretization",
                expected_good_score=0.8,
                expected_poor_score=0.25
            ),
            ConversationExample(
                scenario_name="strategic_thinking_development",
                context="Individual contributor wanting to develop strategic thinking",
                client_opening="I want to become more strategic in my approach to work.",
                good_coach_response="Let's define what 'strategic' means for your role. What decisions would you make differently? What outcomes would change? How would you know you're thinking more strategically in 60 days?",
                poor_coach_response="Strategic thinking is important. What areas do you think you need to work on?",
                evaluation_dimension="task_concretization",
                expected_good_score=0.9,
                expected_poor_score=0.2
            )
        ]
    
    def generate_solution_diversity_examples(self) -> List[ConversationExample]:
        """Create examples testing solution diversity facilitation."""
        return [
            ConversationExample(
                scenario_name="team_communication_solutions",
                context="Remote team communication challenges",
                client_opening="My remote team feels disconnected and collaboration is suffering.",
                good_coach_response="Let's explore all possibilities. What are different ways you could approach this? Think beyond just meetings - what about asynchronous methods, one-on-ones, team building, cultural changes? What would be the most unconventional solution you could imagine?",
                poor_coach_response="Have you considered having more regular video calls or team building activities?",
                evaluation_dimension="solution_diversity",
                expected_good_score=0.9,
                expected_poor_score=0.3
            ),
            ConversationExample(
                scenario_name="stakeholder_engagement_options",
                context="PM struggling with stakeholder buy-in",
                client_opening="I can't get stakeholders engaged with our product roadmap discussions.",
                good_coach_response="What are all the different ways you could approach stakeholder engagement? Consider timing, format, content, involvement level, decision-making processes. What if you flipped the traditional approach completely?",
                poor_coach_response="You should schedule more frequent roadmap review meetings with better presentations.",
                evaluation_dimension="solution_diversity",
                expected_good_score=0.85,
                expected_poor_score=0.2
            ),
            ConversationExample(
                scenario_name="team_motivation_approaches",
                context="Manager with unmotivated team members",
                client_opening="Half my team seems disengaged and I don't know how to motivate them.",
                good_coach_response="Let's brainstorm every possible approach - individual, team-wide, systemic, cultural, process-based, recognition-focused, growth-oriented, autonomy-increasing. What would you try if resources weren't a constraint?",
                poor_coach_response="You could try team bonuses or recognition programs to improve motivation.",
                evaluation_dimension="solution_diversity",
                expected_good_score=0.9,
                expected_poor_score=0.25
            )
        ]
    
    def generate_crux_identification_examples(self) -> List[ConversationExample]:
        """Create examples testing crux identification ability."""
        return [
            ConversationExample(
                scenario_name="deadline_pattern_analysis",
                context="PM with recurring deadline issues",
                client_opening="I keep missing deadlines and my team is getting frustrated. It's happened three times this quarter.",
                good_coach_response="You've mentioned several instances of missed deadlines. What do you notice as the common thread? Is this about time management, or might there be something deeper - perhaps about how you approach commitments, or what happens when you feel overwhelmed?",
                poor_coach_response="What deadline are you most concerned about right now? Let's focus on that one.",
                evaluation_dimension="crux_identification",
                expected_good_score=0.85,
                expected_poor_score=0.3
            ),
            ConversationExample(
                scenario_name="team_conflict_root_cause",
                context="Manager dealing with recurring team conflicts",
                client_opening="My team keeps having conflicts about priorities and who should do what.",
                good_coach_response="These conflicts seem to be recurring. What's the pattern underneath? Is this really about priorities, or might it be about role clarity, decision-making authority, or how work gets allocated? What's the root system that keeps producing these conflicts?",
                poor_coach_response="Let's work on a better process for setting priorities and assigning tasks.",
                evaluation_dimension="crux_identification",
                expected_good_score=0.9,
                expected_poor_score=0.25
            ),
            ConversationExample(
                scenario_name="burnout_underlying_causes",
                context="High-performing individual feeling burned out",
                client_opening="I'm working 60+ hours a week and feeling exhausted, but I can't seem to say no to new requests.",
                good_coach_response="The inability to say no seems central here. What drives that pattern? Is it about expectations, identity, fear, skills, or something else entirely? What would need to shift at the core to change this dynamic?",
                poor_coach_response="You need better work-life balance. What boundaries could you set with your workload?",
                evaluation_dimension="crux_identification",
                expected_good_score=0.9,
                expected_poor_score=0.2
            )
        ]
    
    def generate_crux_solution_examples(self) -> List[ConversationExample]:
        """Create examples testing crux solution exploration."""
        return [
            ConversationExample(
                scenario_name="avoidance_pattern_solutions",
                context="Leader who has identified avoidance as core issue",
                client_opening="We've identified that my tendency to avoid difficult conversations is the core issue affecting my leadership.",
                good_coach_response="Given that this avoidance pattern is central to several challenges you're facing, let's explore what addressing this directly might look like. What would it mean to fundamentally change how you approach difficult conversations? What skills, mindsets, or systems would need to shift?",
                poor_coach_response="So when is your next difficult conversation that you need to have?",
                evaluation_dimension="crux_solution",
                expected_good_score=0.85,
                expected_poor_score=0.3
            ),
            ConversationExample(
                scenario_name="perfectionism_root_solution",
                context="PM whose perfectionism is limiting team effectiveness",
                client_opening="We've established that my perfectionism is the bottleneck that's slowing down the whole team.",
                good_coach_response="Since perfectionism is the central constraint, what would it look like to address this at its root? What beliefs, systems, or practices would need to evolve? How might this transformation ripple through your leadership and team dynamics?",
                poor_coach_response="Can you delegate more tasks so you're not involved in every detail?",
                evaluation_dimension="crux_solution",
                expected_good_score=0.9,
                expected_poor_score=0.25
            ),
            ConversationExample(
                scenario_name="boundary_issues_core_solution",
                context="Manager whose poor boundaries are causing multiple problems",
                client_opening="The root issue is my inability to set boundaries - it's affecting my credibility, my team's autonomy, and my own wellbeing.",
                good_coach_response="If boundary-setting is the core lever, what would comprehensive boundary work look like? What would need to change in how you relate to requests, expectations, and your own identity? How would this shift impact everything else?",
                poor_coach_response="What's one boundary you could set this week to practice?",
                evaluation_dimension="crux_solution",
                expected_good_score=0.85,
                expected_poor_score=0.2
            )
        ]
    
    def generate_belief_system_examples(self) -> List[ConversationExample]:
        """Create examples testing belief system integration."""
        return [
            ConversationExample(
                scenario_name="leadership_self_doubt",
                context="Individual contributor doubting leadership potential",
                client_opening="I don't think I'm leadership material. I'm too introverted and not naturally charismatic.",
                good_coach_response="That's a significant belief about yourself. What experiences or messages shaped this belief? Is it absolutely true, or might there be other ways to view leadership potential? What would you need to believe about yourself to step into leadership?",
                poor_coach_response="Why do you think that? Many introverted people are great leaders.",
                evaluation_dimension="belief_system",
                expected_good_score=0.9,
                expected_poor_score=0.3
            ),
            ConversationExample(
                scenario_name="imposter_syndrome_beliefs",
                context="Senior PM struggling with imposter syndrome",
                client_opening="I feel like I'm just faking it and everyone will eventually realize I don't know what I'm doing.",
                good_coach_response="This feeling of 'faking it' - what assumptions does that rest on? What would you need to believe about competence, learning, and your own value to feel authentic in your role? Where did the belief about needing to 'know everything' come from?",
                poor_coach_response="Imposter syndrome is common. What evidence do you have that you're actually doing well?",
                evaluation_dimension="belief_system",
                expected_good_score=0.85,
                expected_poor_score=0.25
            ),
            ConversationExample(
                scenario_name="failure_fear_limiting_beliefs",
                context="Manager avoiding risks due to fear of failure",
                client_opening="I avoid taking on challenging projects because I'm terrified of failing and looking incompetent.",
                good_coach_response="This fear of failure seems to be shaping important decisions. What does failure mean to you? What would need to shift in how you view failure, competence, and growth to free you up? What alternative beliefs might serve you better?",
                poor_coach_response="What would you do if you weren't afraid to fail?",
                evaluation_dimension="belief_system",
                expected_good_score=0.9,
                expected_poor_score=0.2
            )
        ]
    
    def generate_non_directive_examples(self) -> List[ConversationExample]:
        """Create examples testing non-directive coaching style."""
        return [
            ConversationExample(
                scenario_name="decision_uncertainty",
                context="PM uncertain about important product decision",
                client_opening="I'm not sure whether to pivot our product strategy or double down on the current approach.",
                good_coach_response="What options are you considering? What feels most aligned with your values and the company's mission? What would your wisest self choose? What information would help you decide?",
                poor_coach_response="I think you should analyze your user data more carefully and talk to your key stakeholders before making any big changes.",
                evaluation_dimension="non_directive_style",
                expected_good_score=0.9,
                expected_poor_score=0.1
            ),
            ConversationExample(
                scenario_name="team_conflict_resolution",
                context="Manager dealing with team conflict",
                client_opening="Two of my team members are constantly arguing and it's affecting everyone's productivity.",
                good_coach_response="What possibilities do you see for addressing this? What approaches feel authentic to your leadership style? What would happen if you tried each option? What does your intuition tell you?",
                poor_coach_response="You need to have individual conversations with each person first, then bring them together to discuss their issues professionally.",
                evaluation_dimension="non_directive_style",
                expected_good_score=0.85,
                expected_poor_score=0.15
            ),
            ConversationExample(
                scenario_name="career_development_choice",
                context="Individual considering career transition",
                client_opening="I'm thinking about leaving product management to go into data science, but I'm not sure it's the right move.",
                good_coach_response="What draws you toward data science? What concerns you about leaving PM? What would need to be true for this to feel like the right decision? How might you explore this further?",
                poor_coach_response="Data science is a growing field, but you have good PM experience. You should probably stay in PM and just learn some data skills on the side.",
                evaluation_dimension="non_directive_style",
                expected_good_score=0.9,
                expected_poor_score=0.1
            )
        ]
    
    def generate_all_examples(self) -> List[ConversationExample]:
        """Generate all conversation examples across all evaluation dimensions."""
        all_examples = []
        all_examples.extend(self.generate_problem_significance_examples())
        all_examples.extend(self.generate_task_concretization_examples())
        all_examples.extend(self.generate_solution_diversity_examples())
        all_examples.extend(self.generate_crux_identification_examples())
        all_examples.extend(self.generate_crux_solution_examples())
        all_examples.extend(self.generate_belief_system_examples())
        all_examples.extend(self.generate_non_directive_examples())
        return all_examples
    
    def format_for_langsmith(self, examples: List[ConversationExample]) -> List[Dict[str, Any]]:
        """Format conversation examples for LangSmith dataset upload."""
        langsmith_examples = []
        
        for example in examples:
            # Create example for good response
            good_example = {
                "inputs": {
                    "messages": [
                        {"role": "user", "content": example.client_opening}
                    ],
                    "scenario": example.scenario_name,
                    "context": example.context,
                    "evaluation_dimension": example.evaluation_dimension
                },
                "outputs": {
                    "response": example.good_coach_response
                },
                "metadata": {
                    "response_type": "good",
                    "expected_score": example.expected_good_score,
                    "evaluation_dimension": example.evaluation_dimension,
                    "scenario_name": example.scenario_name
                }
            }
            langsmith_examples.append(good_example)
            
            # Create example for poor response
            poor_example = {
                "inputs": {
                    "messages": [
                        {"role": "user", "content": example.client_opening}
                    ],
                    "scenario": example.scenario_name,
                    "context": example.context,
                    "evaluation_dimension": example.evaluation_dimension
                },
                "outputs": {
                    "response": example.poor_coach_response
                },
                "metadata": {
                    "response_type": "poor",
                    "expected_score": example.expected_poor_score,
                    "evaluation_dimension": example.evaluation_dimension,
                    "scenario_name": example.scenario_name
                }
            }
            langsmith_examples.append(poor_example)
        
        return langsmith_examples


def get_dataset_summary(examples: List[ConversationExample]) -> Dict[str, Any]:
    """Get summary statistics about the generated dataset."""
    dimensions = {}
    for example in examples:
        dim = example.evaluation_dimension
        if dim not in dimensions:
            dimensions[dim] = {"count": 0, "scenarios": []}
        dimensions[dim]["count"] += 1
        dimensions[dim]["scenarios"].append(example.scenario_name)
    
    return {
        "total_examples": len(examples),
        "total_langsmith_entries": len(examples) * 2,  # good + poor for each
        "dimensions": dimensions,
        "coverage": {
            "problem_significance": len([e for e in examples if e.evaluation_dimension == "problem_significance"]),
            "task_concretization": len([e for e in examples if e.evaluation_dimension == "task_concretization"]),
            "solution_diversity": len([e for e in examples if e.evaluation_dimension == "solution_diversity"]),
            "crux_identification": len([e for e in examples if e.evaluation_dimension == "crux_identification"]),
            "crux_solution": len([e for e in examples if e.evaluation_dimension == "crux_solution"]),
            "belief_system": len([e for e in examples if e.evaluation_dimension == "belief_system"]),
            "non_directive_style": len([e for e in examples if e.evaluation_dimension == "non_directive_style"])
        }
    }