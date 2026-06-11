import { useStore } from '@tanstack/react-form'
import { useSuspenseQuery } from '@tanstack/react-query'

import { Button } from '@/shared/components/ui/button'
import {
  Item,
  ItemContent,
  ItemDescription,
  ItemTitle,
} from '@/shared/components/ui/item'
import { withForm } from '@/shared/contexts/form-context'
import { cn } from '@/shared/lib/utils'
import { getNetworkProviders } from '@/shared/queries/network'

import { networkAccessDefaultValues } from './network-access.defaults'

export const NetworkSelector = withForm({
  defaultValues: networkAccessDefaultValues,
  render: ({ form }) => {
    const { data: providers } = useSuspenseQuery(getNetworkProviders)

    const formValues = useStore(form.store, (state) => state.values)

    const isNone = formValues.mode === 'none'
    const isAuto = formValues.mode === 'auto'
    const isManual = formValues.mode === 'manual'

    const handleProviderSelect = (providerId: string) => {
      form.baseStore.setState((state) => ({
        ...state,
        values: {
          mode: 'auto',
          provider: providerId,
          email: '',
          host: '',
          token: '',
          connection: 'local',
        },
      }))
    }

    const handleManualSelect = () => {
      form.baseStore.setState((state) => ({
        ...state,
        values: {
          mode: 'manual',
          host: '',
          reverseProxy: true,
        },
      }))
    }

    const handleReset = () => {
      form.baseStore.setState((state) => ({
        ...state,
        values: {
          mode: 'none',
        },
      }))
    }

    return (
      <div className="grid gap-4">
        {providers.map((provider) => {
          const isSelected =
            formValues.mode === 'auto' && formValues.provider === provider.id

          if (!isNone && !isSelected) return null

          return (
            <Item
              variant="outline"
              key={provider.id}
              className={cn(
                'transition-all duration-200 cursor-pointer hover:bg-primary/5',
                isSelected && 'bg-primary/10',
              )}
              onClick={() => handleProviderSelect(provider.id)}
            >
              <ItemContent>
                <ItemTitle
                  className={cn(isSelected && 'text-primary font-semibold')}
                >
                  {provider.name}
                </ItemTitle>
                <ItemDescription className="line-clamp-none text-wrap">
                  {provider.name}
                </ItemDescription>
              </ItemContent>
            </Item>
          )
        })}
        {isNone && (
          <Item
            variant="outline"
            className={cn(
              'transition-all duration-200',
              isManual && 'border-primary bg-primary/5 dark:bg-primary/10',
            )}
            onClick={handleManualSelect}
          >
            <ItemContent>
              <ItemTitle>Kézi beállítás / Reverse proxy</ItemTitle>
              <ItemDescription className="line-clamp-none text-wrap">
                Saját domain használata, reverse proxy segítségével vagy SSL
                tanúsítvány használatával. <b>Haladóknak ajánlott!</b>
              </ItemDescription>
            </ItemContent>
          </Item>
        )}
        {!isNone && (
          <div className="flex justify-end">
            <Button
              type="button"
              variant="link"
              size="sm"
              className="p-0 text-xs underline-offset-4 h-auto hover:underline"
              onClick={handleReset}
            >
              Konfiguráció újrakezdése
            </Button>
          </div>
        )}
      </div>
    )
  },
})
