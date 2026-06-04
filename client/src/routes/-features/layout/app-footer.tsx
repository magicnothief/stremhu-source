import { useQuery } from '@tanstack/react-query'

import { assertExists } from '@/shared/lib/utils'
import { getSystemStatus } from '@/shared/queries/system'

export function AppFooter() {
  const { data: systemStatus } = useQuery(getSystemStatus)
  assertExists(systemStatus)

  return (
    <div className="bg-card border-t shadow-sm">
      <div className="container mx-auto max-w-3xl p-4">
        <div className="flex flex-col gap-1 sm:flex-row sm:justify-between sm:items-center text-muted-foreground text-sm">
          <p>StremHU Source · {systemStatus.version}</p>
          <div className="flex flex-col sm:items-end gap-1">
            <p>
              Hibát találtál?{' '}
              <a
                href="https://discord.gg/jRSPPY5XaN"
                target="_blank"
                className="link-primary underline"
              >
                Jelentsd Discordon
              </a>
            </p>
            <p>
              Elakadtál?{' '}
              <a
                href="https://stremhu.app"
                target="_blank"
                className="link-primary underline"
              >
                Nézd át a dokumentációt
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
