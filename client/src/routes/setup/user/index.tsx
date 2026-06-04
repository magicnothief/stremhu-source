import { createFileRoute, redirect, useNavigate } from '@tanstack/react-router'
import type { SubmitEventHandler } from 'react'
import { toast } from 'sonner'
import * as z from 'zod'

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/shared/components/ui/card'
import { useAppForm } from '@/shared/contexts/form-context'
import { parseApiError } from '@/shared/lib/utils'
import { useRegistration } from '@/shared/queries/auth'
import { getSystemStatus } from '@/shared/queries/system'

export const Route = createFileRoute('/setup/user/')({
  beforeLoad: async ({ context }) => {
    const queryClient = context.queryClient
    const { configured } = await queryClient.ensureQueryData(getSystemStatus)

    if (configured) {
      throw redirect({ to: '/' })
    }
  },
  component: SetupUserRoute,
})

const schema = z.object({
  username: z.string().trim().nonempty('A felhasználónév kitöltése kötelező'),
  password: z.string().trim().nonempty('A jelszó kitöltése kötelező'),
})

function SetupUserRoute() {
  const navigate = useNavigate({ from: '/setup/user/' })

  const { mutateAsync: registration } = useRegistration()

  const form = useAppForm({
    defaultValues: { username: '', password: '' },
    validators: {
      onChange: schema,
    },
    onSubmit: async ({ value }) => {
      try {
        await registration(value)

        navigate({
          to: '/dashboard',
        })
      } catch (error) {
        const message = parseApiError(error)
        toast.error(message)
      }
    },
  })

  const onSubmit: SubmitEventHandler<HTMLFormElement> = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    await form.handleSubmit()
  }

  return (
    <form.AppForm>
      <form
        name="registration"
        className="py-10 flex flex-col items-center"
        onSubmit={onSubmit}
      >
        <Card className="w-sm">
          <CardHeader>
            <CardTitle>Adminisztrátor fiók létrehozása</CardTitle>
            <CardDescription>
              Kezdjük a beállítást! Hozd létre az első fiókot, ami{' '}
              <span className="font-bold">Adminisztrátor</span> jogosultsággal
              fog rendelkezni.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4">
            <form.AppField
              name="username"
              children={(field) => (
                <field.AppTextField label="Felhasználónév" />
              )}
            />
            <form.AppField
              name="password"
              children={(field) => (
                <field.AppTextField label="Jelszó" type="password" />
              )}
            />
          </CardContent>
          <CardFooter className="grid gap-4">
            <form.SubscribeButton type="submit">
              Létrehozás
            </form.SubscribeButton>
          </CardFooter>
        </Card>
      </form>
    </form.AppForm>
  )
}
