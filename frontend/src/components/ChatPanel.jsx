import React, { useState, useRef, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { addMessage, setLoading, populateForm } from '../store';

const ChatPanel = () => {
  const dispatch = useDispatch();
  const { messages, loading } = useSelector((state) => state.chat);
  const formState = useSelector((state) => state.form);
  const [input, setInput] = useState('');
  const historyEndRef = useRef(null);

  useEffect(() => {
    historyEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessageText = input.trim();
    setInput('');

    // 1. Add user message
    dispatch(addMessage({ sender: 'user', text: userMessageText }));
    dispatch(setLoading(true));

    try {
      // 2. Post to backend
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessageText,
          form_state: formState,
          history: messages
        }),
      });

      if (!response.ok) {
        throw new Error('Server returned an error');
      }

      const data = await response.json();

      // 3. Add assistant reply
      dispatch(addMessage({
        sender: 'assistant',
        text: data.reply,
        toolCalls: data.tool_calls || []
      }));

      // 4. Populate form values
      if (data.form_state) {
        dispatch(populateForm(data.form_state));
        window.dispatchEvent(new CustomEvent('refresh-logs'));
      }

    } catch (err) {
      console.error(err);
      dispatch(addMessage({
        sender: 'assistant',
        text: 'Sorry, I encountered an error communicating with the agent server. Please make sure the backend is running.',
      }));
    } finally {
      dispatch(setLoading(false));
    }
  };

  const getToolDisplayName = (name) => {
    switch (name) {
      case 'log_interaction': return 'Log Interaction Tool';
      case 'edit_interaction': return 'Edit Field Tool';
      case 'search_hcp_profile': return 'Search Database Tool';
      case 'suggest_shared_materials': return 'Marketing Suggestion Tool';
      case 'create_follow_up_task': return 'Create Follow-up Tool';
      default: return name;
    }
  };

  return (
    <div className="chat-panel">
      {/* Header matching screenshot exactly */}
      <header className="chat-header">
        <div className="chat-header-main">
          <span className="chat-avatar-icon">🤖</span>
          <div className="chat-title-group">
            <h3>AI Assistant</h3>
            <p>Log Interaction details here via chat</p>
          </div>
        </div>
      </header>

      {/* Message history layout */}
      <div className="chat-history-container">
        <div className="chat-messages">
          {messages.map((msg) => {
            const isWelcome = msg.id === 'welcome';
            const isSuccess = msg.sender === 'assistant' && (
              msg.text.toLowerCase().includes("logged successfully") || 
              msg.text.toLowerCase().includes("logged the interaction")
            );
            
            // Format success response if needed to start with checkbox emoji
            let displayTest = msg.text;
            if (isSuccess && !displayTest.startsWith("✅")) {
              displayTest = "✅ " + displayTest;
            }

            const bubbleClass = isWelcome 
              ? 'welcome-card' 
              : (isSuccess ? 'success-card' : (msg.sender === 'user' ? 'user-card' : 'assistant-card'));

            return (
              <div key={msg.id} className="chat-bubble-wrap">
                <div className={`message-bubble ${bubbleClass}`}>
                  <p>{displayTest}</p>
                </div>
              </div>
            );
          })}

          {loading && (
            <div className="chat-bubble-wrap">
              <div className="message-bubble assistant-card typing-bubble">
                <div className="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}

          <div ref={historyEndRef} />
        </div>
      </div>

      {/* Input container matching screenshot layout */}
      <div className="chat-input-container">
        <form className="chat-input-form" onSubmit={handleSubmit}>
          <input
            type="text"
            className="chat-text-input"
            placeholder="Describe Interaction..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button type="submit" className="chat-log-btn" disabled={loading || !input.trim()}>
            <div className="chat-log-btn-content">
              <span className="log-btn-icon">▲</span>
              <span className="log-btn-text">Log</span>
            </div>
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatPanel;
