import type { IndexerResponse } from '@/shared/lib/source/source-client'

export type EditIndexerOptions = {
  indexer: IndexerResponse
}

export type EditIndexerDialog = {
  type: 'EDIT_INDEXER'
  options: EditIndexerOptions
}

export enum EditIndexerOptionEnum {
  INHERIT = 'inherit',
  ENABLED = 'enabled',
  DISABLED = 'disabled',
}

export type EditIndexerOption = {
  value: EditIndexerOptionEnum
  label: string
}
