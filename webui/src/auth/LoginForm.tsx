import React, { useState } from 'react'
import { useAuth } from './AuthProvider'

export default function LoginForm() {
  const { login } = useAuth()
  const [apiKey, setApiKey] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    const ok = await login(apiKey)
    setLoading(false)
    if (!ok) alert('Login failed')
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
      <label style={{ display: 'flex', flexDirection: 'column' }}>
        API Key
        <input value={apiKey} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setApiKey(e.target.value)} />
      </label>
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  )
}
