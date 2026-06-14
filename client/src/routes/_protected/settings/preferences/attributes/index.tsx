import { useSuspenseQueries } from '@tanstack/react-query'
import { createFileRoute } from '@tanstack/react-router'
import { BanIcon, CircleIcon } from 'lucide-react'
import type { MouseEventHandler } from 'react'

import { Alert, AlertTitle } from '@/shared/components/ui/alert'
import { Button } from '@/shared/components/ui/button'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/shared/components/ui/card'
import { ItemDescription, ItemTitle } from '@/shared/components/ui/item'
import { Separator } from '@/shared/components/ui/separator'
import {
  getMeAttributeExclusions,
  getMeAttributes,
  useAddAttributeToExclusion,
  useRemoveAttributeFromExclusion,
} from '@/shared/queries/me'

import { PreferenceItem } from '../-components/preference-item'

export const Route = createFileRoute(
  '/_protected/settings/preferences/attributes/',
)({
  component: RouteComponent,
})

function RouteComponent() {
  const [{ data: attributes }, { data: exclusions }] = useSuspenseQueries({
    queries: [getMeAttributes(), getMeAttributeExclusions()],
  })

  const { mutate: addAttributeToExclusion } = useAddAttributeToExclusion()
  const { mutate: removeAttributeFromExclusion } =
    useRemoveAttributeFromExclusion()

  const handleAddToExclusion =
    (attributeId: string): MouseEventHandler<HTMLButtonElement> =>
    (event) => {
      event.preventDefault()
      event.stopPropagation()

      addAttributeToExclusion({ attributeId })
    }

  const handleRemoveFromExclusion =
    (attributeId: string): MouseEventHandler<HTMLButtonElement> =>
    (event) => {
      event.preventDefault()
      event.stopPropagation()

      removeAttributeFromExclusion(attributeId)
    }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Kizárt tulajdonságok konfigurációja</CardTitle>
      </CardHeader>
      <Separator />
      <CardContent className="grid gap-8">
        <div className="grid gap-4">
          <div className="grid">
            <ItemTitle>Kizárt tulajdonságok</ItemTitle>
            <ItemDescription>
              Az ezekben a tulajdonságokban rejlő értékeket nem fogod látni az
              oldalon. Ez akkor hasznos, ha például nem érdekel a ruha márkája.
            </ItemDescription>
          </div>
          {exclusions.map((exclusion) => (
            <PreferenceItem
              key={exclusion.id}
              attribute={exclusion}
              actions={[
                <Button
                  key="delete"
                  size="icon-sm"
                  className="rounded-full"
                  onPointerDown={(event) => event.stopPropagation()}
                  onClick={handleRemoveFromExclusion(exclusion.id)}
                >
                  <CircleIcon />
                </Button>,
              ]}
            />
          ))}
          {exclusions.length === 0 && (
            <Alert>
              <BanIcon />
              <AlertTitle>Nincs kizárt tulajdonság.</AlertTitle>
            </Alert>
          )}
        </div>
        <Separator />
        <div className="grid gap-4">
          <div className="grid">
            <ItemTitle>Kizárható tulajdonságok</ItemTitle>
            <ItemDescription>
              Az ezekben a tulajdonságokban rejlő értékeket nem fogod látni az
              oldalon. Ez akkor hasznos, ha például nem érdekel a ruha márkája.
            </ItemDescription>
          </div>
          {attributes.map((attribute) => (
            <PreferenceItem
              key={attribute.id}
              attribute={attribute}
              actions={[
                <Button
                  key="add"
                  size="icon-sm"
                  variant="destructive"
                  className="rounded-full"
                  onPointerDown={(event) => event.stopPropagation()}
                  onClick={handleAddToExclusion(attribute.id)}
                >
                  <BanIcon />
                </Button>,
              ]}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
