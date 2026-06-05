import { Label } from '@/shared/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/shared/components/ui/radio-group'
import { withForm } from '@/shared/contexts/form-context'

import { networkAccessDefaultValues } from './network-access.defaults'

const accessOptions = [
  {
    label: 'DuckDNS',
    description: (
      <>
        Ingyenes DDNS szolgáltatás. Regisztrálj a{' '}
        <a
          className="link-primary"
          href="https://www.duckdns.org"
          target="_blank"
          rel="noreferrer"
        >
          duckdns.org
        </a>{' '}
        oldalon, majd add meg a választott domaint és a tokenedet.
      </>
    ),
    value: 'duckdns',
  },
  {
    label: 'MyAddr',
    description: (
      <>
        Ingyenes DDNS szolgáltatás. Regisztrálj a{' '}
        <a
          className="link-primary"
          href="https://myaddr.tools"
          target="_blank"
          rel="noreferrer"
        >
          myaddr.tools
        </a>{' '}
        oldalon, majd add meg a domaint és a tokenedet.
      </>
    ),
    value: 'myaddr',
  },
  {
    label: 'Kézi beállítás (Manual)',
    description: (
      <>
        Saját domain, egyedi proxy beállítása. Csak haladóknak!
      </>
    ),
    value: 'manual',
  },
]

export const NetworkSelector = withForm({
  defaultValues: networkAccessDefaultValues,
  render: ({ form }) => {
    return (
      <form.Field name="mode">
        {(field) => (
          <RadioGroup
            value={field.state.value}
            onValueChange={(val) => field.handleChange(val as any)}
          >
            {accessOptions.map((accessOption) => (
              <div key={accessOption.value} className="flex items-start gap-3">
                <RadioGroupItem
                  value={accessOption.value}
                  id={accessOption.value}
                />
                <div className="grid gap-2 mt-[-2px]">
                  <Label htmlFor={accessOption.value}>
                    {accessOption.label}
                  </Label>
                  <p className="text-muted-foreground text-sm">
                    {accessOption.description}
                  </p>
                </div>
              </div>
            ))}
          </RadioGroup>
        )}
      </form.Field>
    )
  },
})
