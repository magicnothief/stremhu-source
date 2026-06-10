import { queryOptions, useMutation } from '@tanstack/react-query'

import type {
  NetworkAutoSetupRequest,
  NetworkManualSetupRequest,
} from '../lib/source/source-client'
import {
  networkGetDdnsProviders,
  networkGetSettings,
  networkReset,
  networkSetup,
} from '../lib/source/source-client'

export const getNetworkSettings = queryOptions({
  queryKey: ['network', 'settings'],
  queryFn: async () => {
    const settings = await networkGetSettings()
    return settings
  },
})

export const getNetworkProviders = queryOptions({
  queryKey: ['network', 'providers'],
  queryFn: async () => {
    const providers = await networkGetDdnsProviders()
    return providers
  },
})

export function useNetworkConfig() {
  return useMutation({
    mutationFn: async (
      payload: NetworkAutoSetupRequest | NetworkManualSetupRequest,
    ) => {
      const response = await networkSetup(payload)
      return response
    },
  })
}

export function useNetworkReset() {
  return useMutation({
    mutationFn: async () => {
      const response = await networkReset()
      return response
    },
  })
}
