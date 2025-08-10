"""
Cost optimization and tracking for LLM API usage
"""
import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


@dataclass
class CostConfig:
    """Configuration for cost tracking and optimization"""
    # Pricing per 1K tokens (as of 2024)
    opus_cost_per_1k_input: float = 0.015  # $15 per million
    opus_cost_per_1k_output: float = 0.075  # $75 per million
    sonnet_cost_per_1k_input: float = 0.003  # $3 per million
    sonnet_cost_per_1k_output: float = 0.015  # $15 per million
    haiku_cost_per_1k_input: float = 0.00025  # $0.25 per million
    haiku_cost_per_1k_output: float = 0.00125  # $1.25 per million
    
    # Budget limits
    daily_budget_usd: float = 10.0
    per_user_budget_usd: float = 1.0
    
    # Quality thresholds
    quality_threshold: float = 0.8  # Min quality score for model selection
    
    # Alert thresholds
    budget_warning_threshold: float = 0.8  # Warn at 80% of budget
    budget_critical_threshold: float = 0.95  # Critical at 95% of budget


@dataclass
class LLMCall:
    """Represents a single LLM API call"""
    timestamp: datetime
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    agent: str
    conversation_id: str
    user_id: Optional[str] = None


@dataclass
class ConversationCost:
    """Cost tracking for a conversation"""
    conversation_id: str
    user_id: Optional[str]
    start_time: datetime
    calls: List[LLMCall] = field(default_factory=list)
    
    @property
    def total_cost(self) -> float:
        """Calculate total cost"""
        return sum(call.cost for call in self.calls)
    
    @property
    def total_input_tokens(self) -> int:
        """Total input tokens used"""
        return sum(call.input_tokens for call in self.calls)
    
    @property
    def total_output_tokens(self) -> int:
        """Total output tokens generated"""
        return sum(call.output_tokens for call in self.calls)
    
    @property
    def call_count(self) -> int:
        """Number of LLM calls"""
        return len(self.calls)
    
    @property
    def agent_costs(self) -> Dict[str, float]:
        """Cost breakdown by agent"""
        costs = defaultdict(float)
        for call in self.calls:
            costs[call.agent] += call.cost
        return dict(costs)
    
    @property
    def model_distribution(self) -> Dict[str, int]:
        """Count of calls by model"""
        distribution = defaultdict(int)
        for call in self.calls:
            distribution[call.model] += 1
        return dict(distribution)


@dataclass
class UserCost:
    """Cost tracking for a user"""
    user_id: str
    conversations: List[ConversationCost] = field(default_factory=list)
    
    @property
    def total_cost(self) -> float:
        """Total cost for user"""
        return sum(conv.total_cost for conv in self.conversations)
    
    @property
    def conversation_count(self) -> int:
        """Number of conversations"""
        return len(self.conversations)
    
    @property
    def average_cost_per_conversation(self) -> float:
        """Average cost per conversation"""
        if self.conversation_count == 0:
            return 0.0
        return self.total_cost / self.conversation_count


@dataclass
class DailyCost:
    """Daily cost aggregation"""
    date: datetime
    conversations: List[ConversationCost] = field(default_factory=list)
    
    @property
    def total_cost(self) -> float:
        """Total cost for the day"""
        return sum(conv.total_cost for conv in self.conversations)
    
    @property
    def conversation_count(self) -> int:
        """Number of conversations"""
        return len(self.conversations)
    
    @property
    def hourly_costs(self) -> Dict[int, float]:
        """Cost breakdown by hour"""
        costs = defaultdict(float)
        for conv in self.conversations:
            hour = conv.start_time.hour
            costs[hour] += conv.total_cost
        return dict(costs)


@dataclass
class ModelChoice:
    """Model selection decision"""
    model: str
    reasoning: str
    estimated_cost: float
    quality_score: float
    override_budget: bool = False


@dataclass
class ResponseGuidance:
    """Guidance for response generation"""
    max_tokens: int
    style: str  # "concise", "balanced", "detailed"
    include_examples: bool
    structured_output: bool


