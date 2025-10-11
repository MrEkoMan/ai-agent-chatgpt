import React from 'react'
import { AuthProvider } from './auth/AuthProvider'
import LoginForm from './auth/LoginForm'
import InvokeForm from './components/InvokeForm'
import StreamViewer from './components/StreamViewer'

export default function App() {
  return (
    <AuthProvider>
      <div style={{ maxWidth: 800, margin: '0 auto', padding: 24 }}>
        <h1>AI Agent WebUI</h1>
        <LoginForm />
        <InvokeForm />
        <hr />
        <StreamViewer />
      </div>
    </AuthProvider>
  )
}
