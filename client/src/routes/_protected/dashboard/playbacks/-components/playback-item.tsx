import { FilePlayIcon, PlayIcon, UserIcon } from 'lucide-react'

import { Badge } from '@/shared/components/ui/badge'
import { Item, ItemContent, ItemTitle } from '@/shared/components/ui/item'
import { Progress } from '@/shared/components/ui/progress'
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/shared/components/ui/tooltip'
import type {
  PlaybackHistoryResponse,
  PlaybackResponse,
} from '@/shared/lib/source/source-client'
import { formatDateTime } from '@/shared/lib/utils'

type PlaybackItemProps = {
  playback: PlaybackResponse | PlaybackHistoryResponse
}

export function PlaybackItem(props: PlaybackItemProps) {
  const { playback } = props

  return (
    <div className="grid gap-2 border border-transparent rounded-md bg-muted/50 p-4">
      {'progress' in playback ? <Progress value={playback.progress} /> : null}
      <Item className="p-0">
        <ItemContent>
          <ItemTitle>
            [{playback.indexerDefinition.name}] {playback.torrentName}
          </ItemTitle>
        </ItemContent>
      </Item>
      <div className="grid gap-2 text-muted-foreground text-sm font-normal">
        <div className="mt-1 flex flex-wrap gap-2">
          <Badge
            variant="secondary"
            title={`Felhasználó: ${playback.user.username}`}
          >
            <UserIcon />
            {playback.user.username}
          </Badge>
          <Tooltip>
            <TooltipTrigger asChild>
              <Badge variant="secondary">
                <FilePlayIcon />
                Fájl
              </Badge>
            </TooltipTrigger>
            <TooltipContent>{playback.fileName}</TooltipContent>
          </Tooltip>

          <Badge
            variant="secondary"
            title={`Lejátszás időpontja: ${formatDateTime(playback.createdAt)}`}
          >
            <PlayIcon />
            {formatDateTime(playback.createdAt)}
          </Badge>
        </div>
      </div>
    </div>
  )
}
