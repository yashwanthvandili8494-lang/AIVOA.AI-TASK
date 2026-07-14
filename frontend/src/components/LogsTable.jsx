import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { setLogsList, populateForm } from '../store';

const LogsTable = () => {
  const dispatch = useDispatch();
  const logs = useSelector((state) => state.logs.list);

  const fetchLogs = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/logs');
      if (response.ok) {
        const data = await response.json();
        dispatch(setLogsList(data));
      }
    } catch (err) {
      console.error("Failed to fetch logs:", err);
    }
  };

  useEffect(() => {
    fetchLogs();
    
    const handleRefresh = () => {
      fetchLogs();
    };
    window.addEventListener('refresh-logs', handleRefresh);
    
    const interval = setInterval(fetchLogs, 4000);
    return () => {
      clearInterval(interval);
      window.removeEventListener('refresh-logs', handleRefresh);
    };
  }, [dispatch]);

  const handleRowClick = (log) => {
    dispatch(populateForm(log));
  };

  const getSentimentClass = (sent) => {
    if (!sent) return 'sent-neutral';
    switch (sent.toLowerCase()) {
      case 'positive': return 'sent-positive';
      case 'negative': return 'sent-negative';
      default: return 'sent-neutral';
    }
  };

  return (
    <div className="logs-history-container">
      <div className="logs-header-row">
        <h3 className="logs-section-title">📊 Logged Interactions History</h3>
        <button className="refresh-logs-btn" onClick={fetchLogs}>
          🔄 Refresh
        </button>
      </div>

      <div className="table-responsive">
        {logs.length === 0 ? (
          <div className="empty-logs-view">
            <p>No interactions logged yet. Use the AI Assistant on the right to log your first meeting!</p>
          </div>
        ) : (
          <table className="custom-logs-table">
            <thead>
              <tr>
                <th>HCP Name</th>
                <th>Type</th>
                <th>Date & Time</th>
                <th>Sentiment</th>
                <th>Materials Shared</th>
                <th>Outcomes</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr 
                  key={log.id} 
                  className="table-row-entry" 
                  onClick={() => handleRowClick(log)}
                  style={{ cursor: 'pointer' }}
                >
                  <td className="log-hcp-name">{log.hcpName || 'Unknown'}</td>
                  <td>
                    <span className="log-type-tag">{log.interactionType}</span>
                  </td>
                  <td>
                    <div className="log-datetime">
                      <span>{log.date}</span>
                      <span className="log-time-lbl">{log.time}</span>
                    </div>
                  </td>
                  <td>
                    <span className={`sentiment-badge ${getSentimentClass(log.sentiment)}`}>
                      {log.sentiment === 'Positive' ? '😊 Positive' : log.sentiment === 'Negative' ? '😞 Negative' : '😐 Neutral'}
                    </span>
                  </td>
                  <td>
                    <div className="log-chips-container">
                      {log.materialsShared && log.materialsShared.length > 0 ? (
                        log.materialsShared.map((mat, i) => (
                          <span key={i} className="table-mini-chip">{mat}</span>
                        ))
                      ) : (
                        <span className="no-materials-label">-</span>
                      )}
                    </div>
                  </td>
                  <td className="log-outcomes-col" title={log.outcomes}>
                    {log.outcomes || '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default LogsTable;
