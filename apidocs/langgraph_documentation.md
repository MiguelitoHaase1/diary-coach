# langgraph API Documentation

*Fetched using Context7 MCP server on 2025-07-28 10:00:39*

---

========================
CODE SNIPPETS
========================
TITLE: Instantiating LangGraph Workflow (Python)
DESCRIPTION: Initializes a LangGraph `StateGraph` instance, which serves as the foundation for defining the agent's workflow structure. It is configured to use the specified `AgentState` object to manage the state passed between nodes.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/project_manager_assistant_agent.ipynb#_snippet_16

LANGUAGE: python
CODE:
```
# Instantiate the workflow    
workflow = StateGraph(AgentState)
```

----------------------------------------

TITLE: Defining LangGraph Workflow (Python)
DESCRIPTION: Defines the state (MessagesState) and nodes of the LangGraph workflow, including functions for the researcher and chart_generator nodes that invoke their respective agents and determine the next node (END or the other agent) based on the agent's output. It then constructs the graph by adding nodes and defining the starting edge.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/Multi-agent network.md#_snippet_4

LANGUAGE: Python
CODE:
```
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.types import Command

# Define state mapping
def get_next_node(last_message, goto):
    if "FINAL ANSWER" in last_message.content:
        return END
    return goto

def research_node(state: MessagesState):
    result = research_agent.invoke(state)
    goto = get_next_node(result["messages"][-1], "chart_generator")
    return Command(update={"messages": result["messages"]}, goto=goto)

def chart_node(state: MessagesState):
    result = chart_agent.invoke(state)
    goto = get_next_node(result["messages"][-1], "researcher")
    return Command(update={"messages": result["messages"]}, goto=goto)

# Create the graph
workflow = StateGraph(MessagesState)
workflow.add_node("researcher", research_node)
workflow.add_node("chart_generator", chart_node)
workflow.add_edge(START, "researcher")
graph = workflow.compile()
```

----------------------------------------

TITLE: Constructing LangGraph Workflow | Python
DESCRIPTION: This code builds the core LangGraph workflow for the Reflexion agent. It defines the graph `State`, initializes a `StateGraph`, and adds nodes representing the initial draft, tool execution, and revision steps. It sets up sequential edges (`draft` -> `execute_tools` -> `revise`) and a conditional edge from `revise` that either loops back to `execute_tools` or ends the graph, controlled by an iteration count limit.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/Reflexion.md#_snippet_7

LANGUAGE: python
CODE:
```
from typing import Literal
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from typing import Annotated
from typing_extensions import TypedDict

class State(TypedDict):
    messages: Annotated[list, add_messages]

MAX_ITERATIONS = 5
builder = StateGraph(State)
builder.add_node("draft", first_responder.respond)
builder.add_node("execute_tools", tool_node)
builder.add_node("revise", revisor.respond)

# draft -> execute_tools
builder.add_edge("draft", "execute_tools")
# execute_tools -> revise
builder.add_edge("execute_tools", "revise")

# Define looping logic
def _get_num_iterations(state: list):
    i = 0
    for m in state[::-1]:
        if m.type not in {"tool", "ai"}:
            break
        i += 1
    return i

def event_loop(state: list):
    # in our case, we'll just stop after N plans
    num_iterations = _get_num_iterations(state["messages"])
    if num_iterations > MAX_ITERATIONS:
        return END
    return "execute_tools"

# revise -> execute_tools OR end
builder.add_conditional_edges("revise", event_loop, ["execute_tools", END])
builder.add_edge(START, "draft")
graph = builder.compile()
```

----------------------------------------

TITLE: Building Agent State Graph with LangGraph (Python)
DESCRIPTION: This code constructs the agent's execution flow as a state graph using LangGraph. It defines nodes for the main agent reasoning step (`agent`), a node to update the agent's scratchpad history (`update_scratchpad`), and nodes for each specific browser interaction tool (`Click`, `Type`, etc.). It sets up edges to dictate transitions between states (START to agent, tools back to update_scratchpad). A router function (`select_tool`) conditionally chooses the next node based on the agent's predicted action (executing a tool, retrying, or ending the graph).

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/Web Voyager.md#_snippet_5

LANGUAGE: python
CODE:
```
import re
from langchain_core.runnables import RunnableLambda
from langgraph.graph import END, START, StateGraph

# Function to update agent's scratchpad with previous actions
def update_scratchpad(state: AgentState):
    old = state.get("scratchpad")
    if old:
        txt = old[0].content
        last_line = txt.rsplit("\n", 1)[-1]
        step = int(re.match(r"\d+", last_line).group()) + 1
    else:
        txt = "Previous action observations:\n"
        step = 1
    
    txt += f"\n{step}. {state['observation']}"
    return {**state, "scratchpad": [SystemMessage(content=txt)]}

# Create the state graph
graph_builder = StateGraph(AgentState)

# Add agent node
graph_builder.add_node("agent", agent)
graph_builder.add_edge(START, "agent")

# Add scratchpad update node
graph_builder.add_node("update_scratchpad", update_scratchpad)
graph_builder.add_edge("update_scratchpad", "agent")

# Define available tools
tools = {
    "Click": click,
    "Type": type_text,
    "Scroll": scroll,
    "Wait": wait,
    "GoBack": go_back,
    "Google": to_google,
}

# Add tool nodes
for node_name, tool in tools.items():
    graph_builder.add_node(
        node_name,
        # Map tool output to "observation" key in state
        RunnableLambda(tool) | (lambda observation: {"observation": observation}),
    )
    # All tools return to update_scratchpad
    graph_builder.add_edge(node_name, "update_scratchpad")

# Router function to select appropriate tool
def select_tool(state: AgentState):
    action = state["prediction"]["action"]
    if action == "ANSWER":
        return END
    if action == "retry":
        return "agent"
    return action

# Add conditional routing
graph_builder.add_conditional_edges("agent", select_tool)

# Compile the graph
graph = graph_builder.compile()
```

----------------------------------------

TITLE: LangGraph Agent Workflow Definition - Python
DESCRIPTION: Defines the core LangGraph agent workflow. It sets up state management, initializes language models (Anthropic and OpenAI) and tools (Tavily Search), loads prompts, defines nodes for model invocation and tool execution, and constructs the graph with conditional edges based on model output.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/src/libs/langchain-ai-langgraph graph_req_a.txt#_snippet_3

LANGUAGE: Python
CODE:
```
from pathlib import Path
from typing import Annotated, Sequence, TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, add_messages
from langgraph.prebuilt import ToolNode

tools = [TavilySearchResults(max_results=1)]

model_anth = ChatAnthropic(temperature=0, model_name="claude-3-sonnet-20240229")
model_oai = ChatOpenAI(temperature=0)

model_anth = model_anth.bind_tools(tools)
model_oai = model_oai.bind_tools(tools)

prompt = open("prompt.txt").read()
subprompt = open(Path(__file__).parent / "subprompt.txt").read()


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# Define the function that determines whether to continue or not
def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    # If there are no tool calls, then we finish
    if not last_message.tool_calls:
        return "end"
    # Otherwise if there is, we continue
    else:
        return "continue"


# Define the function that calls the model
def call_model(state, config):
    if config["configurable"].get("model", "anthropic") == "anthropic":
        model = model_anth
    else:
        model = model_oai
    messages = state["messages"]
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


# Define the function to execute tools
tool_node = ToolNode(tools)


# Define a new graph
workflow = StateGraph(AgentState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point("agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
    # Finally we pass in a mapping.
    # The keys are strings, and the values are other nodes.
    # END is a special node marking that the graph should finish.
    # What will happen is we will call `should_continue`, and then the output of that
    # will be matched against the keys in this mapping.
    # Based on which one it matches, that node will then be called.
    {
        # If `tools`, then we call the tool node.
        "continue": "action",
        # Otherwise we finish.
        "end": END,
    },
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("action", "agent")

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
graph = workflow.compile()
```

----------------------------------------

TITLE: Create Agent Workflow with Tool Breakpoint - Python
DESCRIPTION: Sets up a LangGraph agent workflow using `MessagesState`, including an LLM and a tool. A breakpoint is configured using `interrupt_before` to pause the workflow just before the 'action' node, which represents the tool execution.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/How to edit graph state.md#_snippet_5

LANGUAGE: python
CODE:
```
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode

# Define a search tool
@tool
def search(query: str) -> str:
    """Search for information online.
    
    Args:
        query: The search query
        
    Returns:
        Search results
    """
    # In a real application, this would call a search API
    return f"Results for '{query}': Sample information about {query}."

# Create a tool node
tools = [search]
tool_node = ToolNode(tools)

# Set up the language model
model = ChatAnthropic(model="claude-3-haiku")

# Define the agent logic
def should_continue(state):
    """Determine if we should continue to tools or end."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # Check if the last message has tool calls
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "continue"
    return "end"

def call_model(state):
    """Call the model with the current messages."""
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}

# Build the agent workflow
workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent", 
    should_continue, 
    {"continue": "action", "end": END}
)
workflow.add_edge("action", "agent")

# Set up memory and add breakpoint before tool execution
memory = MemorySaver()
agent_app = workflow.compile(
    checkpointer=memory, 
    interrupt_before=["action"]  # Add breakpoint before tools run
)
```

----------------------------------------

TITLE: Creating LangGraph StateGraph with Agents (Python)
DESCRIPTION: Defines a LangGraph StateGraph that orchestrates multiple agents (planner, executor, replanner) to process user input. It includes nodes for planning, execution, and replanning, and conditional edges to determine the workflow based on the state.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/alidhl-multi-agent-chatbot.txt#_snippet_3

LANGUAGE: Python
CODE:
```
def get_graph():
    # Create agents
    executor = get_executor()
    planner = get_planner()
    replanner = get_replanner()

    def execute(state: State):
        task = state['plan'][0]
        output = executor.invoke({'input': task, "chat_history" : []})
        return {"past_steps" : (task, output['agent_outcome'].return_values['output'])}

    def plan(state: State):
        plan = planner.invoke({'objective': state['input']})
        return {"plan" : plan.steps}

    def replan(state: State):
        output = replanner.invoke(state)
        # If the output is a response (the plan is complete), then return the response else update the plan
        if isinstance(output, Response):
            return {"response" : output.response}
        else:
            return {"plan" : output.steps}

    def should_end(state: State):
        if (state['response']):
            return True
        else:
            return False
        
    graph = StateGraph(State)
    graph.add_node("planner", plan)
    graph.add_node("executor", execute)
    graph.add_node("replanner", replan)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "replanner")
    graph.add_conditional_edges(
        'replanner',
        should_end,
        {
            True: END,
            False: "executor"
        })
    return graph.compile()
```

----------------------------------------

TITLE: Define and Compile LangGraph Workflow
DESCRIPTION: Sets up the LangGraph workflow by initializing a StateGraph with the defined state and configuration schema. It adds the 'agent' (model call) and 'action' (tool execution) nodes, sets the entry point, defines conditional edges based on the 'should_continue' function, adds a normal edge from 'action' back to 'agent', and finally compiles the graph.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/src/libs/langchain-ai-langgraph graph.txt#_snippet_6

LANGUAGE: python
CODE:
```
# Define a new graph
workflow = StateGraph(AgentState, config_schema=ConfigSchema)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point("agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
    # Finally we pass in a mapping.
    # The keys are strings, and the values are other nodes.
    # END is a special node marking that the graph should finish.
    # What will happen is we will call `should_continue`, and then the output of that
    # will be matched against the keys in this mapping.
    # Based on which one it matches, that node will then be called.
    {
        # If `tools`, then we call the tool node.
        "continue": "action",
        # Otherwise we finish.
        "end": END,
    },
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("action", "agent")

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
graph = workflow.compile()
```

----------------------------------------

TITLE: Building LangGraph State Graph - Python
DESCRIPTION: Constructs a simple LangGraph state graph using the defined `llm_node` and `end_node`. It sets up the flow from START to `llm_node`, then to `end_node`, and finally to END.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/agntcy-agentic-apps (6).txt#_snippet_61

LANGUAGE: python
CODE:
```
def build_graph() -> Any:
    """
    Constructs the state graph for handling requests.

    Returns:
        StateGraph: A compiled LangGraph state graph.
    """
    builder = StateGraph(GraphState)
    builder.add_node("llm_node", llm_node)
    builder.add_node("end_node", end_node)
    builder.add_edge(START, "llm_node")
    builder.add_edge("llm_node", "end_node")
    builder.add_edge("end_node", END)
    return builder.compile()
```

----------------------------------------

TITLE: Building Tool-Calling Agent - LangGraph Graph API Python
DESCRIPTION: Constructs a tool-calling agent using LangGraph's StateGraph and Graph API. It defines nodes for LLM calls and tool execution, sets up a conditional edge to decide between calling tools or ending, and compiles the graph into a runnable agent. Requires `langgraph.graph` and `langchain_core.messages`.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/docs/docs/tutorials/workflows/index.md#_snippet_10

LANGUAGE: python
CODE:
```
from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage


# Nodes
def llm_call(state: MessagesState):
    """LLM decides whether to call a tool or not"""

    return {
        "messages": [
            llm_with_tools.invoke(
                [
                    SystemMessage(
                        content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
                    )
                ]
                + state["messages"]
            )
        ]
    }


def tool_node(state: dict):
    """Performs the tool call"""

    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}


# Conditional edge function to route to the tool node or end based upon whether the LLM made a tool call
def should_continue(state: MessagesState) -> Literal["environment", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]
    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls:
        return "Action"
    # Otherwise, we stop (reply to the user)
    return END


# Build workflow
agent_builder = StateGraph(MessagesState)

# Add nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("environment", tool_node)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    {
        # Name returned by should_continue : Name of next node to visit
        "Action": "environment",
        END: END,
    },
)
agent_builder.add_edge("environment", "llm_call")

# Compile the agent
agent = agent_builder.compile()

# Show the agent
display(Image(agent.get_graph(xray=True).draw_mermaid_png()))

# Invoke
messages = [HumanMessage(content="Add 3 and 4.")]
messages = agent.invoke({"messages": messages})
for m in messages["messages"]:
    m.pretty_print()
```

----------------------------------------

TITLE: Defining LangGraph State and Workflow for Self-Discover Agent Python
DESCRIPTION: Defines the state for the LangGraph using a TypedDict, initializes a ChatOpenAI model, creates functions for each step (select, adapt, structure, reason) that chain prompts with the model and parser, and constructs a LangGraph state graph with nodes and edges defining the sequential workflow.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/Self-Discover Agent.md#_snippet_2

LANGUAGE: python
CODE:
```
from typing import Optional
from typing_extensions import TypedDict

from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from langgraph.graph import END, START, StateGraph

class SelfDiscoverState(TypedDict):
    reasoning_modules: str
    task_description: str
    selected_modules: Optional[str]
    adapted_modules: Optional[str]
    reasoning_structure: Optional[str]
    answer: Optional[str]

model = ChatOpenAI(temperature=0, model="gpt-4-turbo-preview")

def select(inputs):
    select_chain = select_prompt | model | StrOutputParser()
    return {"selected_modules": select_chain.invoke(inputs)}

def adapt(inputs):
    adapt_chain = adapt_prompt | model | StrOutputParser()
    return {"adapted_modules": adapt_chain.invoke(inputs)}

def structure(inputs):
    structure_chain = structured_prompt | model | StrOutputParser()
    return {"reasoning_structure": structure_chain.invoke(inputs)}

def reason(inputs):
    reasoning_chain = reasoning_prompt | model | StrOutputParser()
    return {"answer": reasoning_chain.invoke(inputs)}

graph = StateGraph(SelfDiscoverState)
graph.add_node(select)
graph.add_node(adapt)
graph.add_node(structure)
graph.add_node(reason)
graph.add_edge(START, "select")
graph.add_edge("select", "adapt")
graph.add_edge("adapt", "structure")
graph.add_edge("structure", "reason")
graph.add_edge("reason", END)
app = graph.compile()
```

----------------------------------------

TITLE: Implementing Prompt Chaining Workflow in LangGraph (Python)
DESCRIPTION: Demonstrates building a sequential workflow where LLM calls are chained together based on predefined logic and conditional routing. It defines a shared state (`TypedDict`), implements node functions that process the state, and constructs a `StateGraph` connecting these nodes with edges and conditional transitions.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/Workflows and Agents.md#_snippet_1

LANGUAGE: python
CODE:
```
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# Define state structure
class State(TypedDict):
    topic: str
    joke: str
    improved_joke: str
    final_joke: str

# Define node functions
def generate_joke(state: State):
    msg = llm.invoke(f"Write a short joke about {state['topic']}")
    return {"joke": msg.content}

def check_punchline(state: State):
    if "?" in state["joke"] or "!" in state["joke"]:
        return "Fail"
    return "Pass"

def improve_joke(state: State):
    msg = llm.invoke(f"Make this joke funnier by adding wordplay: {state['joke']}")
    return {"improved_joke": msg.content}

def polish_joke(state: State):
    msg = llm.invoke(f"Add a surprising twist to this joke: {state['improved_joke']}")
    return {"final_joke": msg.content}
```

LANGUAGE: python
CODE:
```
# Build and connect the graph
workflow = StateGraph(State)
workflow.add_node("generate_joke", generate_joke)
workflow.add_node("improve_joke", improve_joke)
workflow.add_node("polish_joke", polish_joke)
workflow.add_edge(START, "generate_joke")
workflow.add_conditional_edges(
    "generate_joke", check_punchline, {"Fail": "improve_joke", "Pass": END}
)
workflow.add_edge("improve_joke", "polish_joke")
workflow.add_edge("polish_joke", END)

# Compile and run
chain = workflow.compile()
result = chain.invoke({"topic": "cats"})
```

----------------------------------------

TITLE: Creating a Generic Agent Graph with LangGraph
DESCRIPTION: This Python function `create_generic_agent_graph` constructs a LangGraph StateGraph. It takes a state definition (`GraphState`), a dictionary of node functions, and various configuration parameters to define the workflow's nodes, entry point, and edges, including conditional logic for retries and human review. It dynamically adds nodes based on configuration flags like `human_in_the_loop`, `bypass_recommended_steps`, and `bypass_explain_code`.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/business-science-ai-data-science-team (5).txt#_snippet_19

