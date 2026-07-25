import { useEffect, useReducer } from 'react'
import { AppStateContext, buildInitialState, pickPersistedFields, reducer } from './store.js'
import { saveState, STORAGE_KEY } from '../lib/storage.js'
import { clearStoredSessionId } from '../api/client.js'

export function AppStateProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, undefined, buildInitialState)

  useEffect(() => {
    saveState(STORAGE_KEY, pickPersistedFields(state))
  }, [state])

  // Every app open starts a brand new conversation (ChatGPT-style) — clear
  // any leftover backend session id from a previous run so the first message
  // sent creates a fresh session, rather than silently resuming an old one.
  // The farmer's profile and identity (farmer_key) are untouched here, so
  // memory still carries forward into that new session; past conversations
  // remain reachable via the chat sidebar.
  useEffect(() => {
    clearStoredSessionId()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return <AppStateContext.Provider value={{ state, dispatch }}>{children}</AppStateContext.Provider>
}
