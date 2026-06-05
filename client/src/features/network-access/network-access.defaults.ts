import { NetworkConnectionEnum } from '@/shared/lib/source/source-client'

import type { NetworkAccessFormValues } from './network-access.types'

export const networkAccessDefaultValues: NetworkAccessFormValues = {
  mode: 'duckdns',
  host: '',
  token: '',
  email: '',
  connection: NetworkConnectionEnum.local,
}
