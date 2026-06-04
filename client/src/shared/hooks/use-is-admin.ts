import { useQuery } from '@tanstack/react-query'

import { UserRole } from '../lib/source/source-client'
import { getMe } from '../queries/me'

export const useIsAdmin = () => {
  const { data: me } = useQuery(getMe())

  const isAdmin = me?.role.id === UserRole.admin

  return { isAdmin }
}
