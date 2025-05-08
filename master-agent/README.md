# 🧠 Master Agent (Supervisor)

The Master Agent is a central orchestrator component of the platform, powered by an LLM. 
It receives user queries and intelligently breaks them down into actionable steps, coordinating a set of 
developer-defined tools and agents (including flows) to complete the task. 
While the Master Agent itself is driven by an LLM, the tools and agents it manages can be anything the developer 
defines—ranging from simple functions and external APIs to other LLM-powered agents. 
It operates iteratively using the ReAct reasoning framework to plan and act step by step.

## 🚀 Purpose

The **Master Agent** serves as the **Supervisor** of the agent ecosystem. It doesn't solve tasks directly but:
- Analyzes the user's query,
- Breaks the problem down into substeps,
- Selects and invokes the appropriate tools/agents to perform each step,
- Aggregates results and produces a final response.

It acts as a **thinking-and-acting LLM agent**, using reasoning + action loops to achieve the task goal.

---

## 🧩 How It Works

The Master Agent is built using the **LangGraph framework**, following the **ReAct (Reasoning + Acting)** paradigm. It operates in the following stages:

1. **Receive Inputs**
   - User query
   - List of available agents and tools (including **flows**)
   - Optional files metadata

2. **Plan and Decompose**
   - Analyze the user query
   - Break down into steps

3. **Select Flow or Agent**
   - First, search for a **flow** capable of handling the current step.
     - If found, expand the flow into its component agents and enqueue them.
   - If no flow is suitable, select a **single agent/tool** capable of handling the step and enqueue it.
   - If no suitable tool/agent is found, produce a final response.

4. **Execute Agents**
   - Pop the next agent from the queue.
   - Call the remote agent/tool using the `GenAI Protocol` library.
   - Append the result to chat messages.
   - Repeat step 3 until task is completed or no agents are applicable.

> ⚠️ If the **agent queue is not empty**, the Master Agent **must execute only the next agent** in the queue (part of an active flow). It cannot choose a new agent or flow in this state.

---

## 🏗️ Key Concepts

### 🔧 Agents & Tools
Agents are developer-defined Python processes that are remotely callable via `GenAI Protocol`. Each agent advertises:
- Its name and description
- Accepted parameters
- Expected input types

### 🔁 Flows
A **flow** is a **predefined sequence of agents/tools** designed to complete a larger task. Flows:
- Are not recursive (flows cannot contain other flows)
- Can be decomposed and executed step-by-step by Master Agent

### 🧠 ReAct via LangGraph
The Master Agent:
- Thinks → "What step is needed?"
- Acts → "Which tool can perform this step?"
- Iterates until the task is complete or no tools apply

### 📁 Files Support
Master Agent does not process file contents but receives **metadata only**, such as:
```json
{
  "original_name": "invoice.pdf",
  "mimetype": "application/pdf",
  "internal_id": "abc123",
  ...
}
```
If a step requires file input, Master Agent:
- Selects file(s) based on metadata
- Passes their IDs to the chosen agent

---

## 🧠 System Prompts

### 🔤 Default System Prompt
Guides the Master Agent in tool selection and ReAct-based reasoning:

```text
- Analyze user query
- Identify the next logical step
- Select a tool ONLY if it can perform the step
- Format correct tool names and parameters
```

### 📁 File-Aware Prompt
Activates when files are included in the request, instructing the Master Agent to match tools to files via metadata.

---

## 🤖 LLM Compatibility

The Master Agent supports any LLM that implements **tool-calling features**, including:

- 🔷 OpenAI models (via OpenAI API)
- 🔷 Azure OpenAI models
- 🟠 Ollama (local LLMs)

---

## 📡 Integration with GenAI Protocol

All tool/agent communication is done via `GenAI Protocol`, a platform-internal library enabling remote calls, session tracking, and streaming results.

---

## ✅ Usage Summary

| Step  | Description                                 |
|-------|---------------------------------------------|
| 1     | Receive user query and agents/tools list    |
| 2     | Decompose task into steps                   |
| 3     | Find matching flow or agent                 |
| 4     | Enqueue selected agents                     |
| 5     | Execute agent via `GenAI Protocol`          |
| 6     | Repeat until done or no agent is applicable |

---

## 🧪 Development Tips

- Ensure agents advertise correct input types (including file support)
- Avoid overloading flows—each flow must be linear and non-nested
- Test flow behavior: Master Agent will enforce strict queue ordering
- Monitor tool-call logs and traces to debug ReAct cycles and agent decisions
