import { Handle, Position } from '@xyflow/react';

export default function ResourceNode({ data }) {
  return (
    <div className="w-16 h-16 border-2 border-green-600 bg-green-50 rounded-md flex flex-col items-center justify-center text-xs font-bold text-green-800 shadow-md">
      <Handle type="target" position={Position.Top} style={{ background: '#555' }} />
      <span className="text-sm font-bold">{data.label}</span>
      <span className="text-[9px] opacity-70">{data.available_instances}/{data.total_instances}</span>
      <Handle type="source" position={Position.Bottom} style={{ background: '#555' }} />
    </div>
  );
}
