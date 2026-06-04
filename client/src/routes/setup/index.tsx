import { createFileRoute, redirect } from '@tanstack/react-router'

import { getSystemStatus } from '@/shared/queries/system'

export const Route = createFileRoute('/setup/')({
  beforeLoad: async ({ context }) => {
    const queryClient = context.queryClient
    const { configured } = await queryClient.ensureQueryData(getSystemStatus)

    if (!configured) {
      throw redirect({ to: '/setup/user' })
    }

    throw redirect({ to: '/' })
  },
})
