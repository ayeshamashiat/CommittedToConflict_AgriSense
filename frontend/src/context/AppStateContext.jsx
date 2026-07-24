import { useEffect, useReducer } from 'react'
import { AppStateContext, buildInitialState, pickPersistedFields, reducer } from './store.js'
import { saveState, STORAGE_KEY } from '../lib/storage.js'

export function AppStateProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, undefined, buildInitialState)

  useEffect(() => {
    saveState(STORAGE_KEY, pickPersistedFields(state))
  }, [state])

  return <AppStateContext.Provider value={{ state, dispatch }}>{children}</AppStateContext.Provider>
}
