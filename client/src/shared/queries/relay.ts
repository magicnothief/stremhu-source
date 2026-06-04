import {
  queryOptions,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query'

import type { RelaySettingsUpdateRequest } from '../lib/source/source-client'
import {
  relayGetSettings,
  relayUpdateSettings,
} from '../lib/source/source-client'

export const getRelaySettings = queryOptions({
  queryKey: ['relay', 'settings'],
  queryFn: async () => {
    const settings = await relayGetSettings()
    return settings
  },
})

export function useUpdateRelaySetting() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: RelaySettingsUpdateRequest) => {
      const setting = await relayUpdateSettings(payload)
      return setting
    },
    onSuccess: async () => {
      await queryClient.fetchQuery({ ...getRelaySettings, staleTime: 0 })
    },
  })
}
