'use client'

import { useEffect, useRef, useState, useCallback } from 'react'

interface WebSocketMessage {
  type: string
  data: any
}

interface UseWebSocketOptions {
  url: string
  onMessage?: (message: WebSocketMessage) => void
  onError?: (error: Event) => void
  onOpen?: () => void
  onClose?: () => void
  reconnect?: boolean
  reconnectInterval?: number
}

export function useWebSocket({
  url,
  onMessage,
  onError,
  onOpen,
  onClose,
  reconnect = true,
  reconnectInterval = 3000,
}: UseWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false)
  const [hasReceivedMessage, setHasReceivedMessage] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const shouldReconnectRef = useRef(true)
  
  // Use refs for callbacks to prevent reconnection on every render
  const onMessageRef = useRef(onMessage)
  const onErrorRef = useRef(onError)
  const onOpenRef = useRef(onOpen)
  const onCloseRef = useRef(onClose)
  
  // Update refs when callbacks change
  useEffect(() => {
    onMessageRef.current = onMessage
    onErrorRef.current = onError
    onOpenRef.current = onOpen
    onCloseRef.current = onClose
  }, [onMessage, onError, onOpen, onClose])

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    try {
      // Convert http(s) to ws(s)
      const wsUrl = url.replace(/^http/, 'ws')
      console.log(`[WebSocket] Connecting to ${wsUrl}`)
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        console.log(`[WebSocket] Connection opened to ${wsUrl}`)
        // Set connected state, but we'll also track if we've received messages
        setIsConnected(true)
        setHasReceivedMessage(false) // Reset on new connection
        onOpenRef.current?.()
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          console.log(`[WebSocket] Received message:`, message)
          setLastMessage(message)
          setHasReceivedMessage(true) // Mark that we've received at least one message
          onMessageRef.current?.(message)
        } catch (error) {
          console.error('[WebSocket] Failed to parse WebSocket message:', error, event.data)
        }
      }

      ws.onerror = (error) => {
        console.error(`[WebSocket] Error on connection to ${wsUrl}:`, error)
        // On error, mark as not connected so polling can resume
        setIsConnected(false)
        setHasReceivedMessage(false)
        onErrorRef.current?.(error)
      }

      ws.onclose = (event) => {
        console.log(`[WebSocket] Connection closed to ${wsUrl}`, { code: event.code, reason: event.reason, wasClean: event.wasClean })
        setIsConnected(false)
        setHasReceivedMessage(false)
        onCloseRef.current?.()

        // Attempt to reconnect if enabled
        if (shouldReconnectRef.current && reconnect) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`[WebSocket] Attempting to reconnect to ${wsUrl}`)
            connect()
          }, reconnectInterval)
        }
      }
    } catch (error) {
      console.error('[WebSocket] Connection error:', error)
      setIsConnected(false)
      setHasReceivedMessage(false)
    }
  }, [url, reconnect, reconnectInterval])

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }, [])

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected. Cannot send message.')
    }
  }, [])

  useEffect(() => {
    connect()
    return () => {
      disconnect()
    }
    // Only reconnect if URL changes, not if callbacks change
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url])

  return {
    isConnected,
    hasReceivedMessage, // Export this so components can check if messages are actually flowing
    lastMessage,
    sendMessage,
    disconnect,
    connect,
  }
}

