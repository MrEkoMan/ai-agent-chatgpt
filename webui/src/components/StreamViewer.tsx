import React, { useEffect, useState } from 'react'
import { useAuth } from '../auth/AuthProvider'
import { Box, Heading } from '../ui'

export default function StreamViewer() {
  const { token } = useAuth()
  const [lines, setLines] = useState<string[]>([])

  useEffect(() => {
    if (!token) return

    const url = '/v1/invoke/stream' + (token ? `?token=${encodeURIComponent(token)}` : '')
    const evtSource = new EventSource(url, { withCredentials: false } as any)
    evtSource.onmessage = (e: MessageEvent) => {
      try {
        const payload = JSON.parse(e.data)
        setLines((s: string[]) => [...s, payload.output || JSON.stringify(payload)])
      } catch (err) {
        setLines((s: string[]) => [...s, e.data])
      }
    }
    evtSource.onerror = (e) => {
      console.error('SSE error', e)
      evtSource.close()
    }

    return () => evtSource.close()
  }, [token])

  return (
    <Box>
      <Heading size="md">Stream</Heading>
      <Box bg="#111" color="#eee" p={3} minH="120px">
        {lines.map((l: string, i: number) => (
          <Box key={i} mb={2}>
            <pre>{l}</pre>
          </Box>
        ))}
      </Box>
    </Box>
  )
}
