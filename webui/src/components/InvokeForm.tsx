import React, { useState } from 'react'
import { useAuth } from '../auth/AuthProvider'
import { Button, Input, Box, Stack } from '../ui'

export default function InvokeForm() {
  const { token, login } = useAuth()
  const [input, setInput] = useState('')
  const [output, setOutput] = useState('')

  async function handleInvoke(e: React.FormEvent) {
    e.preventDefault()
    if (!token) {
      const ok = await login(prompt('Enter API key') || '')
      if (!ok) return
    }

    const res = await fetch('/v1/invoke', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ input }),
    })
    const data = await res.json()
    setOutput(data.output || '')
  }

  return (
    <form onSubmit={handleInvoke}>
      <Box mb={4}>
        <label>
          Prompt
          <Input value={input} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInput(e.target.value)} />
        </label>
      </Box>
      <Box mb={4}>
        <Button type="submit" colorScheme="blue">
          Invoke
        </Button>
      </Box>
      <Box>
        <strong>Output</strong>
        <pre>{output}</pre>
      </Box>
    </form>
  )
}
