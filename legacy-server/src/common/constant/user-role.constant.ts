import { UserRoleEnum } from 'src/users/enum/user-role.enum';

import { UserRoleOption } from '../type/user-role-option.type';

export const USER_ROLE_OPTIONS: UserRoleOption[] = [
  { value: UserRoleEnum.ADMIN, label: 'adminisztrátor' },
  { value: UserRoleEnum.USER, label: 'felhasználó' },
];

export const USER_ROLE_LABEL_MAP = USER_ROLE_OPTIONS.reduce(
  (previousValue, value) => ({
    ...previousValue,
    [value.value]: value.label,
  }),
  {} as Record<UserRoleEnum, string>,
);
