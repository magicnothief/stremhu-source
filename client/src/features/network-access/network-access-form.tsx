import { Address4 } from 'ip-address'
import type { ReactEventHandler, SubmitEventHandler } from 'react'
import { useState } from 'react'
import { toast } from 'sonner'
import * as z from 'zod'

import { useConfirmDialog } from '@/features/confirm/use-confirm-dialog'
import { useAppForm } from '@/shared/contexts/form-context'
import { parseApiError } from '@/shared/lib/utils'

import { Separator } from '../../shared/components/ui/separator'
import { networkAccessDefaultValues } from './network-access.defaults'
import type { ConnectionType } from './network-access.types'
import { NetworkSelector } from './network-selector'
import { UrlConfiguration } from './url-configuration'

export { networkAccessDefaultValues } from './network-access.defaults'

export const NETWORK_ACCESS_FORM_ID = 'network-access-form'
export const NETWORK_ACCESS_HEADER = {
  TITLE: 'Elérés beállítása',
  DESCRIPTION:
    'Bizonyos kliensek (Stremio web) csak biztonságos (HTTPS) kapcsolaton keresztül tudnak addont telepíteni. Itt adhatod meg, milyen címen érje el a StremHU Source-ot.',
}

const schema = z
  .object({
    enebledlocalIp: z.boolean(),
    address: z.string().trim(),
  })
  .superRefine(({ address, enebledlocalIp }, ctx) => {
    if (enebledlocalIp) {
      try {
        new Address4(address)
        if (
          address.includes('/') ||
          address.includes(':') ||
          address === '127.0.0.1'
        ) {
          throw new Error()
        }
      } catch (error) {
        ctx.addIssue({
          code: 'custom',
          path: ['address'],
          message:
            'Csak IPv4 cím adható meg (protokoll/subnet/port nélkül) a 127.0.0.1 nem használható',
        })
      }

      return
    }

    const httpsUrl = z.url({
      protocol: /^https$/,
      error: 'Csak HTTPS engedélyezett',
    })

    const parsedUrl = httpsUrl.safeParse(address)

    if (!parsedUrl.success) {
      ctx.addIssue({
        code: 'custom',
        path: ['address'],
        message: 'Érvénytelen HTTPS URL',
      })
      return
    }

    const parseUrl = new URL(parsedUrl.data)
    const lastCharacter = address.substring(address.length - 1)
    const noPath = parseUrl.pathname === '/' && lastCharacter !== '/'

    if (!noPath || parseUrl.search || parseUrl.hash) {
      ctx.addIssue({
        code: 'custom',
        path: ['address'],
        message: 'Nem tartalmazhat elérési utat, query-t vagy fragmentet',
      })
    }
  })

export type NetworkAccessProps = {
  onSuccess?: () => void
  onSkip?: () => void
  onValidated?: (isValid: boolean) => void
}

export function NetworkAccess(props: NetworkAccessProps) {
  const { onSuccess, onSkip, onValidated } = props

  const [connection, setConnection] = useState<ConnectionType>('idle')

  const { confirm } = useConfirmDialog()

  const form = useAppForm({
    defaultValues: networkAccessDefaultValues,
    validators: {
      onChange: schema,
    },
    listeners: {
      onBlur: async ({ formApi }) => {
        const { isValid, values } = formApi.state

        if (!isValid) {
          if (onValidated) onValidated(false)
          return
        }

        const { enebledlocalIp, address } = values

        let appUrl = address

        if (enebledlocalIp) {
          appUrl = ''
        }

        try {
          if (onValidated) onValidated(false)
          setConnection('pending')
          setConnection('success')
          if (onValidated) onValidated(true)
        } catch (error) {
          setConnection('error')
          if (onValidated) onValidated(false)
        }
      },
      onChange: async ({ formApi }) => {
        const { isValid, values } = formApi.state

        if (!isValid) {
          if (onValidated) onValidated(false)
          return
        }

        const { enebledlocalIp, address } = values

        let appUrl = address

        if (enebledlocalIp) {
          appUrl = ''
        }

        try {
          if (onValidated) onValidated(false)
          setConnection('pending')

          setConnection('success')
          if (onValidated) onValidated(true)
        } catch (error) {
          setConnection('error')
          if (onValidated) onValidated(false)
        }
      },
      onChangeDebounceMs: 500,
    },
    onSubmit: async ({ value, formApi }) => {
      try {
        let appUrl = '0.0.0.0'

        if (value.enebledlocalIp) {
          appUrl = ''
        }

        if (onSuccess) onSuccess()
      } catch (error) {
        formApi.reset()
        const message = parseApiError(error)
        toast.error(message)
      }
    },
  })

  const handleSubmit: SubmitEventHandler<HTMLFormElement> = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    await form.handleSubmit()
  }

  const handleSkip: ReactEventHandler<HTMLFormElement> = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    await confirm({
      title: 'Biztos kihagyod a beállítást?',
      description:
        'A lépés kihagyása után a "Beállítások" menüpont alatt tudod elvégezni a beállítást, addig az addon nem fog működni!',
      onConfirm: async () => {
        try {
          if (onSkip) onSkip()
        } catch (error) {
          const message = parseApiError(error)
          toast.error(message)
          throw error
        }
      },
    })
  }

  return (
    <form.AppForm>
      <form
        id={NETWORK_ACCESS_FORM_ID}
        className="grid gap-4"
        onSubmit={handleSubmit}
        onReset={handleSkip}
      >
        <NetworkSelector form={form} />
        <Separator />
        <UrlConfiguration form={form} connection={connection} />
      </form>
    </form.AppForm>
  )
}
