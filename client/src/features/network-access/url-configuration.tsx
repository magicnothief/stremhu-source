import { Field, FieldError, FieldLabel } from '@/shared/components/ui/field'
import { Input } from '@/shared/components/ui/input'
import { Label } from '@/shared/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/shared/components/ui/select'
import { Switch } from '@/shared/components/ui/switch'
import { withForm } from '@/shared/contexts/form-context'
import { NetworkConnectionEnum } from '@/shared/lib/source/source-client'

import { networkAccessDefaultValues } from './network-access.defaults'

export const UrlConfiguration = withForm({
  defaultValues: networkAccessDefaultValues,
  render: ({ form }) => {
    return (
      <form.Subscribe selector={(state) => [state.values.mode]}>
        {([mode]) => {
          return (
            <div className="grid gap-4">
              <form.Field name="host">
                {(field) => (
                  <Field>
                    <FieldLabel>Domain vagy Host</FieldLabel>
                    <Input
                      name={field.name}
                      value={field.state.value}
                      onBlur={field.handleBlur}
                      onChange={(e) => field.handleChange(e.target.value)}
                      placeholder="Pl.: sub.duckdns.org vagy pelda.com"
                    />
                    {field.state.meta.isTouched && (
                      <FieldError errors={field.state.meta.errors} />
                    )}
                  </Field>
                )}
              </form.Field>

              {mode !== 'manual' && (
                <>
                  <form.Field name="token">
                    {(field) => (
                      <Field>
                        <FieldLabel>Token</FieldLabel>
                        <Input
                          name={field.name}
                          value={field.state.value}
                          onBlur={field.handleBlur}
                          onChange={(e) => field.handleChange(e.target.value)}
                          placeholder="A szolgáltatótól kapott API token"
                          type="password"
                        />
                        {field.state.meta.isTouched && (
                          <FieldError errors={field.state.meta.errors} />
                        )}
                      </Field>
                    )}
                  </form.Field>

                  <form.Field name="email">
                    {(field) => (
                      <Field>
                        <FieldLabel>E-mail cím (Let's Encrypt)</FieldLabel>
                        <Input
                          name={field.name}
                          value={field.state.value}
                          onBlur={field.handleBlur}
                          onChange={(e) => field.handleChange(e.target.value)}
                          placeholder="SSL tanúsítvány generálásához"
                          type="email"
                        />
                        {field.state.meta.isTouched && (
                          <FieldError errors={field.state.meta.errors} />
                        )}
                      </Field>
                    )}
                  </form.Field>

                  <form.Field name="connection">
                    {(field) => (
                      <Field>
                        <FieldLabel>Hálózati elérés</FieldLabel>
                        <Select
                          value={field.state.value}
                          onValueChange={(value) =>
                            field.handleChange(value as NetworkConnectionEnum)
                          }
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Válassz típust" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value={NetworkConnectionEnum.local}>
                              Helyi (Local - a router mögött vagyok)
                            </SelectItem>
                            <SelectItem value={NetworkConnectionEnum.public}>
                              Publikus (Public - nyitott portom van)
                            </SelectItem>
                          </SelectContent>
                        </Select>
                        {field.state.meta.isTouched && (
                          <FieldError errors={field.state.meta.errors} />
                        )}
                      </Field>
                    )}
                  </form.Field>
                </>
              )}

              {mode === 'manual' && (
                <form.Field name="reverseProxy">
                  {(field) => (
                    <div className="flex items-center space-x-2">
                      <Switch
                        id={field.name}
                        checked={field.state.value}
                        onCheckedChange={field.handleChange}
                      />
                      <Label htmlFor={field.name}>Reverse Proxy mögött van</Label>
                    </div>
                  )}
                </form.Field>
              )}
            </div>
          )
        }}
      </form.Subscribe>
    )
  },
})
