import React, { useState, useEffect, useRef } from 'react';
import DependencyGraph from './DependencyGraph';

export default function MissionReplay() {
  const [missions, setMissions] = useState([]);
  const [selectedMission, setSelectedMission] = useState(null);
  const [replayData, setReplayData] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [hoveredStep, setHoveredStep] = useState(null);
  const animationRef = useRef(null);
  const lastTimeRef = useRef(0);

  // Load missions on mount
  useEffect(() => {
    const loadMissions = async () => {
      try {
        const response = await fetch('/api/missions');
        const data = await response.json();
        setMissions(data);
      } catch (error) {
        console.error('Failed to load missions:', error);
      }
    };
    loadMissions();
    const interval = setInterval(loadMissions, 20000);
    return () => clearInterval(interval);
  }, []);

  // Load replay data when mission is selected
  useEffect(() => {
    if (!selectedMission) return;

    const loadReplay = async () => {
      try {
        const response = await fetch(`/api/missions/${selectedMission}/replay`);
        const data = await response.json();
        setReplayData(data);
        setCurrentStep(0);
        setIsPlaying(false);
      } catch (error) {
        console.error('Failed to load replay:', error);
      }
    };

    loadReplay();
  }, [selectedMission]);

  // Animation loop for playback
  useEffect(() => {
    if (!isPlaying || !replayData) return;

    const animate = (now) => {
      const elapsed = now - lastTimeRef.current;
      const stepDuration = 1000 / speed; // Duration per step in ms

      if (elapsed >= stepDuration) {
        setCurrentStep((prev) => {
          if (prev >= replayData.steps.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
        lastTimeRef.current = now;
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    lastTimeRef.current = performance.now();
    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isPlaying, replayData, speed]);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleReset = () => {
    setCurrentStep(0);
    setIsPlaying(false);
  };

  const handleSliderChange = (e) => {
    setCurrentStep(parseInt(e.target.value));
    setIsPlaying(false);
  };

  const handleSpeedChange = (newSpeed) => {
    setSpeed(newSpeed);
  };

  const getStepColor = (stepType) => {
    const colors = {
      'agent_action': '#3b82f6',
      'service_call': '#8b5cf6',
      'decision': '#f59e0b',
      'validation': '#10b981',
      'error': '#ef4444',
      'deployment': '#06b6d4',
    };
    return colors[stepType] || '#6b7280';
  };

  const getStepIcon = (stepType) => {
    const icons = {
      'agent_action': '🤖',
      'service_call': '📡',
      'decision': '🧠',
      'validation': '✅',
      'error': '❌',
      'deployment': '🚀',
    };
    return icons[stepType] || '▪';
  };

  if (!selectedMission) {
    return (
      <div style={{ padding: '2rem', backgroundColor: 'var(--bg-page)', minHeight: '100vh' }}>
        <h1 style={{ marginBottom: '2rem', color: 'var(--text-primary)' }}>Mission Replay</h1>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2rem'
        }}>
          {missions.map((mission) => (
            <div
              key={mission.id}
              onClick={() => setSelectedMission(mission.id)}
              style={{
                padding: '1.5rem',
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '0.75rem',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                hoveredStep: hoveredStep === mission.id ? { borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.05)' } : {}
              }}
              onMouseEnter={() => setHoveredStep(mission.id)}
              onMouseLeave={() => setHoveredStep(null)}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                <h3 style={{ margin: 0, color: 'var(--text-primary)', flex: 1 }}>{mission.name}</h3>
                <span style={{
                  padding: '0.25rem 0.75rem',
                  backgroundColor: mission.status === 'completed' ? '#10b981' : mission.status === 'in_progress' ? '#3b82f6' : '#6b7280',
                  color: 'white',
                  borderRadius: '0.25rem',
                  fontSize: '0.75rem',
                  fontWeight: 'bold'
                }}>
                  {mission.status.toUpperCase()}
                </span>
              </div>

              <p style={{ margin: '0.5rem 0', color: 'var(--text-secondary)', fontSize: '0.875rem', lineHeight: 1.4 }}>
                {mission.description}
              </p>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '0.75rem',
                marginTop: '1rem',
                paddingTop: '1rem',
                borderTop: '1px solid var(--border-color)'
              }}>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', letterSpacing: '0.05em' }}>PROGRESS</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>
                    {mission.progress_percent}%
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', letterSpacing: '0.05em' }}>AGENTS</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#3b82f6' }}>
                    {mission.agents_involved.length}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', letterSpacing: '0.05em' }}>PRIORITY</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#f59e0b' }}>
                    P{mission.priority}
                  </div>
                </div>
              </div>

              <button
                style={{
                  width: '100%',
                  marginTop: '1rem',
                  padding: '0.75rem',
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '0.5rem',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                  transition: 'background-color 0.2s'
                }}
                onMouseOver={(e) => e.target.style.backgroundColor = '#2563eb'}
                onMouseOut={(e) => e.target.style.backgroundColor = '#3b82f6'}
              >
                ▶ Watch Replay
              </button>
            </div>
          ))}
        </div>

        {missions.length === 0 && (
          <div style={{
            padding: '3rem',
            textAlign: 'center',
            backgroundColor: 'var(--bg-card)',
            borderRadius: '0.75rem',
            border: '1px dashed var(--border-color)'
          }}>
            <p style={{ color: 'var(--text-secondary)' }}>No missions available for replay</p>
          </div>
        )}
      </div>
    );
  }

  if (!replayData) {
    return (
      <div style={{ padding: '2rem', backgroundColor: 'var(--bg-page)', minHeight: '100vh' }}>
        <button
          onClick={() => setSelectedMission(null)}
          style={{ marginBottom: '1rem', padding: '0.5rem 1rem', cursor: 'pointer' }}
        >
          ← Back
        </button>
        <p style={{ color: 'var(--text-secondary)' }}>Loading replay data...</p>
      </div>
    );
  }

  const currentStepData = replayData.steps[currentStep];
  const progressPercent = (currentStep / (replayData.steps.length - 1)) * 100;

  return (
    <div style={{ padding: '2rem', backgroundColor: 'var(--bg-page)', minHeight: '100vh' }}>
      {/* Header */}
      <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <button
            onClick={() => setSelectedMission(null)}
            style={{
              marginBottom: '0.5rem',
              padding: '0.5rem 1rem',
              cursor: 'pointer',
              backgroundColor: 'transparent',
              border: '1px solid var(--border-color)',
              borderRadius: '0.5rem',
              color: 'var(--text-primary)'
            }}
          >
            ← Back to Missions
          </button>
          <h1 style={{ margin: '0.5rem 0', color: 'var(--text-primary)' }}>
            Replaying: {replayData.mission_name}
          </h1>
          <p style={{ margin: '0.25rem 0', color: 'var(--text-secondary)' }}>
            {replayData.mission_description}
          </p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Total Steps</div>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>
            {currentStep + 1} / {replayData.steps.length}
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 400px', gap: '2rem' }}>
        {/* Main Replay Area */}
        <div>
          {/* Player Controls */}
          <div style={{
            padding: '1.5rem',
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: '0.75rem',
            marginBottom: '2rem'
          }}>
            {/* Play/Pause/Speed Controls */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
              <button
                onClick={handlePlayPause}
                style={{
                  width: '48px',
                  height: '48px',
                  borderRadius: '50%',
                  border: 'none',
                  backgroundColor: isPlaying ? '#ef4444' : '#10b981',
                  color: 'white',
                  cursor: 'pointer',
                  fontSize: '1.25rem',
                  fontWeight: 'bold',
                  transition: 'all 0.2s',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
                title={isPlaying ? 'Pause' : 'Play'}
              >
                {isPlaying ? '⏸' : '▶'}
              </button>

              <button
                onClick={handleReset}
                style={{
                  padding: '0.75rem 1rem',
                  backgroundColor: 'var(--bg-input)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '0.5rem',
                  cursor: 'pointer',
                  color: 'var(--text-primary)',
                  transition: 'all 0.2s'
                }}
                onMouseOver={(e) => e.target.style.backgroundColor = 'rgba(59, 130, 246, 0.1)'}
                onMouseOut={(e) => e.target.style.backgroundColor = 'var(--bg-input)'}
              >
                ↻ Reset
              </button>

              <div style={{ flex: 1, display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', minWidth: '45px' }}>Speed:</span>
                {[0.5, 1, 2, 4].map((s) => (
                  <button
                    key={s}
                    onClick={() => handleSpeedChange(s)}
                    style={{
                      padding: '0.5rem 0.75rem',
                      backgroundColor: speed === s ? '#3b82f6' : 'var(--bg-input)',
                      border: '1px solid var(--border-color)',
                      borderRadius: '0.375rem',
                      cursor: 'pointer',
                      color: speed === s ? 'white' : 'var(--text-primary)',
                      fontSize: '0.75rem',
                      fontWeight: 'bold',
                      transition: 'all 0.2s'
                    }}
                  >
                    {s}x
                  </button>
                ))}
              </div>
            </div>

            {/* Progress Bar and Slider */}
            <div style={{ marginBottom: '1rem' }}>
              <div style={{
                width: '100%',
                height: '6px',
                backgroundColor: 'var(--bg-input)',
                borderRadius: '3px',
                overflow: 'hidden',
                marginBottom: '0.5rem'
              }}>
                <div style={{
                  width: `${progressPercent}%`,
                  height: '100%',
                  backgroundColor: '#3b82f6',
                  transition: 'width 0.05s linear'
                }} />
              </div>

              <input
                type="range"
                min="0"
                max={replayData.steps.length - 1}
                value={currentStep}
                onChange={handleSliderChange}
                style={{
                  width: '100%',
                  cursor: 'pointer',
                  accentColor: '#3b82f6'
                }}
              />
            </div>

            {/* Time indicators */}
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              <span>{currentStepData?.timestamp_display || '00:00'}</span>
              <span>{replayData.total_duration || '00:00'}</span>
            </div>
          </div>

          {/* Current Step Details */}
          <div style={{
            padding: '1.5rem',
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: '0.75rem',
            marginBottom: '2rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'start', gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{
                fontSize: '2.5rem',
                opacity: 0.8
              }}>
                {getStepIcon(currentStepData?.type)}
              </div>

              <div style={{ flex: 1 }}>
                <h2 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-primary)' }}>
                  Step {currentStep + 1}: {currentStepData?.title}
                </h2>
                <p style={{ margin: '0', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                  {currentStepData?.description}
                </p>
              </div>

              <span style={{
                padding: '0.5rem 1rem',
                backgroundColor: getStepColor(currentStepData?.type),
                color: 'white',
                borderRadius: '0.5rem',
                fontSize: '0.75rem',
                fontWeight: 'bold',
                whiteSpace: 'nowrap'
              }}>
                {currentStepData?.type.toUpperCase().replace('_', ' ')}
              </span>
            </div>

            {/* Step specifics */}
            {currentStepData?.agent_id && (
              <div style={{ marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Agent</div>
                <div style={{ color: 'var(--text-primary)', fontWeight: 'bold' }}>{currentStepData.agent_id}</div>
              </div>
            )}

            {currentStepData?.service_call && (
              <div style={{ marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Service Call</div>
                <div style={{ color: 'var(--text-primary)', fontFamily: 'monospace', fontSize: '0.875rem' }}>
                  {currentStepData.service_call}
                </div>
              </div>
            )}

            {currentStepData?.decision && (
              <div style={{ marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Decision</div>
                <div style={{
                  padding: '0.75rem',
                  backgroundColor: 'var(--bg-input)',
                  borderRadius: '0.5rem',
                  borderLeft: `3px solid ${getStepColor('decision')}`
                }}>
                  <p style={{ margin: '0 0 0.5rem 0', color: 'var(--text-primary)', fontWeight: 'bold' }}>
                    {currentStepData.decision.action}
                  </p>
                  <p style={{ margin: '0', color: 'var(--text-secondary)', fontSize: '0.875rem', lineHeight: 1.3 }}>
                    Confidence: <span style={{ color: 'var(--text-primary)', fontWeight: 'bold' }}>
                      {(currentStepData.decision.confidence * 100).toFixed(0)}%
                    </span>
                  </p>
                </div>
              </div>
            )}

            {currentStepData?.performance && (
              <div>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>Performance</div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem' }}>
                  <div style={{ padding: '0.75rem', backgroundColor: 'var(--bg-input)', borderRadius: '0.5rem' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Latency</div>
                    <div style={{ color: 'var(--text-primary)', fontWeight: 'bold' }}>{currentStepData.performance.latency_ms}ms</div>
                  </div>
                  <div style={{ padding: '0.75rem', backgroundColor: 'var(--bg-input)', borderRadius: '0.5rem' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Status</div>
                    <div style={{ color: currentStepData.performance.status === 'success' ? '#10b981' : '#ef4444', fontWeight: 'bold' }}>
                      {currentStepData.performance.status.toUpperCase()}
                    </div>
                  </div>
                  <div style={{ padding: '0.75rem', backgroundColor: 'var(--bg-input)', borderRadius: '0.5rem' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Impact</div>
                    <div style={{ color: 'var(--text-primary)', fontWeight: 'bold' }}>{currentStepData.performance.impact}</div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Timeline */}
          <div style={{
            padding: '1.5rem',
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: '0.75rem'
          }}>
            <h3 style={{ margin: '0 0 1rem 0', color: 'var(--text-primary)', fontSize: '1rem' }}>Timeline</h3>

            <div style={{ display: 'flex', gap: '0.5rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
              {replayData.steps.map((step, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setCurrentStep(idx);
                    setIsPlaying(false);
                  }}
                  onMouseEnter={() => setHoveredStep(idx)}
                  onMouseLeave={() => setHoveredStep(null)}
                  title={step.title}
                  style={{
                    minWidth: '32px',
                    height: '32px',
                    borderRadius: '0.5rem',
                    border: idx === currentStep ? '2px solid #3b82f6' : '1px solid var(--border-color)',
                    backgroundColor: idx === currentStep ? 'rgba(59, 130, 246, 0.2)' : (hoveredStep === idx ? 'var(--bg-input)' : 'transparent'),
                    color: getStepColor(step.type),
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: 'bold',
                    transition: 'all 0.2s',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  {idx + 1}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Live Dependency Graph */}
        <div style={{
          padding: '1.5rem',
          backgroundColor: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: '0.75rem',
          height: 'fit-content',
          position: 'sticky',
          top: '2rem'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: 'var(--text-primary)', fontSize: '1rem' }}>Active Services</h3>

          <div style={{ marginBottom: '1.5rem' }}>
            {currentStepData?.active_services && currentStepData.active_services.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {currentStepData.active_services.map((service, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: '0.75rem',
                      backgroundColor: 'var(--bg-input)',
                      borderLeft: `3px solid ${getStepColor('service_call')}`,
                      borderRadius: '0.375rem',
                      animation: 'pulse 1.5s infinite'
                    }}
                  >
                    <div style={{ color: 'var(--text-primary)', fontWeight: 'bold', fontSize: '0.875rem' }}>
                      📡 {service.name}
                    </div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                      {service.status}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', margin: 0 }}>No active services</p>
            )}
          </div>

          {/* Agents Involved */}
          <div style={{ paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
            <h4 style={{ margin: '0 0 0.75rem 0', color: 'var(--text-primary)', fontSize: '0.875rem' }}>Agents</h4>
            {replayData.agents_involved && replayData.agents_involved.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {replayData.agents_involved.map((agent, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: '0.5rem 0.75rem',
                      backgroundColor: 'var(--bg-input)',
                      borderRadius: '0.375rem',
                      fontSize: '0.75rem'
                    }}
                  >
                    <div style={{ color: 'var(--text-primary)', fontWeight: 'bold' }}>🤖 {agent.agent_id}</div>
                    <div style={{ color: 'var(--text-secondary)' }}>{agent.role}</div>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', margin: 0 }}>No agents assigned</p>
            )}
          </div>

          {/* Key Metrics */}
          <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
            <h4 style={{ margin: '0 0 0.75rem 0', color: 'var(--text-primary)', fontSize: '0.875rem' }}>Mission Stats</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Efficiency</span>
                <span style={{ color: 'var(--text-primary)', fontWeight: 'bold' }}>{replayData.efficiency_score}%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Quality</span>
                <span style={{ color: 'var(--text-primary)', fontWeight: 'bold' }}>{replayData.quality_score}%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Total Steps</span>
                <span style={{ color: 'var(--text-primary)', fontWeight: 'bold' }}>{replayData.steps.length}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }
      `}</style>
    </div>
  );
}
