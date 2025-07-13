"""Extract evaluation scores from Deep Thoughts reports."""

import re
from typing import Dict, Optional
import json


class DeepThoughtsScoreExtractor:
    """Extracts evaluation scores from Deep Thoughts reports."""
    
    def __init__(self):
        """Initialize the score extractor."""
        # Define the evaluation criteria we're looking for
        self.criteria = {
            "problem_definition": {
                "keywords": ["problem", "define", "biggest", "important", "matters"],
                "description": "Define biggest problem to solve - and understand why it matters"
            },
            "crux_recognition": {
                "keywords": ["crux", "constraint", "bottleneck", "key", "leverage"],
                "description": "Recognize the key constraint to address"
            },
            "today_accomplishment": {
                "keywords": ["today", "specific", "concrete", "accomplish", "action"],
                "description": "Define exactly what to accomplish today"
            },
            "multiple_paths": {
                "keywords": ["paths", "approaches", "options", "different", "multiple"],
                "description": "Define multiple viable paths forward"
            },
            "core_beliefs": {
                "keywords": ["beliefs", "values", "principles", "tenets", "underlying"],
                "description": "Identify core beliefs/tenets to focus on"
            }
        }
    
    def extract_scores(self, deep_thoughts_report: str) -> Dict[str, float]:
        """Extract evaluation scores from a Deep Thoughts report.
        
        Args:
            deep_thoughts_report: The full Deep Thoughts report text
            
        Returns:
            Dictionary mapping criterion names to scores (0.0-1.0)
        """
        scores = {}
        
        # Try to find explicit scores in the report
        score_section = self._find_score_section(deep_thoughts_report)
        if score_section:
            explicit_scores = self._parse_explicit_scores(score_section)
            if explicit_scores:
                return explicit_scores
        
        # Otherwise, analyze the report content
        report_lower = deep_thoughts_report.lower()
        
        # Check for each criterion
        for criterion_key, criterion_info in self.criteria.items():
            score = self._analyze_criterion(report_lower, criterion_info)
            scores[criterion_key] = score
        
        return scores
    
    def _find_score_section(self, report: str) -> Optional[str]:
        """Find a section with explicit scores if it exists."""
        # Look for sections like "Evaluation", "Scores", "Assessment"
        patterns = [
            r'#{1,3}\s*(?:evaluation|scores|assessment|rating).*?(?=#{1,3}|\Z)',
            r'(?:evaluation|scores|assessment|rating):\s*\n(.*?)(?=\n\n|\Z)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, report, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(0)
        
        return None
    
    def _parse_explicit_scores(self, score_section: str) -> Optional[Dict[str, float]]:
        """Parse explicit scores from a score section."""
        scores = {}
        
        # Look for patterns like "Problem Definition: 8/10" or "Crux: 0.8"
        score_patterns = [
            r'(problem\s*definition|biggest\s*problem)[:\s]+(\d+(?:\.\d+)?)\s*/?\s*(?:10)?',
            r'(crux|constraint)[:\s]+(\d+(?:\.\d+)?)\s*/?\s*(?:10)?',
            r'(today|action|accomplish)[:\s]+(\d+(?:\.\d+)?)\s*/?\s*(?:10)?',
            r'(paths?|approaches?|options?)[:\s]+(\d+(?:\.\d+)?)\s*/?\s*(?:10)?',
            r'(beliefs?|values?|principles?)[:\s]+(\d+(?:\.\d+)?)\s*/?\s*(?:10)?'
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, score_section, re.IGNORECASE)
            if match:
                key = self._map_to_criterion_key(match.group(1))
                score_value = float(match.group(2))
                # Normalize to 0-1 if score is out of 10
                if score_value > 1:
                    score_value = score_value / 10.0
                if key:
                    scores[key] = score_value
        
        return scores if scores else None
    
    def _map_to_criterion_key(self, text: str) -> Optional[str]:
        """Map extracted text to a criterion key."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["problem", "biggest"]):
            return "problem_definition"
        elif any(word in text_lower for word in ["crux", "constraint"]):
            return "crux_recognition"
        elif any(word in text_lower for word in ["today", "action", "accomplish"]):
            return "today_accomplishment"
        elif any(word in text_lower for word in ["path", "approach", "option"]):
            return "multiple_paths"
        elif any(word in text_lower for word in ["belief", "value", "principle"]):
            return "core_beliefs"
        
        return None
    
    def _analyze_criterion(self, report_lower: str, criterion_info: Dict) -> float:
        """Analyze report content for a specific criterion."""
        keywords = criterion_info["keywords"]
        
        # Count keyword occurrences and context
        keyword_count = 0
        strong_indicators = 0
        weak_indicators = 0
        
        for keyword in keywords:
            count = report_lower.count(keyword)
            keyword_count += count
            
            # Check for strong positive indicators
            if self._check_positive_context(report_lower, keyword):
                strong_indicators += 1
            
            # Check for negative indicators
            if self._check_negative_context(report_lower, keyword):
                weak_indicators += 1
        
        # Calculate score based on indicators
        if strong_indicators >= 2:
            return 1.0
        elif strong_indicators >= 1 and weak_indicators == 0:
            return 0.8
        elif keyword_count >= 3 and weak_indicators == 0:
            return 0.6
        elif keyword_count >= 1:
            return 0.4
        else:
            return 0.2
    
    def _check_positive_context(self, text: str, keyword: str) -> bool:
        """Check if keyword appears in positive context."""
        positive_patterns = [
            f"successfully.*{keyword}",
            f"effectively.*{keyword}",
            f"clear.*{keyword}",
            f"strong.*{keyword}",
            f"excellent.*{keyword}",
            f"{keyword}.*identified",
            f"{keyword}.*achieved",
            f"{keyword}.*addressed"
        ]
        
        for pattern in positive_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def _check_negative_context(self, text: str, keyword: str) -> bool:
        """Check if keyword appears in negative context."""
        negative_patterns = [
            f"failed.*{keyword}",
            f"missed.*{keyword}",
            f"lack.*{keyword}",
            f"no.*{keyword}",
            f"didn't.*{keyword}",
            f"{keyword}.*unclear",
            f"{keyword}.*vague"
        ]
        
        for pattern in negative_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def format_scores_for_langsmith(self, scores: Dict[str, float]) -> Dict[str, Dict]:
        """Format scores for LangSmith evaluation format.
        
        Args:
            scores: Dictionary of criterion scores
            
        Returns:
            Dictionary formatted for LangSmith with score and reasoning
        """
        formatted = {}
        
        for criterion, score in scores.items():
            formatted[criterion] = {
                "score": score,
                "reasoning": f"Extracted from Deep Thoughts analysis (score: {score:.2f})"
            }
        
        # Add average score
        if scores:
            avg_score = sum(scores.values()) / len(scores)
            formatted["average_score"] = {
                "score": avg_score,
                "reasoning": f"Average of {len(scores)} criteria"
            }
        
        return formatted