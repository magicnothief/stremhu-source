import { useSuspenseQuery } from '@tanstack/react-query'
import { toast } from 'sonner'
import { useDialogsStore } from '@/routes/-features/dialogs/dialogs-store'
import type { OpenedDialog } from '@/routes/-features/dialogs/dialogs-store'
import { Button } from '@/shared/components/ui/button'
import {
  Dialog,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogScrollContent,
  DialogTitle,
} from '@/shared/components/ui/dialog'
import { getNetworkSettings, useNetworkReset } from '@/shared/queries/network'
import { useConfirmDialog } from '@/features/confirm/use-confirm-dialog'
import { parseApiError } from '@/shared/lib/utils'

import {
  NETWORK_ACCESS_FORM_ID,
  NETWORK_ACCESS_HEADER,
  NetworkAccess,
} from './network-access-form'
import type { NetworkAccessDialog } from './network-access.types'

export function NetworkAccessDialog(
  dialog: OpenedDialog & NetworkAccessDialog,
) {
  const dialogsStore = useDialogsStore()
  const { data: networkSettings } = useSuspenseQuery(getNetworkSettings)
  const { mutateAsync: resetNetwork, isPending: isResetting } = useNetworkReset()
  const { confirm } = useConfirmDialog()

  const handleReset = async () => {
    await confirm({
      title: 'Biztosan visszaállítod a hálózati beállításokat?',
      description: 'Ezzel a szerver újraindul, és ismét csak a helyi hálózaton lesz elérhető.',
      confirmText: 'Visszaállítás',
      onConfirm: async () => {
        try {
          await resetNetwork()
          toast.success('Hálózati beállítások visszaállítva. A szerver újraindul...', {
            duration: Infinity,
          })
          dialogsStore.closeDialog(dialog.id)
        } catch (error) {
          toast.error(parseApiError(error))
        }
      },
    })
  }

  return (
    <Dialog open={dialog.open}>
      <DialogScrollContent
        className="md:max-w-md"
        onEscapeKeyDown={() => dialogsStore.closeDialog(dialog.id)}
      >
        <DialogHeader>
          <DialogTitle>{NETWORK_ACCESS_HEADER.TITLE}</DialogTitle>
          <DialogDescription>
            {NETWORK_ACCESS_HEADER.DESCRIPTION}
          </DialogDescription>
        </DialogHeader>
        <NetworkAccess onSuccess={() => dialogsStore.closeDialog(dialog.id)} />
        <DialogFooter className="flex justify-between items-center sm:justify-between">
          <div className="flex gap-2">
            {networkSettings.mode !== 'local' && (
              <Button
                type="button"
                variant="destructive"
                onClick={handleReset}
                disabled={isResetting}
              >
                Reset
              </Button>
            )}
          </div>
          <div className="flex gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => dialogsStore.closeDialog(dialog.id)}
            >
              Mégsem
            </Button>
            <Button type="submit" form={NETWORK_ACCESS_FORM_ID}>
              Konfigurálás
            </Button>
          </div>
        </DialogFooter>
      </DialogScrollContent>
    </Dialog>
  )
}
