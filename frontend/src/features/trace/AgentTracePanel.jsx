import Panel from '../../components/ui/Panel.jsx'
import EmptyState from '../../components/ui/EmptyState.jsx'
import TraceEvent from './TraceEvent.jsx'
import { useAppState } from '../../context/useAppState.js'

export default function AgentTracePanel() {
  const { state } = useAppState()
  const { agentTrace } = state

  return (
    <Panel title="Agent Activity" contentClassName="p-3">
      {agentTrace.length === 0 ? (
        <EmptyState
          icon="🔍"
          title="No tool calls yet"
          description="Every backend tool call the agent makes will be logged here in order."
        />
      ) : (
        <div className="flex flex-col gap-2">
          {agentTrace.map((event) => (
            <TraceEvent key={event.id} event={event} />
          ))}
        </div>
      )}
    </Panel>
  )
}
