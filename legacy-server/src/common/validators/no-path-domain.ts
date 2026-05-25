import {
  ValidatorConstraint,
  ValidatorConstraintInterface,
} from 'class-validator';

@ValidatorConstraint({ name: 'NoPathDomain', async: false })
export class NoPathDomain implements ValidatorConstraintInterface {
  validate(value: string) {
    try {
      const parseUrl = new URL(value);
      const lastCharacter = value.substring(value.length - 1);
      return parseUrl.pathname === '/' && lastCharacter !== '/';
    } catch {
      return false;
    }
  }
  defaultMessage() {
    return 'Csak HTTPS és kizárólag domain (pl. https://example.com)';
  }
}
