export default function ResultPanel({ result, recoveryResult }) {
  if (!result && !recoveryResult) return (
    <div className="flex items-center justify-center h-full text-gray-400 text-sm p-4 text-center">
      Run detection or recovery to see results here
    </div>
  );

  return (
    <div className="p-4 flex flex-col gap-4 overflow-y-auto h-full">
      {result && (
        <div>
          <div className="text-xs font-semibold text-gray-500 uppercase mb-2">Detection Result</div>
          <div className={`rounded-lg p-3 text-sm font-medium ${result.has_deadlock ? 'bg-red-50 border border-red-300 text-red-700' : 'bg-green-50 border border-green-300 text-green-700'}`}>
            {result.has_deadlock ? '⚠ DEADLOCK DETECTED' : '✓ SAFE STATE'}
          </div>
          {result.has_deadlock && (
            <div className="mt-2 text-sm flex flex-col gap-1">
              <div><span className="font-medium">Deadlocked:</span> {result.deadlocked_processes.join(', ')}</div>
              <div><span className="font-medium">Cycle:</span> {[...result.cycle_path, result.cycle_path[0]].join(' → ')}</div>
            </div>
          )}
        </div>
      )}

      {recoveryResult && (
        <div>
          <div className="text-xs font-semibold text-gray-500 uppercase mb-2">Recovery Log ({recoveryResult.strategy})</div>
          {recoveryResult.had_deadlock ? (
            <div className="flex flex-col gap-1">
              {recoveryResult.recovery_log.map((entry, i) => (
                <div key={i} className={`text-xs px-2 py-1 rounded ${entry.includes('complete') ? 'bg-green-50 text-green-700 font-medium' : 'bg-gray-50 text-gray-600'}`}>
                  {entry}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-green-600 bg-green-50 border border-green-200 rounded p-2">No deadlock — nothing to recover</div>
          )}
        </div>
      )}
    </div>
  );
}