LANGUAGE: Python
CODE:
```
def create_generic_agent_graph(
    GraphState: Type,
    node_functions: dict,
    recommended_steps_node_name: str,
    create_code_node_name: str,
    execute_code_node_name: str,
    fix_code_node_name: str,
    explain_code_node_name: str,
    error_key: str,
    max_retries_key: str = "max_retries",
    retry_count_key: str = "retry_count",
    human_in_the_loop: bool = False,
    human_review_node_name: str = "human_review",
    checkpointer: Optional[Callable] = None,
    bypass_recommended_steps: bool = False,
    bypass_explain_code: bool = False,
    agent_name: str = "coding_agent"
):
    """
    Creates a generic agent graph using the provided node functions and node names.
    
    Parameters
    ----------
    GraphState : Type
        The TypedDict or class used as state for the workflow.
    node_functions : dict
        A dictionary mapping node names to their respective functions.
        Example: {
            "recommend_cleaning_steps": recommend_cleaning_steps,
            "human_review": human_review,
            "create_data_cleaner_code": create_data_cleaner_code,
            "execute_data_cleaner_code": execute_data_cleaner_code,
            "fix_data_cleaner_code": fix_data_cleaner_code,
            "explain_data_cleaner_code": explain_data_cleaner_code
        }
    recommended_steps_node_name : str
        The node name that recommends steps.
    create_code_node_name : str
        The node name that creates the code.
    execute_code_node_name : str
        The node name that executes the generated code.
    fix_code_node_name : str
        The node name that fixes code if errors occur.
    explain_code_node_name : str
        The node name that explains the final code.
    error_key : str
        The state key used to check for errors.
    max_retries_key : str, optional
        The state key used for the maximum number of retries.
    retry_count_key : str, optional
        The state key for the current retry count.
    human_in_the_loop : bool, optional
        Whether to include a human review step.
    human_review_node_name : str, optional
        The node name for human review if human_in_the_loop is True.
    checkpointer : callable, optional
        A checkpointer callable if desired.
    bypass_recommended_steps : bool, optional
        Whether to skip the recommended steps node.
    bypass_explain_code : bool, optional
        Whether to skip the final explain code node.
    name : str, optional
        The name of the agent graph.

    Returns
    -------
    app : langchain.graphs.StateGraph
        The compiled workflow application.
    """

    workflow = StateGraph(GraphState)
    
    # * NODES
    
    # Always add create, execute, and fix nodes
    workflow.add_node(create_code_node_name, node_functions[create_code_node_name])
    workflow.add_node(execute_code_node_name, node_functions[execute_code_node_name])
    workflow.add_node(fix_code_node_name, node_functions[fix_code_node_name])
    
    # Conditionally add the recommended-steps node
    if not bypass_recommended_steps:
        workflow.add_node(recommended_steps_node_name, node_functions[recommended_steps_node_name])
    
    # Conditionally add the human review node
    if human_in_the_loop:
        workflow.add_node(human_review_node_name, node_functions[human_review_node_name])
    
    # Conditionally add the explanation node
    if not bypass_explain_code:
        workflow.add_node(explain_code_node_name, node_functions[explain_code_node_name])
    
    # * EDGES
    
    # Set the entry point
    entry_point = create_code_node_name if bypass_recommended_steps else recommended_steps_node_name
    
    workflow.set_entry_point(entry_point)
    
    if not bypass_recommended_steps:
        workflow.add_edge(recommended_steps_node_name, create_code_node_name)
    
    workflow.add_edge(create_code_node_name, execute_code_node_name)
    workflow.add_edge(fix_code_node_name, execute_code_node_name)
    
    # Define a helper to check if we have an error & can still retry
    def error_and_can_retry(state):
        return (
            state.get(error_key) is not None
            and state.get(retry_count_key) is not None
            and state.get(max_retries_key) is not None
            and state[retry_count_key] < state[max_retries_key]
        )
        
    # If human in the loop, add a branch for human review
    if human_in_the_loop:
        workflow.add_conditional_edges(
            execute_code_node_name,
            lambda s: "fix_code" if error_and_can_retry(s) else "human_review",
            {
                "human_review": human_review_node_name,
                "fix_code": fix_code_node_name,
            },
        )
    else:
        # If no human review, the next node is fix_code if error, else explain_code.
        if not bypass_explain_code:
            workflow.add_conditional_edges(
                execute_code_node_name,
                lambda s: "fix_code" if error_and_can_retry(s) else "explain_code",
                {
                    "fix_code": fix_code_node_name,

```

----------------------------------------

TITLE: Defining LangGraph Workflow Structure (Python)
DESCRIPTION: Initializes a LangGraph StateGraph with a specified state structure (GraphState). It then adds a node named 'data_loader_agent' to the workflow, representing a step in the graph's execution.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/business-science-ai-data-science-team.txt#_snippet_40

LANGUAGE: Python
CODE:
```
workflow = StateGraph(GraphState)
    
    workflow.add_node("data_loader_agent", data_loader_agent)
```

----------------------------------------

TITLE: Building a LangGraph Workflow with Conditional Edges and Interruption (Python)
DESCRIPTION: Defines the state transition logic (`should_continue`), the model invocation node (`call_model`), and constructs a LangGraph workflow. It sets up nodes for the agent and tool action, defines edges including a conditional edge based on `should_continue`, and compiles the graph with memory and an interruption point before the 'action' node.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/docs/docs/how-tos/human_in_the_loop/edit-graph-state.ipynb#_snippet_7

LANGUAGE: python
CODE:
```
# Define the function that determines whether to continue or not
def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    # If there is no function call, then we finish
    if not last_message.tool_calls:
        return "end"
    # Otherwise if there is, we continue
    else:
        return "continue"


# Define the function that calls the model
def call_model(state):
    messages = state["messages"]
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


# Define a new graph
workflow = StateGraph(MessagesState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.add_edge(START, "agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
    # Finally we pass in a mapping.
    # The keys are strings, and the values are other nodes.
    # END is a special node marking that the graph should finish.
    # What will happen is we will call `should_continue`, and then the output of that
    # will be matched against the keys in this mapping.
    # Based on which one it matches, that node will then be called.
    {
        # If `tools`, then we call the tool node.
        "continue": "action",
        # Otherwise we finish.
        "end": END,
    },
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("action", "agent")

# Set up memory
memory = MemorySaver()

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable

# We add in `interrupt_before=["action"]`
# This will add a breakpoint before the `action` node is called
app = workflow.compile(checkpointer=memory, interrupt_before=["action"])
```

----------------------------------------

TITLE: Defining Workflow State with TypedDict (Python)
DESCRIPTION: Defines a `TypedDict` named `State` to represent the state object used in the LangGraph workflow. It includes fields for the date, raw calendar data string, parsed calendar events list, results from React agent, and markdown formatted results. This structure manages the data flow between nodes in the graph.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/tavily-ai-meeting-prep-agent.txt#_snippet_24

LANGUAGE: Python
CODE:
```
class State(TypedDict):
    date: str
    calendar_data: str
    calendar_events: List[Dict]
    react_results: List[str]
    markdown_results: str
```

----------------------------------------

TITLE: Creating State Class and Supervisor Node Function
DESCRIPTION: Defines the `State` class, inheriting from `MessagesState`, to manage the workflow's state, including a `next` attribute for routing. The `make_supervisor_node` function creates a node that uses an LLM to decide the next worker or 'FINISH' based on the current state messages and a defined list of members.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/Hierarchical Agent Teams.md#_snippet_3

LANGUAGE: python
CODE:
```
from langgraph.graph import StateGraph, MessagesState
from langgraph.types import Command
from langchain_core.language_models import BaseChatModel

class State(MessagesState):
    next: str

def make_supervisor_node(llm: BaseChatModel, members: list[str]):
    """Create a supervisor node with routing capabilities."""
    system_prompt = (
        f"You are a supervisor managing workers: {', '.join(members)}. "
        f"Your job is to decide which worker should handle the current task or if the task is complete.\n"
        f"Available options: {', '.join(members + ['FINISH'])}\n"
        f"Respond with the name of the next worker or FINISH if the task is complete."
    )
    
    def supervisor_node(state: State) -> Command:
        messages = state["messages"]
        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            *[{"role": m[0], "content": m[1]} for m in messages]
        ])
        
        # Extract the decision from the response
        content = response.content
        for member in members + ["FINISH"]:
            if member.lower() in content.lower():
                goto = member
                break
        else:
            goto = "FINISH"
        
        # Return command with destination and state update
        return Command(
            goto=goto if goto != "FINISH" else "__end__", 
            update={"messages": [("assistant", response.content)], "next": goto}
        )
    
    return supervisor_node
```

----------------------------------------

TITLE: Defining LangGraph State and Nodes - Python
DESCRIPTION: Defines the `GraphState` TypedDict to manage the state passed between graph nodes, including the question, generation, and documents. Implements node functions (`retrieve`, `generate`, `grade_documents`, `transform_query`) that perform specific actions within the LangGraph workflow, updating the state.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/Self-RAG.md#_snippet_7

LANGUAGE: python
CODE:
```
from typing import List
from typing_extensions import TypedDict

# Define graph state
class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
    """
    question: str
    generation: str
    documents: List[str]

# Define node functions
def retrieve(state):
    """Retrieve documents"""
    print("---RETRIEVE---")
    question = state["question"]
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}

def generate(state):
    """Generate answer"""
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]
    generation = rag_chain.invoke({"context": documents, "question": question})
    return {"documents": documents, "question": question, "generation": generation}

def grade_documents(state):
    """Determine document relevance"""
    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]
    
    # Score each doc
    filtered_docs = []
    for d in documents:
        score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
        grade = score.binary_score
        if grade == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            continue
    return {"documents": filtered_docs, "question": question}

def transform_query(state):
    """Transform the query to produce a better question"""
    print("---TRANSFORM QUERY---")
    question = state["question"]
    documents = state["documents"]
    better_question = question_rewriter.invoke({"question": question})
    return {"documents": documents, "question": better_question}
```

----------------------------------------

TITLE: Defining and Compiling LangGraph Workflow in Python
DESCRIPTION: This code defines the LangGraph `StateGraph` using the previously defined state and nodes. It adds the `agent` and `tools` nodes, sets `agent` as the entry point, adds a conditional edge from `agent` based on the `should_continue` function, and adds a direct edge from `tools` back to `agent`. Finally, the workflow is compiled into a runnable graph.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/docs/docs/how-tos/react-agent-from-scratch.ipynb#_snippet_5

LANGUAGE: python
CODE:
```
from langgraph.graph import StateGraph, END

# Define a new graph
workflow = StateGraph(AgentState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point("agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
    # Finally we pass in a mapping.
    # The keys are strings, and the values are other nodes.
    # END is a special node marking that the graph should finish.
    # What will happen is we will call `should_continue`, and then the output of that
    # will be matched against the keys in this mapping.
    # Based on which one it matches, that node will then be called.
    {
        # If `tools`, then we call the tool node.
        "continue": "tools",
        # Otherwise we finish.
        "end": END,
    },
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("tools", "agent")

# Now we can compile and visualize our graph
graph = workflow.compile()

from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass
```

----------------------------------------

TITLE: Defining and Compiling LangGraph Workflow Python
DESCRIPTION: This Python snippet defines a `StateGraph` named `workflow` for an agent application, incorporating custom nodes (`call_model`, `should_continue`, `tool_node`) and a state definition (`AgentState`). It sets up the graph structure with edges and conditional transitions based on the `should_continue` node's output, and finally compiles the workflow into a `CompiledGraph` object assigned to the variable `graph`. It requires dependencies like `langgraph` and locally defined modules.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/docs/docs/cloud/deployment/setup_pyproject.md#_snippet_0

LANGUAGE: python
CODE:
```
# my_agent/agent.py
from typing import Literal
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END, START
from my_agent.utils.nodes import call_model, should_continue, tool_node # import nodes
from my_agent.utils.state import AgentState # import state

# Define the config
class GraphConfig(TypedDict):
    model_name: Literal["anthropic", "openai"]

workflow = StateGraph(AgentState, config_schema=GraphConfig)
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END,
    },
)
workflow.add_edge("action", "agent")

graph = workflow.compile()
```

----------------------------------------

TITLE: Setup LangGraph Workflow with MLflow Agent (Python)
DESCRIPTION: This Python code initializes a LangGraph `StateGraph` with a defined `GraphState`. It adds a node named 'mlflow_tools_agent' using the `mflfow_tools_agent` function. It then defines the workflow edges, creating a simple linear flow from the graph's START point to the 'mlflow_tools_agent' node and from the agent node to the graph's END point. Finally, it compiles the workflow, providing a checkpointer and a name for the agent.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/business-science-ai-data-science-team (2).txt#_snippet_50

LANGUAGE: python
CODE:
```
    
    workflow = StateGraph(GraphState)
    
    workflow.add_node("mlflow_tools_agent", mflfow_tools_agent)
    
    workflow.add_edge(START, "mlflow_tools_agent")
    workflow.add_edge("mlflow_tools_agent", END)
    
    app = workflow.compile(
        checkpointer=checkpointer,
        name=AGENT_NAME,
    )

    return app
```

----------------------------------------

TITLE: Initialize Langgraph StateGraph - Python
DESCRIPTION: Creates a directed graph instance using `StateGraph` from `langgraph.graph` to manage the workflow state defined by `AgentState`.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/nirdiamant-genai_agents (18).txt#_snippet_38

LANGUAGE: python
CODE:
```
graph = StateGraph(AgentState)
```

----------------------------------------

TITLE: Defining ReAct Agent Full State (Python)
DESCRIPTION: Defines a dataclass `State` that extends `InputState` to represent the complete internal state of the agent workflow. It adds fields like `is_last_step` (managed by LangGraph), `current_agent` (tracking the active sub-agent), `story_context`, `solution_plans`, and `completed_variations` to manage the agent's progress and data.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/danmas0n-multi-agent-with-mcp.txt#_snippet_55

LANGUAGE: Python
CODE:
```
@dataclass
class State(InputState):
    """Represents the complete state of the agent, extending InputState with additional attributes."""

    is_last_step: IsLastStep = field(default=False)
    """
    Indicates whether the current step is the last one before the graph raises an error.

    This is a 'managed' variable, controlled by the state machine rather than user code.
    It is set to 'True' when the step count reaches recursion_limit - 1.
    """

    current_agent: Literal["orchestrator", "planner", "coder"] = field(
        default="orchestrator"
    )
    """Tracks which agent is currently active in the workflow."""

    story_context: Optional[dict] = field(default=None)
    """Stores the Linear story context and Git repo info gathered by the orchestrator."""
    
solution_plans: List[dict] = field(default_factory=list)
    """Stores the technical solution variations created by the planner."""
    
    completed_variations: List[dict] = field(default_factory=list)
    """Tracks which solution variations have been implemented by the coder."""
```

----------------------------------------

TITLE: Build LangGraph State Graph (Python)
DESCRIPTION: Constructs and configures the LangGraph state graph for the email workflow. It initializes an LLM, defines nodes for external agents (mail composer, email reviewer) and an API bridge for SendGrid, adds these nodes along with processing functions to the graph, and defines edges including conditional routing based on the presence of a final email and using I/O mappers.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/agntcy-agentic-apps (4).txt#_snippet_6

LANGUAGE: Python
CODE:
```
def build_graph() -> CompiledStateGraph:
    llm = AzureChatOpenAI(
        model="gpt-4o-mini",
        api_version="2024-07-01-preview",
        seed=42,
        temperature=0,
    )

    # Instantiate the local ACP node for the remote agent
    acp_mailcomposer = ACPNode(
        name="mailcomposer",
        agent_id=MAILCOMPOSER_AGENT_ID,
        client_config=MAILCOMPOSER_CLIENT_CONFIG,
        input_path="mailcomposer_state.input",
        input_type=mailcomposer.InputSchema,
        output_path="mailcomposer_state.output",
        output_type=mailcomposer.OutputSchema,
    )

    acp_email_reviewer = ACPNode(
        name="email_reviewer",
        agent_id=EMAIL_REVIEWER_AGENT_ID,
        client_config=EMAIL_REVIEWER_CONFIG,
        input_path="email_reviewer_state.input",
        input_type=email_reviewer.InputSchema,
        output_path="email_reviewer_state.output",
        output_type=email_reviewer.OutputSchema,
    )

    # Instantiate APIBridge Agent Node
    sendgrid_api_key = os.environ.get("SENDGRID_API_KEY", None)
    if sendgrid_api_key is None:
        raise ValueError("SENDGRID_API_KEY environment variable is not set")

    send_email = APIBridgeAgentNode(
        name="sendgrid",
        input_path="sendgrid_state.input",
        output_path="sendgrid_state.output",
        service_api_key=sendgrid_api_key,
        hostname=SENDGRID_HOST,
        service_name="sendgrid",
    )

    # Create the state graph
    sg = StateGraph(state.OverallState)

    # Add nodes
    sg.add_node(process_inputs)
    sg.add_node(acp_mailcomposer)
    sg.add_node(acp_email_reviewer)
    sg.add_node(send_email)
    sg.add_node(prepare_output)

    # Add edges
    sg.add_edge(START, "process_inputs")
    sg.add_edge("process_inputs", acp_mailcomposer.get_name())
    ## Add conditional edge between mailcomposer and either send_email or END, adding io_mappers between them
    add_io_mapped_conditional_edge(
        sg,
        start=acp_mailcomposer,
        path=check_final_email,
        iomapper_config_map={
            "done": {
                "end": acp_email_reviewer,
                "metadata": {
                    "input_fields": [
                        "mailcomposer_state.output.final_email",
                        "target_audience",
                    ]
                }
            },
            "user": {"end": "prepare_output", "metadata": None}
        },
        llm=llm,
    )

    ## Add conditional edge between mail reviewer and either send_email or END, adding io_mappers between them

    add_io_mapped_edge(
        sg,
        start=acp_email_reviewer,
        end=send_email,
        iomapper_config={
            "input_fields": [
                "sender_email_address",
                "recipient_email_address",

```

----------------------------------------

