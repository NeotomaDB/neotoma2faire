# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in neotoma2faire, please report it privately. **Do not open a public GitHub issue.**

**Email:** [dominguezvid@wisc.edu]

Please include:

- A description of the vulnerability
- Steps to reproduce the issue
- Any relevant logs or screenshots

## Response Timeline

We aim to acknowledge all vulnerability reports within **14 days** and will provide an update on next steps within **30 days**.

## Scope

neotoma2faire is a data transformation tool that connects to PostgreSQL databases. Security concerns most relevant to this project include:

- SQL injection via user-supplied CSV or YAML input
- Credential exposure in `.env` files or logs
- Dependency vulnerabilities in Python packages

## Disclosure Policy

We follow coordinated disclosure. Once a fix is available, we will publish details in the [CHANGELOG](CHANGELOG.md) and, if applicable, issue a GitHub Security Advisory.
