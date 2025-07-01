# Session 4: Morning Coach Excellence

## Executive Summary (Pyramid Peak)

Transform the generic diary coach into a specialized morning excellence system that ensures users identify the RIGHT problem, think deeply about it, and get excited to tackle it. Replace generic evaluation reports with transformative "Deep Thoughts" markdown documents that users want to pin and revisit throughout their day.

**Duration**: 4-5 hours  
**Approach**: Test-Driven Development with incremental specialization  
**Result**: Morning-specific coach that generates breakthrough insights users actually use

## Three Core Transformations

### 1. Morning Coach Specialization ✅
Extract and enhance the excellent evening coaching elements for morning use. Build a dedicated morning agent that challenges users on problem selection, not just problem clarification.

### 2. Deep Thoughts Revolution 🚀
Replace generic evaluation reports with AI-powered "Deep Thoughts" documents that:
- Summarize the conversation's core problem and approach
- Fact-check key assumptions
- Play devil's advocate using Columbo's "just one more thing" style
- Provide hints that get users unstuck without solving for them

### 3. Morning-Specific Evaluations 🎯
New evaluation metrics that measure what matters:
- **Right Problem Selection**: Does coach challenge the user's initial problem choice?
- **Thinking Pivot Rate**: How often does coach help user reframe their thinking?
- **Excitement Generation**: Does the conversation overcome "clean slate fear"?

## Implementation Increments (Following VibeCoding Manifesto)

### Increment 4.1: Morning Coach Prompt Integration (45-60 min)
**Goal**: Focus `CoachAgent` on morning-specific prompt injection

**Test First**:
```python
# tests/agents/test_morning_coach.py
async def test_morning_coach_challenges_problem_selection():
    """Morning coach should question if this is really today's biggest problem"""
    
async def test_morning_coach_uses_creative_greeting():
    """Coach should use witty creative format for opening question"""
    
async def test_morning_coach_asks_about_core_value():
    """After problem is energizing, coach asks about core value to fight for"""
```

**Implementation Approach**:
- Use @docs/prototype/MorningPrompt.md content to make it morning focused

**Learning Opportunities**:
- Dynamic prompt injection patterns
- Time-based behavioral switching
- Maintaining backwards compatibility while adding features

### Increment 4.2: Deep Thoughts Generator (60-90 min)
**Goal**: Create new `DeepThoughtsGenerator` using Opus to create transformative insights

**Test First**:
```python
# tests/reporting/test_deep_thoughts.py
async def test_deep_thoughts_summarizes_problem_clearly():
    """Report should crystallize the core problem in 2-3 sentences"""
    
async def test_deep_thoughts_fact_checks_assumptions():
    """Report should identify and verify key claims from conversation"""
    
async def test_deep_thoughts_uses_columbo_style():
    """Devil's advocate section uses 'just one more thing' phrasing"""
    
async def test_deep_thoughts_provides_actionable_hints():
    """Hints guide without solving - Socratic not prescriptive"""
    
async def test_deep_thoughts_filename_format():
    """Files named DeepThoughts_YYYYMMDD_HHMM.md in docs/prototype/DeepThoughts/"""
```

**Implementation Approach**:
- New `DeepThoughtsGenerator` class using Opus-4 for analysis
- Structured prompt for consistent sections
- Output to `docs/prototype/DeepThoughts/DeepThoughts_YYYYMMDD_HHMM.md`
- Separate from existing evaluation infrastructure

**Tech Stack Details**: 
- Use Claude Opus 4 for deep analysis
- Structured output with clear markdown sections
- File naming: `DeepThoughts_20250130_1430.md` (no seconds)

**Learning Opportunities**:
- Multi-model orchestration (Sonnet for coach, Opus for analysis)
- Structured generation with section templates
- File organization patterns for daily documents


### Increment 4.3: Morning-Specific Evaluators (45-60 min)
**Goal**: Build three new behavioral analyzers for morning effectiveness

**Test First**:
```python
# tests/evaluation/analyzers/test_morning_analyzers.py
async def test_problem_selection_analyzer():
    """Measures how well coach challenges initial problem choice"""
    
async def test_thinking_pivot_analyzer():
    """Counts reframing moments and perspective shifts"""
    
async def test_excitement_builder_analyzer():
    """Detects energy/motivation increases through conversation"""
```

**New Analyzer Classes**:
1. `ProblemSelectionAnalyzer`: Detects challenging questions about priorities
2. `ThinkingPivotAnalyzer`: Identifies reframing and "aha" moments  
3. `ExcitementBuilderAnalyzer`: Measures motivation trajectory

**Learning Opportunities**:
- LLM-as-judge prompt engineering
- Behavioral pattern recognition
- Metric design for subjective qualities

### Increment 4.4: Deep Thoughts Evaluator (30-45 min)
**Goal**: Measure quality of generated Deep Thoughts reports

**Test First**:
```python
# tests/evaluation/test_deep_thoughts_eval.py
async def test_deep_thoughts_conciseness():
    """Report should be scannable in under 2 minutes"""
    
async def test_deep_thoughts_devil_advocate_quality():
    """Columbo section should feel insightful not annoying"""
    
async def test_deep_thoughts_rereadability():
    """Report should offer new value on second reading"""
```

**Evaluation Metrics**:
- Succinct summary score (brevity + completeness)
- Devil's advocate effectiveness (challenging but supportive)
- Hint quality (guides without prescribing)

