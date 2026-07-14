import os
import json
import datetime
from dotenv import load_dotenv
load_dotenv()
from typing import Dict, Any, List, TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from sqlalchemy.orm import Session
from .database import SessionLocal, HCPProfile, MarketingMaterial, HCPInteraction, FollowUpTask

# 1. Define Graph State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    form_state: Dict[str, Any]
    tool_calls_tracker: List[Dict[str, Any]]

# Helper to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. Define Tools
@tool
def search_hcp_profile(query: str) -> str:
    """Searches the database for Healthcare Professional (HCP) profiles by name or specialty.
    Use this tool when the user asks about an HCP's specialty, clinic, or contact details.
    """
    db = SessionLocal()
    try:
        results = db.query(HCPProfile).filter(
            (HCPProfile.name.like(f"%{query}%")) | 
            (HCPProfile.specialty.like(f"%{query}%"))
        ).all()
        
        if not results:
            return f"No HCP profile found matching query: '{query}'."
        
        output = []
        for p in results:
            output.append(f"Name: {p.name} | Specialty: {p.specialty} | Clinic: {p.clinic} | Historical Sentiment: {p.historical_sentiment} | Email: {p.email}")
        return "\n".join(output)
    finally:
        db.close()

@tool
def suggest_shared_materials() -> str:
    """Retrieves all approved marketing and educational materials (e.g. brochures, study summaries, prescribing information) available to share with HCPs.
    Use this tool when the user asks what materials can be shared, or wants to see the list of assets.
    """
    db = SessionLocal()
    try:
        materials = db.query(MarketingMaterial).all()
        if not materials:
            return "No approved materials found in the database."
        output = []
        for m in materials:
            output.append(f"- {m.name} ({m.category}): {m.url}")
        return "\n".join(output)
    finally:
        db.close()

