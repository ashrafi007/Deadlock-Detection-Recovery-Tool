import { Handle, Position } from '@xyflow/react';

export default function ProcessNode({ data }) {
  const base = 'rounded-full border-2 w-16 h-16 flex flex-col items-center justify-center text-xs font-bold shadow-md transition-all';
  const color = data.is_deadlocked
    ? 'bg-red-100 border-red-500 text-red-700'
    : 'bg-blue-100 border-blue-500 text-blue-700';

  return (
    <div className={`${base} ${color}`}>
      <Handle type="target" position={Position.Top} style={{ background: '#555' }} />
      <span className="text-sm font-bold">{data.label}</span>
      <span className="text-[9px] opacity-70">P{data.priority}</span>
      <Handle type="source" position={Position.Bottom} style={{ background: '#555' }} />
    </div>
  );
}
