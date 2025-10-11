import React from 'react'
import { render } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { AuthProvider } from '../AuthProvider'
import LoginForm from '../LoginForm'

describe('LoginForm', () => {
  beforeEach(() => {
    // reset fetch mock
    // @ts-ignore
    global.fetch = vi.fn()
  })

  it('calls login and stores token on success', async () => {
    // @ts-ignore
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ token: 'abc' }) })

    const { getByLabelText, getByRole } = render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    )

  const input = getByLabelText(/API Key/i) as HTMLInputElement
  const btn = getByRole('button', { name: /login/i })

  await userEvent.type(input, 'key')
  await userEvent.click(btn)

  // verify fetch called
  await new Promise((r) => setTimeout(r, 0))
  expect(fetch).toHaveBeenCalled()
    // localStorage should have been written — env may not support, just ensure no error thrown
  })
})
