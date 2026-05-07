import { useCallback, useEffect } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
} from '@xyflow/react';
import ProcessNode from './ProcessNode';
import ResourceNode from './ResourceNode';

const nodeTypes = { process: ProcessNode, resource: ResourceNode };

function layoutNodes(rawNodes) {
  const processes = rawNodes.filter(n => n.type === 'process');
  const resources = rawNodes.filter(n => n.type === 'resource');
  const cols = Math.max(Math.ceil(Math.sqrt(processes.length + resources.length)), 2);
  const hGap = 160, vGap = 140;

  const positioned = [];
  processes.forEach((n, i) => {
    positioned.push({ ...n, position: { x: (i % cols) * hGap + 40, y: Math.floor(i / cols) * vGap + 60 } });
  });
  resources.forEach((n, i) => {
    const row = Math.floor(processes.length / cols) + 1;
    positioned.push({ ...n, position: { x: (i % cols) * hGap + 40, y: row * vGap + (Math.floor(i / cols) * vGap) + 60 } });
  });
  return positioned;
}

function buildFlowNodes(graphNodes) {
  return layoutNodes(
    graphNodes.map(n => ({
      id: n.id,
      type: n.type,
      data: { ...n },
    }))
  );
}

function buildFlowEdges(graphEdges) {
  return graphEdges.map(e => ({
    id: e.id,
    source: e.source,
    target: e.target,
    animated: e.edge_type === 'request',
    style: {
      stroke: e.edge_type === 'assignment' ? '#1e40af' : '#ea580c',
      strokeWidth: 2,
      strokeDasharray: e.edge_type === 'request' ? '5,5' : undefined,
    },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: e.edge_type === 'assignment' ? '#1e40af' : '#ea580c',
    },
    label: e.edge_type === 'assignment' ? 'holds' : 'wants',
    labelStyle: { fontSize: 10, fill: e.edge_type === 'assignment' ? '#1e40af' : '#ea580c' },
  }));
}

export default function GraphView({ graph, title }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    if (!graph) return;
    setNodes(buildFlowNodes(graph.nodes));
    setEdges(buildFlowEdges(graph.edges));
  }, [graph]);

  if (!graph) return (
    <div className="flex items-center justify-center h-full text-gray-400 text-sm">
      Load a scenario to see the graph
    </div>
  );

  return (
    <div className="flex flex-col h-full">
      {title && (
        <div className="px-3 py-2 text-sm font-semibold text-gray-700 bg-gray-50 border-b">
          {title}
        </div>
      )}
      <div className="flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.3 }}
        >
          <Background />
          <Controls />
          <MiniMap
            nodeColor={n => n.data?.is_deadlocked ? '#ef4444' : n.type === 'process' ? '#3b82f6' : '#22c55e'}
          />
        </ReactFlow>
      </div>
      <div className="flex gap-4 px-3 py-2 text-xs border-t bg-white flex-wrap">
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-blue-500 inline-block"/> Process</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-green-600 inline-block"/> Resource (avail/total)</span>
        <span className="flex items-center gap-1 text-red-500"><span className="w-3 h-3 rounded-full bg-red-400 inline-block"/> Deadlocked</span>
        <span className="flex items-center gap-1"><span className="w-6 border-t-2 border-blue-700 inline-block"/> holds (assignment)</span>
        <span className="flex items-center gap-1"><span className="w-6 border-t-2 border-dashed border-orange-600 inline-block"/> wants (request)</span>
      </div>
    </div>
  );
}
