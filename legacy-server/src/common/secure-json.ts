import { CompactEncrypt, compactDecrypt, importJWK } from 'jose';
import { TextDecoder, TextEncoder } from 'node:util';

// 32 byte hex kulcs (64 hex karakter)
const KEY_HEX = process.env.COOKIE_ENC_KEY || '';
if (KEY_HEX.length !== 64) {
  throw new Error('COOKIE_ENC_KEY must be 32 bytes hex (64 hex chars).');
}

async function getKey() {
  const jwk = await importJWK({ kty: 'oct', k: '' }, 'A256GCM');
  return jwk;
}

/** JSON -> kompakt JWE string (AES-GCM, A256GCM) */
export async function encryptJson(obj: unknown): Promise<string> {
  const key = await getKey();
  const stringify = JSON.stringify(obj);
  const payload = new TextEncoder().encode(stringify);

  const encrypted = new CompactEncrypt(payload)
    .setProtectedHeader({
      alg: 'dir',
      enc: 'A256GCM',
    })
    .encrypt(key);

  return await encrypted; // pl. "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0...."
}

/** kompakt JWE string -> JSON */
export async function decryptJson<T = any>(token: string): Promise<T> {
  const key = await getKey();
  const { plaintext } = await compactDecrypt(token, key);
  const payload = new TextDecoder().decode(plaintext);

  const json = JSON.parse(payload) as T;

  return json;
}