class CostTracker:
    """Tracks costs across conversations"""
    
    def __init__(self, config: CostConfig):
        self.config = config
        self.conversations: Dict[str, ConversationCost] = {}
        self.user_costs: Dict[str, List[str]] = defaultdict(list)  # user_id -> conversation_ids
        
    def start_conversation(self, conversation_id: str, user_id: Optional[str] = None):
        """Start tracking a new conversation"""
        self.conversations[conversation_id] = ConversationCost(
            conversation_id=conversation_id,
            user_id=user_id,
            start_time=datetime.now()
        )
        
        if user_id:
            self.user_costs[user_id].append(conversation_id)
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a single LLM call"""
        
        # Get rates based on model
        if "opus" in model.lower():
            input_rate = self.config.opus_cost_per_1k_input
            output_rate = self.config.opus_cost_per_1k_output
        elif "sonnet" in model.lower():
            input_rate = self.config.sonnet_cost_per_1k_input
            output_rate = self.config.sonnet_cost_per_1k_output
        elif "haiku" in model.lower():
            input_rate = self.config.haiku_cost_per_1k_input
            output_rate = self.config.haiku_cost_per_1k_output
        else:
            # Default to Sonnet pricing for unknown models
            input_rate = self.config.sonnet_cost_per_1k_input
            output_rate = self.config.sonnet_cost_per_1k_output
        
        # Calculate cost
        input_cost = (input_tokens / 1000) * input_rate
        output_cost = (output_tokens / 1000) * output_rate
        
        return input_cost + output_cost
    
    def add_call(
        self,
        conversation_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        agent: str
    ):
        """Add an LLM call to tracking"""
        
        if conversation_id not in self.conversations:
            logger.warning(f"Conversation {conversation_id} not started, starting now")
            self.start_conversation(conversation_id)
        
        cost = self.calculate_cost(model, input_tokens, output_tokens)
        
        call = LLMCall(
            timestamp=datetime.now(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            agent=agent,
            conversation_id=conversation_id,
            user_id=self.conversations[conversation_id].user_id
        )
        
        self.conversations[conversation_id].calls.append(call)
        
        logger.debug(
            f"Added call: {model} ({input_tokens}+{output_tokens} tokens) "
            f"= ${cost:.4f} for {agent}"
        )
    
    def get_conversation_cost(self, conversation_id: str) -> Optional[ConversationCost]:
        """Get cost for a specific conversation"""
        return self.conversations.get(conversation_id)
    
    def get_user_cost(self, user_id: str, period_hours: int = 24) -> UserCost:
        """Get cost for a user over a time period"""
        
        cutoff = datetime.now() - timedelta(hours=period_hours)
        user_cost = UserCost(user_id=user_id)
        
        for conv_id in self.user_costs.get(user_id, []):
            conv = self.conversations.get(conv_id)
            if conv and conv.start_time >= cutoff:
                user_cost.conversations.append(conv)
        
        return user_cost
    
    def get_daily_cost(self, date: Optional[datetime] = None) -> DailyCost:
        """Get cost for a specific day"""
        
        if date is None:
            date = datetime.now()
        
        # Get start and end of day
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        
        daily_cost = DailyCost(date=date)
        
        for conv in self.conversations.values():
            if start <= conv.start_time < end:
                daily_cost.conversations.append(conv)
        
        return daily_cost


class ModelSelector:
    """Selects optimal model based on query and context"""
    
    def __init__(self, config: CostConfig):
        self.config = config
        
        # Complexity indicators
        self.SIMPLE_PATTERNS = [
            r'^(hi|hello|hey|good morning|thank)',
            r'^(ok|okay|sure|got it|yes|no)$',
            r'^what time',
            r'^what day',
            r'^\w{1,3}$'  # Very short responses
        ]
        
        self.COMPLEX_PATTERNS = [
            r'help me understand',
            r'struggling with',
            r'feeling (overwhelmed|anxious|depressed)',
            r'deep (dive|reflection|analysis)',
            r'comprehensive',
            r'analyze',
            r'pattern'
        ]
        
        self.CRITICAL_PATTERNS = [
            r'suicidal',
            r'crisis',
            r'emergency',
            r'self-harm',
            r'danger'
        ]
    
    def select_model(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ModelChoice:
        """Select the optimal model for a query"""
        
        context = context or {}
        query_lower = query.lower()
        
        # Check for critical queries - always use best model
        if self._is_critical(query_lower):
            return ModelChoice(
                model="claude-3-opus",
                reasoning="Critical query requiring highest quality response",
                estimated_cost=self._estimate_cost("claude-3-opus", query),
                quality_score=1.0,
                override_budget=True
            )
        
        # Deep reflection mode overrides everything except critical
        if context.get("mode") == "deep_reflection":
            return ModelChoice(
                model="claude-3-opus",
                reasoning="Deep reflection context requires highest quality",
                estimated_cost=self._estimate_cost("claude-3-opus", query),
                quality_score=1.0
            )
        
        # Check budget constraints early
        budget_remaining = context.get("budget_remaining", float('inf'))
        daily_budget = context.get("daily_budget", self.config.daily_budget_usd)
        
        if budget_remaining / daily_budget < 0.02:  # Less than 2% budget
            # Unless it's critical, use the cheapest model
            return ModelChoice(
                model="claude-3-haiku",
                reasoning="Near budget limit - using most cost-effective model",
                estimated_cost=self._estimate_cost("claude-3-haiku", query),
                quality_score=0.7
            )
        
        # Morning protocol - use Sonnet
        if context.get("protocol") == "morning_routine":
            return ModelChoice(
                model="claude-3-sonnet",
                reasoning="Morning protocol - balanced model sufficient",
                estimated_cost=self._estimate_cost("claude-3-sonnet", query),
                quality_score=0.85
            )
        
        # Check context complexity
        complexity = context.get("complexity", self._assess_complexity(query_lower))
        
        # Simple queries - use Haiku or Sonnet
        if complexity == "simple":
            # Very simple - use Haiku
            if len(query.split()) <= 5:
                return ModelChoice(
                    model="claude-3-haiku",
                    reasoning="Simple query - using efficient model",
                    estimated_cost=self._estimate_cost("claude-3-haiku", query),
                    quality_score=0.7
                )
            else:
                return ModelChoice(
                    model="claude-3-sonnet",
                    reasoning="Simple query - using efficient model",
                    estimated_cost=self._estimate_cost("claude-3-sonnet", query),
                    quality_score=0.85
                )
        
        # Complex queries
        if complexity == "complex":
            # Check budget constraints for complex queries
            if budget_remaining / daily_budget < 0.1:  # Less than 10% budget
                return ModelChoice(
                    model="claude-3-sonnet",
                    reasoning="Complex query but budget constraints apply",
                    estimated_cost=self._estimate_cost("claude-3-sonnet", query),
                    quality_score=0.85
                )
            
            return ModelChoice(
                model="claude-3-opus",
                reasoning="Complex query requiring advanced reasoning",
                estimated_cost=self._estimate_cost("claude-3-opus", query),
                quality_score=1.0
            )
        
        # Medium complexity - use Sonnet
        return ModelChoice(
            model="claude-3-sonnet",
            reasoning="Standard query - balanced model optimal",
            estimated_cost=self._estimate_cost("claude-3-sonnet", query),
            quality_score=0.85
        )
    
    def _is_critical(self, query: str) -> bool:
        """Check if query is critical/safety-related"""
        return any(re.search(pattern, query) for pattern in self.CRITICAL_PATTERNS)
    
    def _assess_complexity(self, query: str) -> str:
        """Assess query complexity"""
        
        # Check for simple patterns
        if any(re.match(pattern, query) for pattern in self.SIMPLE_PATTERNS):
            return "simple"
        
        # Check for complex patterns
        if any(re.search(pattern, query) for pattern in self.COMPLEX_PATTERNS):
            return "complex"
        
        # Check length
        word_count = len(query.split())
        if word_count <= 10:
            return "simple"
        elif word_count >= 50:
            return "complex"
        
        return "medium"
    
    def _estimate_cost(self, model: str, query: str) -> float:
        """Estimate cost for a query with model"""
        
        # Rough token estimation
        input_tokens = len(query.split()) * 2  # Approximate
        output_tokens = 200 if "haiku" in model else 500  # Approximate
        
        tracker = CostTracker(self.config)
        return tracker.calculate_cost(model, input_tokens, output_tokens)


class TokenOptimizer:
    """Optimizes token usage in prompts and responses"""
    
    def __init__(self):
        self.redundancy_patterns = [
            (r'\b(\w+)\s+\1\b', r'\1'),  # Duplicate words
            (r'\s+', ' '),  # Multiple spaces
            (r'^\s+|\s+$', ''),  # Leading/trailing spaces
        ]
    
    def compress_prompt(self, prompt: str) -> str:
        """Compress prompt while maintaining meaning"""
        
        compressed = prompt
        
        # Remove redundant whitespace
        compressed = re.sub(r'\s+', ' ', compressed).strip()
        
        # Remove filler phrases
        filler_phrases = [
            "Please ",
            "I would like you to ",
            "Can you please ",
            "Would you mind ",
            "If possible, ",
            "When you get a chance, "
        ]
        
        for phrase in filler_phrases:
            compressed = compressed.replace(phrase, "")
        
        # Simplify verbose instructions
        replacements = {
            "provide helpful, accurate, and detailed responses": "provide accurate responses",
            "at all times": "",
            "Make sure to be": "Be",
            "Please make sure": "Ensure",
            "in order to": "to",
            "for the purpose of": "to"
        }
        
        for verbose, simple in replacements.items():
            compressed = compressed.replace(verbose, simple)
        
        # Remove duplicate instructions
        sentences = compressed.split('. ')
        unique_sentences = []
        seen_concepts = set()
        
        for sentence in sentences:
            # Extract key concept (first few meaningful words)
            words = sentence.lower().split()
            if len(words) >= 2:
                concept = ' '.join(words[:3])
                if concept not in seen_concepts:
                    unique_sentences.append(sentence)
                    seen_concepts.add(concept)
        
        compressed = '. '.join(unique_sentences)
        
        # Ensure we didn't over-compress
        if len(compressed) < len(prompt) * 0.3:  # Lost more than 70%
            logger.warning("Aggressive compression detected, using original")
            return prompt
        
        return compressed
    
    def prune_context(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        preserve_recent: int = 2
    ) -> List[Dict[str, str]]:
        """Prune conversation context to fit token limit"""
        
        if len(messages) <= preserve_recent:
            return messages
        
        # Always keep the most recent messages
        recent = messages[-preserve_recent:]
        older = messages[:-preserve_recent]
        
        # Estimate tokens (rough approximation)
        def estimate_tokens(msgs):
            return sum(len(m.get("content", "").split()) * 1.5 for m in msgs)
        
        current_tokens = estimate_tokens(recent)
        pruned = []
        
        # Add older messages if they fit
        for msg in reversed(older):
            msg_tokens = estimate_tokens([msg])
            if current_tokens + msg_tokens <= max_tokens:
                pruned.insert(0, msg)
                current_tokens += msg_tokens
            else:
                # Try to add a summary instead
                if msg["role"] == "user" and current_tokens + 10 <= max_tokens:
                    summary = {"role": "user", "content": "[Earlier context omitted]"}
                    pruned.insert(0, summary)
                    break
        
        return pruned + recent
    
    def get_response_guidance(self, query: str) -> ResponseGuidance:
        """Get guidance for response generation"""
        
        query_lower = query.lower()
        word_count = len(query.split())
        
        # Very short queries get concise responses
        if word_count <= 5 or any(pattern in query_lower for pattern in ["time", "thank", "ok"]):
            return ResponseGuidance(
                max_tokens=100,
                style="concise",
                include_examples=False,
                structured_output=False
            )
        
        # Complex queries get detailed responses
        if any(pattern in query_lower for pattern in ["explain", "understand", "analyze", "help me"]):
            return ResponseGuidance(
                max_tokens=800,
                style="detailed",
                include_examples=True,
                structured_output=True
            )
        
        # Default balanced response
        return ResponseGuidance(
            max_tokens=400,
            style="balanced",
            include_examples=False,
            structured_output=False
        )
    
    def optimize_template(self, template: str) -> str:
        """Optimize a prompt template"""
        
        lines = template.split('\n')
        optimized_lines = []
        seen_instructions = set()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remove duplicate instructions
            instruction_key = re.sub(r'[^a-z\s]', '', line.lower())[:20]
            if instruction_key and instruction_key in seen_instructions:
                continue
            seen_instructions.add(instruction_key)
            
            # Simplify bullet points
            if line.startswith('- '):
                line = line[2:]
            
            optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)


class CostDashboard:
    """Dashboard for cost visualization and reporting"""
    
    def __init__(self, tracker: CostTracker):
        self.tracker = tracker
    
    def get_metrics(self, period_hours: int = 24) -> Dict[str, Any]:
        """Get dashboard metrics for period"""
        
        cutoff = datetime.now() - timedelta(hours=period_hours)
        
        # Filter conversations in period
        recent_conversations = [
            conv for conv in self.tracker.conversations.values()
            if conv.start_time >= cutoff
        ]
        
        if not recent_conversations:
            return {
                "total_cost": 0,
                "conversation_count": 0,
                "average_cost_per_conversation": 0,
                "model_distribution": {},
                "agent_distribution": {},
                "top_users": []
            }
        
        # Calculate metrics
        total_cost = sum(conv.total_cost for conv in recent_conversations)
        
        # Model distribution
        model_dist = defaultdict(int)
        for conv in recent_conversations:
            for model, count in conv.model_distribution.items():
                model_dist[model] += count
        
        # Agent distribution
        agent_costs = defaultdict(float)
        for conv in recent_conversations:
            for agent, cost in conv.agent_costs.items():
                agent_costs[agent] += cost
        
        # Top users by cost
        user_costs = defaultdict(float)
        for conv in recent_conversations:
            if conv.user_id:
                user_costs[conv.user_id] += conv.total_cost
        
        top_users = sorted(
            user_costs.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "total_cost": total_cost,
            "conversation_count": len(recent_conversations),
            "average_cost_per_conversation": total_cost / len(recent_conversations),
            "model_distribution": dict(model_dist),
            "agent_distribution": dict(agent_costs),
            "top_users": [
                {"user_id": user, "cost": cost}
                for user, cost in top_users
            ]
        }
    
    def get_cost_trends(self, days: int = 7) -> Dict[str, Any]:
        """Get cost trends over time"""
        
        daily_costs = []
        trend_data = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i-1)
            daily = self.tracker.get_daily_cost(date)
            daily_costs.append(daily.total_cost)
            trend_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "cost": daily.total_cost,
                "conversations": daily.conversation_count
            })
        
        # Calculate trend
        if len(daily_costs) >= 2:
            if daily_costs[-1] > daily_costs[-2] * 1.1:
                trend = "increasing"
            elif daily_costs[-1] < daily_costs[-2] * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Simple projection
        if len(daily_costs) >= 3:
            recent_avg = sum(daily_costs[-3:]) / 3
            projection = recent_avg * 1.1  # Conservative projection
        else:
            projection = daily_costs[-1] if daily_costs else 0
        
        return {
            "daily_costs": daily_costs,
            "trend": trend,
            "projection_next_day": projection,
            "detailed_data": trend_data
        }
    
    def get_agent_breakdown(self, period_hours: int = 24) -> Dict[str, Dict[str, Any]]:
        """Get cost breakdown by agent"""
        
        cutoff = datetime.now() - timedelta(hours=period_hours)
        
        agent_stats = defaultdict(lambda: {
            "total_cost": 0,
            "call_count": 0,
            "avg_input_tokens": 0,
            "avg_output_tokens": 0,
            "models_used": defaultdict(int)
        })
        
        for conv in self.tracker.conversations.values():
            if conv.start_time >= cutoff:
                for call in conv.calls:
                    stats = agent_stats[call.agent]
                    stats["total_cost"] += call.cost
                    stats["call_count"] += 1
                    stats["avg_input_tokens"] += call.input_tokens
                    stats["avg_output_tokens"] += call.output_tokens
                    stats["models_used"][call.model] += 1
        
        # Calculate averages
        for agent, stats in agent_stats.items():
            if stats["call_count"] > 0:
                stats["avg_input_tokens"] //= stats["call_count"]
                stats["avg_output_tokens"] //= stats["call_count"]
                stats["models_used"] = dict(stats["models_used"])
        
        return dict(agent_stats)
    
    def generate_report(self, period_hours: int = 24) -> str:
        """Generate text report"""
        
        metrics = self.get_metrics(period_hours)
        trends = self.get_cost_trends(days=7)
        agent_breakdown = self.get_agent_breakdown(period_hours)
        
        report = f"""
