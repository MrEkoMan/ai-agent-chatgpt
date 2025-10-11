import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'

type AuthContextValue = {
  token: string | null
  login: (apiKey: string) => Promise<boolean>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null)

  async function login(apiKey: string) {
    try {
      const res = await fetch('/v1/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey }),
      })
      if (!res.ok) return false
      const data = await res.json()
      setToken(data.token)
      try {
        localStorage.setItem('agent_token', data.token)
      } catch (e) {
        // ignore storage errors in constrained environments
      }
      return true
    } catch (e) {
      console.error(e)
      return false
    }
  }

  function logout() {
    setToken(null)
    try {
      localStorage.removeItem('agent_token')
    } catch (e) {
      // ignore
    }
  }

  useEffect(() => {
    try {
      const t = localStorage.getItem('agent_token')
      if (t) setToken(t)
    } catch (e) {
      // ignore
    }
  }, [])

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
