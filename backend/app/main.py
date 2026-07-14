import os
from dotenv import load_dotenv
load_dotenv()
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage

from .database import init_db, SessionLocal, HCPInteraction, HCPProfile, MarketingMaterial
from .agent import agent_graph

# Initialize FastAPI App
app = FastAPI(title="HCP Interaction Agent Backend")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and seed records
@app.on_event("startup")
def startup_event():
    init_db()

# Pydantic Schemas
class ChatMessage(BaseModel):
    id: Optional[str] = None
    sender: str
    text: str
    toolCalls: Optional[List[Dict[str, Any]]] = None

class ChatRequest(BaseModel):
    message: str
    form_state: Optional[Dict[str, Any]] = None
    history: Optional[List[ChatMessage]] = None

class ChatResponse(BaseModel):
    reply: str
    form_state: Dict[str, Any]
    tool_calls: List[Dict[str, Any]]

class UpdateInteractionRequest(BaseModel):
    id: int
    hcpName: Optional[str] = None
    interactionType: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    attendees: Optional[str] = None
    topicsDiscussed: Optional[str] = None
    materialsShared: Optional[List[str]] = None
    samplesDistributed: Optional[List[str]] = None
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    followUpActions: Optional[str] = None

class CreateInteractionRequest(BaseModel):
    hcpName: Optional[str] = None
    interactionType: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    attendees: Optional[str] = None
    topicsDiscussed: Optional[str] = None
    materialsShared: Optional[List[str]] = None
    samplesDistributed: Optional[List[str]] = None
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    followUpActions: Optional[str] = None

# Endpoints
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    message = payload.message
    form_state = payload.form_state or {
        "hcpName": "",
        "date": "",
        "interactionType": "",
        "sentiment": "",
        "materialsShared": [],
        "notes": ""
    }
    
    # 1. Reconstruct message history
    messages_history = []
    if payload.history:
        for msg in payload.history:
            if msg.sender == "user":
                messages_history.append(HumanMessage(content=msg.text))
            elif msg.sender == "assistant":
                # Convert back tool calls
                tool_calls = []
                if msg.toolCalls:
                    for idx, tc in enumerate(msg.toolCalls):
                        tool_calls.append({
                            "name": tc["name"],
                            "args": tc["args"],
                            "id": f"call_{tc['name']}_{idx}"
                        })
                messages_history.append(AIMessage(content=msg.text, tool_calls=tool_calls))
                
    # Append current user prompt
    messages_history.append(HumanMessage(content=message))
    
    # 2. Invoke LangGraph agent
    try:
        inputs = {
            "messages": messages_history,
            "form_state": form_state,
            "tool_calls_tracker": []
        }
        
        outputs = agent_graph.invoke(inputs)
        
        # Get final response message
        final_msg = outputs["messages"][-1]
        reply_text = final_msg.content
        
        return ChatResponse(
            reply=reply_text,
            form_state=outputs.get("form_state", {}),
            tool_calls=outputs.get("tool_calls_tracker", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent invocation failed: {str(e)}")

@app.get("/api/logs")
def get_logs():
    db = SessionLocal()
    try:
        interactions = db.query(HCPInteraction).order_by(HCPInteraction.id.desc()).all()
        result = []
        for i in interactions:
            import json
            try:
                mat = json.loads(i.materials_shared) if i.materials_shared else []
            except:
                mat = []
            try:
                sam = json.loads(i.samples_distributed) if i.samples_distributed else []
            except:
                sam = []
            result.append({
                "id": i.id,
                "hcpName": i.hcp_name,
                "interactionType": i.interaction_type,
                "date": i.date,
                "time": i.time,
                "attendees": i.attendees,
                "topicsDiscussed": i.topics_discussed,
                "materialsShared": mat,
                "samplesDistributed": sam,
                "sentiment": i.sentiment,
                "outcomes": i.outcomes,
                "followUpActions": i.follow_up_actions
            })
        return result
    finally:
        db.close()

@app.post("/api/interactions/update")
def update_interaction(payload: UpdateInteractionRequest):
    import json
    db = SessionLocal()
    try:
        interaction = db.query(HCPInteraction).filter(HCPInteraction.id == payload.id).first()
        if not interaction:
            raise HTTPException(status_code=404, detail="Interaction not found")
        
        if payload.hcpName is not None:
            interaction.hcp_name = payload.hcpName
        if payload.interactionType is not None:
            interaction.interaction_type = payload.interactionType
        if payload.date is not None:
            interaction.date = payload.date
        if payload.time is not None:
            interaction.time = payload.time
        if payload.attendees is not None:
            interaction.attendees = payload.attendees
        if payload.topicsDiscussed is not None:
            interaction.topics_discussed = payload.topicsDiscussed
        if payload.materialsShared is not None:
            interaction.materials_shared = json.dumps(payload.materialsShared)
        if payload.samplesDistributed is not None:
            interaction.samples_distributed = json.dumps(payload.samplesDistributed)
        if payload.sentiment is not None:
            interaction.sentiment = payload.sentiment
        if payload.outcomes is not None:
            interaction.outcomes = payload.outcomes
        if payload.followUpActions is not None:
            interaction.follow_up_actions = payload.followUpActions
            
        db.commit()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/api/interactions/create")
def create_interaction(payload: CreateInteractionRequest):
    import json
    db = SessionLocal()
    try:
        interaction = HCPInteraction(
            hcp_name=payload.hcpName,
            interaction_type=payload.interactionType or "Meeting",
            date=payload.date,
            time=payload.time,
            attendees=payload.attendees,
            topics_discussed=payload.topicsDiscussed,
            materials_shared=json.dumps(payload.materialsShared or []),
            samples_distributed=json.dumps(payload.samplesDistributed or []),
            sentiment=payload.sentiment or "Neutral",
            outcomes=payload.outcomes,
            follow_up_actions=payload.followUpActions
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return {"status": "success", "id": interaction.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
