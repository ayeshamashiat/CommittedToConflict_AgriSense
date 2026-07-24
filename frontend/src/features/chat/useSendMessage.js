import { useCallback } from 'react'
import { useAppState } from '../../context/useAppState.js'
import { sendChatMessage } from '../../api/index.js'

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export function useSendMessage() {
  const { state, dispatch } = useAppState()

  const send = useCallback(
    async (text) => {
      const trimmed = text.trim()
      if (!trimmed) return

      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          id: `msg_${Date.now()}`,
          role: 'user',
          content: trimmed,
          timestamp: new Date().toISOString(),
        },
      })
      dispatch({ type: 'SET_AGENT_TYPING', payload: true })
      dispatch({ type: 'RESET_TRACE' })

      const response = await sendChatMessage(trimmed, state.farmerProfile)

      for (const event of response.trace) {
        await sleep(350)
        dispatch({ type: 'APPEND_TRACE_EVENT', payload: event })
      }

      dispatch({ type: 'SET_AGENT_TYPING', payload: false })
      dispatch({ type: 'ADD_MESSAGE', payload: response.reply })

      if (response.profile) {
        dispatch({ type: 'SET_PROFILE', payload: response.profile })
      }
      dispatch({ type: 'SET_RECOMMENDATIONS', payload: response.recommendations })
      dispatch({ type: 'SET_TIMELINE', payload: response.timeline })
      dispatch({ type: 'SET_FINANCIALS', payload: response.financials })
      if (response.alerts) {
        dispatch({ type: 'SET_ALERTS', payload: response.alerts })
      }
      if (response.weather) {
        dispatch({ type: 'SET_WEATHER', payload: response.weather })
      }
    },
    [dispatch, state.farmerProfile],
  )

  return send
}
