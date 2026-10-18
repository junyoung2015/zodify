# Privacy and local validation

What the static documentation frontend does, where hosting policies apply, and how to handle sensitive validation errors.

HTML: https://zodify.dev/privacy/

Released zodify 0.8.1; Python >=3.10; alpha. Release manifest verified 2026-10-18.

## Documentation frontend

This website serves static documentation from GitHub Pages. Its shipped frontend contains no analytics scripts, advertising pixels, contact forms, account sign-in, or code that stores data in cookies or browser storage. Pages and examples are readable without JavaScript. The optional local enhancement copies the displayed command or example to your clipboard when you press its copy button; it does not send clipboard contents to a validation service.

Hosting requests still go to GitHub Pages. GitHub documents that Pages logs and stores visitor IP addresses for security, whether or not visitors are signed in. GitHub's own privacy statement governs its processing of hosting requests and any GitHub pages you choose to visit. This description of the frontend is not a promise that a hosting provider keeps no access logs. PyPI, GitHub Issues, and other linked websites have their own policies and may require accounts.

- [GitHub Pages hosting and IP logging](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
- [GitHub privacy statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement)

## Your Python application controls its data

The examples call the installed zodify Python library in your own process; this website does not provide a hosted validation endpoint or upload form. Your application decides where its input, results, and logs are stored or sent. Review that application and any callbacks before processing sensitive data.

Validation errors may contain original strings from coercion failures or messages from custom callbacks. Avoid posting or logging secrets and personal data in full errors. Use synthetic values when reporting bugs, and use the private reporting route for suspected vulnerabilities.

- [Error handling and privacy](https://zodify.dev/docs/errors/)
- [Contact and security reporting](https://zodify.dev/contact/)

Updated 2026-10-18. [Project source](https://github.com/junyoung2015/zodify).