TITLE: Define Agent State Dataclass (Python)
DESCRIPTION: Defines a Python dataclass `State` that combines `InputState` and `OutputState` and adds fields for tracking the agent's progress, outline, related topics, perspectives, article content, references, and topic validation status.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/andrestorres123-breeze-agent.txt#_snippet_31

LANGUAGE: Python
CODE:
```
@dataclass
class State(InputState, OutputState):
    """Represents the complete state of the agent."""

    is_last_step: IsLastStep = field(default=False)
    outline: Optional[Outline] = field(default=None)
    related_topics: Optional[RelatedTopics] = field(default=None)
    perspectives: Optional[Perspectives] = field(default=None)
    article: Optional[str] = field(default=None)
    references: Annotated[Optional[dict], field(default=None)] = None
    topic: TopicValidation = field(default_factory=default_topic_validation)
```

----------------------------------------

TITLE: Compiling LangGraph Workflow
DESCRIPTION: Compiles the defined `workflow` graph into an executable agent. The `store` is passed during compilation, making it available to nodes within the graph that require access to memory or state storage.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/nirdiamant-genai_agents (13).txt#_snippet_10

LANGUAGE: Python
CODE:
```
# Compile the graph
agent = workflow.compile(store=store)
```

----------------------------------------

TITLE: Building and Compiling the LangGraph Workflow
DESCRIPTION: This code initializes a `StateGraph` with the defined `PlanExecute` state. It adds the `planner`, `agent`, and `replan` functions as nodes. It then defines the workflow edges, starting from `START` to `planner`, then `planner` to `agent`, `agent` to `replan`, and finally a conditional edge from `replan` that uses `should_end` to transition to either `agent` or `END`. The graph is then compiled into an executable `app`.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/Plan-and-Execute.md#_snippet_10

LANGUAGE: python
CODE:
```
workflow = StateGraph(PlanExecute)

# Add nodes
workflow.add_node("planner", plan_step)
workflow.add_node("agent", execute_step)
workflow.add_node("replan", replan_step)

# Define workflow paths
workflow.add_edge(START, "planner")
workflow.add_edge("planner", "agent")
workflow.add_edge("agent", "replan")
workflow.add_conditional_edges(
    "replan",
    should_end,
    ["agent", END],
)

# Compile the graph
app = workflow.compile()
```

----------------------------------------

TITLE: Building the LangGraph Workflow (Python)
DESCRIPTION: Demonstrates how to build the workflow graph for the SQL agent using LangGraph's `StateGraph`. It initializes the graph with the `AgentState`, adds nodes corresponding to different steps (`analyze_question`, `generate_query`, `execute_query`, `format_response`), defines the edges connecting these nodes sequentially from `START` to `END`, and compiles the graph into a runnable agent.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/An agent for interacting with a SQL database.md#_snippet_10

LANGUAGE: Python
CODE:
```
# Build the workflow graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("analyze_question", analyze_question)
workflow.add_node("generate_query", generate_query)
workflow.add_node("execute_query", execute_query)
workflow.add_node("format_response", format_response)

# Define edges
workflow.add_edge(START, "analyze_question")
workflow.add_edge("analyze_question", "generate_query")
workflow.add_edge("generate_query", "execute_query")
workflow.add_edge("execute_query", "format_response")
workflow.add_edge("format_response", END)

# Compile the workflow
sql_agent = workflow.compile()
```

----------------------------------------

TITLE: Initialize Agent Workflow (Python)
DESCRIPTION: Imports necessary Python libraries for UUID generation, OS interaction, LangGraph state management, and the custom multi-agent builder. Initializes a MemorySaver checkpointer and compiles the supervisor-led agent graph. Prints the version of the `open_deep_research` package.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/libs/langchain-ai-open_deep_research.txt#_snippet_41

LANGUAGE: python
CODE:
```
import uuid 
import os, getpass
import open_deep_research   
print(open_deep_research.__version__) 
from IPython.display import Image, display, Markdown
from langgraph.checkpoint.memory import MemorySaver
from open_deep_research.multi_agent import supervisor_builder

# Create a MemorySaver for checkpointing the agent's state
# This enables tracking and debugging of the multi-agent interaction
checkpointer = MemorySaver()
agent = supervisor_builder.compile(name="research_team", checkpointer=checkpointer)
```

----------------------------------------

TITLE: Building LangGraph Workflow (Python)
DESCRIPTION: Constructs the LangGraph workflow by initializing a StateGraph with the defined State. It adds the call_model node as "agent" and the tool_node as "action". It sets the entry point from START to "agent", adds conditional edges from "agent" based on the should_continue function's output, and adds a direct edge from "action" back to "agent". Finally, it compiles the graph into a runnable application.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/How to run a graph asynchronously.md#_snippet_5

LANGUAGE: python
CODE:
```
# Define a new graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

# Set the entrypoint
workflow.add_edge(START, "agent")

# Add conditional edges
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END,
    },
)

# Add normal edge from action back to agent
workflow.add_edge("action", "agent")

# Compile the graph
app = workflow.compile()
```

----------------------------------------

TITLE: Defining Initial Agent State (Python)
DESCRIPTION: Defines the initial state dictionary (`state_input`) required to start the LangGraph agent workflow. It includes parameters like project description, team, iteration limits, and empty lists for tracking results.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/project_manager_assistant_agent.ipynb#_snippet_20

LANGUAGE: python
CODE:
```
# Definition of the AgentState 
state_input = {
    "project_description": project_description,
    "team": team,
    "insights": "",
    "iteration_number": 0,
    "max_iteration": 3,
    "schedule_iteration": [],
    "task_allocations_iteration": [],
    "risks_iteration": [],
    "project_risk_score_iterations": []
}
```

----------------------------------------

TITLE: Build LangGraph State Machine
DESCRIPTION: Constructs the LangGraph state machine. It initializes a StateGraph with the defined AgentState, adds nodes for the supervisor and each agent, defines edges connecting agents back to the supervisor, sets up conditional edges from the supervisor based on its output, and compiles the graph.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/menonpg-agentic_search_openai_langgraph.txt#_snippet_22

LANGUAGE: Python
CODE:
```
import json
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from agents import AgentState, create_supervisor, create_search_agent, create_insights_researcher_agent, get_members

def build_graph():
    supervisor_chain = create_supervisor()
    search_node = create_search_agent()
    insights_research_node = create_insights_researcher_agent()

    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("Supervisor", supervisor_chain)
    graph_builder.add_node("Web_Searcher", search_node)
    graph_builder.add_node("Insight_Researcher", insights_research_node)

    members = get_members()
    for member in members:
        graph_builder.add_edge(member, "Supervisor")

    conditional_map = {k: k for k in members}
    conditional_map["FINISH"] = END
    graph_builder.add_conditional_edges("Supervisor", lambda x: x["next"], conditional_map)
    graph_builder.set_entry_point("Supervisor")

    graph = graph_builder.compile()

    return graph
```

----------------------------------------

TITLE: Defining LangGraph State for H2O Agent (Python)
DESCRIPTION: Defines the `GraphState` TypedDict, which specifies the structure and types of the state object used to manage data and context throughout the LangGraph workflow for the H2O AutoML agent.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/business-science-ai-data-science-team (2).txt#_snippet_17

LANGUAGE: Python
CODE:
```
class GraphState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]
        user_instructions: str
        recommended_steps: str
        data_raw: dict
        leaderboard: dict
        best_model_id: str
        model_path: str
        model_results: dict
        target_variable: str
        all_datasets_summary: str
        h2o_train_function: str
        h2o_train_function_path: str
        h2o_train_file_name: str
        h2o_train_function_name: str
        h2o_train_error: str
        max_retries: int
        retry_count: int
```

----------------------------------------

TITLE: Build Basic LangGraph ReAct Agent Python
DESCRIPTION: Constructs a simple ReAct-style agent using LangGraph. It defines a search tool, integrates it with an Anthropic model, sets up a graph with 'agent' and 'action' nodes, and defines edges for the workflow. This initial agent uses the full conversation history from the state.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/docs/docs/how-tos/memory/manage-conversation-history.ipynb#_snippet_2

LANGUAGE: python
CODE:
```
from typing import Literal

from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode

memory = MemorySaver()


@tool
def search(query: str):
    """Call to surf the web."""
    # This is a placeholder for the actual implementation
    # Don't let the LLM know this though 😊
    return "It's sunny in San Francisco, but you better look out if you're a Gemini 😈."


tools = [search]
tool_node = ToolNode(tools)
model = ChatAnthropic(model_name="claude-3-haiku-20240307")
bound_model = model.bind_tools(tools)


def should_continue(state: MessagesState):
    """Return the next node to execute."""
    last_message = state["messages"][-1]
    # If there is no function call, then we finish
    if not last_message.tool_calls:
        return END
    # Otherwise if there is, we continue
    return "action"


# Define the function that calls the model
def call_model(state: MessagesState):
    response = bound_model.invoke(state["messages"])
    # We return a list, because this will get added to the existing list
    return {"messages": response}


# Define a new graph
workflow = StateGraph(MessagesState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.add_edge(START, "agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
    # Next, we pass in the path map - all the possible nodes this edge could go to
    ["action", END],
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("action", "agent")

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
app = workflow.compile(checkpointer=memory)
```

----------------------------------------

TITLE: Invoke LangGraph Agent Stream (Python)
DESCRIPTION: Invokes the `simple_graph_plan` agent with a given state input and configuration. It streams updates, printing the name of the current node being processed during execution, and finally retrieves the complete final state of the graph.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/project_manager_assistant_agent.ipynb#_snippet_26

LANGUAGE: python
CODE:
```
# Invoke the agent
config = {"configurable": {"thread_id": "2"}}
for event in simple_graph_plan.stream(state_input, config, stream_mode=["updates"]):
    "Print the different nodes as the agent progresses"
    print(f"Current node: {next(iter(event[1]))}")
    
simple_final_state = simple_graph_plan.get_state(config).values
```

----------------------------------------

TITLE: Build LangGraph StateGraph with Custom Agents (Python)
DESCRIPTION: Constructs a LangGraph `StateGraph` using the custom agent functions defined previously. It initializes the graph with a message-based state, adds the agent functions as nodes, and sets the starting point of the graph's execution.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/How to build a multi-agent network.md#_snippet_3

LANGUAGE: python
CODE:
```
from langgraph.graph import StateGraph, START

# Create a state graph with message-based state
builder = StateGraph(MessagesState)

# Add agent nodes
builder.add_node("travel_advisor", travel_advisor)
builder.add_node("hotel_advisor", hotel_advisor)

# Define the starting point (conversation begins with travel advisor)
builder.add_edge(START, "travel_advisor")

# Compile the graph
graph = builder.compile()
```

----------------------------------------

TITLE: Defining and Compiling LangGraph Workflow - Python
DESCRIPTION: Initializes a `StateGraph` with the defined `State`, adds the `human_node` to the graph, sets the `human_node` as the starting point, compiles the workflow into an executable graph, and assigns a name for identification in tools like LangSmith.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/langchain-ai-agent-inbox-langgraph-example.txt#_snippet_7

LANGUAGE: Python
CODE:
```
# Define a new graph
workflow = StateGraph(State)

# Add the node to the graph. This node will interrupt when it is invoked.
workflow.add_node("human_node", human_node)

# Set the entrypoint as `human_node` so the first node will interrupt
workflow.add_edge("__start__", "human_node")

# Compile the workflow into an executable graph
graph = workflow.compile()
graph.name = "Agent Inbox Example"  # This defines the custom name in LangSmith
```

----------------------------------------

TITLE: Building LangGraph Workflow (Python)
DESCRIPTION: Constructs the stateful graph using `StateGraph` from LangGraph. It defines the graph state schema using a `TypedDict` with message history, adds previously defined 'plan_and_schedule' and 'joiner' components as nodes, sets up a directed edge from planning to joiner, and creates a conditional edge from the joiner to either end the graph or loop back to planning based on the output.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/LLMCompiler.md#_snippet_23

LANGUAGE: Python
CODE:
```
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from typing import Annotated


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

# 1.  Define vertices
# We defined plan_and_schedule above already
# Assign each node to a state variable to update
graph_builder.add_node("plan_and_schedule", plan_and_schedule)
graph_builder.add_node("join", joiner)


## Define edges
graph_builder.add_edge("plan_and_schedule", "join")

### This condition determines looping logic


def should_continue(state):
    messages = state["messages"]
    if isinstance(messages[-1], AIMessage):
        return END
    return "plan_and_schedule"


graph_builder.add_conditional_edges(
    "join",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
)
graph_builder.add_edge(START, "plan_and_schedule")
chain = graph_builder.compile()
```

----------------------------------------

TITLE: Defining Explicit Agent Workflow (Python)
DESCRIPTION: Builds a basic LangGraph `StateGraph` defining a fixed sequential workflow. Execution starts at `agent_1` and always transitions to `agent_2` via explicitly added edges. Requires LangGraph, LangChain, ChatOpenAI. Input: MessagesState. Output: StateGraph builder object (before compiling).

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/Multi-agent Systems.md#_snippet_8

LANGUAGE: python
CODE:
```
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START

model = ChatOpenAI()

def agent_1(state: MessagesState):
    response = model.invoke(...)
    return {"messages": [response]}

def agent_2(state: MessagesState):
    response = model.invoke(...)
    return {"messages": [response]}

builder = StateGraph(MessagesState)
builder.add_node(agent_1)
builder.add_node(agent_2)
# Define the flow explicitly
builder.add_edge(START, "agent_1")
builder.add_edge("agent_1", "agent_2")
```

----------------------------------------

TITLE: Define LangGraph State and Environment (Python)
DESCRIPTION: Imports necessary modules for the LangGraph state and agent interactions, sets environment variables for LangSmith tracing, initializes a LangSmith client, and defines the State TypedDict structure used to manage the graph's state throughout execution.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/alidhl-multi-agent-chatbot.txt#_snippet_2

LANGUAGE: python
CODE:
```
from typing import List, Tuple, Annotated, TypedDict
import operator
from agents.planner import get_planner, get_replanner
from agents.executor import get_executor
from agents.planner import Response
from langgraph.graph import StateGraph, END

import os
from uuid import uuid4
from langsmith import Client

unique_id = uuid4().hex[0:8]
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "multi-agent-search"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
client = Client()
# Define the State
class State(TypedDict):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str

```

----------------------------------------

TITLE: Building LangGraph Workflow Structure (Python)
DESCRIPTION: Demonstrates how to add nodes and define edges, including a conditional edge, to a LangGraph workflow. It also shows how to set the entry point and compile the graph with a checkpointer.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/project_manager_assistant_agent.ipynb#_snippet_17

LANGUAGE: python
CODE:
```
# Add nodes to the workflow
workflow.add_node("task_generation", task_generation_node)
workflow.add_node("task_dependencies", task_dependency_node)
workflow.add_node("task_scheduler", task_scheduler_node)
workflow.add_node("task_allocator", task_allocation_node)
workflow.add_node("risk_assessor", risk_assessment_node)
workflow.add_node("insight_generator", insight_generation_node)

# Add edges to the workflow
workflow.set_entry_point("task_generation")
workflow.add_edge("task_generation", "task_dependencies")
workflow.add_edge("task_dependencies", "task_scheduler")
workflow.add_edge("task_scheduler", "task_allocator")
workflow.add_edge("task_allocator", "risk_assessor")
workflow.add_conditional_edges("risk_assessor", router, ["insight_generator", END])
workflow.add_edge("insight_generator", "task_scheduler")

# Set up memory
memory = MemorySaver()

# Compile the workflow
graph_plan = workflow.compile(checkpointer=memory)
```

----------------------------------------

TITLE: Define LangGraph State for Feature Engineering Agent - Python
DESCRIPTION: Defines the `GraphState` TypedDict used to manage the state passed between nodes in a LangGraph workflow. It includes fields for messages, user instructions, recommended steps, raw/engineered data, target variable, data summaries, feature engineering function details, error handling, and retry counts.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/business-science-ai-data-science-team.txt#_snippet_116

LANGUAGE: Python
CODE:
```
class GraphState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_instructions: str
    recommended_steps: str
    data_raw: dict
    data_engineered: dict
    target_variable: str
    all_datasets_summary: str
    feature_engineer_function: str
    feature_engineer_function_path: str
    feature_engineer_file_name: str
    feature_engineer_function_name: str
    feature_engineer_error: str
    max_retries: int
    retry_count: int
```

----------------------------------------

TITLE: Creating Email Agent Workflow (LangGraph/Python)
DESCRIPTION: Defines a Python function `create_email_agent` that constructs a LangGraph workflow for processing emails. It sets up nodes for 'triage' (using procedural memory) and a 'response_agent' (a ReAct agent), defines the edges for routing based on the triage result, and compiles the graph for execution. It requires `StateGraph`, `State`, `triage_email_with_procedural_memory`, `create_react_agent`, `tools`, `create_agent_prompt`, `store`, `llm`, `START`, `route_based_on_triage`, and `END` to be defined elsewhere.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/nirdiamant-genai_agents (13).txt#_snippet_18

LANGUAGE: Python
CODE:
```
def create_email_agent(store):
    # Define the workflow
    workflow = StateGraph(State)
    workflow.add_node("triage", lambda state, config: triage_email_with_procedural_memory(state, config, store))

    # Create a fresh response agent that will use the latest prompts
    response_agent = create_react_agent(
        tools=tools,
        prompt=create_agent_prompt,
        store=store,
        model=llm
    )

    workflow.add_node("response_agent", response_agent)

    # The routing logic remains the same
    workflow.add_edge(START, "triage")
    workflow.add_conditional_edges("triage", route_based_on_triage,
                                {
                                    "response_agent": "response_agent",
                                    END: END
                                })

    # Compile and return the graph
    return workflow.compile(store=store)
```

----------------------------------------

TITLE: Constructing a LangGraph Agent Workflow (Python)
DESCRIPTION: Initializes a StateGraph, adds 'agent' and 'tools' nodes, optionally adds a 'pre_model_hook' and 'generate_structured_response' node, sets the entry point, and defines conditional edges for routing based on the 'should_continue' function.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/src/libs/langchain-ai-langgraph prebuilt.txt#_snippet_34

