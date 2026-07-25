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

      try {
        const response = await sendChatMessage(trimmed, state.farmerProfile, state.ui.language)

        for (const event of response.trace) {
          await sleep(350)
          dispatch({ type: 'APPEND_TRACE_EVENT', payload: event })
        }

        dispatch({ type: 'SET_AGENT_TYPING', payload: false })
        dispatch({ type: 'ADD_MESSAGE', payload: response.reply })
        dispatch({ type: 'SET_CURRENT_SESSION', payload: response.sessionId })

        if (response.profile) {
          dispatch({ type: 'SET_PROFILE', payload: response.profile })
        }
        // A plain chat reply (a greeting, a general question) carries no new
        // recommendations/timeline/financials/weather/alerts — don't let an
        // empty response wipe out the dashboard from the last real recommendation.
        if (response.recommendations.length) {
          dispatch({ type: 'SET_RECOMMENDATIONS', payload: response.recommendations })
        }
        if (response.timeline.length) {
          dispatch({ type: 'SET_TIMELINE', payload: response.timeline })
        }
        if (response.financials) {
          dispatch({ type: 'SET_FINANCIALS', payload: response.financials })
        }
        if (response.fertilizerSchedule) {
          dispatch({ type: 'SET_FERTILIZER_SCHEDULE', payload: response.fertilizerSchedule })
        }
        if (response.irrigationSchedule) {
          dispatch({ type: 'SET_IRRIGATION_SCHEDULE', payload: response.irrigationSchedule })
        }
        if (response.pestRisks) {
          dispatch({ type: 'SET_PEST_RISKS', payload: response.pestRisks })
        }
        if (response.marketplaceOffers) {
          dispatch({ type: 'SET_MARKETPLACE_OFFERS', payload: response.marketplaceOffers })
        }
        if (response.alerts.length) {
          dispatch({ type: 'SET_ALERTS', payload: response.alerts })
        }
        if (response.weather) {
          dispatch({ type: 'SET_WEATHER', payload: response.weather })
        }
      } catch (error) {
        dispatch({ type: 'SET_AGENT_TYPING', payload: false })
        dispatch({
          type: 'ADD_MESSAGE',
          payload: {
            id: `msg_${Date.now()}`,
            role: 'assistant',
            content: `Sorry, something went wrong talking to the agent: ${error.message}`,
            timestamp: new Date().toISOString(),
          },
        })
      }
    },
    [dispatch, state.farmerProfile, state.ui.language],
  )

  return send
}
