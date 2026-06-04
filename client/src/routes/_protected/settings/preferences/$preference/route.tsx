import { Outlet, createFileRoute } from '@tanstack/react-router'
import { upperFirst } from 'lodash'
import * as z from 'zod'

import { getMePreference } from '@/shared/queries/me'

const preferenceParamsSchema = z.object({
  preference: z.string(),
})

const RouteComponent = () => <Outlet />

export const Route = createFileRoute(
  '/_protected/settings/preferences/$preference',
)({
  component: RouteComponent,
  params: {
    parse: (rawParams) => preferenceParamsSchema.parse(rawParams),
  },
  beforeLoad: async ({ context, params }) => {
    const { preference } = params

    const mePreference = await context.queryClient.ensureQueryData(
      getMePreference(preference),
    )

    return {
      mePreference,
    }
  },
  loader: ({ context }) => {
    const { mePreference } = context

    return {
      breadcrumb: `${upperFirst(mePreference.name)} konfigurációja`,
    }
  },
})