LANGUAGE: python
CODE:
```
# Define a new graph
workflow = StateGraph(state_schema or AgentState, config_schema=config_schema)

# Define the two nodes we will cycle between
workflow.add_node(
    "agent", RunnableCallable(call_model, acall_model), input=input_schema
)
workflow.add_node("tools", tool_node)

# Optionally add a pre-model hook node that will be called
# every time before the "agent" (LLM-calling node)
if pre_model_hook is not None:
    workflow.add_node("pre_model_hook", pre_model_hook)
    workflow.add_edge("pre_model_hook", "agent")
    entrypoint = "pre_model_hook"
else:
    entrypoint = "agent"

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point(entrypoint)

# Add a structured output node if response_format is provided
if response_format is not None:
    workflow.add_node(
        "generate_structured_response",
        RunnableCallable(
            generate_structured_response, agenerate_structured_response
        ),
    )
    workflow.add_edge("generate_structured_response", END)
    should_continue_destinations = ["tools", "generate_structured_response"]
else:
    should_continue_destinations = ["tools", END]

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
    path_map=should_continue_destinations,
)
```

----------------------------------------

TITLE: Building the Research Team Graph in LangGraph
DESCRIPTION: Constructs a LangGraph graph specifically for a research team. It includes a supervisor node and specialized agent nodes for searching and web scraping, defining the edges and workflow to route tasks between them and back to the supervisor based on the state.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/Hierarchical Agent Teams.md#_snippet_4

LANGUAGE: python
CODE:
```
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Initialize language model
llm = ChatOpenAI(model="gpt-4o")

# Create individual agents with their specialized tools
search_agent = create_react_agent(llm, tools=[tavily_tool])
web_scraper_agent = create_react_agent(llm, tools=[scrape_webpages])

# Build the research team graph
research_builder = StateGraph(State)
research_builder.add_node("supervisor", make_supervisor_node(llm, ["search", "web_scraper"]))
research_builder.add_node("search", lambda state: search_agent.invoke(state))
research_builder.add_node("web_scraper", lambda state: web_scraper_agent.invoke(state))

# Define the workflow
research_builder.add_edge("START", "supervisor")
research_builder.add_edge("supervisor", "search")
research_builder.add_edge("supervisor", "web_scraper")
research_builder.add_edge("search", "supervisor")
research_builder.add_edge("web_scraper", "supervisor")
research_builder.add_edge("supervisor", "END")

# Compile the graph
research_graph = research_builder.compile()
```

----------------------------------------

TITLE: Initializing LangGraph StateGraph (Python)
DESCRIPTION: This line initializes a StateGraph object from the LangGraph library. The StateGraph is the core component for defining the workflow structure and managing the state transitions between nodes.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/nirdiamant-genai_agents (12).txt#_snippet_18

LANGUAGE: Python
CODE:
```
builder = StateGraph(State)
```

----------------------------------------

TITLE: Construct LangGraph Workflow - Python
DESCRIPTION: Initializes the StateGraph with the MessagesState, adds the supervisor and worker nodes, and defines the starting point and edges to connect the supervisor to the other nodes.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/Multi-agent supervisor.md#_snippet_5

LANGUAGE: python
CODE:
```
builder = StateGraph(MessagesState)
builder.add_node("supervisor", supervisor_node)
builder.add_node("researcher", research_node)
builder.add_node("coder", code_node)
builder.add_edge(START, "supervisor")
graph = builder.compile()
```

----------------------------------------

TITLE: Creating a LangGraph State Graph with Agent Nodes (Python)
DESCRIPTION: Defines the `create_graph` function which initializes a `StateGraph` and adds nodes for different agents (Planner, Selector, Reporter, Reviewer, Router). Each node is associated with a lambda function that invokes the corresponding agent, passing necessary state information and configuration parameters. This function sets up the structure for the agent workflow.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/john-adeojo-graph_websearch_agent.txt#_snippet_14

LANGUAGE: python
CODE:
```
def create_graph(server=None, model=None, stop=None, model_endpoint=None, temperature=0):
    graph = StateGraph(AgentGraphState)

    graph.add_node(
        "planner", 
        lambda state: PlannerAgent(
            state=state,
            model=model,
            server=server,
            guided_json=planner_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            research_question=state["research_question"],
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
            # previous_plans=lambda: get_agent_graph_state(state=state, state_key="planner_all"),
            prompt=planner_prompt_template
        )
    )

    graph.add_node(
        "selector",
        lambda state: SelectorAgent(
            state=state,
            model=model,
            server=server,
            guided_json=selector_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            research_question=state["research_question"],
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
            previous_selections=lambda: get_agent_graph_state(state=state, state_key="selector_all"),
            serp=lambda: get_agent_graph_state(state=state, state_key="serper_latest"),
            prompt=selector_prompt_template,
        )
    )

    graph.add_node(
        "reporter", 
        lambda state: ReporterAgent(
            state=state,
            model=model,
            server=server,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            research_question=state["research_question"],
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
            previous_reports=lambda: get_agent_graph_state(state=state, state_key="reporter_all"),
            research=lambda: get_agent_graph_state(state=state, state_key="scraper_latest"),
            prompt=reporter_prompt_template
        )
    )

    graph.add_node(
        "reviewer", 
        lambda state: ReviewerAgent(
            state=state,
            model=model,
            server=server,
            guided_json=reviewer_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            research_question=state["research_question"],
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_all"),
            # planner=lambda: get_agent_graph_state(state=state, state_key="planner_latest"),
            # selector=lambda: get_agent_graph_state(state=state, state_key="selector_latest"),
            reporter=lambda: get_agent_graph_state(state=state, state_key="reporter_latest"),
            # planner_agent=planner_prompt_template,
            # selector_agent=selector_prompt_template,
            # reporter_agent=reporter_prompt_template,
            # serp=lambda: get_agent_graph_state(state=state, state_key="serper_latest"),
            prompt=reviewer_prompt_template
        )
    )

    graph.add_node(
        "router", 
        lambda state: RouterAgent(
            state=state,
            model=model,
            server=server,
            guided_json=router_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            research_question=state["research_question"],
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_all"),
            # planner=lambda: get_agent_graph_state(state=state, state_key="planner_latest"),
            # selector=lambda: get_agent_graph_state(state=state, state_key="selector_latest"),

```

----------------------------------------

TITLE: Building LangGraph with InjectedState Tool | Python
DESCRIPTION: Constructs a LangGraph agent graph using `create_react_agent`, incorporating the `get_context` tool that uses injected state and setting up a memory checkpointer for managing graph state persistence across turns.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/How to pass runtime values to tools.md#_snippet_3

LANGUAGE: python
CODE:
```
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode, create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# Initialize language model
model = ChatOpenAI(model="gpt-4o", temperature=0)

# Define tools that will use injected state
tools = [get_context]

# Create a tool node to handle tool execution
tool_node = ToolNode(tools)

# Set up persistent storage
checkpointer = MemorySaver()

# Create the agent graph
graph = create_react_agent(model, tools, state_schema=State, checkpointer=checkpointer)
```

----------------------------------------

TITLE: Creating LangGraph Workflow with Conditional Edges in Python
DESCRIPTION:  Constructs a LangGraph workflow that defines the state transitions between nodes. It adds 'solver' and 'evaluate' nodes, sets up initial edges, and defines a conditional edge from 'evaluate' that sends the flow back to the 'solver' if the solution is not successful, or ends the graph execution if it passes.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/Competitive Programming.md#_snippet_13

LANGUAGE: python
CODE:
```
from langgraph.graph import END, StateGraph, START



builder = StateGraph(State)

builder.add_node("solver", solver)

builder.add_edge(START, "solver")

builder.add_node("evaluate", evaluate)

builder.add_edge("solver", "evaluate")



def control_edge(state: State):

    if state.get("status") == "success":

        return END

    return "solver"



builder.add_conditional_edges("evaluate", control_edge, {END: END, "solver": "solver"})

graph = builder.compile()
```

----------------------------------------

TITLE: Define Assistant Graph State - Python
DESCRIPTION: Defines a TypedDict `AssistantGraphState` to represent the state managed by the langgraph workflow. It includes fields for the user's question, collected required information, message history, and verification status.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/emarco177-langgraph-customer-support.txt#_snippet_18

LANGUAGE: Python
CODE:
```
class AssistantGraphState(TypedDict):

    user_question: str
    required_information: RequiredInformation
    messages: Annotated[list, add_messages]
    verified: bool
```

----------------------------------------

TITLE: Defining Qualitative Answer Graph State - Python
DESCRIPTION: Defines a `TypedDict` named `QualitativeAnswerGraphState` to represent the state managed by the qualitative answer LangGraph workflow. It includes fields for the user's question, the retrieved context, and the generated answer.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/nirdiamant-controllable-rag-agent.txt#_snippet_38

LANGUAGE: Python
CODE:
```
class QualitativeAnswerGraphState(TypedDict):
        """
        Represents the state of our graph.

        """

        question: str
        context: str
        answer: str
```

----------------------------------------

TITLE: Implementing Task Generation Node - LangGraph - Python
DESCRIPTION: This LangGraph node function takes the current agent state, extracts the project description, uses an LLM configured for structured output (TaskList) to generate a list of tasks, updates the 'tasks' field in the state, and returns the modified state for the next node in the graph. Requires an 'llm' object configured externally.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/project_manager_assistant_agent.ipynb#_snippet_7

LANGUAGE: Python
CODE:
```
def task_generation_node(state: AgentState):
 """LangGraph node that will extract tasks from given project description"""
    description = state["project_description"]
    prompt = f"""You are an experienced project description analyzer. Analyze the 
    project description '{description}' and create a list of actionable and
    realistic tasks with estimated time (in days) to complete each task.
    If the task takes longer than 5 days, break it down into independent smaller tasks.
    """
    structure_llm = llm.with_structured_output(TaskList)
    tasks: TaskList = structure_llm.invoke(prompt)
    state['tasks'] = tasks
    return state
```

----------------------------------------

TITLE: Define Self-Discover Agent Graph Langgraph Python
DESCRIPTION: Defines the state schema for the LangGraph, initializes an OpenAI chat model, and creates functions (`select`, `adapt`, `structure`, `reason`) representing the graph's nodes by chaining prompts with the model. It then constructs the LangGraph, adding nodes and edges to define the workflow.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/docs/docs/tutorials/self-discover/self-discover.ipynb#_snippet_3

LANGUAGE: python
CODE:
```
from typing import Optional
from typing_extensions import TypedDict

from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from langgraph.graph import END, START, StateGraph


class SelfDiscoverState(TypedDict):
    reasoning_modules: str
    task_description: str
    selected_modules: Optional[str]
    adapted_modules: Optional[str]
    reasoning_structure: Optional[str]
    answer: Optional[str]


model = ChatOpenAI(temperature=0, model="gpt-4-turbo-preview")


def select(inputs):
    select_chain = select_prompt | model | StrOutputParser()
    return {"selected_modules": select_chain.invoke(inputs)}


def adapt(inputs):
    adapt_chain = adapt_prompt | model | StrOutputParser()
    return {"adapted_modules": adapt_chain.invoke(inputs)}


def structure(inputs):
    structure_chain = structured_prompt | model | StrOutputParser()
    return {"reasoning_structure": structure_chain.invoke(inputs)}


def reason(inputs):
    reasoning_chain = reasoning_prompt | model | StrOutputParser()
    return {"answer": reasoning_chain.invoke(inputs)}


graph = StateGraph(SelfDiscoverState)
graph.add_node(select)
graph.add_node(adapt)
graph.add_node(structure)
graph.add_node(reason)
graph.add_edge(START, "select")
graph.add_edge("select", "adapt")
graph.add_edge("adapt", "structure")
graph.add_edge("structure", "reason")
graph.add_edge("reason", END)
app = graph.compile()
```

----------------------------------------

TITLE: Initializing LangGraph Workflow - Python
DESCRIPTION: Starts the process of building the LangGraph workflow by initializing a `StateGraph` with the defined `GraphState`. This graph will orchestrate the flow between the various nodes and decision points.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/Self-RAG.md#_snippet_9

LANGUAGE: python
CODE:
```
from langgraph.graph import END, StateGraph, START

# Create workflow graph
workflow = StateGraph(GraphState)
```

----------------------------------------

TITLE: Defining Basic Assistant Graph (Python)
DESCRIPTION: Defines a simple LangGraph StateGraph for the assistant's part of the workflow. It uses `MessagesState` to manage conversation history, adds the `call_model` function as a node, and defines a direct edge from the start of the graph to the `call_model` node and then to the end.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/langchain-ai-langgraph-reflection.txt#_snippet_15

LANGUAGE: python
CODE:
```
assistant_graph = (
    StateGraph(MessagesState)
    .add_node(call_model)
    .add_edge(START, "call_model")
    .add_edge("call_model", END)
    .compile()
)
```

----------------------------------------

TITLE: Building Simulation LangGraph Workflow | Python
DESCRIPTION: Constructs the LangGraph `StateGraph` that orchestrates the agent simulation. It defines a `State` TypedDict for the graph state (using `add_messages` annotation for list appending), adds the 'user' and 'chat_bot' nodes defined previously, creates a fixed edge directing output from 'chat_bot' to 'user', and adds a conditional edge from 'user' that uses the `should_continue` function to route to either 'chat_bot' (continue) or `END` (terminate).

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/Chat Bot Evaluation as Multi-agent Simulation.md#_snippet_8

LANGUAGE: python
CODE:
```
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from typing import Annotated
from typing_extensions import TypedDict


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)
graph_builder.add_node("user", simulated_user_node)
graph_builder.add_node("chat_bot", chat_bot_node)
# Every response from  your chat bot will automatically go to the
# simulated user
graph_builder.add_edge("chat_bot", "user")
graph_builder.add_conditional_edges(
    "user",
    should_continue,
    # If the finish criteria are met, we will stop the simulation,
    # otherwise, the virtual user's message will be sent to your chat bot
    {
        "end": END,
        "continue": "chat_bot",
    },
)
```

----------------------------------------

TITLE: Building LangGraph Workflow for ReAct Agent (Python)
DESCRIPTION: Constructs the LangGraph workflow by creating a `StateGraph`, adding the defined `agent` (model call) and `tools` (tool execution) nodes. It sets the initial entry point to the `agent` node, defines a conditional edge from `agent` to either `tools` or `END` based on the `should_continue` function, and adds a regular edge from `tools` back to `agent` to form the ReAct loop. Finally, it compiles the graph for execution.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/How to create a ReAct agent from scratch.md#_snippet_4

LANGUAGE: python
CODE:
```
from langgraph.graph import StateGraph, END

# Define a new graph
workflow = StateGraph(AgentState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point("agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
    # Finally we pass in a mapping.
    # The keys are strings, and the values are other nodes.
    # END is a special node marking that the graph should finish.
    # What will happen is we will call `should_continue`, and then the output of that
    # will be matched against the keys in this mapping.
    # Based on which one it matches, that node will then be called.
    {
        # If `tools`, then we call the tool node.
        "continue": "tools",
        # Otherwise we finish.
        "end": END,
    },
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("tools", "agent")

# Now we can compile and visualize our graph
graph = workflow.compile()
```

----------------------------------------

TITLE: Building LangGraph State Graph Python
DESCRIPTION: Constructs the state graph for handling requests. Initializes the client connection to the AGP gateway as part of the graph setup.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/agntcy-agentic-apps (6).txt#_snippet_22

LANGUAGE: python
CODE:
```
async def build_graph() -> Any:
    """
    Constructs the state graph for handling requests.

    Returns:
        StateGraph: A compiled LangGraph state graph.
    """
    await init_client_gateway_conn(remote_agent=Config.remote_agent)
```

----------------------------------------

TITLE: Define and Build LangGraph Workflow
DESCRIPTION: Initializes a StateGraph, adds the 'agent' and 'action' nodes, defines a conditional edge from 'agent' based on tool calls, and adds a direct edge from 'action' back to 'agent'.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/whitew1994ww-langgraphreceptionisttutorial.txt#_snippet_8

LANGUAGE: python
CODE:
```
# Graph 
caller_workflow = StateGraph(MessagesState)

# Add Nodes
caller_workflow.add_node("agent", call_caller_model)
caller_workflow.add_node("action", tool_node)

# Add Edges
caller_workflow.add_conditional_edges(
    "agent",
    should_continue_caller,
    {
        "continue": "action",
        "end": END,
    },
)
caller_workflow.add_edge("action", "agent")
```

----------------------------------------

TITLE: Building Parallel Workflow with LangGraph API in Python
DESCRIPTION: This snippet demonstrates constructing a parallel LLM workflow using the LangGraph StateGraph API. It defines a state to manage inputs and outputs, creates nodes for individual parallel LLM calls and a final aggregation step, adds nodes and edges to connect them for parallel execution followed by aggregation, compiles the graph, and shows how to invoke it with an initial topic.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/docs/docs/tutorials/workflows/index.md#_snippet_0

LANGUAGE: python
CODE:
```
# Graph state
class State(TypedDict):
    topic: str
    joke: str
    story: str
    poem: str
    combined_output: str


# Nodes
def call_llm_1(state: State):
    """First LLM call to generate initial joke"""

    msg = llm.invoke(f"Write a joke about {state['topic']}")
    return {"joke": msg.content}


def call_llm_2(state: State):
    """Second LLM call to generate story"""

    msg = llm.invoke(f"Write a story about {state['topic']}")
    return {"story": msg.content}


def call_llm_3(state: State):
    """Third LLM call to generate poem"""

    msg = llm.invoke(f"Write a poem about {state['topic']}")
    return {"poem": msg.content}


def aggregator(state: State):
    """Combine the joke and story into a single output"""

    combined = f"Here's a story, joke, and poem about {state['topic']}!\n\n"
    combined += f"STORY:\n{state['story']}\n\n"
    combined += f"JOKE:\n{state['joke']}\n\n"
    combined += f"POEM:\n{state['poem']}"
    return {"combined_output": combined}


# Build workflow
parallel_builder = StateGraph(State)

# Add nodes
parallel_builder.add_node("call_llm_1", call_llm_1)
parallel_builder.add_node("call_llm_2", call_llm_2)
parallel_builder.add_node("call_llm_3", call_llm_3)
parallel_builder.add_node("aggregator", aggregator)

# Add edges to connect nodes
parallel_builder.add_edge(START, "call_llm_1")
parallel_builder.add_edge(START, "call_llm_2")
parallel_builder.add_edge(START, "call_llm_3")
parallel_builder.add_edge("call_llm_1", "aggregator")
parallel_builder.add_edge("call_llm_2", "aggregator")
parallel_builder.add_edge("call_llm_3", "aggregator")
parallel_builder.add_edge("aggregator", END)
parallel_workflow = parallel_builder.compile()

# Show workflow
display(Image(parallel_workflow.get_graph().draw_mermaid_png()))

# Invoke
state = parallel_workflow.invoke({"topic": "cats"})
print(state["combined_output"])
```

