import React, { useState, useEffect } from 'react';
import { fetchApi } from '../utils/api';
import '../styles/components.css';

function MissionReplay() {
  const [missions, setMissions] = useState([]);
  const [selectedMission, setSelectedMission] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(true);
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    const fetchMissions = async () => {
      try {
        const data = await fetchApi('/api/missions');
        setMissions(data);
        if (data.length > 0) {
          setSelectedMission(data[0]);
        }
      } catch (err) {
        console.error('Failed to fetch missions:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMissions();
  }, []);

  useEffect(() => {
    if (!playing || !selectedMission) return;
    
    const timer = setTimeout(() => {
      if (currentStep < (selectedMission.stages?.length || 0) - 1) {
        setCurrentStep(currentStep + 1);
      } else {
        setPlaying(false);
      }
    }, 2000);
    
    return () => clearTimeout(timer);
  }, [playing, currentStep, selectedMission]);

  const getStepIcon = (stepType) => {
    switch(stepType) {
      case 'agent_action': return '🧠';
      case 'service_call': return '📄';
      case 'decision': return '🦨';
      case 'validation': return '✔';
      case 'error': return '⚠';
      case 'deployment': return '🚀';
      default: return '•';
    }
  };

  if (loading) return <div className="page">Loading mission replay...</div>;

  return (
    <div className="page">
      <div className="section-header">
        <h1>🎬 Mission Replay</h1>
      </div>

      <div className="replay-container">
        <div className="missions-select">
          <label>Select Mission:</label>
          <select onChange={(e) => {
            const mission = missions.find(m => m.id === e.target.value);
            setSelectedMission(mission);
            setCurrentStep(0);
            setPlaying(false);
          }}>
            {missions.map(m => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </select>
        </div>

        {selectedMission && (
          <>
            <div className="replay-controls">
              <button onClick={() => setPlaying(!playing)} className="control-btn">
                {playing ? '⏸ Pause' : '▶ Play'}
              </button>
              <button onClick={() => setCurrentStep(0)} className="control-btn">Reset</button>
              <div className="step-progress">
                <span>{currentStep + 1} / {selectedMission.stages?.length || 0}</span>
              </div>
            </div>

            <div className="timeline">
              {selectedMission.stages?.map((step, idx) => (
                <div
                  key={idx}
                  className={`timeline-step ${idx === currentStep ? 'active' : ''} ${idx < currentStep ? 'completed' : ''}`}
                  onClick={() => {
                    setCurrentStep(idx);
                    setPlaying(false);
                  }}
                >
                  <div className="step-icon">{getStepIcon(step.type)}</div>
                  <div className="step-label">{step.title}</div>
                </div>
              ))}
            </div>

            {selectedMission.stages && selectedMission.stages[currentStep] && (
              <div className="step-details">
                <div className="detail-header">
                  <h3>{selectedMission.stages[currentStep].title}</h3>
                  <span className="step-type">{selectedMission.stages[currentStep].type}</span>
                </div>
                <div className="detail-description">
                  {selectedMission.stages[currentStep].description}
                </div>
                <div className="detail-time">
                  {new Date(selectedMission.stages[currentStep].timestamp).toLocaleString()}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default MissionReplay;
