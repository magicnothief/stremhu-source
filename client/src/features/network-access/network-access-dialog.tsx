import type { MouseEventHandler, SubmitEventHandler } from 'react'

import type { OpenedDialog } from '@/routes/-features/dialogs/dialogs-store'
import { useDialogsStore } from '@/routes/-features/dialogs/dialogs-store'
import { Button } from '@/shared/components/ui/button'
import {
  Dialog,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogScrollContent,
  DialogTitle,
} from '@/shared/components/ui/dialog'

import type { NetworkAccessDialog } from './network-access.types'
import { NetworkSelector } from './network-selector'
import { UrlConfiguration } from './url-configuration'
import { useNetworkAccessForm } from './use-network-access-form'

export function NetworkAccessDialog(
  dialog: OpenedDialog & NetworkAccessDialog,
) {
  const dialogsStore = useDialogsStore()

  const form = useNetworkAccessForm({
    onSuccess: () => {
      dialogsStore.closeDialog(dialog.id)
    },
  })

  const handleSubmit: SubmitEventHandler<HTMLFormElement> = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    await form.handleSubmit()
  }

  const handleClose: MouseEventHandler<HTMLButtonElement> = (e) => {
    e.preventDefault()
    e.stopPropagation()
    dialogsStore.closeDialog(dialog.id)
  }

  return (
    <Dialog open={dialog.open}>
      <DialogScrollContent
        className="md:max-w-lg"
        onEscapeKeyDown={() => dialogsStore.closeDialog(dialog.id)}
      >
        <form.AppForm>
          <form className="grid gap-4" onSubmit={handleSubmit}>
            <DialogHeader>
              <DialogTitle>Elérés beállítása</DialogTitle>
              <DialogDescription>
                A kliensek elvárják a biztonságos domain alapú SSL
                tanúsítvánnyal rendelkező elérést.
              </DialogDescription>
            </DialogHeader>
            <NetworkSelector form={form} />
            <UrlConfiguration form={form} />
            <DialogFooter>
              <form.SubscribeButton variant="outline" onClick={handleClose}>
                Mégsem
              </form.SubscribeButton>
              <form.Subscribe
                selector={(state) => ({
                  mode: state.values.mode,
                  isSubmitting: state.isSubmitting,
                })}
              >
                {({ mode, isSubmitting }) => {
                  if (mode === 'none') return null

                  return (
                    <Button type="submit" disabled={isSubmitting}>
                      Alkalmazás
                    </Button>
                  )
                }}
              </form.Subscribe>
            </DialogFooter>
          </form>
        </form.AppForm>
      </DialogScrollContent>
    </Dialog>
  )
}
