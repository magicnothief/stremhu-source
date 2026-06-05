import { useSuspenseQuery } from '@tanstack/react-query'
import type { ReactEventHandler, SubmitEventHandler } from 'react'
import { toast } from 'sonner'
import * as z from 'zod'

import { useConfirmDialog } from '@/features/confirm/use-confirm-dialog'
import { useAppForm } from '@/shared/contexts/form-context'
import type {
  NetworkAutoSetupRequest,
  NetworkManualSetupRequest,
} from '@/shared/lib/source/source-client'
import { NetworkConnectionEnum } from '@/shared/lib/source/source-client'
import { parseApiError } from '@/shared/lib/utils'
import { getNetworkSettings, useNetworkConfig } from '@/shared/queries/network'

import { Separator } from '../../shared/components/ui/separator'
import { networkAccessDefaultValues } from './network-access.defaults'
import type { NetworkAccessFormValues } from './network-access.types'
import { NetworkSelector } from './network-selector'
import { UrlConfiguration } from './url-configuration'

export { networkAccessDefaultValues } from './network-access.defaults'

export const NETWORK_ACCESS_FORM_ID = 'network-access-form'
export const NETWORK_ACCESS_HEADER = {
  TITLE: 'Elérés beállítása',
  DESCRIPTION:
    'Bizonyos kliensek (Stremio web) csak biztonságos (HTTPS) kapcsolaton keresztül tudnak addont telepíteni. Itt adhatod meg, milyen címen érje el a StremHU Source-ot.',
}

const schema = z.discriminatedUnion('mode', [
  z.object({
    mode: z.enum(['duckdns', 'myaddr']),
    host: z.string().min(1, 'A host megadása kötelező'),
    token: z.string().min(1, 'A token megadása kötelező'),
    email: z.string().email('Érvénytelen e-mail cím'),
    connection: z.nativeEnum(NetworkConnectionEnum),
  }),
  z.object({
    mode: z.literal('manual'),
    host: z.string().min(1, 'A host megadása kötelező'),
    reverseProxy: z.boolean(),
  }),
])

export type NetworkAccessProps = {
  onSuccess?: () => void
  onSkip?: () => void
  onValidated?: (isValid: boolean) => void
}

export function NetworkAccess(props: NetworkAccessProps) {
  const { onSuccess, onSkip, onValidated } = props

  const { confirm } = useConfirmDialog()
  const { data: networkSettings } = useSuspenseQuery(getNetworkSettings)
  const { mutateAsync: configNetwork } = useNetworkConfig()

  let defaultValues: NetworkAccessFormValues = { ...networkAccessDefaultValues }

  if (networkSettings.mode === 'auto') {
    defaultValues = {
      mode: networkSettings.provider as 'duckdns' | 'myaddr',
      host: networkSettings.host,
      token: networkSettings.token,
      email: networkSettings.email,
      connection: networkSettings.connection,
    }
  } else if (networkSettings.mode === 'manual') {
    defaultValues = {
      mode: 'manual',
      host: networkSettings.host,
      reverseProxy: networkSettings.reverseProxy,
    }
  }

  const form = useAppForm({
    defaultValues,
    validators: {
      onChange: schema,
    },
    listeners: {
      onBlur: async ({ formApi }) => {
        if (onValidated) onValidated(formApi.state.isValid)
      },
      onChange: async ({ formApi }) => {
        if (onValidated) onValidated(formApi.state.isValid)
      },
      onChangeDebounceMs: 500,
    },
    onSubmit: async ({ value }) => {
      try {
        let payload: NetworkAutoSetupRequest | NetworkManualSetupRequest

        if (value.mode === 'manual') {
          payload = {
            mode: 'manual',
            host: value.host,
            reverseProxy: value.reverseProxy,
          }
        } else {
          payload = {
            mode: 'auto',
            provider: value.mode,
            host: value.host,
            token: value.token,
            email: value.email,
            connection: value.connection,
          }
        }

        await configNetwork(payload)

        const appUrl = `https://${value.host}`

        toast.success(
          <div className="flex flex-col gap-1">
            <p>Hálózati beállítások sikeresen elmentve! A szerver újraindul.</p>
            <p>
              Az új elérhetőség:{' '}
              <a
                href={appUrl}
                target="_blank"
                rel="noreferrer"
                className="underline font-bold"
              >
                {appUrl}
              </a>
            </p>
          </div>,
          {
            duration: Infinity,
          },
        )

        if (onSuccess) onSuccess()
      } catch (error) {
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
        <UrlConfiguration form={form} />
      </form>
    </form.AppForm>
  )
}
