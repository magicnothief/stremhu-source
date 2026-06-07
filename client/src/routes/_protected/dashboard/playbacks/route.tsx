import { Outlet, createFileRoute } from '@tanstack/react-router'

import { getPlaybackHistories, getPlaybacks } from '@/shared/queries/playbacks'

export const DASHBOARD_PLAYBACKS_NAME = 'Lejátszások'

const RouteComponent = () => <Outlet />

export const Route = createFileRoute('/_protected/dashboard/playbacks')({
  component: RouteComponent,
  beforeLoad: async ({ context }) => {
    await Promise.all([
      context.queryClient.ensureQueryData(getPlaybacks),
      context.queryClient.ensureQueryData(getPlaybackHistories),
    ])
  },
  loader: () => {
    return { breadcrumb: DASHBOARD_PLAYBACKS_NAME }
  },
})
