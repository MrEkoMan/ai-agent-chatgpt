import React, { useEffect, useState } from 'react'
import { useAuth } from '../auth/AuthProvider'

export default function StreamViewer() {
  const { token } = useAuth()
  const [lines, setLines] = useState<string[]>([])

  useEffect(() => {
    if (!token) return

    const evtSource = new EventSource('/v1/invoke/stream', { withCredentials: false } as any)
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
    <div>
      <h2>Stream</h2>
      <div style={{ background: '#111', color: '#eee', padding: 12, minHeight: 120 }}>
        {lines.map((l: string, i: number) => (
          <div key={i}>
            <pre>{l}</pre>
          </div>
        ))}
      </div>
    </div>
  )
}
