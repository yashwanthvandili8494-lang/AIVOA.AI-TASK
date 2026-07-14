# HCP Interaction Agent Logging System 🤖💼

An AI-powered co-pilot dashboard designed for pharmaceutical sales representatives to search Healthcare Professional (HCP) profiles, suggest marketing materials, log interactions, and schedule follow-ups seamlessly using conversation. Powered by a **FastAPI** backend, a **LangGraph/LangChain** agent framework, and a modern **React + Redux Toolkit** frontend.

---

## 🌟 Key Features

- **AI Co-pilot Chat**: Converse naturally with an agent to log details, fetch profiles, update forms, and schedule actions.
- **Form Synchronization**: Real-time form population and updates synchronized directly from agent tool outputs.
- **Offline / Fallback Mode**: Works out of the box! If no `GROQ_API_KEY` is provided, a local mock-routing fallback processor handles core representative workflows.
- **HCP Profile Queries**: Instantly search HCP information, specialties, clinics, and contact details from SQLite.
- **Marketing Material Library**: Get references to approved, high-value clinical brochures and PDFs to share with HCPs.
- **Interaction Logs History**: A robust historical log view allowing you to view and manually update logged sessions.
- **Task Scheduling**: Plan and save follow-up reminders associated with specific physicians.

---

## 🏗️ Project Architecture & Tech Stack

### Frontend (`/frontend`)
- **React (Vite)**: Quick HMR and modern UI setup.
- **Redux Toolkit**: Manage application-wide state for the chat history, current interaction form fields, and logs.
- **Vanilla CSS**: Clean, premium responsive layout with styled inputs and scrolling message history.

### Backend (`/backend`)
- **FastAPI / Uvicorn**: High-performance asynchronous API endpoints.
- **LangGraph**: Orchestrates the agent workflow loop (message history reconstruction -> LLM response / Mock fallback -> Tool execution -> Synthesized output).
- **SQLAlchemy & SQLite**: Handles local ORM definitions and keeps track of HCP tables.
- **LangChain & Groq**: Powers semantic tool binding and LLM logic via Groq Cloud (`gemma2-9b-it`).

---

## 📁 Repository Structure

```text
TASK1/
├── backend/
│   ├── app/
│   │   ├── agent.py          # LangGraph state workflow, custom tools, LLM & mock router
│   │   ├── database.py       # SQLite database initialization, schemas & seeding logic
│   │   └── main.py           # FastAPI app & endpoints (/api/chat, /api/logs, etc.)
│   ├── requirements.txt      # Python dependencies
│   ├── test_agent_directly.py# Direct test run of the LangGraph agent state machine
│   └── test_api.py           # Integration API endpoint tests
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatPanel.jsx # Conversational AI UI
│   │   │   ├── InteractionForm.jsx # Interactive Details editor
│   │   │   └── LogsTable.jsx # Historical logged CRM table
│   │   ├── App.jsx           # Parent Dashboard Layout
│   │   ├── store.js          # Redux Toolkit Slices (Form, Chat, Logs)
│   │   └── main.jsx          # React app entry point
│   ├── package.json          # Node scripts and dependencies
│   └── vite.config.js        # Vite configurations
└── README.md                 # Project instructions and overview
```

---

## ⚙️ Prerequisites

Ensure you have the following installed locally:
- **Python**: version `3.10` or higher
- **Node.js**: version `18` or higher
- **npm**: (comes with Node.js)

---

## 🚀 Step-by-Step Setup Guide

### 1. Setup the Backend API

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # On Windows (PowerShell)
   python -m venv .venv
   .venv\Scripts\Activate.ps1

   # On macOS/Linux
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. *(Optional)* Setup your environment variables for LLM support. Create a `.env` file inside the `backend` folder and add your key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
   *Note: If no key is provided, the backend automatically falls back to an offline rule-based router simulating agent tool executions.*

5. Run the FastAPI development server:
   ```bash
   python app/main.py
   ```
   The backend server will launch and listen at **`http://localhost:8000`**. On startup, the database is auto-created (`backend/interactions.db`) and seeded with default doctor profiles.

---

### 2. Setup the Frontend Client

1. Open a new terminal, navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install JavaScript packages:
   ```bash
   npm install
   ```

3. Spin up the Vite development server:
   ```bash
   npm run dev
   ```
   The client application will start running, usually at **`http://localhost:5173`**. Open this link in your browser to view the application.

---

## 🧪 Running Tests

We provide scripts to test functionality directly in the backend. Ensure your backend server is running before executing API tests.

- **Test Backend API Endpoint (`/api/chat`)**:
  Ensures that chat payloads execute correctly, run tools, and return expected form state responses.
  ```bash
  cd backend
  python test_api.py
  ```

- **Test LangGraph Agent Directly**:
  Simulates raw LangGraph invocation workflows without starting the HTTP server.
  ```bash
  cd backend
  python test_agent_directly.py
  ```

---

## 🛠️ DB Seeded Entities
The following demo entities are seeded during the initial startup:
- **Physicians**: Dr. John Doe (Cardiologist), Dr. Sarah Jenkins (Oncologist), Dr. Robert Adams (Neurologist), Dr. Emily Taylor (Pediatrician).
- **Approved Assets**: Product Brochure, Clinical Study, Prescribing Info.
