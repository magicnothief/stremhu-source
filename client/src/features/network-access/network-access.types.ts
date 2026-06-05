import type { NetworkConnectionEnum } from '@/shared/lib/source/source-client'

export type NetworkAccessDialog = {
  type: 'NETWORK_ACCESS'
}

export type NetworkMode = 'duckdns' | 'myaddr' | 'manual'

export type NetworkAutoFormValues = {
  mode: 'duckdns' | 'myaddr'
  host: string
  token: string
  email: string
  connection: NetworkConnectionEnum
}

export type NetworkManualFormValues = {
  mode: 'manual'
  host: string
  reverseProxy: boolean
}

export type NetworkAccessFormValues =
  | NetworkAutoFormValues
  | NetworkManualFormValues

export type ConnectionCheckType = 'idle' | 'pending' | 'success' | 'error'