### Increment 4.5: Evaluation Report Extractor (30-45 min)
**Goal**: Create markdown exporter for existing evaluation metrics - after a deepthoughts report is made

**Test First**:
```python
# tests/reporting/test_eval_exporter.py
async def test_eval_exporter_includes_all_metrics():
    """Export includes all 4 behavioral analyzers + performance"""
    
async def test_eval_exporter_filename_format():
    """Files named Eval_YYYYMMDD_HHMM.md in docs/prototype/Evals/"""
    
async def test_eval_exporter_preserves_scores():
    """All numeric scores and analysis preserved in markdown"""
```

**Implementation Approach**:
- New `EvaluationExporter` that uses existing `EvaluationReporter`
- Export all metrics to `docs/prototype/Evals/Eval_YYYYMMDD_HHMM.md`
- Clean markdown formatting for easy scanning
- Reuse existing evaluation data structures

**File Organization**:
```
docs/prototype/
├── DeepThoughts/
│   └── DeepThoughts_20250130_1430.md
└── Evals/
    └── Eval_20250130_1430.md
```


### Increment 4.5: Integration and Command Updates (45-60 min)
**Goal**: Wire everything together with updated CLI commands

**Test First**:
```python
# tests/integration/test_morning_flow.py
async def test_morning_coach_to_deep_thoughts_flow():
    """Complete morning conversation → Deep Thoughts generation"""
    
async def test_deep_thoughts_command_variations():
    """'deep research', 'think deeper', 'deep thoughts' all work"""
    
async def test_eval_export_command():
    """'export eval' saves evaluation to Evals folder"""
```

**CLI Updates**:
- "deep report" triggers Deep Thoughts generation to DeepThoughts folder and saves all evaluation metrics to Evals folder
- Both reports use YYYYMMDD_HHMM naming convention

**Integration Points**:
- Modify `CoachAgent` to detect time and switch prompts
- Add `DeepThoughtsGenerator` to enhanced CLI
- Add `EvaluationExporter` for eval markdown export
- Create folder structure if not exists

**File Output Structure**:
```
docs/prototype/
├── DeepThoughts/
│   ├── DeepThoughts_20250130_0930.md
│   └── DeepThoughts_20250130_1545.md
└── Evals/
    ├── Eval_20250130_0930.md
    └── Eval_20250130_1545.md
```

## Success Metrics

### Must Complete ✅
- [ ] Dedicated morning coach that challenges problem selection
- [ ] Deep Thoughts reports users want to save and reread  
- [ ] 3 new morning-specific evaluation metrics
- [ ] Columbo-style devil's advocate that feels helpful not adversarial
- [ ] All tests passing with comprehensive coverage

### Should Complete 🎯
- [ ] Problem selection improves by 40% (measured by analyzer)
- [ ] 80% of Deep Thoughts reports get "would pin this" rating
- [ ] Excitement scores increase 30% vs generic coach
- [ ] Response time remains under 1 second

### Stretch Goals 🚀
- [ ] Auto-suggest alternative problems from user's context
- [ ] Deep Thoughts includes visualization of thinking evolution
- [ ] Integration with todo list for problem alternatives

## Learning Focus Areas (from Learning Ledger)

### 🔴 Critical Learning: Multi-Model Orchestration
**Gap**: No experience coordinating multiple LLM calls  
**Session 4 Opportunity**: Sonnet for coaching + Opus for Deep Thoughts
**Practice**: Cost/quality trade-offs, async coordination, error handling

### 🟡 Supporting Learning: Evaluation Design
**Gap**: Measuring subjective qualities like "excitement"  
**Session 4 Opportunity**: Design morning-specific behavioral metrics
**Practice**: LLM-as-judge prompting, metric validation, score calibration

### 🟡 Supporting Learning: Structured Generation
**Gap**: Getting consistent formatted output from LLMs  
**Session 4 Opportunity**: Deep Thoughts report structure
**Practice**: XML prompting, JSON mode, validation patterns

## Technical Decisions for Claude Code

### Architecture Approach Options
1. **Modular**: Separate morning coach as independent agent
2. **Configured**: Single coach with morning/evening modes
3. **Hybrid**: Base coach with morning/evening subclasses

**Recommendation**: Start modular (option 1) for clarity, refactor later if needed

### Deep Thoughts Generation Options  
1. **Single Opus Call**: One prompt analyzes entire conversation
2. **Multi-Phase**: Separate calls for summary/facts/devil's advocate
3. **Streaming**: Generate sections as conversation progresses

**Recommendation**: Single call (option 1) for simplicity, optimize if slow

### Evaluation Integration Options
1. **Replace**: Deep Thoughts replaces evaluation reports
2. **Complement**: Both reports available via different commands
3. **Unified**: Single report with light/deep modes

**Recommendation**: Complement (option 2) to preserve Session 3 work

## Anti-Patterns to Avoid

### ❌ Perfect Prompt Paralysis
Don't spend 2 hours tweaking prompts. Use tests to define "good enough" and iterate.

### ❌ Feature Creep  
Deep Thoughts should be simple and focused. Resist adding sections.

### ❌ Ignoring Cost
Opus is expensive. Add cost tracking from the start.

### ❌ Breaking Existing Tests
Session 3 evaluation should still work. New features, don't break old ones.
