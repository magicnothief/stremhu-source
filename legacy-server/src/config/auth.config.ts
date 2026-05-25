import { registerAs } from '@nestjs/config';
import { z } from 'zod';

import { AuthConfig } from './interfaces/auth-config.interface';
import ZodUtil, { ZodConfig } from './utils/zod-util';

export default registerAs('auth', () => {
  const sessionSecret = process.env.SESSION_SECRET ?? 'stremhu-source';

  const configs: ZodConfig<AuthConfig> = {
    'session-secret': {
      value: sessionSecret,
      zod: z.string().trim().nonempty(),
    },
  };

  return ZodUtil.validate<AuthConfig>(configs);
});