Cost Optimization Report
========================
Period: Last {period_hours} hours

Summary
-------
Total Cost: ${metrics['total_cost']:.2f}
Conversations: {metrics['conversation_count']}
Avg Cost/Conv: ${metrics['average_cost_per_conversation']:.2f}

Model Usage
-----------
"""
        for model, count in metrics['model_distribution'].items():
            report += f"  {model}: {count} calls\n"
        
        report += "\nAgent Costs\n-----------\n"
        for agent, cost in sorted(metrics['agent_distribution'].items(), key=lambda x: x[1], reverse=True):
            report += f"  {agent}: ${cost:.2f}\n"
        
        report += f"\n7-Day Trend: {trends['trend']}\n"
        report += f"Projected Tomorrow: ${trends['projection_next_day']:.2f}\n"
        
        if metrics['top_users']:
            report += "\nTop Users by Cost\n-----------------\n"
            for user_data in metrics['top_users'][:5]:
                report += f"  {user_data['user_id']}: ${user_data['cost']:.2f}\n"
        
        return report


class BudgetManager:
    """Manages budget alerts and enforcement"""
    
    def __init__(self, config: CostConfig, tracker: CostTracker):
        self.config = config
        self.tracker = tracker
        self._alerts: List[Dict[str, Any]] = []
    
    def is_within_daily_budget(self) -> bool:
        """Check if within daily budget"""
        daily = self.tracker.get_daily_cost()
        return daily.total_cost < self.config.daily_budget_usd
    
    def is_user_within_budget(self, user_id: str) -> bool:
        """Check if user is within their budget"""
        user_cost = self.tracker.get_user_cost(user_id, period_hours=24)
        return user_cost.total_cost < self.config.per_user_budget_usd
    
    def get_user_budget_remaining(self, user_id: str) -> float:
        """Get remaining budget for user"""
        user_cost = self.tracker.get_user_cost(user_id, period_hours=24)
        return max(0, self.config.per_user_budget_usd - user_cost.total_cost)
    
    def get_daily_budget_remaining(self) -> float:
        """Get remaining daily budget"""
        daily = self.tracker.get_daily_cost()
        return max(0, self.config.daily_budget_usd - daily.total_cost)
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get current budget alerts"""
        
        alerts = []
        daily = self.tracker.get_daily_cost()
        daily_percentage = daily.total_cost / self.config.daily_budget_usd
        
        # Check daily budget thresholds
        if daily_percentage >= self.config.budget_critical_threshold:
            alerts.append({
                "level": "critical",
                "type": "daily_budget",
                "message": f"Daily budget critical: {daily_percentage*100:.0f}% used",
                "remaining": self.get_daily_budget_remaining()
            })
        elif daily_percentage >= self.config.budget_warning_threshold:
            alerts.append({
                "level": "warning",
                "type": "daily_budget",
                "message": f"Daily budget warning: {daily_percentage*100:.0f}% used",
                "remaining": self.get_daily_budget_remaining()
            })
        elif daily_percentage >= 0.5:
            alerts.append({
                "level": "info",
                "type": "daily_budget",
                "message": f"Daily budget: {daily_percentage*100:.0f}% used",
                "remaining": self.get_daily_budget_remaining()
            })
        
        # Check high-cost users
        for user_id, conv_ids in self.tracker.user_costs.items():
            user_cost = self.tracker.get_user_cost(user_id, period_hours=24)
            user_percentage = user_cost.total_cost / self.config.per_user_budget_usd
            
            if user_percentage >= 0.9:
                alerts.append({
                    "level": "warning",
                    "type": "user_budget",
                    "message": f"User {user_id} near budget limit",
                    "user_id": user_id,
                    "remaining": self.get_user_budget_remaining(user_id)
                })
        
        return alerts
    
    def should_throttle(self, user_id: Optional[str] = None) -> bool:
        """Check if should throttle due to budget"""
        
        # Check daily budget
        if not self.is_within_daily_budget():
            return True
        
        # Check user budget
        if user_id and not self.is_user_within_budget(user_id):
            return True
        
        # Check if approaching limits
        daily_remaining = self.get_daily_budget_remaining()
        if daily_remaining < self.config.daily_budget_usd * 0.05:  # Less than 5%
            return True
        
        return False
    
    def reset_daily_budgets(self):
        """Reset daily budget tracking (called at midnight)"""
        # In production, this would clear or archive old data
        # For now, just log
        logger.info("Daily budget reset triggered")


# Singleton instances
_cost_tracker: Optional[CostTracker] = None
_model_selector: Optional[ModelSelector] = None
_token_optimizer: Optional[TokenOptimizer] = None
_budget_manager: Optional[BudgetManager] = None


def get_cost_tracker(config: Optional[CostConfig] = None) -> CostTracker:
    """Get global cost tracker instance"""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker(config or CostConfig())
    return _cost_tracker


def get_model_selector(config: Optional[CostConfig] = None) -> ModelSelector:
    """Get global model selector instance"""
    global _model_selector
    if _model_selector is None:
        _model_selector = ModelSelector(config or CostConfig())
    return _model_selector


def get_token_optimizer() -> TokenOptimizer:
    """Get global token optimizer instance"""
    global _token_optimizer
    if _token_optimizer is None:
        _token_optimizer = TokenOptimizer()
    return _token_optimizer


def get_budget_manager(config: Optional[CostConfig] = None) -> BudgetManager:
    """Get global budget manager instance"""
    global _budget_manager
    if _budget_manager is None:
        tracker = get_cost_tracker(config)
        _budget_manager = BudgetManager(config or CostConfig(), tracker)
    return _budget_manager