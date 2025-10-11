import React from 'react'

export const Box: React.FC<any> = ({ children, ...props }) => (
  <div {...props as any}>{children}</div>
)

export const Button: React.FC<any> = ({ children, ...props }) => (
  <button {...props as any}>{children}</button>
)

export const Input: React.FC<any> = (props) => <input {...props as any} />

export const Heading: React.FC<any> = ({ children, ...props }) => (
  <h2 {...props as any}>{children}</h2>
)

export const Stack: React.FC<any> = ({ children, ...props }) => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }} {...props as any}>
    {children}
  </div>
)

export default {
  Box,
  Button,
  Input,
  Heading,
  Stack,
}
