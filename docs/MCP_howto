## MCP (Model Context Protocol) Integration
This markdown file describes best practices for MCP integrations with LLMs. Please use as context when integrating an MCP.

### The Seven MCP Laws

1. **Real Servers Only**: Never mock MCP data or bypass with direct API calls. Always use an actual MCP server.

2. **Research First**: Search for reputable MCP servers before building. Check GitHub stars, recent commits, and community adoption.

3. **Read, Then Code**: Study the MCP server's README thoroughly. Note:
   - Exact tool names (often use hyphens: `get-tasks` not `get_tasks`)
   - Response formats (TextContent objects vs direct JSON)
   - Environment variable names (API_KEY vs API_TOKEN)

4. **E2E Test Setup**: Start with a test that validates the complete flow:
   ```python
   async def test_mcp_integration_e2e():
       """Should fetch real data and inject into coach prompt"""
       # Not just fetching - ensure it reaches the LLM
   ```

5. **Sandbox Before Integration**: Create a minimal test script:
   ```python
   # mcp_sandbox.py - Test MCP connection in isolation
   async def test_mcp_direct():
       # Verify connection, auth, and data retrieval
       # BEFORE touching main codebase
   ```

6. **Architecture First**: Map the data flow completely:
   ```
   MCP Server → Client → Agent → System Prompt → LLM
                                    ↑
                              INJECTION POINT
   ```

7. **Observability Required**: Build debug tools immediately:
   - Connection status endpoint
   - Raw response logging
   - Injection verification

### MCP Integration Checklist

```bash
# 1. Server Setup
git clone [mcp-server-repo]
cd [mcp-server]
npm install && npm run build
# Verify: node build/index.js works with env vars

# 2. Client Dependencies
pip install mcp python-dotenv

# 3. Environment Variables
# Check server README for EXACT names
echo "API_KEY_NAME_FROM_DOCS=..." >> .env

# 4. Test Connection First
python mcp_sandbox.py  # Before any integration

# 5. Verify Injection
# Log system prompt AFTER enhancement
logger.debug(f"Prompt length: {len(prompt)}")
```

### Common MCP Pitfalls

1. **Silent Fallbacks**: Never default to mock data - fail loudly
2. **Async Context Managers**: Use explicit cleanup to avoid TaskGroup errors
3. **Response Parsing**: MCP returns TextContent objects, not raw JSON
4. **Tool Names**: Always use exact names from server docs (check hyphens!)
5. **Prompt Injection**: Data must reach the LLM prompt, not just be fetched

### MCP Error Patterns

```python
# ❌ WRONG: Fetching without injection
todos = await mcp.get_todos()
return self.llm.generate(prompt)  # Todos never used!

# ✅ RIGHT: Enhance prompt before LLM call
todos = await mcp.get_todos()
enhanced_prompt = self._inject_context(prompt, todos)
return self.llm.generate(enhanced_prompt)
```
```