import { vi } from 'vitest'
// Provide lightweight mocks for Chakra UI components used in tests so we don't need full provider
vi.mock('@chakra-ui/react', () => {
  const React = require('react')
  const passthrough = (props: any) => React.createElement('div', props, props.children)
  return {
    __esModule: true,
    Box: passthrough,
    Button: (props: any) => React.createElement('button', props, props.children),
    Input: (props: any) => React.createElement('input', props),
    Container: passthrough,
    Heading: passthrough,
  }
})
