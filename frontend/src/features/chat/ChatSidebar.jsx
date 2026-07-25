import { useCallback, useEffect, useState } from 'react'
import clsx from 'clsx'
import { useAppState } from '../../context/useAppState.js'
import { useTranslation } from '../../context/useTranslation.js'
import {
  clearStoredSessionId,
  fetchSessionHistory,
  fetchSessionList,
  getFarmerKey,
  storeSessionId,
} from '../../api/client.js'
import { formatDate } from '../../lib/formatters.js'

export default function ChatSidebar() {
  const { state, dispatch } = useAppState()
  const { t } = useTranslation()
  const [sessions, setSessions] = useState([])
  const [loadingSessionId, setLoadingSessionId] = useState(null)

  const refreshList = useCallback(async () => {
    const farmerKey = getFarmerKey(state.farmerProfile)
    try {
      const rows = await fetchSessionList(farmerKey)
      setSessions(rows)
    } catch {
      // Sidebar list is a nice-to-have, not load-bearing — leave it as-is on failure.
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    refreshList()
  }, [refreshList, state.currentSessionId])

  const startNewChat = () => {
    clearStoredSessionId()
    dispatch({ type: 'START_NEW_CHAT' })
  }

  const openSession = async (sessionId) => {
    if (sessionId === state.currentSessionId) return
    setLoadingSessionId(sessionId)
    try {
      const hydrated = await fetchSessionHistory(sessionId, state.farmerProfile)
      storeSessionId(sessionId)
      dispatch({ type: 'SWITCH_SESSION', payload: { sessionId, ...hydrated } })
    } catch {
      // Session may have been cleared server-side — leave the current chat open.
    } finally {
      setLoadingSessionId(null)
    }
  }

  return (
    <div className="flex h-full w-64 shrink-0 flex-col border-r border-earth-100 bg-wheat-50">
      <div className="p-3">
        <button
          type="button"
          onClick={startNewChat}
          className="flex w-full items-center justify-center gap-2 rounded-lg border border-earth-200 bg-white px-3 py-2 text-sm font-medium text-stone-700 hover:bg-wheat-100"
        >
          <span aria-hidden>+</span> {t('newChat').replace('+ ', '')}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2 pb-3">
        <p className="px-2 pb-1 text-xs font-semibold uppercase tracking-wide text-stone-400">{t('chats')}</p>
        {sessions.length === 0 && (
          <p className="px-2 py-2 text-sm text-stone-400">{t('noPreviousChats')}</p>
        )}
        <ul className="flex flex-col gap-0.5">
          {sessions.map((s) => (
            <li key={s.sessionId}>
              <button
                type="button"
                onClick={() => openSession(s.sessionId)}
                disabled={loadingSessionId === s.sessionId}
                className={clsx(
                  'flex w-full flex-col items-start gap-0.5 rounded-lg px-3 py-2 text-left transition-colors',
                  s.sessionId === state.currentSessionId
                    ? 'bg-leaf-100 text-leaf-800'
                    : 'text-stone-600 hover:bg-wheat-100',
                )}
              >
                <span className="w-full truncate text-sm">{s.preview}</span>
                <span className="text-xs text-stone-400">{formatDate(s.updatedAt)}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