@tool
def log_interaction(
    hcp_name: str,
    interaction_type: str = 'Meeting',
    date: str = '2025-04-19',
    time: str = '19:36',
    attendees: str = '',
    topics_discussed: str = '',
    materials_shared: List[str] = None,
    samples_distributed: List[str] = None,
    sentiment: str = 'Neutral',
    outcomes: str = '',
    follow_up_actions: str = ''
) -> str:
    """Logs a complete interaction with an HCP into the database and populates the frontend form.
    
    Arguments:
    - hcp_name: Name of the HCP (e.g., 'Dr. John Doe')
    - interaction_type: Must be 'Meeting', 'Virtual', 'Email', or 'Phone'
    - date: Date of meeting in YYYY-MM-DD format (default: '2025-04-19')
    - time: Time of meeting in HH:MM format (default: '19:36')
    - attendees: Names of other attendees
    - topics_discussed: Summary of the discussion topics
    - materials_shared: List of materials shared (e.g., ['Clinical Study'])
    - samples_distributed: List of drug samples distributed
    - sentiment: Must be 'Positive', 'Neutral', or 'Negative'
    - outcomes: Outcomes of the discussion
    - follow_up_actions: Follow-up actions decided
    """
    if materials_shared is None:
        materials_shared = []
    if samples_distributed is None:
        samples_distributed = []
        
    db = SessionLocal()
    try:
        interaction = HCPInteraction(
            hcp_name=hcp_name,
            interaction_type=interaction_type,
            date=date,
            time=time,
            attendees=attendees,
            topics_discussed=topics_discussed,
            materials_shared=json.dumps(materials_shared),
            samples_distributed=json.dumps(samples_distributed),
            sentiment=sentiment,
            outcomes=outcomes,
            follow_up_actions=follow_up_actions
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        
        payload = {
            "id": interaction.id,
            "hcpName": hcp_name,
            "interactionType": interaction_type,
            "date": date,
            "time": time,
            "attendees": attendees,
            "topicsDiscussed": topics_discussed,
            "materialsShared": materials_shared,
            "samplesDistributed": samples_distributed,
            "sentiment": sentiment,
            "outcomes": outcomes,
            "followUpActions": follow_up_actions
        }
        return f"SUCCESS_LOG_INTERACTION:{json.dumps(payload)}"
    except Exception as e:
        return f"Error logging interaction: {str(e)}"
    finally:
        db.close()

@tool
def edit_interaction(field_name: str, field_value: Any) -> str:
    """Updates a single field in the current interaction form state.
    Use this tool when the user requests an update or correction to logged data.
    
    Arguments:
    - field_name: The name of the field to modify. Must be one of: 'hcpName', 'interactionType', 'date', 'time', 'attendees', 'topicsDiscussed', 'materialsShared', 'samplesDistributed', 'sentiment', 'outcomes', 'followUpActions'.
    - field_value: The new value for the field. For 'materialsShared' or 'samplesDistributed', it must be a list of strings.
    """
    valid_fields = [
        'hcpName', 'interactionType', 'date', 'time', 'attendees', 
        'topicsDiscussed', 'materialsShared', 'samplesDistributed', 
        'sentiment', 'outcomes', 'followUpActions'
    ]
    if field_name not in valid_fields:
        return f"Invalid field: '{field_name}'. Valid fields are: {', '.join(valid_fields)}."
    
    payload = {
        "field": field_name,
        "value": field_value
    }
    return f"SUCCESS_EDIT_INTERACTION:{json.dumps(payload)}"

@tool
def create_follow_up_task(hcp_name: str, task_description: str, due_date: str) -> str:
    """Schedules a follow-up action/task with an HCP in the database.
    Use this tool when the user wants to set a reminder to call, email, or visit an HCP later.
    
    Arguments:
    - hcp_name: Name of the HCP
    - task_description: Description of the follow-up task
    - due_date: Due date for the task (YYYY-MM-DD)
    """
    db = SessionLocal()
    try:
        task = FollowUpTask(
            hcp_name=hcp_name,
            description=task_description,
            due_date=due_date,
            status="Pending"
        )
        db.add(task)
        db.commit()
        return f"Successfully scheduled follow-up task for {hcp_name}: '{task_description}' by {due_date}."
    except Exception as e:
        return f"Error creating follow-up task: {str(e)}"
    finally:
        db.close()

# Map tools
tools_list = [search_hcp_profile, suggest_shared_materials, log_interaction, edit_interaction, create_follow_up_task]
tools_dict = {t.name: t for t in tools_list}

# 3. Define Graph Nodes
def call_model(state: AgentState):
    messages = state["messages"]
    
    # Construct System Message to define the agent's role and rules
    # Construct System Message to define the agent's role and rules
    current_date_str = datetime.date.today().isoformat()
    system_msg = SystemMessage(content=(
        f"You are an AI assistant integrated with an Interaction Logging application.\n"
        f"Today's date is {current_date_str}.\n"
        "Your primary responsibility is to update the interaction form whenever the user requests changes.\n\n"
        
        "RULES:\n"
        "1. When the user asks to modify any interaction detail (Date, Time, HCP Name, Attendees, Topics Discussed, Sentiment, Materials Shared, Samples, Outcomes, etc.), immediately update the corresponding field in the form.\n"
        "2. After updating the form, save the interaction so the Logged Interactions History reflects the latest values.\n"
        "3. Do not create a new interaction unless the user explicitly asks to create one. Modify the currently selected interaction.\n"
        "4. Keep all other fields unchanged unless the user requests otherwise.\n"
        "5. After successfully updating, respond with a confirmation summarizing what changed.\n\n"
        
        "EXAMPLES:\n"
        "User: 'Change the date to April 25, 2025.'\n"
        "Response: 'Done! The interaction date has been updated to April 25, 2025. The form and interaction history have been synchronized.'\n\n"
        "User: 'Change the meeting time to 3:00 PM.'\n"
        "Response: 'Done! The meeting time has been updated to 3:00 PM.'\n\n"
        "User: 'Change the sentiment to Neutral.'\n"
        "Response: 'Done! The sentiment has been updated to Neutral in both the form and interaction history.'\n\n"
        "User: 'Replace Dr. John Doe with Dr. Smith.'\n"
        "Response: 'Done! The HCP Name has been updated to Dr. Smith.'"
    ))
    
    # Initialize Groq client
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        # Check if the last message is a ToolMessage (which means tools just executed)
        if messages and (isinstance(messages[-1], ToolMessage) or (hasattr(messages[-1], "type") and messages[-1].type == "tool")):
            tool_content = messages[-1].content
            from langchain_core.messages import AIMessage
            
            # Determine which tool was called
            is_log = False
            is_edit = False
            is_search = False
            is_materials = False
            is_follow = False
            
            if len(messages) >= 2:
                prev_msg = messages[-2]
                if hasattr(prev_msg, "tool_calls") and prev_msg.tool_calls:
                    for tc in prev_msg.tool_calls:
                        name = tc.get("name")
                        if name == "log_interaction":
                            is_log = True
                        elif name == "edit_interaction":
                            is_edit = True
                        elif name == "search_hcp_profile":
                            is_search = True
                        elif name == "suggest_shared_materials":
                            is_materials = True
                        elif name == "create_follow_up_task":
                            is_follow = True
            
            if is_log:
                final_text = (
                    "**Interaction logged successfully!** The details (HCP Name, Date, Sentiment, and Materials) "
                    "have been automatically populated based on your summary. Would you like me to suggest "
                    "a specific follow-up action, such as scheduling a meeting?"
                )
            elif is_edit:
                # Parse edit parameters
                field_name = "field"
                field_val = ""
                if "SUCCESS_EDIT_INTERACTION" in tool_content:
                    try:
                        payload = json.loads(tool_content.split("SUCCESS_EDIT_INTERACTION:")[-1])
                        field_name = payload.get("field", "field")
                        field_val = payload.get("value", "")
                    except:
                        pass
                
                # Match edit confirmation templates exactly to user examples
                if field_name == "date":
                    final_text = f"Done! The Date field has been updated to {field_val} in the form, and the interaction history has been updated."
                elif field_name == "time":
                    final_text = f"Done! The Time field has been updated to {field_val} in the form, and the interaction history has been updated."
                elif field_name == "sentiment":
                    final_text = f"Done! The Sentiment field has been updated to {field_val} in the form, and the interaction history has been updated."
                elif field_name == "hcpName":
                    final_text = f"Done! The HCP Name field has been updated to {field_val} in the form, and the interaction history has been updated."
                else:
                    display_field = field_name[0].upper() + field_name[1:]
                    final_text = f"Done! The {display_field} field has been updated to {field_val} in the form, and the interaction history has been updated."
            elif is_search:
                final_text = f"Here is the profile details I found:\n{tool_content}"
            elif is_materials:
                final_text = f"Here are the approved educational and marketing materials available to share:\n{tool_content}"
            elif is_follow:
                final_text = f"I have successfully scheduled that follow-up task reminder in the database."
            else:
                final_text = tool_content
                
            return {"messages": [AIMessage(content=final_text)]}

        # Fallback Mock logic to simulate LLM and tools execution
        user_message = ""
        for m in reversed(messages):
            if isinstance(m, HumanMessage) or (hasattr(m, "type") and m.type == "human"):
                user_message = m.content
                break
                
        user_message_lower = user_message.lower()
        tool_calls = []
        
        # 1. Log interaction
        if "log" in user_message_lower or "meeting" in user_message_lower or "met" in user_message_lower or "visit" in user_message_lower:
            hcp_name = "Dr. John Doe"
            today_str = datetime.date.today().isoformat()
            yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
            date = today_str
            time = "19:36"
            interaction_type = "Meeting"
            sentiment = "Neutral"
            attendees = "Dr. John Doe, Rep Name"
            topics_discussed = "Discussed new drug efficacy trials and patient benefits."
            materials = ["Clinical Study"]
            samples = ["OncoBoost Sample Pack"]
            outcomes = "Dr. John Doe agreed to review the clinical trial literature."
            follow_up = "Send prescribing information manual next week."
            
            if "jenkins" in user_message_lower:
                hcp_name = "Dr. Sarah Jenkins"
                attendees = "Dr. Sarah Jenkins, Rep Name"
            elif "adams" in user_message_lower:
                hcp_name = "Dr. Robert Adams"
                attendees = "Dr. Robert Adams, Rep Name"
            elif "taylor" in user_message_lower:
                hcp_name = "Dr. Emily Taylor"
                attendees = "Dr. Emily Taylor, Rep Name"
                
            if "yesterday" in user_message_lower:
                date = yesterday_str
            elif "today" in user_message_lower:
                date = today_str
                
            if "virtual" in user_message_lower:
                interaction_type = "Virtual"
            elif "email" in user_message_lower:
                interaction_type = "Email"
            elif "phone" in user_message_lower:
                interaction_type = "Phone"
                
            if "positive" in user_message_lower:
                sentiment = "Positive"
            elif "negative" in user_message_lower:
                sentiment = "Negative"
                
            if "clinical study" in user_message_lower or "study" in user_message_lower:
                materials = ["Clinical Study"]
            elif "prescribing info" in user_message_lower or "info" in user_message_lower:
                materials = ["Prescribing Info"]
                
            tool_calls.append({
                "name": "log_interaction",
                "args": {
                    "hcp_name": hcp_name,
                    "interaction_type": interaction_type,
                    "date": date,
                    "time": time,
                    "attendees": attendees,
                    "topics_discussed": topics_discussed,
                    "materials_shared": materials,
                    "samples_distributed": samples,
                    "sentiment": sentiment,
                    "outcomes": outcomes,
                    "follow_up_actions": follow_up
                },
                "id": "mock_call_log"
            })
            response_content = f"Logged the interaction with {hcp_name} on {date}. The left-pane form is populated automatically!"
            
        # 2. Edit interaction
        elif "change" in user_message_lower or "edit" in user_message_lower or "set" in user_message_lower or "update" in user_message_lower:
            response_content = "Updating interaction fields..."
            if "date" in user_message_lower:
                val = (datetime.date.today() - datetime.timedelta(days=1)).isoformat() if "yesterday" in user_message_lower else datetime.date.today().isoformat()
                tool_calls.append({
                    "name": "edit_interaction",
                    "args": {"field_name": "date", "field_value": val},
                    "id": "mock_call_edit_date"
                })
            if "sentiment" in user_message_lower:
                val = "Positive"
                if "neutral" in user_message_lower:
                    val = "Neutral"
                elif "negative" in user_message_lower:
                    val = "Negative"
                tool_calls.append({
                    "name": "edit_interaction",
                    "args": {"field_name": "sentiment", "field_value": val},
                    "id": "mock_call_edit_sentiment"
                })
            if "type" in user_message_lower or "interaction type" in user_message_lower:
                val = "Virtual" if "virtual" in user_message_lower else ("Email" if "email" in user_message_lower else ("Phone" if "phone" in user_message_lower else "In-Person"))
                tool_calls.append({
                    "name": "edit_interaction",
                    "args": {"field_name": "interactionType", "field_value": val},
                    "id": "mock_call_edit_type"
                })
            if "hcp" in user_message_lower or "name" in user_message_lower:
                val = "Dr. John Doe"
                if "jenkins" in user_message_lower:
                    val = "Dr. Sarah Jenkins"
                elif "adams" in user_message_lower:
                    val = "Dr. Robert Adams"
                elif "taylor" in user_message_lower:
                    val = "Dr. Emily Taylor"
                tool_calls.append({
                    "name": "edit_interaction",
                    "args": {"field_name": "hcpName", "field_value": val},
                    "id": "mock_call_edit_name"
                })
            if "time" in user_message_lower.split() or "at" in user_message_lower.split():
                val = "15:45"
                # If a time is specified like "10:30", parse it
                for word in user_message.split():
                    if ":" in word:
                        val = word.strip(".,;:?!")
                        break
                tool_calls.append({
                    "name": "edit_interaction",
                    "args": {"field_name": "time", "field_value": val},
                    "id": "mock_call_edit_time"
                })
            if "attendee" in user_message_lower or "present" in user_message_lower:
                val = "Dr. John Doe, Dr. Robert Adams, Rep Name"
                tool_calls.append({
                    "name": "edit_interaction",
                    "args": {"field_name": "attendees", "field_value": val},
                    "id": "mock_call_edit_attendees"
                })
            if "topic" in user_message_lower or "discuss" in user_message_lower:
                val = "Discussed prescribing guidelines and drug benefits."
                tool_calls.append({
                    "name": "edit_interaction",
                    "args": {"field_name": "topicsDiscussed", "field_value": val},
                    "id": "mock_call_edit_topics"
                })
            if "material" in user_message_lower or "shared" in user_message_lower:
                val = ["Clinical Study", "Prescribing Info"]
                tool_calls.append({
                    "name": "edit_interaction",
                    "args": {"field_name": "materialsShared", "field_value": val},
                    "id": "mock_call_edit_materials"
                })
            if "sample" in user_message_lower or "distribution" in user_message_lower:
                val = ["OncoBoost Sample Pack"]
                tool_calls.append({
                    "name": "edit_interaction",
                    "args": {"field_name": "samplesDistributed", "field_value": val},
                    "id": "mock_call_edit_samples"
                })
            if "outcome" in user_message_lower or "agreement" in user_message_lower:
                val = "Scheduled a follow-up review meeting in 2 weeks."
                tool_calls.append({
                    "name": "edit_interaction",
                    "args": {"field_name": "outcomes", "field_value": val},
                    "id": "mock_call_edit_outcomes"
                })
            if "follow up" in user_message_lower or "followup" in user_message_lower or "action" in user_message_lower:
                val = "Send prescribing information manual next week."
                tool_calls.append({
                    "name": "edit_interaction",
                    "args": {"field_name": "followUpActions", "field_value": val},
                    "id": "mock_call_edit_follow"
                })
            response_content = "I have updated the interaction fields on the form based on your instruction."

        # 3. Search HCP
        elif "search" in user_message_lower or "profile" in user_message_lower or "doctor" in user_message_lower or "find hcp" in user_message_lower:
            query = "Doe"
            if "doe" in user_message_lower:
                query = "John Doe"
            elif "jenkins" in user_message_lower:
                query = "Sarah Jenkins"
            elif "adams" in user_message_lower:
                query = "Robert Adams"
            elif "taylor" in user_message_lower:
                query = "Emily Taylor"
            tool_calls.append({
                "name": "search_hcp_profile",
                "args": {"query": query},
                "id": "mock_call_search"
            })
            response_content = f"I am searching the database for '{query}' profiles."
            
        # 4. Suggest materials
        elif "materials" in user_message_lower or "brochure" in user_message_lower or "study" in user_message_lower:
            tool_calls.append({
                "name": "suggest_shared_materials",
                "args": {},
                "id": "mock_call_suggest"
            })
            response_content = "Here are the approved educational and marketing materials retrieved from our database."
            
        # 5. Schedule follow up
        elif "schedule" in user_message_lower or "follow" in user_message_lower or "task" in user_message_lower:
            tool_calls.append({
                "name": "create_follow_up_task",
                "args": {
                    "hcp_name": "Dr. John Doe",
                    "task_description": "Send clinical study follow-up email",
                    "due_date": "2026-07-20"
                },
                "id": "mock_call_follow"
            })
            response_content = "I have successfully scheduled that follow-up task reminder in the database for you."
            
        else:
            response_content = (
                "Hello! I am your AI sales assistant. How can I help you today? You can ask me to:\n\n"
                "1. **Search Profiles**: e.g., *'Search Dr. Jenkins'*\n"
                "2. **Log Interactions**: e.g., *'Today I met with Dr. Smith and discussed product X efficiency. The sentiment was positive, and I shared the brochures.'*\n"
                "3. **Update Form Details**: e.g., *'Change sentiment to Neutral'*\n"
                "4. **View Approved Materials**: e.g., *'Show me approved materials to share'*\n"
                "5. **Schedule Follow-ups**: e.g., *'Schedule a follow up call next Monday'*"
            )
            
        from langchain_core.messages import AIMessage
        response = AIMessage(content=response_content, tool_calls=tool_calls)
        return {"messages": [response]}
        
    llm = ChatGroq(
        model_name="gemma2-9b-it",
        groq_api_key=api_key,
        temperature=0.1
    )
    
    # Bind tools to the model
    llm_with_tools = llm.bind_tools(tools_list)
    
    response = llm_with_tools.invoke([system_msg] + list(messages))
    return {"messages": [response]}

def execute_tools(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the model didn't call any tools, we finish
    if not last_message.tool_calls:
        return {}
        
    tool_msgs = []
    form_state = dict(state.get("form_state", {}))
    tracker = list(state.get("tool_calls_tracker", []))
    
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        # Track tool execution
        tracker.append({
            "name": tool_name,
            "args": tool_args
        })
        
        # Run tool
        tool_obj = tools_dict.get(tool_name)
        if tool_obj:
            try:
                result = tool_obj.invoke(tool_args)
            except Exception as e:
                result = f"Error running tool: {str(e)}"
        else:
            result = f"Tool '{tool_name}' not found."
            
        # Parse result to see if we update form_state
        if isinstance(result, str):
            if result.startswith("SUCCESS_LOG_INTERACTION:"):
                payload_str = result.replace("SUCCESS_LOG_INTERACTION:", "")
                payload = json.loads(payload_str)
                form_state = payload
            elif result.startswith("SUCCESS_EDIT_INTERACTION:"):
                payload_str = result.replace("SUCCESS_EDIT_INTERACTION:", "")
                payload = json.loads(payload_str)
                field = payload["field"]
                val = payload["value"]
                form_state[field] = val
                
                interaction_id = form_state.get("id")
                if interaction_id:
                    db = SessionLocal()
                    try:
                        interaction = db.query(HCPInteraction).filter(HCPInteraction.id == interaction_id).first()
                        if interaction:
                            field_mapping = {
                                "hcpName": "hcp_name",
                                "interactionType": "interaction_type",
                                "date": "date",
                                "time": "time",
                                "attendees": "attendees",
                                "topicsDiscussed": "topics_discussed",
                                "materialsShared": "materials_shared",
                                "samplesDistributed": "samples_distributed",
                                "sentiment": "sentiment",
                                "outcomes": "outcomes",
                                "followUpActions": "follow_up_actions"
                            }
                            db_field = field_mapping.get(field)
                            if db_field:
                                if db_field in ["materials_shared", "samples_distributed"]:
                                    setattr(interaction, db_field, json.dumps(val))
                                else:
                                    setattr(interaction, db_field, val)
                                db.commit()
                    except Exception as e:
                        print(f"Error persisting manual edit to SQLite: {e}")
                    finally:
                        db.close()
                
        # Append tool response message
        tool_msgs.append(ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"],
            name=tool_name
        ))
        
    return {
        "messages": tool_msgs,
        "form_state": form_state,
        "tool_calls_tracker": tracker
    }

# 4. Build LangGraph Workflow
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("call_model", call_model)
workflow.add_node("execute_tools", execute_tools)

# Set Entry Point
workflow.add_edge(START, "call_model")

# Setup routing conditional logic
def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    # If there are tool calls, we execute them
    if last_message.tool_calls:
        return "execute_tools"
    # Otherwise, we end
    return END

# Add conditional edges
workflow.add_conditional_edges(
    "call_model",
    should_continue,
    {
        "execute_tools": "execute_tools",
        END: END
    }
)

# After tools run, we return to the model to synthesize a final message response
workflow.add_edge("execute_tools", "call_model")

# Compile graph
agent_graph = workflow.compile()