----------------------------------------

TITLE: Implementing Custom Multi-Agent Graph with Handoffs (Python)
DESCRIPTION: Provides a complete Python example demonstrating a custom multi-agent system using LangGraph's `StateGraph` and custom handoff tools. It defines the agents, the handoff tool creation function, structures the graph with agent nodes and transitions, and shows how to execute it with an initial state and query, illustrating manual graph construction with handoffs.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/docs/docs/agents/multi-agent.md#_snippet_7

LANGUAGE: python
CODE:
```
from typing import Annotated
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import create_react_agent, InjectedState
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.types import Command

def create_handoff_tool(*, agent_name: str, description: str | None = None):
    name = f"transfer_to_{agent_name}"
    description = description or f"Transfer to {agent_name}"

    @tool(name, description=description)
    def handoff_tool(
        # highlight-next-line
        state: Annotated[MessagesState, InjectedState], # (1)!
        # highlight-next-line
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": name,
            "tool_call_id": tool_call_id,
        }
        return Command(  # (2)!
            # highlight-next-line
            goto=agent_name,  # (3)!
            # highlight-next-line
            update={"messages": state["messages"] + [tool_message]},  # (4)!
            # highlight-next-line
            graph=Command.PARENT,  # (5)!
        )
    return handoff_tool

# Handoffs
transfer_to_hotel_assistant = create_handoff_tool(
    agent_name="hotel_assistant",
    description="Transfer user to the hotel-booking assistant.",
)
transfer_to_flight_assistant = create_handoff_tool(
    agent_name="flight_assistant",
    description="Transfer user to the flight-booking assistant.",
)

# Simple agent tools
def book_hotel(hotel_name: str):
    """Book a hotel"""
    return f"Successfully booked a stay at {hotel_name}."

def book_flight(from_airport: str, to_airport: str):
    """Book a flight"""
    return f"Successfully booked a flight from {from_airport} to {to_airport}."

# Define agents
flight_assistant = create_react_agent(
    model="anthropic:claude-3-5-sonnet-latest",
    # highlight-next-line
    tools=[book_flight, transfer_to_hotel_assistant],
    prompt="You are a flight booking assistant",
    # highlight-next-line
    name="flight_assistant"
)
hotel_assistant = create_react_agent(
    model="anthropic:claude-3-5-sonnet-latest",
    # highlight-next-line
    tools=[book_hotel, transfer_to_flight_assistant],
    prompt="You are a hotel booking assistant",
    # highlight-next-line
    name="hotel_assistant"
)

# Define multi-agent graph
multi_agent_graph = (
    StateGraph(MessagesState)
    .add_node(flight_assistant)
    .add_node(hotel_assistant)
    .add_edge(START, "flight_assistant")
    .compile()
)

# Run the multi-agent graph
for chunk in multi_agent_graph.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": "book a flight from BOS to JFK and a stay at McKittrick Hotel"
            }
        ]
    }
):
    print(chunk)
    print("\n")
```

----------------------------------------

TITLE: Building and Compiling LangGraph Workflow Python
DESCRIPTION: This code initializes a `StateGraph` with the defined `AgentState`. It adds the previously defined nodes (`agent`, `rewrite`, `generate`) and the `retrieve` node (wrapped in `ToolNode`). It then defines the graph's edges, starting from `START` to `agent`, adding conditional edges based on the agent's decision and the document grading result, and finally connecting `generate` to `END` and `rewrite` back to `agent`. The workflow is then compiled.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/examples/rag/langgraph_agentic_rag.ipynb#_snippet_7

LANGUAGE: python
CODE:
```
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode

# Define a new graph
workflow = StateGraph(AgentState)

# Define the nodes we will cycle between
workflow.add_node("agent", agent)  # agent
retrieve = ToolNode([retriever_tool])
workflow.add_node("retrieve", retrieve)  # retrieval
workflow.add_node("rewrite", rewrite)  # Re-writing the question
workflow.add_node(
    "generate", generate
)  # Generating a response after we know the documents are relevant
# Call agent node to decide to retrieve or not
workflow.add_edge(START, "agent")

# Decide whether to retrieve
workflow.add_conditional_edges(
    "agent",
    # Assess agent decision
    tools_condition,
    {
        # Translate the condition outputs to nodes in our graph
        "tools": "retrieve",
        END: END,
    },
)

# Edges taken after the `action` node is called.
workflow.add_conditional_edges(
    "retrieve",
    # Assess agent decision
    grade_documents,
    {
        "rewrite": "rewrite",
        "generate": "generate",
    }
)
workflow.add_edge("generate", END)
workflow.add_edge("rewrite", "agent")

# Compile
graph = workflow.compile()
```

----------------------------------------

TITLE: Defining LangGraph Agent State with TypedDict
DESCRIPTION: This snippet defines the `AgentState` class using `TypedDict`, which specifies the structure of the state object passed between nodes in the LangGraph workflow. It includes a `messages` field, annotated to automatically add new messages to a sequence of `BaseMessage` objects.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/langchain-ai-langgraph-example-monorepo.txt#_snippet_5

LANGUAGE: Python
CODE:
```
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
```

----------------------------------------

TITLE: Create LangGraph Agent Workflow - Python
DESCRIPTION: Defines and configures a LangGraph `StateGraph` for a plan-and-execute agent. It adds various nodes representing different steps (anonymization, planning, retrieval, answering, task handling, replanning) and defines the edges and conditional transitions between them to form the workflow.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/nirdiamant-controllable-rag-agent.txt#_snippet_71

LANGUAGE: Python
CODE:
```
def create_agent():
    
    agent_workflow = StateGraph(PlanExecute)

    # Add the anonymize node
    agent_workflow.add_node("anonymize_question", anonymize_queries)

    # Add the plan node
    agent_workflow.add_node("planner", plan_step)

    # Add the break down plan node

    agent_workflow.add_node("break_down_plan", break_down_plan_step)

    # Add the deanonymize node
    agent_workflow.add_node("de_anonymize_plan", deanonymize_queries)

    # Add the qualitative chunks retrieval node
    agent_workflow.add_node("retrieve_chunks", run_qualitative_chunks_retrieval_workflow)

    # Add the qualitative summaries retrieval node
    agent_workflow.add_node("retrieve_summaries", run_qualitative_summaries_retrieval_workflow)

    # Add the qualitative book quotes retrieval node
    agent_workflow.add_node("retrieve_book_quotes", run_qualitative_book_quotes_retrieval_workflow)


    # Add the qualitative answer node
    agent_workflow.add_node("answer", run_qualtative_answer_workflow)

    # Add the task handler node
    agent_workflow.add_node("task_handler", run_task_handler_chain)

    # Add a replan node
    agent_workflow.add_node("replan", replan_step)

    # Add answer from context node
    agent_workflow.add_node("get_final_answer", run_qualtative_answer_workflow_for_final_answer)

    # Set the entry point
    agent_workflow.set_entry_point("anonymize_question")

    # From anonymize we go to plan
    agent_workflow.add_edge("anonymize_question", "planner")

    # From plan we go to deanonymize
    agent_workflow.add_edge("planner", "de_anonymize_plan")

    # From deanonymize we go to break down plan

    agent_workflow.add_edge("de_anonymize_plan", "break_down_plan")

    # From break_down_plan we go to task handler
    agent_workflow.add_edge("break_down_plan", "task_handler")

    # From task handler we go to either retrieve or answer
    agent_workflow.add_conditional_edges("task_handler", retrieve_or_answer, {"chosen_tool_is_retrieve_chunks": "retrieve_chunks", "chosen_tool_is_retrieve_summaries":
                                                                            "retrieve_summaries", "chosen_tool_is_retrieve_quotes": "retrieve_book_quotes", "chosen_tool_is_answer": "answer"})

    # After retrieving we go to replan
    agent_workflow.add_edge("retrieve_chunks", "replan")

    agent_workflow.add_edge("retrieve_summaries", "replan")

    agent_workflow.add_edge("retrieve_book_quotes", "replan")

    # After answering we go to replan
    agent_workflow.add_edge("answer", "replan")

    # After replanning we check if the question can be answered, if yes we go to get_final_answer, if not we go to task_handler
    agent_workflow.add_conditional_edges("replan",can_be_answered, {"can_be_answered_already": "get_final_answer", "cannot_be_answered_yet": "break_down_plan"})

    # After getting the final answer we end
    agent_workflow.add_edge("get_final_answer", END)


    plan_and_execute_app = agent_workflow.compile()

    return plan_and_execute_app
```

----------------------------------------

TITLE: Building LangGraph Workflow - LangGraph - Python
DESCRIPTION: Constructs the LangGraph StateGraph, defining the nodes for the agent, structured response processing, and tool execution. Configures the graph's entry point and adds conditional and regular edges to route messages between nodes based on the defined logic.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/How to force tool-calling agent to structure output.md#_snippet_4

LANGUAGE: python
CODE:
```
# Define the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", call_model)
workflow.add_node("respond", respond)
workflow.add_node("tools", ToolNode(tools))

# Set entrypoint
workflow.set_entry_point("agent")

# Add conditional edges
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "respond": "respond",
    },
)

# Add regular edges
workflow.add_edge("tools", "agent")
workflow.add_edge("respond", END)

# Compile the graph
graph = workflow.compile()
```

----------------------------------------

TITLE: Defining LangGraph Workflow (Python)
DESCRIPTION: Initializes a LangGraph StateGraph with the TaskState and adds nodes representing the orchestrator and specialized agents. This sets up the structure for defining transitions and running the workflow.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/emmanuelrtm-magnetic-one-langgraph.txt#_snippet_13

LANGUAGE: Python
CODE:
```
# Create the task execution graph
graph = StateGraph(TaskState)

# Add nodes (agents and orchestrator) to the graph
graph.add_node("Orchestrator", orchestrator_agent)
graph.add_node("WebSurfer", web_surfer_agent)
graph.add_node("FileSurfer", file_surfer_agent)
graph.add_node("Coder", coder_agent)
graph.add_node("ComputerTerminal", computer_terminal_agent)
graph.add_node("FinalReview", finalize_task)
```

----------------------------------------

TITLE: Building a Simple LangGraph Agent - Python
DESCRIPTION: Constructs a basic LangGraph agent workflow that interacts with an Anthropic model and potentially uses a search tool. It defines the agent's nodes and edges, including a conditional edge to decide between tool execution and finishing, using a MessagesState and MemorySaver for state management.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/How to delete messages.md#_snippet_1

LANGUAGE: python
CODE:
```
from typing import Literal

from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode

memory = MemorySaver()

@tool
def search(query: str):
    """Call to surf the web."""
    # This is a placeholder for the actual implementation
    return "It's sunny in San Francisco, but you better look out if you're a Gemini 😈."

tools = [search]
tool_node = ToolNode(tools)
model = ChatAnthropic(model_name="claude-3-haiku-20240307")
bound_model = model.bind_tools(tools)

def should_continue(state: MessagesState):
    """Return the next node to execute."""
    last_message = state["messages"][-1]
    # If there is no function call, then we finish
    if not last_message.tool_calls:
        return END
    # Otherwise if there is, we continue
    return "action"

# Define the function that calls the model
def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    # We return a list, because this will get added to the existing list
    return {"messages": response}

# Define a new graph
workflow = StateGraph(MessagesState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

# Set the entrypoint as `agent`
workflow.add_edge(START, "agent")

# Add a conditional edge
workflow.add_conditional_edges(
    "agent",
    should_continue,
    ["action", END],
)

# Add a normal edge from `tools` to `agent`
workflow.add_edge("action", "agent")

# Compile the graph
app = workflow.compile(checkpointer=memory)
```

----------------------------------------

TITLE: Defining and Compiling LangGraph Workflow
DESCRIPTION: Sets up the LangGraph workflow by creating a StateGraph, adding the previously defined 'researcher' and 'chart_generator' nodes, and defining the initial edge from START to 'researcher'. Finally, it compiles the graph for execution.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/docs/docs/tutorials/multi_agent/multi-agent-collaboration.ipynb#_snippet_9

LANGUAGE: python
CODE:
```
from langgraph.graph import StateGraph, START

workflow = StateGraph(MessagesState)
workflow.add_node("researcher", research_node)
workflow.add_node("chart_generator", chart_node)

workflow.add_edge(START, "researcher")
graph = workflow.compile()
```

----------------------------------------

TITLE: Defining Workflow Execution Function in Python
DESCRIPTION: This function initializes the state for the self-healing code system workflow and invokes the compiled graph. It takes the target function and its arguments as input, captures the function's source code, and passes this information within the initial state to the graph.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/nirdiamant-genai_agents (12).txt#_snippet_22

LANGUAGE: Python
CODE:
```
def execute_self_healing_code_system(function, arguments):

    state = State(
        error=False,
        function=function,
        function_string=inspect.getsource(function),
        arguments=arguments,
    )
    
    return graph.invoke(state)
```

----------------------------------------

TITLE: Assembling the Agentic RAG LangGraph Workflow Python
DESCRIPTION: Initializes a `StateGraph` with the defined `AgentState`. It adds the previously defined node functions (`agent`, `retrieve`, `rewrite`, `generate`) and sets up the conditional edges that define the workflow logic. The graph starts at the `agent` node, transitions to `retrieve` based on `tools_condition`, uses `grade_documents` to decide between `generate` or `rewrite` after retrieval, and ends after `generate` or from the `agent` if no tool is needed. `rewrite` loops back to the `agent`.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/Agentic RAG.md#_snippet_8

LANGUAGE: python
CODE:
```
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode

# Define a new graph
workflow = StateGraph(AgentState)

# Define the nodes we will cycle between
workflow.add_node("agent", agent)  # agent
retrieve = ToolNode([retriever_tool])
workflow.add_node("retrieve", retrieve)  # retrieval
workflow.add_node("rewrite", rewrite)  # Re-writing the question
workflow.add_node(
    "generate", generate
)  # Generating a response after we know the documents are relevant

# Call agent node to decide to retrieve or not
workflow.add_edge(START, "agent")

# Decide whether to retrieve
workflow.add_conditional_edges(
    "agent",
    # Assess agent decision
    tools_condition,
    {
        # Translate the condition outputs to nodes in our graph
        "tools": "retrieve",
        END: END,
    },
)

# Edges taken after the `action` node is called.
workflow.add_conditional_edges(
    "retrieve",
    # Assess agent decision
    grade_documents,
)
workflow.add_edge("generate", END)
workflow.add_edge("rewrite", "agent")

# Compile
graph = workflow.compile()
```

----------------------------------------

TITLE: Modify Agent Tool Call and Resume - Python
DESCRIPTION: Runs the agent workflow up to the breakpoint before tool execution. It retrieves the state, inspects the pending tool call, modifies the arguments of the tool call, updates the state with the modified tool call message, and then resumes execution.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/How to edit graph state.md#_snippet_6

LANGUAGE: python
CODE:
```
# Thread configuration
thread_config = {"configurable": {"thread_id": "agent-thread-1"}}

# Initial user message
initial_messages = [{"role": "user", "content": "Search for information about climate change"}]

# Run until the breakpoint (before tool execution)
print("Running agent until tool execution...")
for event in agent_app.stream({"messages": initial_messages}, thread_config, stream_mode="values"):
    if "messages" in event and event["messages"]:
        last_message = event["messages"][-1]
        print(f"Agent: {last_message.content}")

# Get current state with tool calls
state = agent_app.get_state(thread_config).values
current_message = state["messages"][-1]

# Display the current tool call
print("\nCurrent tool call:")
if hasattr(current_message, "tool_calls") and current_message.tool_calls:
    print(f"Tool: {current_message.tool_calls[0]['name']}")
    print(f"Arguments: {current_message.tool_calls[0]['args']}")

# Modify the tool call arguments
if hasattr(current_message, "tool_calls") and current_message.tool_calls:
    # Change the search query to be more specific
    current_message.tool_calls[0]["args"]["query"] = "recent effects of climate change in polar regions"
    
    # Update the state with the modified message
    agent_app.update_state(thread_config, {"messages": state["messages"]})
    
    print("\nUpdated tool call:")
    print(f"Tool: {current_message.tool_calls[0]['name']}")
    print(f"Arguments: {current_message.tool_calls[0]['args']}")

# Resume execution with the modified tool call
print("\nResuming agent with modified tool call...")
for event in agent_app.stream(None, thread_config, stream_mode="values"):
    if "messages" in event and event["messages"]:
        last_message = event["messages"][-1]
        print(f"Agent: {last_message.content}")
```

----------------------------------------

TITLE: Creating Multi-Agent Swarm Workflow in Python
DESCRIPTION: Constructs a LangGraph StateGraph representing a multi-agent swarm. It incorporates the provided agents as nodes, updates the state schema for 'active_agent', and adds a router to direct execution to the currently active agent. Requires agents to have a 'name' attribute.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/libs/langchain-ai-langgraph-swarm-py.txt#_snippet_98

LANGUAGE: python
CODE:
```
def create_swarm(
    agents: list[Pregel],
    *,
    default_active_agent: str,
    state_schema: StateSchemaType = SwarmState,
    config_schema: Type[Any] | None = None,
) -> StateGraph:
    """Create a multi-agent swarm.

    Args:
        agents: List of agents to add to the swarm
        default_active_agent: Name of the agent to route to by default (if no agents are currently active).
        state_schema: State schema to use for the multi-agent graph.
        config_schema: An optional schema for configuration.
            Use this to expose configurable parameters via supervisor.config_specs.

    Returns:
        A multi-agent swarm StateGraph.
    """
    active_agent_annotation = state_schema.__annotations__.get("active_agent")
    if active_agent_annotation is None:
        raise ValueError("Missing required key 'active_agent' in state_schema")

    agent_names = [agent.name for agent in agents]
    state_schema = _update_state_schema_agent_names(state_schema, agent_names)
    builder = StateGraph(state_schema, config_schema)
    add_active_agent_router(
        builder,
        route_to=agent_names,
        default_active_agent=default_active_agent,
    )
    for agent in agents:
        builder.add_node(
            agent.name,
            agent,
            destinations=tuple(get_handoff_destinations(agent)),
        )

    return builder
```

