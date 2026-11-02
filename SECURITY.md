# Security policy

Thank you for helping keep CtrlF-Droid and the Ctrl apps safe.

## Reporting a problem

**Please don't report security problems in a public issue.** Report them privately instead:

- **A problem with this repo** (the update workflow, the APK checks, the repo signing, the landing page): go to the [Security tab](https://github.com/VoidedKN0X/CtrlF-Droid/security) of this repo and click **Report a vulnerability**.
- **A problem in one of the apps:** use the **Security** tab of that app's repo instead. Each app's README links to it.

Describe what you found and how to reproduce it. Only the maintainer can see the report. I'll reply as soon as I can, work on a fix, and credit you in the changelog if you'd like.

## What counts

- A way to get an APK into this repo that wasn't signed with that app's own release key, or that comes from a different repo
- A way to publish a repo index that isn't signed with the CtrlF-Droid key
- The repo signing key or any app's signing key leaking through the workflow or its logs
- Anything on the landing page that could send people to the wrong repo or the wrong app

## How the repo is protected

- Every app is pinned to the SHA-256 fingerprint of its release signing certificate in `metadata/<package>.yml` (`AllowedAPKSigningKeys`). Before anything is signed, every APK is checked with Google's `apksigner`, and a self-test makes sure forged APKs are rejected. If any check fails, nothing is published and the current repo stays live.
- The repo index is signed by the official F-Droid tools with the CtrlF-Droid key, which only exists in GitHub Actions secrets and is deleted from the runner straight after signing.
- Workflows use pinned actions and the least permissions they need.
