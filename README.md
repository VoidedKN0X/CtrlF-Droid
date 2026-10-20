# CtrlF-Droid

**The VKNXWorks Ctrl series in one F-Droid repo.**

Add this repo to F-Droid, Droid-ify or Neo Store and get every Ctrl app with automatic updates.

Every Ctrl app is **Google-free** and **telemetry-free**: no Google Play services, no analytics, no crash reporting, no usage stats. They only talk to the servers you add.

👉 **[Add the repo](https://voidedkn0x.github.io/CtrlF-Droid/)** (open on your phone, or scan the QR code there)

## Apps

| App | What it's for |
| --- | --- |
| [ArrCtrl](https://github.com/VoidedKN0X/ArrCtrl) | Radarr, Sonarr, Prowlarr, Bazarr, qBittorrent, autobrr and Cleanuparr in one app |
| [BeamCtrl](https://github.com/VoidedKN0X/BeamCtrl) | TV remote for phones with an IR blaster |
| [CraftyCtrl](https://github.com/VoidedKN0X/CraftyCtrl) | Manage Minecraft servers on Crafty Controller |
| [ElementCtrl](https://github.com/VoidedKN0X/ElementCtrl) | Matrix chat client for matrix.org and self-hosted Synapse |
| [FilesCtrl](https://github.com/VoidedKN0X/FilesCtrl) | File manager with NFS, SMB, SFTP, FTP and WebDAV |
| [FrigateCtrl](https://github.com/VoidedKN0X/FrigateCtrl) | Watch and review your Frigate NVR cameras |
| [ImmichCtrl](https://github.com/VoidedKN0X/ImmichCtrl) | Photos and backup for your Immich server |
| [JellyCtrl](https://github.com/VoidedKN0X/JellyCtrl) | Movies, shows, music and Live TV from Jellyfin |
| [NaviCtrl](https://github.com/VoidedKN0X/NaviCtrl) | Music player for Navidrome servers |
| [PaperCtrl](https://github.com/VoidedKN0X/PaperCtrl) | Scan and browse documents on Paperless-ngx |
| [PrintCtrl](https://github.com/VoidedKN0X/PrintCtrl) | Bambu Lab printers through Bambuddy, and Spoolman spools |
| [ProxCtrl](https://github.com/VoidedKN0X/ProxCtrl) | Manage your Proxmox VE server |
| [SeerrCtrl](https://github.com/VoidedKN0X/SeerrCtrl) | Request movies and shows on Seerr / Jellyseerr |
| [TrueCtrl](https://github.com/VoidedKN0X/TrueCtrl) | Monitor and manage your TrueNAS server |

## How it works

Every 3 hours (and on every push), a GitHub Actions workflow:

1. Downloads the latest release APK of each app listed in [`apps.txt`](apps.txt), and turns its release notes into the app's "What's new".
2. Checks every APK before it goes in: its package must belong to the repo it came from, and its signature must verify with Google's `apksigner` and come from that app's own release key (pinned in `AllowedAPKSigningKeys`). A built-in self-test checks that forged APKs are rejected. If any check fails, nothing is published and the current repo stays live.
3. Runs `fdroid update` from the official [F-Droid tools](https://gitlab.com/fdroid/fdroidserver) to build and sign the repo index.
4. Publishes the repo and the landing page to GitHub Pages.

The APKs are the same signed builds as on each app's Releases page.

## Maintaining

- **Add an app:** add its `owner/repo` to `apps.txt` and a store listing in `metadata/<package name>.yml`, including `SourceCode: https://github.com/<owner>/<repo>` and `AllowedAPKSigningKeys` with the SHA-256 of the app's release certificate (`python scripts/apk_signers.py <app>.apk` prints it).
- **An app's signing key changed:** the update run fails on purpose. Put the new SHA-256 in that app's `AllowedAPKSigningKeys`.
- **Update now:** Actions → *Update F-Droid repo* → *Run workflow*.
- **Signing:** the repo index is signed with the key in the `REPO_KEYSTORE_BASE64` and `REPO_KEYSTORE_PASSWORD` secrets and the `REPO_KEY_ALIAS` variable. Never change this key, or users have to re-add the repo.

## Support

The Ctrl apps are free and open source. If they're useful to you, you can [support development on GitHub Sponsors](https://github.com/sponsors/VoidedKN0X).
