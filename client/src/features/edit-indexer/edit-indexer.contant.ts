import type { EditIndexerOption } from './edit-indexer.type'
import { EditIndexerOptionEnum } from './edit-indexer.type'

export const HIT_AND_RUN_OPTIONS: EditIndexerOption[] = [
  {
    value: EditIndexerOptionEnum.INHERIT,
    label: 'Globál beállítás használata',
  },
  {
    value: EditIndexerOptionEnum.ENABLED,
    label: 'Engedélyezés',
  },
  {
    value: EditIndexerOptionEnum.DISABLED,
    label: 'Letiltás',
  },
]
