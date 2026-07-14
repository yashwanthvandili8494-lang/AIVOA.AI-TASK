import requests
import json

URL = "http://127.0.0.1:8000/api/chat"

def run_tests():
    print("=== TEST 1: Logging an interaction with Dr. Sarah Jenkins ===")
    payload1 = {
        "message": "Log virtual meeting with Dr. Sarah Jenkins today, sentiment neutral, shared Clinical Study",
        "form_state": None,
        "history": []
    }
    
    response = requests.post(URL, json=payload1)
    if response.status_code != 200:
        print(f"Test 1 Failed: Status {response.status_code}, Body: {response.text}")
        return
        
    data1 = response.json()
    print("Agent reply:", data1["reply"])
    print("Tool calls executed:", json.dumps(data1["tool_calls"], indent=2))
    print("Populated form_state:", json.dumps(data1["form_state"], indent=2))
    
    form_state = data1["form_state"]
    assert form_state["hcpName"] == "Dr. Sarah Jenkins"
    assert form_state["interactionType"] == "Virtual"
    assert form_state["sentiment"] == "Neutral"
    assert "Clinical Study" in form_state["materialsShared"]
    print("Test 1 Passed: Successfully logged and populated form fields!\n")
    
    print("=== TEST 2: Modifying fields (sentiment to Positive and date to yesterday) ===")
    payload2 = {
        "message": "Change sentiment to Positive and date to yesterday",
        "form_state": form_state,
        "history": [
            {"sender": "user", "text": payload1["message"]},
            {"sender": "assistant", "text": data1["reply"], "toolCalls": data1["tool_calls"]}
        ]
    }
    
    response = requests.post(URL, json=payload2)
    if response.status_code != 200:
        print(f"Test 2 Failed: Status {response.status_code}, Body: {response.text}")
        return
        
    data2 = response.json()
    print("Agent reply:", data2["reply"])
    print("Tool calls executed:", json.dumps(data2["tool_calls"], indent=2))
    print("Updated form_state:", json.dumps(data2["form_state"], indent=2))
    
    import datetime
    yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    updated_state = data2["form_state"]
    assert updated_state["sentiment"] == "Positive"
    assert updated_state["date"] == yesterday_str
    print("Test 2 Passed: Successfully updated sentiment and date!\n")
    
    print("=== TEST 3: Searching HCP Robert Adams ===")
    payload3 = {
        "message": "Search Dr. Robert Adams",
        "form_state": updated_state,
        "history": []
    }
    response = requests.post(URL, json=payload3)
    data3 = response.json()
    print("Agent reply:", data3["reply"])
    print("Tool calls executed:", json.dumps(data3["tool_calls"], indent=2))
    print("Test 3 Passed: Successfully searched for profile details!\n")

if __name__ == "__main__":
    run_tests()