----------------------------------------

TITLE: Define ResearchState TypedDict (Python)
DESCRIPTION: Defines a Python TypedDict to represent the state managed within the research workflow graph, including topic, outline, editors, interview results, sections, and the final article.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/src/libs/langchain-ai-langgraph graph.txt#_snippet_58

LANGUAGE: Python
CODE:
```
class ResearchState(TypedDict):
    topic: str
    outline: Outline
    editors: List[Editor]
    interview_results: List[InterviewState]
    # The final sections output
    sections: List[WikiSection]
    article: str
```

----------------------------------------

TITLE: Construct and Compile LangGraph Workflow - Python
DESCRIPTION: Initializes the `StateGraph` builder with the defined state, adds all the functional nodes, establishes the edges defining the graph's flow (including a conditional edge after the LLM call), and compiles the graph using a `MemorySaver` for persistent state across interruptions.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/How to Review Tool Calls.md#_snippet_2

LANGUAGE: python
CODE:
```
builder = StateGraph(State)
builder.add_node(call_llm)
builder.add_node(run_tool)
builder.add_node(human_review_node)
builder.add_edge(START, "call_llm")
builder.add_conditional_edges("call_llm", route_after_llm)
builder.add_edge("run_tool", "call_llm")

# Set up memory
memory = MemorySaver()

# Add
graph = builder.compile(checkpointer=memory)
```

----------------------------------------

TITLE: Wrapping Agent Invocation LangGraph Python
DESCRIPTION: This Python function call_alice acts as an intermediary, invoking the compiled alice agent graph. It demonstrates how to transform input from a parent workflow's state (SwarmState) into the agent's required input format (alice_messages) and transform the agent's output back into the parent workflow's state format. This pattern facilitates integrating sub-graphs into larger workflows.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/libs/langchain-ai-langgraph-swarm-py.txt#_snippet_7

LANGUAGE: Python
CODE:
```
# wrapper calling the agent
def call_alice(state: SwarmState):
    # you can put any input transformation from parent state -> agent state
    # for example, you can invoke "alice" with "task_description" populated by the LLM
    response = alice.invoke({"alice_messages": state["messages"]})
    # you can put any output transformation from agent state -> parent state
    return {"messages": response["alice_messages"]}

def call_bob(state: SwarmState):
    ...
```

----------------------------------------

TITLE: Defining LangGraph Agent Workflow (Python)
DESCRIPTION: Defines a LangGraph agent workflow using `StateGraph`. The agent uses a `TypedDict` state, integrates with Anthropic and OpenAI models bound to tools (Tavily search), and includes nodes for calling the model (`call_model`) and executing tools (`tool_node`). It uses conditional edges based on tool calls to cycle between the agent and action nodes until no tool calls are made.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/src/libs/langgraph-cli-example-package-structure-with-init.txt#_snippet_3

LANGUAGE: Python
CODE:
```
from pathlib import Path
from typing import Annotated, Sequence, TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, add_messages
from langgraph.prebuilt import ToolNode

tools = [TavilySearchResults(max_results=1)]

model_anth = ChatAnthropic(temperature=0, model_name="claude-3-sonnet-20240229")
model_oai = ChatOpenAI(temperature=0)

model_anth = model_anth.bind_tools(tools)
model_oai = model_oai.bind_tools(tools)

prompt = open("prompt.txt").read()
subprompt = open(Path(__file__).parent / "subprompt.txt").read()


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# Define the function that determines whether to continue or not
def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    # If there are no tool calls, then we finish
    if not last_message.tool_calls:
        return "end"
    # Otherwise if there is, we continue
    else:
        return "continue"


# Define the function that calls the model
def call_model(state, config):
    if config["configurable"].get("model", "anthropic") == "anthropic":
        model = model_anth
    else:
        model = model_oai
    messages = state["messages"]
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


# Define the function to execute tools
tool_node = ToolNode(tools)


# Define a new graph
workflow = StateGraph(AgentState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point("agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
    # Finally we pass in a mapping.
    # The keys are strings, and the values are other nodes.
    # END is a special node marking that the graph should finish.
    # What will happen is we will call `should_continue`, and then the output of that
    # will be matched against the keys in this mapping.
    # Based on which one it matches, that node will then be called.
    {
        # If `tools`, then we call the tool node.
        "continue": "action",
        # Otherwise we finish.
        "end": END,
    },
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("action", "agent")

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
graph = workflow.compile()
```

----------------------------------------

TITLE: Defining Custom State and Invoking Agent (Python)
DESCRIPTION: Shows how to define a custom state schema for a LangGraph agent by inheriting from `AgentState` and adding type-hinted attributes. It also illustrates how to pass initial state data to the agent during the `invoke` call.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/docs/docs/agents/context.md#_snippet_1

LANGUAGE: python
CODE:
```
class CustomState(AgentState):
    user_name: str

agent = create_react_agent(
    # Other agent parameters...
    state_schema=CustomState,
)

agent.invoke({
    "messages": "hi!",
    "user_name": "Jane"
})
```

----------------------------------------

TITLE: Compiling and Invoking LangGraph Workflow - Python
DESCRIPTION: This snippet demonstrates how to compile the constructed LangGraph using `graph.compile`, optionally with a `checkpointer` for state persistence. It then sets up necessary components like the input `topic`, a `thread_id` for state management, tools (`AcademicPaperSearchTool`), and an LLM (`ChatOpenAI`). Finally, it invokes the compiled graph with the defined input and configuration, starting the workflow execution.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/nirdiamant-genai_agents (18).txt#_snippet_43

LANGUAGE: Python
CODE:
```
checkpointer = MemorySaver()
graph = graph.compile(checkpointer=checkpointer)

topic= "diffusion models for music generation"
thread_id = "test18"
temperature=0.1
papers_tool = AcademicPaperSearchTool()
tooling = [papers_tool]
model=ChatOpenAI(model='gpt-4o-mini') # gpt-4o-mini
tools = {t.name: t for t in tooling} if tooling else {}
model = model.bind_tools(tooling) if tools else model

agent_input = {"messages" : [HumanMessage(content=topic)]}
thread_config = {"configurable" : {"thread_id" : thread_id}}
result = graph.invoke(agent_input, thread_config)
```

----------------------------------------

TITLE: Initializing and Structuring LangGraph Workflow
DESCRIPTION: This snippet initializes a `StateGraph` named `workflow` using the defined `AgentState` and `GraphConfig`. It adds two nodes, 'agent' (using the `call_model` function) and 'action' (using the `tool_node`). Finally, it sets the 'agent' node as the entry point for the graph execution.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/langchain-ai-langgraph-example-monorepo.txt#_snippet_10

LANGUAGE: Python
CODE:
```
# Define a new graph
workflow = StateGraph(AgentState, config_schema=GraphConfig)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point("agent")
```

----------------------------------------

TITLE: Retrieving Final Agent State (Python)
DESCRIPTION: Illustrates how to retrieve the final state of the LangGraph workflow after execution using `get_state`. It then accesses and prints specific values from the final state dictionary, such as the iteration number and risk scores.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/project_manager_assistant_agent.ipynb#_snippet_22

LANGUAGE: python
CODE:
```
# Retrive the final state
final_state = graph_plan.get_state(config).values
print(final_state['iteration_number'])
print(final_state['project_risk_score_iterations'])
```

----------------------------------------

TITLE: Building Network Agent Graph (Python)
DESCRIPTION: Constructs a LangGraph `StateGraph` representing a network architecture. Agents invoke an LLM to decide the next agent node (`agent_1`, `agent_2`, `agent_3`) or terminate (`END`), returning a `Command` object. Requires LangGraph, LangChain, ChatOpenAI. Input: MessagesState. Output: Compiled LangGraph object.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/Multi-agent Systems.md#_snippet_4

LANGUAGE: python
CODE:
```
from typing import Literal
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from langgraph.graph import StateGraph, MessagesState, START, END

model = ChatOpenAI()

def agent_1(state: MessagesState) -> Command[Literal["agent_2", "agent_3", END]]:
    # Determine next agent using LLM
    response = model.invoke(...)
    return Command(
        goto=response["next_agent"],
        update={"messages": [response["content"]]}
    )

def agent_2(state: MessagesState) -> Command[Literal["agent_1", "agent_3", END]]:
    response = model.invoke(...)
    return Command(
        goto=response["next_agent"],
        update={"messages": [response["content"]]}
    )

def agent_3(state: MessagesState) -> Command[Literal["agent_1", "agent_2", END]]:
    response = model.invoke(...)
    return Command(
        goto=response["next_agent"],
        update={"messages": [response["content"]]}
    )

builder = StateGraph(MessagesState)
builder.add_node(agent_1)
builder.add_node(agent_2)
builder.add_node(agent_3)

builder.add_edge(START, "agent_1")
network = builder.compile()
```

----------------------------------------

TITLE: Defining Basic LangGraph Agent State and Graph (Python)
DESCRIPTION: Python code demonstrating the basic structure of a LangGraph agent. It defines the agent's state using TypedDict and Annotated, creates a StateGraph, adds nodes (retrieve, generate), defines edges between nodes, and compiles the graph. This sets up a simple sequential workflow.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/README.md#_snippet_2

LANGUAGE: Python
CODE:
```
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# Define agent state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# Create a graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)

# Define the flow
workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

# Compile the graph
graph = workflow.compile()
```

----------------------------------------

TITLE: Accessing State in a Tool (Python)
DESCRIPTION: Demonstrates how a tool function can access the agent's mutable state using the `Annotated` type hint with `InjectedState` and the custom state schema. This allows the tool to read dynamic data from the current state.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/docs/docs/agents/context.md#_snippet_5

LANGUAGE: python
CODE:
```
from typing import Annotated
from langgraph.prebuilt import InjectedState

class CustomState(AgentState):
    user_id: str

def get_user_info(
    state: Annotated[CustomState, InjectedState]
) -> str:
    """Look up user info."""
    user_id = state["user_id"]
    return "User is John Smith" if user_id == "user_123" else "Unknown user"

agent = create_react_agent(
    model="anthropic:claude-3-7-sonnet-latest",
    tools=[get_user_info],
    state_schema=CustomState,
)

agent.invoke({
    "messages": "look up user information",
    "user_id": "user_123"
})
```

----------------------------------------

TITLE: Implementing Parallel Processing Workflow in LangGraph (Python)
DESCRIPTION: Illustrates how to execute multiple LLM calls concurrently within a LangGraph workflow. It defines a state to hold the results of parallel tasks, creates independent node functions for each task, and builds a graph where multiple nodes are branched from the START node and converge into an aggregator node.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/Workflows and Agents.md#_snippet_2

LANGUAGE: python
CODE:
```
# Define state with multiple parallel outputs
class State(TypedDict):
    topic: str
    joke: str
    story: str
    poem: str
    combined_output: str

# Define parallel node functions
def call_llm_1(state: State):
    msg = llm.invoke(f"Write a joke about {state['topic']}")
    return {"joke": msg.content}

def call_llm_2(state: State):
    msg = llm.invoke(f"Write a story about {state['topic']}")
    return {"story": msg.content}

def call_llm_3(state: State):
    msg = llm.invoke(f"Write a poem about {state['topic']}")
    return {"poem": msg.content}

def aggregator(state: State):
    combined = f"Here's a story, joke, and poem about {state['topic']}!\n\n"
    combined += f"STORY:\n{state['story']}\n\n"
    combined += f"JOKE:\n{state['joke']}\n\n"
    combined += f"POEM:\n{state['poem']}"
    return {"combined_output": combined}
```

LANGUAGE: python
CODE:
```
# Build graph with parallel paths
parallel_builder = StateGraph(State)
parallel_builder.add_node("call_llm_1", call_llm_1)
parallel_builder.add_node("call_llm_2", call_llm_2)
parallel_builder.add_node("call_llm_3", call_llm_3)
parallel_builder.add_node("aggregator", aggregator)
parallel_builder.add_edge(START, "call_llm_1")
parallel_builder.add_edge(START, "call_llm_2")
parallel_builder.add_edge(START, "call_llm_3")
parallel_builder.add_edge("call_llm_1", "aggregator")
parallel_builder.add_edge("call_llm_2", "aggregator")
parallel_builder.add_edge("call_llm_3", "aggregator")
parallel_builder.add_edge("aggregator", END)
```

----------------------------------------

TITLE: Build LangGraph State Machine (Python)
DESCRIPTION: This code block constructs a LangGraph StateGraph. It initializes a `StateGraph` with `AgentState` and `InputState`, adds various nodes representing different steps in the agent's process (like query analysis, research, response, etc.), defines fixed edges between nodes, and sets up conditional edges based on specific logic. Finally, it compiles the graph with a `MemorySaver` checkpointer.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/nicoladisabato-multiagenticrag.txt#_snippet_24

LANGUAGE: Python
CODE:
```
checkpointer = MemorySaver()

builder = StateGraph(AgentState, input=InputState)
builder.add_node(analyze_and_route_query)
builder.add_edge(START, "analyze_and_route_query")
builder.add_conditional_edges("analyze_and_route_query", route_query)
builder.add_node(create_research_plan)
builder.add_node(ask_for_more_info)
builder.add_node(respond_to_general_query)
builder.add_node(conduct_research)
builder.add_node("respond", respond)
builder.add_node(check_hallucinations)

builder.add_conditional_edges("check_hallucinations", human_approval, {"END": END, "respond": "respond"})

builder.add_edge("create_research_plan", "conduct_research")
builder.add_conditional_edges("conduct_research", check_finished)

builder.add_edge("respond", "check_hallucinations")

graph = builder.compile(checkpointer=checkpointer)
```

----------------------------------------

TITLE: Creating MLflow Tool Calling Agent (Python)
DESCRIPTION: Constructs a LangGraph agent integrated with MLflow tracking and registry. It handles MLflow setup and defines the agent's state and workflow for tool execution, including an inner function for processing the agent's state.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/business-science-ai-data-science-team (2).txt#_snippet_48

LANGUAGE: Python
CODE:
```
def make_mlflow_tools_agent(
    model: Any,
    mlflow_tracking_uri: str=None,
    mlflow_registry_uri: str=None,
    create_react_agent_kwargs: Optional[Dict]={},
    invoke_react_agent_kwargs: Optional[Dict]={},
    checkpointer: Optional[Checkpointer]=None,
):
    """
    MLflow Tool Calling Agent

    Parameters:
    ----------
    model : Any
        The language model used to generate the agent.
    mlflow_tracking_uri : str, optional
        The tracking URI for MLflow. Defaults to None.
    mlflow_registry_uri : str, optional
        The registry URI for MLflow. Defaults to None.
    create_react_agent_kwargs : dict, optional
        Additional keyword arguments to pass to the agent's create_react_agent method.
    invoke_react_agent_kwargs : dict, optional
        Additional keyword arguments to pass to the agent's invoke method.
    checkpointer : langchain.checkpointing.Checkpointer, optional
        A checkpointer to use for saving and loading the agent's state. Defaults to None.

    Returns
    -------
    app : langchain.graphs.CompiledStateGraph
        A compiled state graph for the MLflow Tool Calling Agent.

    """

    try:
        import mlflow
    except ImportError:
        return "MLflow is not installed. Please install it by running: !pip install mlflow"

    if mlflow_tracking_uri is not None:
        mlflow.set_tracking_uri(mlflow_tracking_uri)

    if mlflow_registry_uri is not None:
        mlflow.set_registry_uri(mlflow_registry_uri)

    class GraphState(AgentState):
        internal_messages: Annotated[Sequence[BaseMessage], operator.add]
        user_instructions: str
        data_raw: dict
        mlflow_artifacts: dict


    def mflfow_tools_agent(state):
        """
        Postprocesses the MLflow state, keeping only the last message
        and extracting the last tool artifact.
        """
        print(format_agent_name(AGENT_NAME))
        print("    * RUN REACT TOOL-CALLING AGENT")

        tool_node = ToolNode(
            tools=tools
        )

        mlflow_agent = create_react_agent(
            model,
            tools=tool_node,
            state_schema=GraphState,
            checkpointer=checkpointer,
            **create_react_agent_kwargs,
        )

        response = mlflow_agent.invoke(
            {
                "messages": [("user", state["user_instructions"])],
                "data_raw": state["data_raw"],
            },
            invoke_react_agent_kwargs,
        )

        print("    * POST-PROCESS RESULTS")

        internal_messages = response['messages']

        # Ensure there is at least one AI message
        if not internal_messages:
            return {
                "internal_messages": [],
                "mlflow_artifacts": None,
            }

        # Get the last AI message
        last_ai_message = AIMessage(internal_messages[-1].content, role = AGENT_NAME)

        # Get the last tool artifact safely
        last_tool_artifact = None
```

----------------------------------------

TITLE: Initializing LangGraph StateGraph
DESCRIPTION: Initializes a StateGraph instance, which is the core component for defining the graph structure in LangGraph. It is initialized with the State object, defining the type of state the graph will manage.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/lucasboscatti-whatsapp-langgraph-agent-integration.txt#_snippet_29

LANGUAGE: Python
CODE:
```
builder = StateGraph(State)
```

----------------------------------------

TITLE: Defining LangGraph Workflow (Python)
DESCRIPTION: Initializes a LangGraph StateGraph, adds nodes for 'agent' and 'tools', sets the entry point, and defines conditional and direct edges to control the flow between nodes based on the 'should_continue' logic.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/yonom-assistant-ui-langgraph-fastapi.txt#_snippet_16

LANGUAGE: Python
CODE:
```
# Define a new graph
workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", run_tools)

workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    ["tools", END],
)

workflow.add_edge("tools", "agent")

assistant_ui_graph = workflow.compile()
```

----------------------------------------

