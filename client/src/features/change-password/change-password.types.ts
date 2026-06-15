import type { UserResponse } from '@/shared/lib/source/source-client'

export type ChangePasswordOptions = {
  user?: UserResponse
}

export type ChangePasswordDialog = {
  type: 'CHANGE_PASSWORD'
  options: ChangePasswordOptions
}
