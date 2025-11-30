from typing import Dict, Any

def build_chat_graph(llm: Any):
    try:
        from langgraph.graph import StateGraph, END
        class S(dict):
            pass
        g = StateGraph(S)
        def agent_node(state: Dict[str, Any]):
            out = llm.predict(state.get("input", ""))
            return {"output": out}
        g.add_node("agent", agent_node)
        g.set_entry_point("agent")
        g.add_edge("agent", END)
        return g.compile()
    except Exception:
        return None
