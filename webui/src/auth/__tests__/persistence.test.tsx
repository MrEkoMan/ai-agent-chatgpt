import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { AuthProvider, useAuth } from '../AuthProvider'
import LoginForm from '../LoginForm'
import React from 'react'

function ReadToken() {
  const { token } = useAuth()
  return <div data-testid="token">{token ?? ''}</div>
}

describe('Auth persistence and logout', () => {
  beforeEach(() => {
    // clear storage and reset fetch mock
    try {
      localStorage.clear()
    } catch (e) {}
    // @ts-ignore
    global.fetch = vi.fn()
  })

  it('persists token to localStorage after successful login', async () => {
    // @ts-ignore
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ token: 'persisted-token' }) })

    const { getByLabelText, getByRole } = render(
      <AuthProvider>
        <LoginForm />
        <ReadToken />
      </AuthProvider>
    )

    const input = getByLabelText(/API Key/i) as HTMLInputElement
    const btn = getByRole('button', { name: /login/i })

    await userEvent.type(input, 'key')
    await userEvent.click(btn)

    // small microtask wait
    await new Promise((r) => setTimeout(r, 0))

    expect(localStorage.getItem('agent_token')).toBe('persisted-token')
    expect(screen.getByTestId('token').textContent).toBe('persisted-token')
  })

  it('clears token on logout', async () => {
    // set a token in storage first
    try {
      localStorage.setItem('agent_token', 'x')
    } catch (e) {}

    // render a small component that calls logout
    function LogoutButton() {
      const { logout } = useAuth()
      return <button onClick={() => logout()}>Logout</button>
    }

    const { getByText } = render(
      <AuthProvider>
        <LogoutButton />
      </AuthProvider>
    )

    const btn = getByText('Logout')
    await userEvent.click(btn)

    // microtask wait
    await new Promise((r) => setTimeout(r, 0))

    expect(localStorage.getItem('agent_token')).toBeNull()
  })
})
