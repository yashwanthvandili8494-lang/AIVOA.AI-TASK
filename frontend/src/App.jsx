import React from 'react';
import InteractionForm from './components/InteractionForm';
import ChatPanel from './components/ChatPanel';
import LogsTable from './components/LogsTable';

function App() {
  return (
    <div className="main-layout-container">
      {/* Top Header Label */}
      <header className="main-top-header">
        <h1 className="main-title">Log HCP Interaction</h1>
      </header>

      {/* Main Workspace Split Grid */}
      <main className="main-workspace-grid">
        {/* Left Side: Interaction Details Form */}
        <InteractionForm />

        {/* Right Side: AI Assistant Chat Panel */}
        <ChatPanel />
      </main>

      {/* Bottom Panel: Logged Interactions Table */}
      <LogsTable />
    </div>
  );
}

export default App;