TITLE: LangGraph Workflow Definition and Compilation - Python
DESCRIPTION: Sets up the LangGraph workflow by adding nodes for the agent and tool execution, defining the entry point, adding a conditional edge from the agent based on tool calls, adding a normal edge from tools back to the agent, and finally compiling the workflow into a runnable graph.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/src/libs/langgraph-cli-example-package-structure-with-utils.txt#_snippet_5

LANGUAGE: python
CODE:
```
# Define a new graph
workflow = StateGraph(AgentState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point("agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
    # Finally we pass in a mapping.
    # The keys are strings, and the values are other nodes.
    # END is a special node marking that the graph should finish.
    # What will happen is we will call `should_continue`, and then the output of that
    # will be matched against the keys in this mapping.
    # Based on which one it matches, that node will then be called.
    {
        # If `tools`, then we call the tool node.
        "continue": "action",
        # Otherwise we finish.
        "end": END,
    },
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("action", "agent")

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
graph = workflow.compile()
```

----------------------------------------

TITLE: Building and Compiling LangGraph StateGraph (Python)
DESCRIPTION: This code block initializes a LangGraph `StateGraph` using the `ResearchState`. It adds several asynchronous functions as nodes, defines sequential transitions between them using edges, sets the starting and ending nodes of the graph, and finally compiles the graph for execution.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/src/libs/langchain-ai-langgraph graph.txt#_snippet_66

LANGUAGE: Python
CODE:
```
builder_of_storm = StateGraph(ResearchState)

nodes = [
    ("init_research", initialize_research),
    ("conduct_interviews", conduct_interviews),
    ("refine_outline", refine_outline),
    ("index_references", index_references),
    ("write_sections", write_sections),
    ("write_article", write_article),
]
for i in range(len(nodes)):
    name, node = nodes[i]
    builder_of_storm.add_node(name, node)
    if i > 0:
        builder_of_storm.add_edge(nodes[i - 1][0], name)

builder_of_storm.set_entry_point(nodes[0][0])
builder_of_storm.set_finish_point(nodes[-1][0])
graph = builder_of_storm.compile()
```

----------------------------------------

TITLE: Building a ReAct Agent Workflow with ToolNode (Python)
DESCRIPTION: This comprehensive snippet constructs a simple ReAct agent using LangGraph's `StateGraph`. It defines nodes for the model ('agent') and the `ToolNode` ('tools'), sets up the state (`MessagesState`), and configures edges to cycle between the agent generating tool calls and the `ToolNode` executing them until the agent finishes.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/How to call tools using ToolNode.md#_snippet_7

LANGUAGE: python
CODE:
```
from langgraph.graph import StateGraph, MessagesState, START, END

# Create a state graph
workflow = StateGraph(MessagesState)

# Define the model node function
def call_model(state: MessagesState):
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

# Define the routing function
def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"  # More tool calls to process
    return END  # No more tool calls, we're done

# Add nodes and edges
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")

# Compile the graph
app = workflow.compile()
```

----------------------------------------

TITLE: Defining Agent State for LangGraph Python
DESCRIPTION: Defines the state structure (`AgentState`) for the LangGraph workflow using a `TypedDict`. The state includes a `messages` field, annotated with `add_messages`, which indicates that new messages should be appended to the existing list of messages in the state as the graph executes.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/Agentic RAG.md#_snippet_3

LANGUAGE: python
CODE:
```
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # The add_messages function defines how an update should be processed
    # Default is to replace. add_messages says "append"
    messages: Annotated[Sequence[BaseMessage], add_messages]
```

----------------------------------------

TITLE: Define Langgraph State Graph
DESCRIPTION: This Python code defines a Langgraph StateGraph named 'agent_workflow' using dummy functions to represent different nodes in an agent's process. It adds nodes for steps like anonymizing questions, planning, breaking down plans, deanonymizing, various retrieval steps, answering, task handling, and replanning. It then sets the entry point and defines initial edges in the graph.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/nirdiamant-controllable-rag-agent.txt#_snippet_7

LANGUAGE: Python
CODE:
```
# Jupyter notebook converted to Python script.


from langgraph.graph import END
from IPython.display import display, Image
from langgraph.graph import StateGraph

## dummy functions for comprehensive visualization

class PlanExecute:
    pass
def anonymize_queries():
    pass
def plan_step():
    pass
def break_down_plan_step():
    pass

def deanonymize_queries():
    pass
def run_qualitative_chunks_retrieval_workflow ():
    pass

def run_qualitative_summaries_retrieval_workflow ():
    pass

def run_qualitative_quotes_retrieval_workflow ():
    pass
def run_qualtative_answer_workflow ():
    pass
def run_task_handler_chain ():
    pass
def replan_step ():
    pass
def run_qualtative_answer_workflow_for_final_answer ():
    pass
def retrieve_or_answer ():
    pass
def can_be_answered ():
    pass

def keep_only_relevant_content ():
    pass

def is_distilled_content_grounded_on_content ():
    pass

def is_answer_grounded_on_context ():
    pass

agent_workflow = StateGraph(PlanExecute)

# Add the anonymize node
agent_workflow.add_node("anonymize_question", anonymize_queries)

# Add the plan node
agent_workflow.add_node("planner", plan_step)

# Add the break down plan node

agent_workflow.add_node("break_down_plan_to_retrieve_or_answer", break_down_plan_step)

# Add the deanonymize node
agent_workflow.add_node("de_anonymize_plan", deanonymize_queries)

# Add the qualitative retrieval node
agent_workflow.add_node("retrieve_book_chunks", run_qualitative_chunks_retrieval_workflow)

agent_workflow.add_node("retrieve_summaries", run_qualitative_summaries_retrieval_workflow)

agent_workflow.add_node("retrieve_book_quotes", run_qualitative_quotes_retrieval_workflow)

# Add the qualitative answer node
agent_workflow.add_node("answer", run_qualtative_answer_workflow)

# Add the task handler node
agent_workflow.add_node("task_handler", run_task_handler_chain)

# Add a replan node
agent_workflow.add_node("replan", replan_step)

# Add answer from context node
agent_workflow.add_node("get_final_answer", run_qualtative_answer_workflow_for_final_answer)

agent_workflow.add_node("keep_only_relevant_content",keep_only_relevant_content)

# Build the graph

# Set the entry point
agent_workflow.set_entry_point("anonymize_question")

# From anonymize we go to plan
agent_workflow.add_edge("anonymize_question", "planner")

# From plan we go to deanonymize
agent_workflow.add_edge("planner", "de_anonymize_plan")
```

----------------------------------------

TITLE: LangGraph Agent Workflow Definition (Python)
DESCRIPTION: This module defines a LangGraph workflow for a simple agent. It uses LangChain components like ChatAnthropic, ChatOpenAI, and TavilySearchResults. The graph includes nodes for calling a language model (call_model) and executing tools (tool_node), with a conditional edge (should_continue) to decide between continuing the agent loop or ending based on tool calls. The workflow is compiled into a runnable graph.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/src/libs/langchain-ai-langgraph graph_req_b.txt#_snippet_3

LANGUAGE: Python
CODE:
```
from pathlib import Path
from typing import Annotated, Sequence, TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, add_messages
from langgraph.prebuilt import ToolNode

tools = [TavilySearchResults(max_results=1)]

model_anth = ChatAnthropic(temperature=0, model_name="claude-3-sonnet-20240229")
model_oai = ChatOpenAI(temperature=0)

model_anth = model_anth.bind_tools(tools)
model_oai = model_oai.bind_tools(tools)

prompt = open("prompt.txt").read()
subprompt = open(Path(__file__).parent / "subprompt.txt").read()


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# Define the function that determines whether to continue or not
def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    # If there are no tool calls, then we finish
    if not last_message.tool_calls:
        return "end"
    # Otherwise if there is, we continue
    else:
        return "continue"


# Define the function that calls the model
def call_model(state, config):
    if config["configurable"].get("model", "anthropic") == "anthropic":
        model = model_anth
    else:
        model = model_oai
    messages = state["messages"]
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


# Define the function to execute tools
tool_node = ToolNode(tools)


# Define a new graph
workflow = StateGraph(AgentState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point("agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
    # Finally we pass in a mapping.
    # The keys are strings, and the values are other nodes.
    # END is a special node marking that the graph should finish.
    # What will happen is we will call `should_continue`, and then the output of that
    # will be matched against the keys in this mapping.
    # Based on which one it matches, that node will then be called.
    {
        # If `tools`, then we call the tool node.
        "continue": "action",
        # Otherwise we finish.
        "end": END,
    },
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("action", "agent")

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
graph = workflow.compile()
```

----------------------------------------

TITLE: Build Research Agent Workflow - LangGraph Python
DESCRIPTION: Defines the LangGraph StateGraph for the research agent. It adds nodes for the research agent's LLM invocation (`research_agent`) and tool handling (`research_agent_tools`), sets the entry point, and defines conditional edges based on the `research_agent_should_continue` logic to loop between the agent and tool nodes or end.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/libs/langchain-ai-open_deep_research.txt#_snippet_68

LANGUAGE: Python
CODE:
```
"""Build the multi-agent workflow"""

# Research agent workflow
research_builder = StateGraph(SectionState, output=SectionOutputState, config_schema=Configuration)
research_builder.add_node("research_agent", research_agent)
research_builder.add_node("research_agent_tools", research_agent_tools)
research_builder.add_edge(START, "research_agent") 
research_builder.add_conditional_edges(
    "research_agent",
    research_agent_should_continue,
    {
        # Name returned by should_continue : Name of next node to visit
        "research_agent_tools": "research_agent_tools",
        END: END,
    },
)
research_builder.add_edge("research_agent_tools", "research_agent")
```

----------------------------------------

TITLE: Define and Compile LangGraph with Dynamic Tool Selection in Python
DESCRIPTION: This snippet defines the LangGraph workflow. It includes a `State` defining the graph's memory, nodes for selecting tools (`select_tools`), executing the agent logic (`agent`), and running the selected tools (`tools`). The graph is configured to first select tools based on the user message via vector search, then pass the selected tools to the agent node, which binds them to the LLM before generation.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/docs/docs/how-tos/many-tools.ipynb#_snippet_4

LANGUAGE: python
CODE:
```
from typing import Annotated

from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


# Define the state structure using TypedDict.
# It includes a list of messages (processed by add_messages)
# and a list of selected tool IDs.
class State(TypedDict):
    messages: Annotated[list, add_messages]
    selected_tools: list[str]


builder = StateGraph(State)

# Retrieve all available tools from the tool registry.
tools = list(tool_registry.values())
llm = ChatOpenAI()


# The agent function processes the current state
# by binding selected tools to the LLM.
def agent(state: State):
    # Map tool IDs to actual tools
    # based on the state's selected_tools list.
    selected_tools = [tool_registry[id] for id in state["selected_tools"]]
    # Bind the selected tools to the LLM for the current interaction.
    llm_with_tools = llm.bind_tools(selected_tools)
    # Invoke the LLM with the current messages and return the updated message list.
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


# The select_tools function selects tools based on the user's last message content.
def select_tools(state: State):
    last_user_message = state["messages"][-1]
    query = last_user_message.content
    tool_documents = vector_store.similarity_search(query)
    return {"selected_tools": [document.id for document in tool_documents]}


builder.add_node("agent", agent)
builder.add_node("select_tools", select_tools)

tool_node = ToolNode(tools=tools)
builder.add_node("tools", tool_node)

builder.add_conditional_edges("agent", tools_condition, path_map=["tools", "__end__"])
builder.add_edge("tools", "agent")
builder.add_edge("select_tools", "agent")
builder.add_edge(START, "select_tools")
graph = builder.compile()
```

----------------------------------------

TITLE: Building LangGraph Workflow Structure (Python)
DESCRIPTION: Initializes a `StateGraph` with the defined `GraphState`. It adds the `exploratory_agent` function as a node and defines the edges, creating a simple linear graph from `START` to `exploratory_agent` and then to `END`.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/business-science-ai-data-science-team (1).txt#_snippet_5

LANGUAGE: Python
CODE:
```
    workflow = StateGraph(GraphState)
    workflow.add_node("exploratory_agent", exploratory_agent)
    workflow.add_edge(START, "exploratory_agent")
    workflow.add_edge("exploratory_agent", END)
```

----------------------------------------

TITLE: Creating LangGraph React Agent with Checkpointer (Python)
DESCRIPTION: Constructs a LangGraph agent using `create_react_agent`. It binds a language model with a token limit, provides a list of tools, includes a pre-model hook for processing before the model call, defines a state schema, and integrates the previously configured Redis checkpointer for state management.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/redis-developer-langgraph-redis (4).txt#_snippet_19

LANGUAGE: python
CODE:
```
graph = create_react_agent(
    # limit the output size to ensure consistent behavior
    model.bind(max_tokens=256),
    tools,
    # highlight-next-line
    pre_model_hook=summarization_node,
    # highlight-next-line
    state_schema=State,
    checkpointer=checkpointer,
)
```

----------------------------------------

TITLE: Building Document Writing StateGraph in LangGraph (Python)
DESCRIPTION: This code builds the LangGraph `StateGraph` for the document writing team. It adds the previously defined supervisor, document writer, note taker, and chart generator nodes to the graph builder. It sets the initial entry point (`START`) to the "supervisor" node and compiles the builder into the final `paper_writing_graph`. Requires `StateGraph` and the defined writing team nodes.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/docs/docs/tutorials/multi_agent/hierarchical_agent_teams.ipynb#_snippet_5

LANGUAGE: python
CODE:
```
# Create the graph here
paper_writing_builder = StateGraph(State)
paper_writing_builder.add_node("supervisor", doc_writing_supervisor_node)
paper_writing_builder.add_node("doc_writer", doc_writing_node)
paper_writing_builder.add_node("note_taker", note_taking_node)
paper_writing_builder.add_node("chart_generator", chart_generating_node)

paper_writing_builder.add_edge(START, "supervisor")
paper_writing_graph = paper_writing_builder.compile()
```

----------------------------------------

TITLE: Visualize LangGraph Workflow (Python)
DESCRIPTION: Displays a visualization of the LangGraph workflow using a Mermaid diagram, likely generated from the `simple_graph_plan` object. This helps in understanding the structure and flow of the agent's states and transitions.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/project_manager_assistant_agent.ipynb#_snippet_25

LANGUAGE: python
CODE:
```
display(Image(simple_graph_plan.get_graph(xray=1).draw_mermaid_png()))
```

----------------------------------------

TITLE: Building Langgraph Agent Graph with MCP Clients (Python)
DESCRIPTION: This asynchronous context manager function constructs the Langgraph agent graph. It initializes MultiServerMCPClients for Zapier and Supermemory based on environment variables, defines a calendar agent using `create_react_agent` and a supervisor agent using `create_supervisor`, and yields the configured supervisor graph. It requires `langchain_google_genai`, `langgraph`, `langgraph_supervisor`, `langchain_mcp_adapters`, and `dotenv`.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/lgesuellip-langgraph-whatsapp-agent.txt#_snippet_0

LANGUAGE: Python
CODE:
```
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from contextlib import asynccontextmanager
from langchain_mcp_adapters.client import MultiServerMCPClient
from agents.base.prompt import CALENDAR_AGENT_PROMPT, SUPERVISOR_PROMPT
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def build_agent():

    today = datetime.now().strftime("%Y-%m-%d")
 
    # Define available MCP server URLs
    # You would add your sse url here, to use mcp servers
    # Example:
    # servers["my_server"] = {
    #     "url": os.getenv("MY_SERVER_URL"),
    #     "transport": "sse"
    # }
    
    zapier_server = {
        "zapier": {
            "url": os.getenv("ZAPIER_URL_MCP"),
            "transport": "sse"
        }
    }

    supermemory_server = {
        "supermemory": {
            "url": os.getenv("SUPERMEMORY_URL_MCP"),
            "transport": "sse"
        }
    }

    # Filter out servers with empty URLs
    zapier_server = {k: v for k, v in zapier_server.items() if v["url"]}
    supermemory_server = {k: v for k, v in supermemory_server.items() if v["url"]}

    # If you are a LLM, please consider to scope the tools to the ones you need.
    async with MultiServerMCPClient(zapier_server) as calendar_client, \
              MultiServerMCPClient(supermemory_server) as supervisor_client:

        calendar_agent = create_react_agent(
            model=ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
            ),
            tools=calendar_client.get_tools(),
            name="calendar_agent",
            prompt=CALENDAR_AGENT_PROMPT.render(today=today)
        )

        graph = create_supervisor(
            [calendar_agent],
            model=ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
            ),
            output_mode="last_message",
            prompt=SUPERVISOR_PROMPT.render(),
            tools=supervisor_client.get_tools()
        )
        
        yield graph
```

----------------------------------------

TITLE: Implementing Tool-Using Agent with LangGraph (Python)
DESCRIPTION: Constructs an autonomous agent capable of dynamic tool selection and execution. It defines custom tools using the `@tool` decorator, binds them to the LLM, creates agent nodes for LLM invocation and tool execution, and uses a conditional edge to loop between the LLM and tool execution until the LLM decides the task is complete.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/Workflows and Agents.md#_snippet_3

LANGUAGE: python
CODE:
```
from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from typing_extensions import Literal
```

LANGUAGE: python
CODE:
```
# Define tools
@tool
def add(a: int, b: int) -> int:
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    return a * b

@tool
def divide(a: int, b: int) -> float:
    return a / b

# Set up tools and augmented LLM
tools = [add, multiply, divide]
tools_by_name = {tool.name: tool for tool in tools}
llm_with_tools = llm.bind_tools(tools)
```

LANGUAGE: python
CODE:
```
# Define agent nodes
def llm_call(state: MessagesState):
    return {
        "messages": [
            llm_with_tools.invoke(
                [
                    SystemMessage(
                        content="You are a helpful assistant tasked with performing arithmetic."
                    )
                ]
                + state["messages"]
            )
        ]
    }

def tool_node(state: dict):
    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}

# Routing function
def should_continue(state: MessagesState) -> Literal["environment", END]:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "Action"
    return END

# Build agent graph
agent_builder = StateGraph(MessagesState)
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("environment", tool_node)
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    {
        "Action": "environment",
        END: END,
    },
)
agent_builder.add_edge("environment", "llm_call")
agent = agent_builder.compile()
```

