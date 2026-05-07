import { useState } from 'react';

const EMPTY = {
  description: '',
  processes: [{ id: 'P1', priority: 1, cpu_time_used: 0.5 }, { id: 'P2', priority: 2, cpu_time_used: 1.0 }],
  resources: [{ id: 'R1', total_instances: 1 }, { id: 'R2', total_instances: 1 }],
  assignments: [{ resource: 'R1', process: 'P1' }, { resource: 'R2', process: 'P2' }],
  requests: [{ process: 'P1', resource: 'R2' }, { process: 'P2', resource: 'R1' }],
};

function Row({ children }) {
  return <div className="flex gap-2 items-center">{children}</div>;
}
function Input({ value, onChange, placeholder, className = '' }) {
  return (
    <input
      value={value}
      onChange={e => onChange(e.target.value)}
      placeholder={placeholder}
      className={`border rounded px-2 py-1 text-sm w-full focus:outline-none focus:ring-1 focus:ring-blue-400 ${className}`}
    />
  );
}
function Btn({ onClick, children, color = 'gray', small }) {
  const colors = {
    gray: 'bg-gray-100 hover:bg-gray-200 text-gray-700',
    red: 'bg-red-50 hover:bg-red-100 text-red-600',
    blue: 'bg-blue-600 hover:bg-blue-700 text-white',
    green: 'bg-green-600 hover:bg-green-700 text-white',
  };
  return (
    <button
      onClick={onClick}
      className={`rounded px-2 ${small ? 'py-0.5 text-xs' : 'py-1 text-sm'} font-medium transition-colors ${colors[color]}`}
    >
      {children}
    </button>
  );
}

export default function ScenarioPanel({ presets, onDetect, onRecover, loading }) {
  const [scenario, setScenario] = useState(EMPTY);
  const [strategy, setStrategy] = useState('terminate');

  const set = (key, val) => setScenario(s => ({ ...s, [key]: val }));

  const loadPreset = (name) => {
    const p = presets[name];
    if (p) setScenario({ description: p.description || '', processes: p.processes.map(x => ({ id: x.id, priority: x.priority ?? 0, cpu_time_used: x.cpu_time_used ?? 0 })), resources: p.resources, assignments: p.assignments, requests: p.requests });
  };

  const updateItem = (key, index, field, value) => {
    const arr = [...scenario[key]];
    arr[index] = { ...arr[index], [field]: value };
    set(key, arr);
  };
  const removeItem = (key, index) => set(key, scenario[key].filter((_, i) => i !== index));
  const addProcess = () => set('processes', [...scenario.processes, { id: `P${scenario.processes.length + 1}`, priority: 0, cpu_time_used: 0 }]);
  const addResource = () => set('resources', [...scenario.resources, { id: `R${scenario.resources.length + 1}`, total_instances: 1 }]);
  const addAssignment = () => set('assignments', [...scenario.assignments, { resource: '', process: '' }]);
  const addRequest = () => set('requests', [...scenario.requests, { process: '', resource: '' }]);

  return (
    <div className="flex flex-col gap-4 overflow-y-auto h-full p-4">
      {/* Presets */}
      {presets && (
        <div>
          <div className="text-xs font-semibold text-gray-500 uppercase mb-1">Load Preset</div>
          <div className="flex flex-wrap gap-2">
            {Object.keys(presets).map(k => (
              <Btn key={k} onClick={() => loadPreset(k)} color="gray" small>{k}</Btn>
            ))}
          </div>
        </div>
      )}

      {/* Processes */}
      <div>
        <div className="flex justify-between items-center mb-1">
          <div className="text-xs font-semibold text-gray-500 uppercase">Processes</div>
          <Btn onClick={addProcess} color="gray" small>+ Add</Btn>
        </div>
        <div className="flex flex-col gap-1">
          {scenario.processes.map((p, i) => (
            <Row key={i}>
              <Input value={p.id} onChange={v => updateItem('processes', i, 'id', v)} placeholder="ID" className="w-16" />
              <Input value={p.priority} onChange={v => updateItem('processes', i, 'priority', Number(v))} placeholder="Priority" className="w-16" />
              <Input value={p.cpu_time_used} onChange={v => updateItem('processes', i, 'cpu_time_used', Number(v))} placeholder="CPU" className="w-16" />
              <Btn onClick={() => removeItem('processes', i)} color="red" small>✕</Btn>
            </Row>
          ))}
        </div>
      </div>

      {/* Resources */}
      <div>
        <div className="flex justify-between items-center mb-1">
          <div className="text-xs font-semibold text-gray-500 uppercase">Resources</div>
          <Btn onClick={addResource} color="gray" small>+ Add</Btn>
        </div>
        <div className="flex flex-col gap-1">
          {scenario.resources.map((r, i) => (
            <Row key={i}>
              <Input value={r.id} onChange={v => updateItem('resources', i, 'id', v)} placeholder="ID" className="w-20" />
              <Input value={r.total_instances} onChange={v => updateItem('resources', i, 'total_instances', Number(v))} placeholder="Instances" className="w-20" />
              <Btn onClick={() => removeItem('resources', i)} color="red" small>✕</Btn>
            </Row>
          ))}
        </div>
      </div>

      {/* Assignments */}
      <div>
        <div className="flex justify-between items-center mb-1">
          <div className="text-xs font-semibold text-gray-500 uppercase">Assignments (R→P holds)</div>
          <Btn onClick={addAssignment} color="gray" small>+ Add</Btn>
        </div>
        <div className="flex flex-col gap-1">
          {scenario.assignments.map((a, i) => (
            <Row key={i}>
              <Input value={a.resource} onChange={v => updateItem('assignments', i, 'resource', v)} placeholder="Resource" />
              <span className="text-gray-400 text-xs">→</span>
              <Input value={a.process} onChange={v => updateItem('assignments', i, 'process', v)} placeholder="Process" />
              <Btn onClick={() => removeItem('assignments', i)} color="red" small>✕</Btn>
            </Row>
          ))}
        </div>
      </div>

      {/* Requests */}
      <div>
        <div className="flex justify-between items-center mb-1">
          <div className="text-xs font-semibold text-gray-500 uppercase">Requests (P wants R)</div>
          <Btn onClick={addRequest} color="gray" small>+ Add</Btn>
        </div>
        <div className="flex flex-col gap-1">
          {scenario.requests.map((r, i) => (
            <Row key={i}>
              <Input value={r.process} onChange={v => updateItem('requests', i, 'process', v)} placeholder="Process" />
              <span className="text-gray-400 text-xs">→</span>
              <Input value={r.resource} onChange={v => updateItem('requests', i, 'resource', v)} placeholder="Resource" />
              <Btn onClick={() => removeItem('requests', i)} color="red" small>✕</Btn>
            </Row>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-col gap-2 pt-2 border-t">
        <Btn onClick={() => onDetect(scenario)} color="blue" disabled={loading}>
          {loading ? 'Running...' : 'Detect Deadlock'}
        </Btn>
        <div className="flex gap-2 items-center">
          <select
            value={strategy}
            onChange={e => setStrategy(e.target.value)}
            className="border rounded px-2 py-1 text-sm flex-1 focus:outline-none focus:ring-1 focus:ring-green-400"
          >
            <option value="terminate">Terminate (kill victim)</option>
            <option value="preempt">Preempt (take resource)</option>
          </select>
          <Btn onClick={() => onRecover(scenario, strategy)} color="green" disabled={loading}>
            Recover
          </Btn>
        </div>
      </div>
    </div>
  );
}
