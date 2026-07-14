import json
import datetime
from app.agent import agent_graph
from app.database import init_db

def test_direct():
    init_db()
    print("Testing direct agent invocation...")
    
    today_str = datetime.date.today().isoformat()
    yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

    # Test 1: Log Interaction
    inputs = {
        "messages": [("user", "Log virtual meeting with Dr. Sarah Jenkins today, sentiment neutral, shared Clinical Study")],
        "form_state": {},
        "tool_calls_tracker": []
    }

    outputs = agent_graph.invoke(inputs)
    print("\n[TEST 1 RESULTS]")
    print("Agent Reply:", outputs["messages"][-1].content)
    print("Tool Calls Tracker:", json.dumps(outputs["tool_calls_tracker"], indent=2))
    print("Form State:", json.dumps(outputs["form_state"], indent=2))
    
    # Verify values
    form = outputs["form_state"]
    assert form["hcpName"] == "Dr. Sarah Jenkins"
    assert form["interactionType"] == "Virtual"
    assert form["sentiment"] == "Neutral"
    assert "Clinical Study" in form["materialsShared"]
    assert form["date"] == today_str
    print("TEST 1 PASSED!")

    # Test 2: Edit Interaction
    inputs2 = {
        "messages": [
            ("user", "Log virtual meeting with Dr. Sarah Jenkins today, sentiment neutral, shared Clinical Study"),
            ("assistant", outputs["messages"][-1].content),
            ("user", "Actually, change the date to yesterday and sentiment to Positive")
        ],
        "form_state": form,
        "tool_calls_tracker": []
    }
    
    outputs2 = agent_graph.invoke(inputs2)
    print("\n[TEST 2 RESULTS]")
    print("Agent Reply:", outputs2["messages"][-1].content)
    print("Tool Calls Tracker:", json.dumps(outputs2["tool_calls_tracker"], indent=2))
    print("Form State:", json.dumps(outputs2["form_state"], indent=2))
    
    form2 = outputs2["form_state"]
    assert form2["sentiment"] == "Positive"
    assert form2["date"] == yesterday_str
    print("TEST 2 PASSED!")

if __name__ == "__main__":
    test_direct()