----------------------------------------

TITLE: Setting up LangGraph Workflow in Python
DESCRIPTION: Initializes a LangGraph StateGraph, adds nodes for different agents and human interaction points, defines directed edges for sequential transitions, and sets up conditional edges based on router functions or state conditions to control workflow flow. Finally, it compiles the graph for execution.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/starpig1129-datagen.txt#_snippet_72

LANGUAGE: python
CODE:
```
def setup_workflow(self):
        """Set up the workflow graph"""
        self.workflow = StateGraph(State)
        
        # Add nodes
        self.workflow.add_node("Hypothesis", lambda state: agent_node(state, self.agents["hypothesis_agent"], "hypothesis_agent"))
        self.workflow.add_node("Process", lambda state: agent_node(state, self.agents["process_agent"], "process_agent"))
        self.workflow.add_node("Visualization", lambda state: agent_node(state, self.agents["visualization_agent"], "visualization_agent"))
        self.workflow.add_node("Search", lambda state: agent_node(state, self.agents["searcher_agent"], "searcher_agent"))
        self.workflow.add_node("Coder", lambda state: agent_node(state, self.agents["code_agent"], "code_agent"))
        self.workflow.add_node("Report", lambda state: agent_node(state, self.agents["report_agent"], "report_agent"))
        self.workflow.add_node("QualityReview", lambda state: agent_node(state, self.agents["quality_review_agent"], "quality_review_agent"))
        self.workflow.add_node("NoteTaker", lambda state: note_agent_node(state, self.agents["note_agent"], "note_agent"))
        self.workflow.add_node("HumanChoice", human_choice_node)
        self.workflow.add_node("HumanReview", human_review_node)
        self.workflow.add_node("Refiner", lambda state: refiner_node(state, self.agents["refiner_agent"], "refiner_agent"))

        # Add edges
        self.workflow.add_edge(START, "Hypothesis")
        self.workflow.add_edge("Hypothesis", "HumanChoice")
        
        self.workflow.add_conditional_edges(
            "HumanChoice",
            hypothesis_router,
            {
                "Hypothesis": "Hypothesis",
                "Process": "Process"
            }
        )

        self.workflow.add_conditional_edges(
            "Process",
            process_router,
            {
                "Coder": "Coder",
                "Search": "Search",
                "Visualization": "Visualization",
                "Report": "Report",
                "Process": "Process",
                "Refiner": "Refiner",
            }
        )

        for member in ["Visualization", 'Search', 'Coder', 'Report']:
            self.workflow.add_edge(member, "QualityReview")

        self.workflow.add_conditional_edges(
            "QualityReview",
            QualityReview_router,
            {
                'Visualization': "Visualization",
                'Search': "Search",
                'Coder': "Coder",
                'Report': "Report",
                'NoteTaker': "NoteTaker",
            }
        )

        self.workflow.add_edge("NoteTaker", "Process")
        self.workflow.add_edge("Refiner", "HumanReview")
        
        self.workflow.add_conditional_edges(
            "HumanReview",
            lambda state: "Process" if state and state.get("needs_revision", False) else "END",
            {
                "Process": "Process",
                "END": END
            }
        )

        # Compile workflow
        self.memory = MemorySaver()
        self.graph = self.workflow.compile()
```

----------------------------------------

TITLE: Defining Agent State Dataclass - Python
DESCRIPTION: Defines a Python dataclass `State` to represent the state managed by the LangGraph workflow. It includes an `interrupt_response` field, initialized to "example", which is used to store the outcome or response from the human interrupt node.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/langchain-ai-agent-inbox-langgraph-example.txt#_snippet_8

LANGUAGE: Python
CODE:
```
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class State:
    """Class representing the state of the agent interaction."""

    interrupt_response: str = "example"
```

----------------------------------------

TITLE: Defining Custom Sequential Agent Workflow with LangGraph Python
DESCRIPTION: Shows how to create a simple multi-agent workflow in LangGraph with a fixed sequence of agent calls. It uses `StateGraph` to define agent nodes and explicit `add_edge` calls to define the flow, ensuring `agent_1` is called after the graph starts and `agent_2` is called after `agent_1` completes.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/docs/docs/concepts/multi_agent.md#_snippet_7

LANGUAGE: python
CODE:
```
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START

model = ChatOpenAI()

def agent_1(state: MessagesState):
    response = model.invoke(...)
    return {"messages": [response]}

def agent_2(state: MessagesState):
    response = model.invoke(...)
    return {"messages": [response]}

builder = StateGraph(MessagesState)
builder.add_node(agent_1)
builder.add_node(agent_2)
# define the flow explicitly
builder.add_edge(START, "agent_1")
builder.add_edge("agent_1", "agent_2")
```

----------------------------------------

TITLE: Build Workflow (No Tool Calling) - LangGraph Python
DESCRIPTION: This block constructs the LangGraph workflow when tool calling is not enabled. It initializes the graph, adds the 'agent' node (using the call model functions), optionally adds a 'pre_model_hook' node and connects it to the agent, sets the entry point, and optionally adds a 'generate_structured_response' node connected from the agent before compiling the final graph.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/src/libs/langchain-ai-langgraph prebuilt.txt#_snippet_31

LANGUAGE: Python
CODE:
```
    if not tool_calling_enabled:
        # Define a new graph
        workflow = StateGraph(state_schema, config_schema=config_schema)
        workflow.add_node(
            "agent",
            RunnableCallable(call_model, acall_model),
            input=input_schema,
        )
        if pre_model_hook is not None:
            workflow.add_node("pre_model_hook", pre_model_hook)
            workflow.add_edge("pre_model_hook", "agent")
            entrypoint = "pre_model_hook"
        else:
            entrypoint = "agent"

        workflow.set_entry_point(entrypoint)

        if response_format is not None:
            workflow.add_node(
                "generate_structured_response",
                RunnableCallable(
                    generate_structured_response, agenerate_structured_response
                ),
            )
            workflow.add_edge("agent", "generate_structured_response")

        return workflow.compile(
            checkpointer=checkpointer,
            store=store,
            interrupt_before=interrupt_before,
            interrupt_after=interrupt_after,
            debug=debug,
            name=name,
        )
```

----------------------------------------

TITLE: Update LangGraph Agent with Message Filtering (Python)
DESCRIPTION: Rebuilds the LangGraph StateGraph workflow, replacing the original `call_model` node with the new `call_model_with_filtering` function. The graph structure and routing logic remain the same, but the agent node now uses the filtered messages. The workflow is then compiled with the memory checkpointer.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/docs/How to manage conversation history.md#_snippet_4

LANGUAGE: python
CODE:
```
# Update the graph with the new model function
workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model_with_filtering)  # Using the filtered version
workflow.add_node("action", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["action", END])
workflow.add_edge("action", "agent")

# Compile the graph
app_with_filtering = workflow.compile(checkpointer=memory)
```

----------------------------------------

TITLE: Setup LangGraph Workflow (Python)
DESCRIPTION: Initializes the LangGraph StateGraph, adds the defined nodes (planner, generator, reflectors, researchers), sets the entry point, and defines the edges connecting the nodes to form the workflow, including a conditional edge for the revision loop.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/botextractai-ai-langgraph-multi-agent.txt#_snippet_10

LANGUAGE: python
CODE:
```
# Initialise the graph with the agent state
builder = StateGraph(AgentState)

# Add all the nodes (agents)
builder.add_node("planner", plan_node)
builder.add_node("generate", generation_node)
builder.add_node("reflect", reflection_node)
builder.add_node("research_plan", research_plan_node)
builder.add_node("research_critique", research_critique_node)

# Set the starting agent
builder.set_entry_point("planner")

# Set the conditional edge
# This decides, whether to do another refinement loop, or to end
builder.add_conditional_edges(
    "generate", 
    should_continue, 
    {END: END, "reflect": "reflect"}
)

# Agent workflow ("generate" is already covered by the conditional edge)
builder.add_edge("planner", "research_plan")
builder.add_edge("research_plan", "generate")

builder.add_edge("reflect", "research_critique")
builder.add_edge("research_critique", "generate")
```

----------------------------------------

TITLE: Building and Compiling LangGraph Workflow - Python
DESCRIPTION: Initializes a `StateGraph` with the defined `GraphState`. It adds the previously defined functions as nodes and configures the graph's control flow by setting a conditional entry point and adding both direct and conditional edges between nodes. Finally, it compiles the workflow into an executable graph and displays a visual representation.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/docs/docs/tutorials/rag/langgraph_adaptive_rag_local.ipynb#_snippet_15

LANGUAGE: Python
CODE:
```
from langgraph.graph import StateGraph
from IPython.display import Image, display

workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node("websearch", web_search)  # web search
workflow.add_node("retrieve", retrieve)  # retrieve
workflow.add_node("grade_documents", grade_documents)  # grade documents
workflow.add_node("generate", generate)  # generate

# Build graph
workflow.set_conditional_entry_point(
    route_question,
    {
        "websearch": "websearch",
        "vectorstore": "retrieve",
    },
)
workflow.add_edge("websearch", "generate")
workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "websearch": "websearch",
        "generate": "generate",
    },
)
workflow.add_conditional_edges(
    "generate",
    grade_generation_v_documents_and_question,
    {
        "not supported": "generate",
        "useful": END,
        "not useful": "websearch",
        "max retries": END,
    },
)

# Compile
graph = workflow.compile()
display(Image(graph.get_graph().draw_mermaid_png()))
```

----------------------------------------

TITLE: Building and Compiling LangGraph StateGraph - Python
DESCRIPTION: Initializes a `StateGraph` with a `MessagesState`. It adds the `travel_advisor` and `hotel_advisor` functions as nodes. It sets the `travel_advisor` as the starting node using `START`. Finally, it compiles the graph, making it ready for execution.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/main/docs/docs/how-tos/multi-agent-network.ipynb#_snippet_4

LANGUAGE: python
CODE:
```
builder = StateGraph(MessagesState)
builder.add_node("travel_advisor", travel_advisor)
builder.add_node("hotel_advisor", hotel_advisor)
# we'll always start with a general travel advisor
builder.add_edge(START, "travel_advisor")

graph = builder.compile()

from IPython.display import display, Image

display(Image(graph.get_graph().draw_mermaid_png()))
```

----------------------------------------

TITLE: Invoking LangGraph Agent Workflow (Python)
DESCRIPTION: Shows how to invoke the compiled LangGraph workflow (`graph_plan`) with the initial state and configuration using the `stream` method. It iterates through the streamed events and prints the current node being executed.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/project_manager_assistant_agent.ipynb#_snippet_21

LANGUAGE: python
CODE:
```
# Invoke the agent
config = {"configurable": {"thread_id": "1"}}
for event in graph_plan.stream(state_input, config, stream_mode=["updates"]):
    "Print the different nodes as the agent progresses"
    print(f"Current node: {next(iter(event[1]))}")
```

----------------------------------------

TITLE: Defining LangGraph Workflow Class Python
DESCRIPTION: Defines the `Graph` class which orchestrates a research workflow using `langgraph`. It manages the state, initializes various research nodes, builds the graph structure, and provides methods for execution and communication.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/pogjester-company-research-agent.txt#_snippet_2

LANGUAGE: python
CODE:
```
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph
from typing import Dict, Any, AsyncIterator
import logging

from .classes.state import InputState
from .nodes import GroundingNode
from .nodes.researchers import (FinancialAnalyst, NewsScanner, 
                               IndustryAnalyzer, CompanyAnalyzer)
from .nodes.collector import Collector
from .nodes.curator import Curator
from .nodes.enricher import Enricher
from .nodes.briefing import Briefing
from .nodes.editor import Editor

logger = logging.getLogger(__name__)

class Graph:
    def __init__(self, company=None, url=None, hq_location=None, industry=None,
                 websocket_manager=None, job_id=None):
        self.websocket_manager = websocket_manager
        self.job_id = job_id
        
        # Initialize InputState
        self.input_state = InputState(
            company=company,
            company_url=url,
            hq_location=hq_location,
            industry=industry,
            websocket_manager=websocket_manager,
            job_id=job_id,
            messages=[
                SystemMessage(content="Expert researcher starting investigation")
            ]
        )

        # Initialize nodes with WebSocket manager and job ID
        self._init_nodes()
        self._build_workflow()

    def _init_nodes(self):
        """Initialize all workflow nodes"""
        self.ground = GroundingNode()
        self.financial_analyst = FinancialAnalyst()
        self.news_scanner = NewsScanner()
        self.industry_analyst = IndustryAnalyzer()
        self.company_analyst = CompanyAnalyzer()
        self.collector = Collector()
        self.curator = Curator()
        self.enricher = Enricher()
        self.briefing = Briefing()
        self.editor = Editor()

    def _build_workflow(self):
        """Configure the state graph workflow"""
        self.workflow = StateGraph(InputState)
        
        # Add nodes with their respective processing functions
        self.workflow.add_node("grounding", self.ground.run)
        self.workflow.add_node("financial_analyst", self.financial_analyst.run)
        self.workflow.add_node("news_scanner", self.news_scanner.run)
        self.workflow.add_node("industry_analyst", self.industry_analyst.run)
        self.workflow.add_node("company_analyst", self.company_analyst.run)
        self.workflow.add_node("collector", self.collector.run)
        self.workflow.add_node("curator", self.curator.run)
        self.workflow.add_node("enricher", self.enricher.run)
        self.workflow.add_node("briefing", self.briefing.run)
        self.workflow.add_node("editor", self.editor.run)

        # Configure workflow edges
        self.workflow.set_entry_point("grounding")
        self.workflow.set_finish_point("editor")
        
        research_nodes = [
            "financial_analyst", 
            "news_scanner",
            "industry_analyst", 
            "company_analyst"
        ]

        # Connect grounding to all research nodes
        for node in research_nodes:
            self.workflow.add_edge("grounding", node)
            self.workflow.add_edge(node, "collector")

        # Connect remaining nodes
        self.workflow.add_edge("collector", "curator")
        self.workflow.add_edge("curator", "enricher")
        self.workflow.add_edge("enricher", "briefing")
        self.workflow.add_edge("briefing", "editor")

    async def run(self, thread: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """Execute the research workflow"""
        compiled_graph = self.workflow.compile()
        
        async for state in compiled_graph.astream(
            self.input_state,
            thread
        ):
            if self.websocket_manager and self.job_id:
                await self._handle_ws_update(state)
            yield state

    async def _handle_ws_update(self, state: Dict[str, Any]):
        """Handle WebSocket updates based on state changes"""
        update = {
            "type": "state_update",
            "data": {
                "current_node": state.get("current_node", "unknown"),
                "progress": state.get("progress", 0),
                "keys": list(state.keys())
            }
        }
        await self.websocket_manager.broadcast_to_job(
            self.job_id,
            update
        )
    
    def compile(self):
        graph = self.workflow.compile()
        return graph
```

----------------------------------------

TITLE: Mapping Task Dependencies with LangGraph (Python)
DESCRIPTION: A LangGraph node that takes the list of tasks from the state and uses an LLM to identify and map dependencies between them, determining blocking tasks and dependent tasks. It returns the dependencies in the state.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/project_manager_assistant_agent.ipynb#_snippet_9

LANGUAGE: Python
CODE:
```
def task_dependency_node(state: AgentState):
    """Evaluate the dependencies between the tasks"""
    tasks = state["tasks"]
    prompt = f"""
        You are a skilled project scheduler responsible for mapping out task dependencies.
        Given the following list of tasks: {tasks}
        Your objectives are to:
            1. **Identify Dependencies:**
                - For each task, determine which other tasks must be completed before it can begin (blocking tasks).
            2. **Map Dependent Tasks:** 
                - For every task, list all tasks that depend on its completion.
        """
    structure_llm = llm.with_structured_output(DependencyList)
    dependencies: DependencyList = structure_llm.invoke(prompt)
    return {"dependencies": dependencies}
```

----------------------------------------

TITLE: Defining Primary Workflow State (Python)
DESCRIPTION: This code defines the `PrimaryState` using `TypedDict` and `Annotated`. This class represents the state object that is passed between nodes in the LangGraph workflow. It includes fields for messages, user instructions (original and agent-specific), routing decisions, SQL query code, data, visualization function, plot results, retry counts, and more.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/business-science-ai-data-science-team (3).txt#_snippet_36

LANGUAGE: python
CODE:
```
class PrimaryState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]    
    user_instructions: str
    user_instructions_sql_database: str
    user_instructions_data_visualization: str
    routing_preprocessor_decision: str
    sql_query_code: str
    sql_database_function: str
    data_sql: dict
    data_raw: dict
    plot_required: bool
    data_visualization_function: str
    plotly_graph: dict
    plotly_error: str
    max_retries: int
    retry_count: int
```

----------------------------------------

TITLE: Defining Agent State with Dataclass (Python)
DESCRIPTION: Defines the `AgentState` dataclass used to manage the state within the retrieval graph or agent. It includes fields for router classification, research steps, retrieved documents, and hallucination grading.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/nicoladisabato-multiagenticrag.txt#_snippet_29

LANGUAGE: Python
CODE:
```
@dataclass(kw_only=True)
class AgentState(InputState):
    """State of the retrieval graph / agent."""

    router: Router = field(default_factory=lambda: Router(type="general", logic=""))
    """The router's classification of the user's query."""
    steps: list[str] = field(default_factory=list)
    """A list of steps in the research plan."""
    documents: Annotated[list[Document], reduce_docs] = field(default_factory=list)
    """Populated by the retriever. This is a list of documents that the agent can reference."""
    hallucination: GradeHallucinations = field(default_factory=lambda: GradeHallucinations(binary_score="0"))
```

----------------------------------------

TITLE: Implementing Preprocess Routing Node (Python)
DESCRIPTION: This function defines the `preprocess_routing` node within the LangGraph workflow. It takes the `PrimaryState` as input. The current implementation is a placeholder, only printing a debug message, but this is where the logic for processing the initial state and potentially calling the routing preprocessor chain would reside.

SOURCE: https://github.com/shak-shat/langgraph4context7/blob/main/community/business-science-ai-data-science-team (3).txt#_snippet_37

LANGUAGE: python
CODE:
```
def preprocess_routing(state: PrimaryState):
    print("---SQL DATA ANALYST---")
```