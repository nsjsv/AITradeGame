// Initialize localStorage FIRST (before any imports)
const store: Record<string, string> = {}
Object.defineProperty(global, 'localStorage', {
  value: {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value },
    removeItem: (key: string) => { delete store[key] },
    clear: () => { Object.keys(store).forEach(key => delete store[key]) },
    key: (index: number) => Object.keys(store)[index] || null,
    get length() { return Object.keys(store).length },
  },
  writable: true,
  configurable: true,
})

import '@testing-library/jest-dom'
