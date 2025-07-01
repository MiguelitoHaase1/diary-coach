"""Deep Thoughts Generator for transformative coaching insights."""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.services.llm_service import AnthropicService


class DeepThoughtsGenerator:
    """Generates Deep Thoughts reports using Opus for breakthrough insights."""
    
    def __init__(self, llm_service: Optional[AnthropicService] = None):
        """Initialize the Deep Thoughts Generator.
        
        Args:
            llm_service: Optional LLM service. If not provided, creates Opus service.
        """
        if llm_service:
            self.llm_service = llm_service
        else:
            self.llm_service = AnthropicService(model="claude-3-opus-20240229")
    
    def _get_output_path(self, timestamp: Optional[datetime] = None) -> Path:
        """Get the output file path for Deep Thoughts report.
        
        Args:
            timestamp: Optional timestamp. If not provided, uses current time.
            
        Returns:
            Path object for the output file
        """
        if not timestamp:
            timestamp = datetime.now()
            
        # Format: DeepThoughts_YYYYMMDD_HHMM.md (no seconds)
        filename = f"DeepThoughts_{timestamp.strftime('%Y%m%d_%H%M')}.md"
        
        # Output to docs/prototype/DeepThoughts/
        output_dir = Path("docs/prototype/DeepThoughts")
        return output_dir / filename
    
    async def generate_deep_thoughts(
        self,
        conversation_history: List[Dict[str, str]],
        conversation_id: str,
        timestamp: Optional[datetime] = None
    ) -> str:
        """Generate Deep Thoughts report and save to file.
        
        Args:
            conversation_history: List of conversation messages
            conversation_id: Unique identifier for the conversation
            timestamp: Optional timestamp for file naming
            
        Returns:
            Deep Thoughts report content
        """
        # Build conversation summary for analysis
        conversation_text = self._format_conversation_for_analysis(conversation_history)
        
        # Generate Deep Thoughts using Opus
        deep_thoughts_content = await self._generate_analysis(conversation_text, conversation_id)
        
        # Get output file path
        output_path = self._get_output_path(timestamp)
        
        # Create directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(deep_thoughts_content)
        
        return deep_thoughts_content
    
    def get_output_filepath(self, timestamp: Optional[datetime] = None) -> str:
        """Get the output file path as string for external use.
        
        Args:
            timestamp: Optional timestamp for file naming
            
        Returns:
            File path as string
        """
        return str(self._get_output_path(timestamp))
    
    def _format_conversation_for_analysis(self, conversation_history: List[Dict[str, str]]) -> str:
        """Format conversation history for analysis.
        
        Args:
            conversation_history: List of conversation messages
            
        Returns:
            Formatted conversation text
        """
        formatted_lines = []
        for msg in conversation_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            if role == "user":
                formatted_lines.append(f"Michael: {content}")
            elif role == "assistant":
                formatted_lines.append(f"Coach: {content}")
        
        return "\n\n".join(formatted_lines)
    
    async def _generate_analysis(self, conversation_text: str, conversation_id: str) -> str:
        """Generate Deep Thoughts analysis using Opus model.
        
        Args:
            conversation_text: Formatted conversation for analysis
            conversation_id: Unique identifier for the conversation
            
        Returns:
            Deep Thoughts report content
        """
        # Structured prompt for consistent Deep Thoughts format
        analysis_prompt = f"""You are an expert executive coach analyzing a coaching conversation with Michael. Generate a "Deep Thoughts" report that transforms this conversation into breakthrough insights he'll want to revisit throughout his day.

CONVERSATION TO ANALYZE:
{conversation_text}

Generate a Deep Thoughts report with exactly these sections:

# Deep Thoughts: [Brief Title Describing the Core Challenge]

## Core Problem
Crystallize the core problem in 2-3 clear sentences. Focus on what Michael is really grappling with, not just what he said explicitly. What's the deeper challenge or opportunity?

## Fact Check
List key claims and assumptions from the conversation:
✅ [Verified facts or reasonable assumptions]
❓ [Questionable claims that need verification]
❌ [Likely incorrect assumptions]

Use checkmarks, question marks, and X marks to indicate confidence levels.

## Just One More Thing... (Devil's Advocate)
Channel Columbo's "just one more thing" style. Gently challenge a key assumption or perspective from the conversation. Be insightful but supportive - like a wise friend who sees a blind spot. Start with "I hear [restate his position], but just one more thing puzzles me..."

## Hints (Without Giving Away the Answer)
Provide 2-3 Socratic hints that guide Michael toward insights without solving the problem for him. Use questions, thought experiments, or gentle suggestions. Focus on helping him think differently, not telling him what to do.

GUIDELINES:
- Write as if speaking to Michael directly
- Be concise but insightful (scannable in under 2 minutes)
- Make it feel like a conversation with a brilliant mentor
- Challenge assumptions while remaining supportive
- Focus on breakthrough thinking, not just problem-solving
- Ensure each section adds unique value

Generate the Deep Thoughts report now:"""

        try:
            # Generate analysis using Opus model with focused parameters
            analysis_content = await self.llm_service.generate_response(
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=1500,  # Allow longer responses for thorough analysis
                temperature=0.2   # Lower temperature for more focused, analytical content
            )
            
            return analysis_content
            
        except Exception as e:
            # Fallback content if generation fails
            fallback_content = f"""# Deep Thoughts: Analysis Failed

## Core Problem
Unable to generate Deep Thoughts analysis due to technical error: {str(e)}

## Fact Check
❌ Deep Thoughts generation failed

## Just One More Thing...
The system needs debugging to provide the intended insights.

## Hints
Try running the analysis again, or check the system logs for more details.

---
*Conversation ID: {conversation_id}*
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"""
            
            return fallback_content