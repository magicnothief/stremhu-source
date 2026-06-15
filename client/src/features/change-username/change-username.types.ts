import type { UserResponse } from '@/shared/lib/source/source-client'

export type ChangeUsernameOptions = {
  user?: UserResponse
}

export type ChangeUsernameDialog = {
  type: 'CHANGE_USERNAME'
  options: ChangeUsernameOptions
}
