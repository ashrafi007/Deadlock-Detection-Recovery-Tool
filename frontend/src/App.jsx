import { useState, useEffect } from 'react';
import GraphView from './components/GraphView';
import ScenarioPanel from './components/ScenarioPanel';
import ResultPanel from './components/ResultPanel';

export default function App() {
  const [presets, setPresets] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [detectResult, setDetectResult] = useState(null);
  const [recoveryResult, setRecoveryResult] = useState(null);

  useEffect(() => {
    fetch('/api/scenarios')
      .then(r => r.json())
      .then(setPresets)
      .catch(() => {});
  }, []);

  const handleDetect = async (scenario) => {
    setLoading(true);
    setError(null);
    setRecoveryResult(null);
    try {
      const res = await fetch('/api/detect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scenario),
      });
      if (!res.ok) throw new Error(await res.text());
      setDetectResult(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRecover = async (scenario, strategy) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/recover?strategy=${strategy}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scenario),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setRecoveryResult(data);
      setDetectResult(prev => prev ? { ...prev, graph: data.after_graph } : null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const currentGraph = recoveryResult ? recoveryResult.after_graph : detectResult?.graph;
  const graphTitle = recoveryResult
    ? `Graph after ${recoveryResult.strategy} recovery`
    : detectResult
    ? detectResult.has_deadlock ? 'Graph — Deadlock Detected' : 'Graph — Safe State'
    : null;

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <header className="bg-white border-b px-6 py-3 flex items-center gap-3 shadow-sm">
        <div className="text-xl font-bold text-gray-800">Deadlock Detection & Recovery</div>
        <span className="text-xs bg-blue-100 text-blue-700 rounded px-2 py-0.5 font-medium">Resource Allocation Graph</span>
        {loading && <span className="text-xs text-gray-400 ml-auto animate-pulse">Processing...</span>}
        {error && <span className="text-xs text-red-500 ml-auto">Error: {error}</span>}
      </header>

      <div className="flex flex-1 overflow-hidden">
        <aside className="w-72 bg-white border-r flex flex-col overflow-hidden shrink-0">
          <div className="px-4 py-2 border-b bg-gray-50 text-xs font-semibold text-gray-600 uppercase tracking-wide">
            Scenario Builder
          </div>
          <div className="flex-1 overflow-y-auto">
            <ScenarioPanel
              presets={presets}
              onDetect={handleDetect}
              onRecover={handleRecover}
              loading={loading}
            />
          </div>
        </aside>

        <main className="flex-1 overflow-hidden">
          <GraphView graph={currentGraph} title={graphTitle} />
        </main>

        <aside className="w-64 bg-white border-l flex flex-col overflow-hidden shrink-0">
          <div className="px-4 py-2 border-b bg-gray-50 text-xs font-semibold text-gray-600 uppercase tracking-wide">
            Results
          </div>
          <div className="flex-1 overflow-y-auto">
            <ResultPanel result={detectResult} recoveryResult={recoveryResult} />
          </div>
        </aside>
      </div>
    </div>
  );
}
