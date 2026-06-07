import { queryOptions } from '@tanstack/react-query'

import {
  playbacksGetHistoryList,
  playbacksGetList,
} from '../lib/source/source-client'

export const getPlaybacks = queryOptions({
  queryKey: ['playbacks'],
  refetchInterval: 1000,
  queryFn: async () => {
    const response = await playbacksGetList()
    return response
  },
})

export const getPlaybackHistories = queryOptions({
  queryKey: ['playbacks', 'histories'],
  refetchInterval: 5000,
  queryFn: async () => {
    const response = await playbacksGetHistoryList()
    return response
  },
})
