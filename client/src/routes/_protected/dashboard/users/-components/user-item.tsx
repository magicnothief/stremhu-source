import { Link } from '@tanstack/react-router'
import { TrashIcon } from 'lucide-react'
import type { MouseEvent } from 'react'

import { useConfirmDialog } from '@/features/confirm/use-confirm-dialog'
import { Button } from '@/shared/components/ui/button'
import {
  Item,
  ItemActions,
  ItemContent,
  ItemTitle,
} from '@/shared/components/ui/item'
import type { UserResponse } from '@/shared/lib/source/source-client'
import { useUserDelete } from '@/shared/queries/users'

type UserItemProps = {
  user: UserResponse
  deleteDisabled: boolean
}

export function UserItem(props: UserItemProps) {
  const { user, deleteDisabled } = props

  const confirmDialog = useConfirmDialog()

  const { mutateAsync: deleteUser } = useUserDelete()

  const handleDeleteUser = async (event: MouseEvent<HTMLButtonElement>) => {
    event.preventDefault()
    event.stopPropagation()

    await confirmDialog.confirm({
      title: `Biztos törölni szeretnéd?`,
      description: `"${user.username}" törlése végleges és nem lehetséges visszaállítani!`,
      onConfirm: async () => {
        await deleteUser(user.id)
      },
    })
  }

  return (
    <Item asChild variant="muted" className="min-h-[66px]">
      <Link
        key={user.id}
        to="/dashboard/users/$userId"
        params={{ userId: user.id }}
      >
        <ItemContent>
          <ItemTitle>
            {user.username}
            <span className="text-xs text-muted-foreground">
              ({user.role.name})
            </span>
          </ItemTitle>
        </ItemContent>
        {!deleteDisabled && (
          <ItemActions>
            <Button
              variant="destructive"
              size="icon-sm"
              className="rounded-full"
              onClick={handleDeleteUser}
            >
              <TrashIcon />
            </Button>
          </ItemActions>
        )}
      </Link>
    </Item>
  )
}
