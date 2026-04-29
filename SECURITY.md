# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** open a public issue
2. Email: security@example.com (replace with your actual security email)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 1 week
- **Fix and release**: Within 2 weeks for critical issues

## Security Best Practices

When using this boilerplate in production:

1. **Never commit `.env` files** — use `.env.example` as a template
2. **Rotate credentials regularly** — JWT signing values, provider credentials, database passwords
3. **Use HTTPS in production** — enforce TLS for all endpoints
4. **Enable rate limiting** — configure appropriate limits for your use case
5. **Review CORS settings** — restrict allowed origins to your frontend domain
6. **Keep dependencies updated** — run `pip audit` regularly
7. **Use read-only database users** where possible
8. **Enable database connection encryption** (SSL/TLS)

## Disclosure Policy

We follow responsible disclosure. Security fixes will be released as patch
versions with a security advisory.
