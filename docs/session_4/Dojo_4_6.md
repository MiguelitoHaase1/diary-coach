# Dojo Session 4.6

**Purpose**: Enable me to copy a learning theme into Claude.ai, so I can personally prompt it further to teach me more about it.

**Context**: We were optimizing the Session 4 morning coach implementation based on user feedback about cost efficiency and file management. The user wanted fewer files generated, cheaper evaluation using Sonnet instead of Opus, and more control over when files are created.

**Challenge**: Balancing feature richness with operational cost and user experience. The initial implementation generated 3 files automatically using expensive Opus model for all analysis, but users wanted more cost-effective and controlled file generation.

**Concept**: **Cost-Conscious AI System Design** - The principle of building AI systems that deliver value while remaining economically sustainable. This involves strategic model selection (using expensive models only where high quality is essential), user-controlled resource consumption, and iterative optimization based on real usage patterns. In this case, we used Opus for creative Deep Thoughts generation where quality matters most, but switched to Sonnet for structured evaluation where consistency matters more than creativity. We also shifted from automatic file generation to user-triggered generation, giving users control over when they incur costs.

This concept matters beyond coaching systems - any production AI application needs to balance feature sophistication with operational sustainability, especially as usage scales.

**Other areas one could explore**: 
- **Caching strategies for LLM responses** - How to cache expensive model outputs intelligently to reduce repeated costs
- **Progressive enhancement in AI UX** - Building systems that start simple and add complexity only when users request it  
- **Multi-model orchestration patterns** - When and how to combine different AI models for optimal cost/quality tradeoffs