import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { clearHighlights, updateField, clearForm } from '../store';

const InteractionForm = () => {
  const dispatch = useDispatch();
  const formState = useSelector((state) => state.form);

  const {
    id,
    hcpName,
    interactionType,
    date,
    time,
    attendees,
    topicsDiscussed,
    materialsShared,
    samplesDistributed,
    sentiment,
    outcomes,
    followUpActions,
    aiSuggestedFollowUps,
    highlightedFields
  } = formState;

  const [isEditMode, setIsEditMode] = useState(false);
  const [showMaterialSelector, setShowMaterialSelector] = useState(false);
  const [showSampleSelector, setShowSampleSelector] = useState(false);

  const ALL_MATERIALS = ["Product Brochure", "Clinical Study", "Prescribing Info"];
  const ALL_SAMPLES = ["OncoBoost Sample Pack", "CardioPlus Trial Kit", "NeuroRelief Sample"];

  useEffect(() => {
    if (highlightedFields.length > 0) {
      const timer = setTimeout(() => {
        dispatch(clearHighlights());
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [highlightedFields, dispatch]);

  const isHighlighted = (field) => highlightedFields.includes(field) ? 'field-highlight' : '';

  const addSuggestedFollowUp = (suggestion) => {
    const currentActions = followUpActions ? `${followUpActions}\n- ${suggestion}` : `- ${suggestion}`;
    dispatch(updateField({ field: 'followUpActions', value: currentActions }));
  };

  const handleInputChange = (field, value) => {
    dispatch(updateField({ field, value }));
  };

  const handleCreateNew = () => {
    dispatch(clearForm());
    setIsEditMode(true);
  };

  const handleSave = async () => {
    try {
      const isNew = !id;
      const endpoint = isNew ? 'http://localhost:8000/api/interactions/create' : 'http://localhost:8000/api/interactions/update';
      const payload = isNew 
        ? { hcpName, interactionType, date, time, attendees, topicsDiscussed, materialsShared, samplesDistributed, sentiment, outcomes, followUpActions }
        : { id, hcpName, interactionType, date, time, attendees, topicsDiscussed, materialsShared, samplesDistributed, sentiment, outcomes, followUpActions };
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        if (isNew) {
          const resData = await response.json();
          dispatch(updateField({ field: 'id', value: resData.id }));
        }
        setIsEditMode(false);
        setShowMaterialSelector(false);
        setShowSampleSelector(false);
        window.dispatchEvent(new Event('refresh-logs'));
      } else {
        alert("Failed to save changes. Please try again.");
      }
    } catch (err) {
      console.error(err);
      alert("Error contacting the server.");
    }
  };

  return (
    <div className="form-panel">
      <div className="form-panel-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
        <h2 className="section-title" style={{ margin: 0 }}>Interaction Details</h2>
        <div className="form-actions-row" style={{ display: 'flex', gap: '0.5rem' }}>
          <button 
            type="button" 
            className="action-btn log-new-btn"
            style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem', background: '#10b981', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: '500' }}
            onClick={handleCreateNew}
          >
            ➕ Log New
          </button>
          <button 
            type="button" 
            className={`action-btn edit-toggle-btn ${isEditMode ? 'active-edit' : ''}`}
            style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem', background: isEditMode ? '#3b82f6' : '#6b7280', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: '500' }}
            onClick={() => setIsEditMode(!isEditMode)}
          >
            {isEditMode ? '🔒 Lock Form' : '✏️ Edit Manually'}
          </button>
        </div>
      </div>

      <form className="details-form" onSubmit={(e) => e.preventDefault()}>
        
        {/* Row 1: HCP Name & Interaction Type */}
        <div className="form-row">
          <div className="form-group flex-1">
            <label>HCP Name</label>
            <div className={`input-wrap ${isHighlighted('hcpName')}`}>
              <input
                type="text"
                className="custom-input"
                placeholder="Search or select HCP..."
                value={hcpName || ''}
                onChange={(e) => handleInputChange('hcpName', e.target.value)}
                disabled={!isEditMode}
              />
            </div>
          </div>
          
          <div className="form-group flex-1">
            <label>Interaction Type</label>
            <div className={`input-wrap ${isHighlighted('interactionType')}`}>
              <select
                className="custom-input custom-select"
                value={interactionType || 'Meeting'}
                onChange={(e) => handleInputChange('interactionType', e.target.value)}
                disabled={!isEditMode}
              >
                <option value="Meeting">Meeting</option>
                <option value="Virtual">Virtual</option>
                <option value="Email">Email</option>
                <option value="Phone">Phone</option>
              </select>
            </div>
          </div>
        </div>

        {/* Row 2: Date & Time */}
        <div className="form-row">
          <div className="form-group flex-1">
            <label>Date</label>
            <div className={`input-wrap ${isHighlighted('date')}`}>
              <input
                type="date"
                className="custom-input"
                value={date || ''}
                onChange={(e) => handleInputChange('date', e.target.value)}
                disabled={!isEditMode}
              />
            </div>
          </div>

          <div className="form-group flex-1">
            <label>Time</label>
            <div className={`input-wrap ${isHighlighted('time')}`}>
              <input
                type="time"
                className="custom-input"
                value={time || ''}
                onChange={(e) => handleInputChange('time', e.target.value)}
                disabled={!isEditMode}
              />
            </div>
          </div>
        </div>

        {/* Attendees */}
        <div className="form-group full-width">
          <label>Attendees</label>
          <div className={`input-wrap ${isHighlighted('attendees')}`}>
            <input
              type="text"
              className="custom-input"
              placeholder="Enter names or search..."
              value={attendees || ''}
              onChange={(e) => handleInputChange('attendees', e.target.value)}
              disabled={!isEditMode}
            />
          </div>
        </div>

        {/* Topics Discussed */}
        <div className="form-group full-width">
          <label>Topics Discussed</label>
          <div className={`input-wrap ${isHighlighted('topicsDiscussed')}`}>
            <div className="textarea-container">
              <textarea
                className="custom-textarea"
                placeholder="Enter key discussion points..."
                value={topicsDiscussed || ''}
                onChange={(e) => handleInputChange('topicsDiscussed', e.target.value)}
                disabled={!isEditMode}
              />
              <button type="button" className="mic-btn" disabled title="Voice dictation (AI control)">
                🎤
              </button>
            </div>
          </div>
        </div>

        {/* Voice Note Button */}
        <div className="voice-btn-container full-width">
          <button type="button" className="voice-note-btn" disabled>
            ✨ Summarize from Voice Note (Requires Consent)
          </button>
        </div>

        {/* Materials & Samples Section */}
        <div className="materials-samples-section full-width">
          <h3 className="sub-section-title">Materials Shared / Samples Distributed</h3>
          
          {/* Materials Shared Box */}
          <div className={`materials-box ${isHighlighted('materialsShared')}`}>
            <div className="box-left">
              <span className="box-label">Materials Shared</span>
              <div className="materials-list">
                {!materialsShared || materialsShared.length === 0 ? (
                  <span className="no-items">No materials added.</span>
                ) : (
                  materialsShared.map((mat, idx) => (
                    <span key={idx} className="active-chip" style={{ display: 'inline-flex', alignItems: 'center' }}>
                      {mat}
                      {isEditMode && (
                        <span 
                          className="chip-remove" 
                          style={{ marginLeft: '6px', cursor: 'pointer', fontWeight: 'bold' }}
                          onClick={() => handleInputChange('materialsShared', materialsShared.filter(m => m !== mat))}
                        >
                          ×
                        </span>
                      )}
                    </span>
                  ))
                )}
              </div>
            </div>
            <button 
              type="button" 
              className={`action-inline-btn ${showMaterialSelector ? 'active-selector' : ''}`}
              disabled={!isEditMode}
              onClick={() => setShowMaterialSelector(!showMaterialSelector)}
            >
              {showMaterialSelector ? 'Close' : '🔍 Search/Add'}
            </button>
          </div>

          {/* Materials Selection Dropdown */}
          {isEditMode && showMaterialSelector && (
            <div className="dropdown-selector" style={{ marginTop: '0.5rem', background: '#f9fafb', padding: '0.75rem', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
              {ALL_MATERIALS.map((mat) => {
                const hasMat = materialsShared && materialsShared.includes(mat);
                return (
                  <label key={mat} className="selector-item" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={hasMat}
                      onChange={() => {
                        const currentVal = materialsShared || [];
                        const newValue = hasMat
                          ? currentVal.filter(m => m !== mat)
                          : [...currentVal, mat];
                        handleInputChange('materialsShared', newValue);
                      }}
                    />
                    {mat}
                  </label>
                );
              })}
            </div>
          )}

          {/* Samples Distributed Box */}
          <div className={`materials-box ${isHighlighted('samplesDistributed')}`}>
            <div className="box-left">
              <span className="box-label">Samples Distributed</span>
              <div className="materials-list">
                {!samplesDistributed || samplesDistributed.length === 0 ? (
                  <span className="no-items">No samples added.</span>
                ) : (
                  samplesDistributed.map((sam, idx) => (
                    <span key={idx} className="active-chip sample-chip" style={{ display: 'inline-flex', alignItems: 'center' }}>
                      {sam}
                      {isEditMode && (
                        <span 
                          className="chip-remove" 
                          style={{ marginLeft: '6px', cursor: 'pointer', fontWeight: 'bold' }}
                          onClick={() => handleInputChange('samplesDistributed', samplesDistributed.filter(s => s !== sam))}
                        >
                          ×
                        </span>
                      )}
                    </span>
                  ))
                )}
              </div>
            </div>
            <button 
              type="button" 
              className={`action-inline-btn ${showSampleSelector ? 'active-selector' : ''}`}
              disabled={!isEditMode}
              onClick={() => setShowSampleSelector(!showSampleSelector)}
            >
              {showSampleSelector ? 'Close' : '📦 Add Sample'}
            </button>
          </div>

          {/* Samples Selection Dropdown */}
          {isEditMode && showSampleSelector && (
            <div className="dropdown-selector" style={{ marginTop: '0.5rem', background: '#f9fafb', padding: '0.75rem', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
              {ALL_SAMPLES.map((sam) => {
                const hasSam = samplesDistributed && samplesDistributed.includes(sam);
                return (
                  <label key={sam} className="selector-item" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={hasSam}
                      onChange={() => {
                        const currentVal = samplesDistributed || [];
                        const newValue = hasSam
                          ? currentVal.filter(s => s !== sam)
                          : [...currentVal, sam];
                        handleInputChange('samplesDistributed', newValue);
                      }}
                    />
                    {sam}
                  </label>
                );
              })}
            </div>
          )}
        </div>

        {/* Inferred HCP Sentiment */}
        <div className="form-group full-width">
          <label>Observed/Inferred HCP Sentiment</label>
          <div className={`sentiment-radio-group ${isHighlighted('sentiment')}`}>
            <label className={`sentiment-radio-lbl ${sentiment === 'Positive' ? 'active-sentiment positive' : ''}`} style={{ cursor: isEditMode ? 'pointer' : 'default' }}>
              <input 
                type="radio" 
                name="sentiment" 
                value="Positive" 
                checked={sentiment === 'Positive'} 
                onChange={() => handleInputChange('sentiment', 'Positive')}
                disabled={!isEditMode} 
              />
              😊 Positive
            </label>
            <label className={`sentiment-radio-lbl ${sentiment === 'Neutral' ? 'active-sentiment neutral' : ''}`} style={{ cursor: isEditMode ? 'pointer' : 'default' }}>
              <input 
                type="radio" 
                name="sentiment" 
                value="Neutral" 
                checked={sentiment === 'Neutral'} 
                onChange={() => handleInputChange('sentiment', 'Neutral')}
                disabled={!isEditMode} 
              />
              😐 Neutral
            </label>
            <label className={`sentiment-radio-lbl ${sentiment === 'Negative' ? 'active-sentiment negative' : ''}`} style={{ cursor: isEditMode ? 'pointer' : 'default' }}>
              <input 
                type="radio" 
                name="sentiment" 
                value="Negative" 
                checked={sentiment === 'Negative'} 
                onChange={() => handleInputChange('sentiment', 'Negative')}
                disabled={!isEditMode} 
              />
              😞 Negative
            </label>
          </div>
        </div>

        {/* Outcomes */}
        <div className="form-group full-width">
          <label>Outcomes</label>
          <div className={`input-wrap ${isHighlighted('outcomes')}`}>
            <textarea
              className="custom-textarea"
              placeholder="Key outcomes or agreements..."
              value={outcomes || ''}
              onChange={(e) => handleInputChange('outcomes', e.target.value)}
              disabled={!isEditMode}
            />
          </div>
        </div>

        {/* Follow-up Actions */}
        <div className="form-group full-width">
          <label>Follow-up Actions</label>
          <div className={`input-wrap ${isHighlighted('followUpActions')}`}>
            <textarea
              className="custom-textarea"
              placeholder="Enter next steps or tasks..."
              value={followUpActions || ''}
              onChange={(e) => handleInputChange('followUpActions', e.target.value)}
              disabled={!isEditMode}
            />
          </div>
        </div>

        {/* AI Suggested Follow-ups */}
        <div className="form-group full-width suggested-actions-wrap">
          <label>AI Suggested Follow-ups:</label>
          <ul className="suggested-list">
            {aiSuggestedFollowUps && aiSuggestedFollowUps.map((item, index) => (
              <li key={index} className="suggested-item" onClick={() => addSuggestedFollowUp(item)} style={{ cursor: 'pointer' }}>
                + {item}
              </li>
            ))}
          </ul>
        </div>

        {/* Save/Cancel Buttons */}
        {isEditMode && (
          <div className="form-submit-row" style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
            <button type="button" className="save-btn" onClick={handleSave} style={{ flex: 1, padding: '0.75rem', background: 'linear-gradient(135deg, #2563eb, #1d4ed8)', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}>
              ✨ Save Changes
            </button>
            <button type="button" className="cancel-btn" onClick={() => {
              setIsEditMode(false);
              setShowMaterialSelector(false);
              setShowSampleSelector(false);
            }} style={{ padding: '0.75rem 1.25rem', background: '#f3f4f6', color: '#374151', border: '1px solid #d1d5db', borderRadius: '8px', cursor: 'pointer' }}>
              Cancel
            </button>
          </div>
        )}

      </form>
    </div>
  );
};

export default InteractionForm;
