import React, { useState } from 'react'
import { Button, Input, Box } from '../ui'
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
    <form onSubmit={handleSubmit}>
      <Box display="flex" gap={4} alignItems="center">
  <label htmlFor="apiKey">API Key</label>
  <Input id="apiKey" value={apiKey} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setApiKey(e.target.value)} />
        <Button type="submit" loading={loading} colorScheme="teal">
          {loading ? 'Logging...' : 'Login'}
        </Button>
      </Box>
    </form>
  )
}
