import React from 'react'
import { Button, Box } from './ui'
import { AuthProvider, useAuth } from './auth/AuthProvider'
import LoginForm from './auth/LoginForm'
import InvokeForm from './components/InvokeForm'
import StreamViewer from './components/StreamViewer'

function InnerApp() {
  const { token, logout } = useAuth()
  return (
    <Box maxW={800} mx="auto" p={6}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <h1>AI Agent WebUI</h1>
        <Button onClick={() => logout()} size="sm" colorScheme="red">
          Logout
        </Button>
      </Box>

      <LoginForm />
      <InvokeForm />
      <hr />
      <StreamViewer />
      <Box mt={4} fontSize="sm" color="gray.500">Token: {token ?? 'none'}</Box>
    </Box>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <InnerApp />
    </AuthProvider>
  )
}
