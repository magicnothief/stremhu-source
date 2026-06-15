//  @ts-check
import { tanstackConfig } from '@tanstack/eslint-config'

export default [
  {
    ignores: [
      'node_modules/',
      'dist/',
      'build/',
      'coverage/',
      'src/routeTree.gen.ts',
    ],
  },
  ...tanstackConfig,
  {
    rules: {
      'import/order': 'off',
      '@typescript-eslint/array-type': ['error', { default: 'array' }],
    },
  },
]
