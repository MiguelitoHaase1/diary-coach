"""Centralized JSON parsing utilities for LLM outputs."""

import json
import re
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def extract_json_from_llm_output(
    text: str,
    strict: bool = False
) -> Optional[Dict[str, Any]]:
    """Extract JSON from LLM output that may contain markdown or other formatting.
    
    Args:
        text: The LLM output text
        strict: If True, raise exception on parse failure
        
    Returns:
        Parsed JSON as dict, or None if parsing fails and not strict
        
    Raises:
        ValueError: If strict=True and parsing fails
    """
    if not text:
        if strict:
            raise ValueError("Empty text provided")
        return None
    
    # Try to clean and parse the text
    try:
        # Step 1: Check if it's already valid JSON
        text_stripped = text.strip()
        try:
            return json.loads(text_stripped)
        except json.JSONDecodeError:
            pass
        
        # Step 2: Extract from markdown code blocks
        if "```json" in text:
            json_str = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            # Try generic code block
            json_str = text.split("```")[1].split("```")[0].strip()
        else:
            json_str = text_stripped
        
        # Try parsing the extracted string
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # Step 3: Use regex to find JSON objects
        # This regex matches balanced braces
        json_pattern = r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}'
        matches = list(re.finditer(json_pattern, text, re.DOTALL))
        
        # Try each match, starting from the largest
        matches.sort(key=lambda m: len(m.group()), reverse=True)
        
        for match in matches:
            json_text = match.group()
            # Clean up control characters
            json_text = (json_text
                        .replace('\n', ' ')
                        .replace('\r', ' ')
                        .replace('\t', ' ')
                        .replace('\\n', '\\\\n')
                        .replace('\\r', '\\\\r')
                        .replace('\\t', '\\\\t'))
            
            try:
                result = json.loads(json_text)
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError:
                continue
        
        # Step 4: Try to extract key-value pairs manually
        # Look for patterns like "score": 0.5
        score_match = re.search(r'"score"\s*:\s*([0-9.]+)', text)
        reasoning_match = re.search(r'"reasoning"\s*:\s*"([^"]+)"', text)
        
        if score_match:
            result = {}
            try:
                result["score"] = float(score_match.group(1))
            except ValueError:
                pass
            
            if reasoning_match:
                result["reasoning"] = reasoning_match.group(1)
            
            if result:
                return result
        
        # If all parsing attempts fail
        if strict:
            raise ValueError(f"Could not extract JSON from text: {text[:200]}...")
        
        logger.warning(f"Failed to extract JSON from LLM output: {text[:100]}...")
        return None
        
    except Exception as e:
        if strict:
            raise ValueError(f"JSON extraction failed: {str(e)}")
        logger.error(f"Error extracting JSON: {e}")
        return None


def parse_llm_score(
    text: str,
    default_score: float = 0.0,
    default_reasoning: str = "No reasoning provided"
) -> Dict[str, Any]:
    """Parse score and reasoning from LLM evaluation output.
    
    Args:
        text: The LLM output text
        default_score: Default score if parsing fails
        default_reasoning: Default reasoning if not found
        
    Returns:
        Dict with 'score' and 'reasoning' keys
    """
    try:
        parsed = extract_json_from_llm_output(text, strict=False)
        
        if parsed and isinstance(parsed, dict):
            # Ensure score is a float
            score = parsed.get("score", default_score)
            try:
                score = float(score)
            except (ValueError, TypeError):
                score = default_score
            
            # Ensure reasoning is a string
            reasoning = parsed.get("reasoning", default_reasoning)
            if not isinstance(reasoning, str):
                reasoning = str(reasoning) if reasoning else default_reasoning
            
            return {
                "score": score,
                "reasoning": reasoning
            }
        else:
            # Fallback to regex extraction
            score = default_score
            reasoning = default_reasoning
            
            # Try to find score
            score_match = re.search(r'(?:score|Score)\s*[:\-=]\s*([0-9.]+)', text)
            if score_match:
                try:
                    score = float(score_match.group(1))
                except ValueError:
                    pass
            
            # Try to find reasoning
            reasoning_match = re.search(
                r'(?:reasoning|Reasoning|explanation|Explanation)'
                r'\s*[:\-=]\s*(.+?)(?:\n|$)',
                text,
                re.IGNORECASE | re.DOTALL
            )
            if reasoning_match:
                reasoning = reasoning_match.group(1).strip()
            
            return {
                "score": score,
                "reasoning": reasoning
            }
            
    except Exception as e:
        logger.error(f"Error parsing LLM score: {e}")
        return {
            "score": default_score,
            "reasoning": f"Parse error: {str(e)}"
        }


def validate_json_schema(
    data: Dict[str, Any],
    required_fields: list,
    field_types: Optional[Dict[str, type]] = None
) -> bool:
    """Validate that JSON data has required fields and correct types.
    
    Args:
        data: The JSON data to validate
        required_fields: List of required field names
        field_types: Optional dict mapping field names to expected types
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(data, dict):
        return False
    
    # Check required fields
    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field: {field}")
            return False
    
    # Check field types if specified
    if field_types:
        for field, expected_type in field_types.items():
            if field in data and not isinstance(data[field], expected_type):
                logger.warning(
                    f"Field {field} has wrong type: expected {expected_type}, "
                    f"got {type(data[field])}"
                )
                return False
    
    return True
