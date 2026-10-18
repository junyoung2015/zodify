# Security policy

## Reporting a vulnerability

Report suspected vulnerabilities through the repository's
[private vulnerability report form](https://github.com/junyoung2015/zodify/security/advisories/new).
GitHub sign-in is required. Do not put exploit details or secrets in public issues.

Include the affected zodify and Python versions, the affected API, a minimal
reproduction using synthetic data, and the potential impact. Remove credentials,
personal data and other sensitive input from examples and logs.

Reports are reviewed as maintainer time allows. There are no promised response
deadlines, bounties or guaranteed fixes. Use
[GitHub Issues](https://github.com/junyoung2015/zodify/issues) for ordinary bugs
and usage questions that do not disclose a vulnerability.

## Maintained versions

Security fixes target the latest published release, currently **0.8.1**.
Older release lines are not maintained separately; automatic backports are not
promised. See [PyPI](https://pypi.org/project/zodify/) for released versions and
the [API compatibility contract](API_CONTRACT.md) for the supported behavior
and Python interpreter matrix.
