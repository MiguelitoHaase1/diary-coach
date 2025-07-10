"""Deep Thoughts Generator for transformative coaching insights."""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.services.llm_service import AnthropicService
from src.services.llm_factory import LLMFactory, LLMTier
from src.agents.prompts import get_deep_thoughts_system_prompt


class DeepThoughtsGenerator:
    """Generates Deep Thoughts reports with configurable LLM tier."""
    
    def __init__(self, llm_service: Optional[AnthropicService] = None, tier: LLMTier = LLMTier.PREMIUM):
        """Initialize the Deep Thoughts Generator.
        
        Args:
            llm_service: Optional LLM service. If not provided, creates service based on tier.
            tier: LLM tier to use (CHEAP, STANDARD, or PREMIUM)
        """
        if llm_service:
            self.llm_service = llm_service
        else:
            self.llm_service = LLMFactory.create_service(tier)
        
        self.tier = tier
    
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
        timestamp: Optional[datetime] = None,
        include_evals: bool = False,
        include_transcript: bool = False
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
        
        # Generate Deep Thoughts analysis
        deep_thoughts_content = await self._generate_analysis(
            conversation_text, 
            conversation_id,
            include_evals=include_evals,
            include_transcript=include_transcript
        )
        
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
    
    async def _generate_analysis(
        self, 
        conversation_text: str, 
        conversation_id: str,
        include_evals: bool = False,
        include_transcript: bool = False
    ) -> str:
        """Generate Deep Thoughts analysis using the system prompt.
        
        Args:
            conversation_text: Formatted conversation for analysis
            conversation_id: Unique identifier for the conversation
            include_evals: Whether to include evaluation summary
            include_transcript: Whether to include conversation transcript
            
        Returns:
            Deep Thoughts report content
        """
        # Load the system prompt from the markdown file
        system_prompt = get_deep_thoughts_system_prompt()
        
        # Build the user prompt with conversation context
        user_prompt = f"""CONVERSATION TO ANALYZE:
{conversation_text}

Generate a Deep Thoughts report now following the structure and guidelines provided in the system prompt."""
        
        # Add optional enhancement sections if requested
        if include_evals or include_transcript:
            enhanced_sections = ""
            if include_evals:
                enhanced_sections += """

Additionally, include an Evaluation Summary section with:
- Key coaching moves that worked well
- Areas for improvement
- Overall coaching effectiveness score (1-10) with brief justification
"""
            
            if include_transcript:
                enhanced_sections += """

Additionally, include a Conversation Transcript section with the full conversation for reference.
"""
            
            user_prompt += enhanced_sections

        try:
            # Generate analysis with parameters based on tier
            max_tokens = 1500 if self.tier == LLMTier.PREMIUM else 1000
            temperature = 0.2 if self.tier == LLMTier.PREMIUM else 0.3
            
            analysis_content = await self.llm_service.generate_response(
                messages=[{"role": "user", "content": user_prompt}],
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature
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