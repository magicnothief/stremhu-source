import { queryOptions } from '@tanstack/react-query'

import { preferencesGet, preferencesGetAll } from '../lib/source/source-client'

export const getPreferences = queryOptions({
  queryKey: ['preferences'],
  queryFn: async () => {
    const response = await preferencesGetAll()

    return response
  },
})

export const getPreference = (preference_id: string) =>
  queryOptions({
    queryKey: ['preferences', preference_id],
    queryFn: async () => {
      const response = await preferencesGet(preference_id)

      return response
    },
  })
