import { Outlet, createFileRoute } from '@tanstack/react-router'

import { getTorrents } from '@/shared/queries/torrents'

export const RELAY_TORRENTS_NAME = 'Torrentek'

const RouteComponent = () => <Outlet />

export const Route = createFileRoute('/_protected/relay/torrents')({
  component: RouteComponent,
  beforeLoad: async ({ context }) => {
    await Promise.all([context.queryClient.ensureQueryData(getTorrents)])
  },
  loader: () => {
    return { breadcrumb: RELAY_TORRENTS_NAME }
  },
})
