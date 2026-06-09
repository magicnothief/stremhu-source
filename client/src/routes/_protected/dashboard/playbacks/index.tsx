import { useSuspenseQueries } from '@tanstack/react-query'
import { createFileRoute } from '@tanstack/react-router'
import { HistoryIcon, PlayIcon } from 'lucide-react'

import { Alert, AlertTitle } from '@/shared/components/ui/alert'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/shared/components/ui/card'
import { Separator } from '@/shared/components/ui/separator'
import { getPlaybackHistories, getPlaybacks } from '@/shared/queries/playbacks'

import { PlaybackItem } from './-components/playback-item'
import { DASHBOARD_PLAYBACKS_NAME } from './route'

export const Route = createFileRoute('/_protected/dashboard/playbacks/')({
  component: RouteComponent,
})

function RouteComponent() {
  const [{ data: playbacks }, { data: playbackHistories }] = useSuspenseQueries(
    {
      queries: [getPlaybacks, getPlaybackHistories],
    },
  )

  return (
    <div className="grid gap-8">
      <Card>
        <CardHeader>
          <CardTitle>Aktív {DASHBOARD_PLAYBACKS_NAME.toLowerCase()}</CardTitle>
          <CardDescription>
            Aktív lejátszások és a legfontosabb adatok.
          </CardDescription>
        </CardHeader>
        <Separator />
        <CardContent className="grid gap-3">
          {playbacks.length === 0 ? (
            <Alert>
              <PlayIcon />
              <AlertTitle>Nincs aktív lejátszás</AlertTitle>
            </Alert>
          ) : (
            playbacks.map((playback) => (
              <PlaybackItem key={playback.playbackId} playback={playback} />
            ))
          )}
        </CardContent>
      </Card>
      <Separator />
      <Card>
        <CardHeader>
          <CardTitle>Lejátszási előzmények</CardTitle>
          <CardDescription>
            Elindított lejátszások története és részletes adatai.
          </CardDescription>
        </CardHeader>
        <Separator />
        <CardContent className="grid gap-3">
          {playbackHistories.length === 0 ? (
            <Alert>
              <HistoryIcon />
              <AlertTitle>Nincs lejátszási előzmény</AlertTitle>
            </Alert>
          ) : (
            playbackHistories.map((playback_history) => (
              <PlaybackItem
                key={playback_history.playbackId}
                playback={playback_history}
              />
            ))
          )}
        </CardContent>
      </Card>
    </div>
  )
}
