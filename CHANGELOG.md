# Changelog

Changes to the CtrlF-Droid repo itself: how it checks, signs and publishes the Ctrl apps. Each app's own changes are in that app's changelog and show up as "What's new" in your F-Droid client.

## 2026-10-19

### Changed

- **ImmichCtrl no longer has a "Non-free dependency" mark.** ImmichCtrl 0.3.0 removed Google Cast, so the app no longer contains any Google Play services code. Its listing no longer mentions casting, and says you choose its home or public address yourself.
- **NaviCtrl's listing mentions its new Playlists tab** (NaviCtrl 0.2.0). Internet radio was removed from the app and was never in the listing.
- **PrintCtrl's listing says you pick which of a server's two addresses is used** (PrintCtrl 0.5.0 no longer switches by itself).
- **Every listing says the app is Google-free**: no Google Play services and no Google libraries that contact Google. The apps no longer ask Google Play services for an emoji font either.

### Changed

- **Store listings match the apps as they are today.** Every app's summary and feature list was rewritten from its up-to-date README, so the repo only lists features that are in the current version. Features still being built (for example ProxCtrl's Storage, Tasks and Node tabs, or TrueCtrl's datasets and sharing) are no longer listed, and newer ones are (PaperCtrl's scanner and documents, ProxCtrl's snapshots and backups, TrueCtrl's pools, scrubs and disks, and more).
- **BeamCtrl's summary says it "works offline"** instead of "fully offline", since its optional usage stats can go online if you opt in.
- **ImmichCtrl is marked "Non-free dependency".** Casting to a TV uses Google Play services (Google Cast). It only starts when you tap the Cast button, but F-Droid clients now show this before you install.

### Changed

- **Every app's description now says it has optional usage stats.** All 14 Ctrl apps can send anonymous usage stats, but only if you opt in. Each store listing now says so up front, so you know before installing (this matters most for BeamCtrl, which otherwise never uses the internet).
- **Descriptions only promise security features the apps have.** PaperCtrl's listing no longer mentions an app lock, and ProxCtrl's and TrueCtrl's no longer mention typed confirmations or a fingerprint lock, because those aren't in the apps yet. ProxCtrl and TrueCtrl now describe their read-only mode, which blocks every change, and their screenshot protection.

### New

- **ArrCtrl, PaperCtrl, ProxCtrl and TrueCtrl join the repo**, so all 14 Ctrl apps are now in one place:
  - **ArrCtrl**: Radarr, Sonarr, Prowlarr, Bazarr, qBittorrent, autobrr and Cleanuparr in one app
  - **PaperCtrl**: scan paper into Paperless-ngx and browse your documents
  - **ProxCtrl**: manage your Proxmox VE server
  - **TrueCtrl**: monitor and manage your TrueNAS server
- Each new app's release signing certificate is pinned in its listing like every other app's, so only APKs signed with that app's own release key are accepted. All four certificates were checked: they're VKNXWorks release keys, not debug keys.
- The repo description now mentions Paperless-ngx, Proxmox VE, TrueNAS and the *arr apps, and the README's app table lists all 14 apps.

### New

- **PrintCtrl** joins the repo: Bambu Lab printers through Bambuddy, and Spoolman spools. Its release signing certificate is pinned in its listing like every other app's, so only APKs signed with PrintCtrl's own release key are accepted.
- The repo description now mentions Bambuddy and Spoolman.

## 2026-10-18

### Security

- **Every APK's signature is now cryptographically verified before it can enter the repo.** Until now the repo's own check only read which certificate an APK claimed to be signed with and left the actual signature check to `fdroid update`. If the Android SDK's `apksigner` was ever missing on the build machine, `fdroid update` would quietly fall back to `jarsigner`, which only checks old-style v1 signatures, so an APK carrying a copy of an app's certificate next to a forged signature could have slipped through. Now each APK goes through Google's `apksigner verify` (every v1/v2/v3/v3.1 signature and v3 key-rotation history), it must have a valid v2 or v3 signature, and every signer `apksigner` verified must be the app's pinned release key. Any failure stops the run before the repo is signed, and the current repo stays live.
- **The run stops if `apksigner` can't be found**, instead of letting `fdroid update` fall back to `jarsigner`. It uses `apksigner` from build-tools 34 or newer (33.x is skipped because it passes some invalid v3 signatures), and `fdroid update` uses the same one.
- **Ambiguous or malformed APKs are refused.** The independent certificate reader now rejects APKs whose signing block contains the same signature block twice (different tools would read different copies), finds the ZIP end record the same way Android does so a fake one hidden in the ZIP comment can't redirect it, refuses ZIP64 and multi-disk archives, and checks that the central directory ends exactly where the ZIP end record starts.
- **Both checks must agree.** An APK is only added if every certificate found by the independent reader *and* every signer verified by `apksigner` is in the app's `AllowedAPKSigningKeys`.
- **Built-in self-test on every run.** Before the signing key is touched, the workflow feeds forged copies of a real release APK (one changed byte, signing block removed, duplicated signing block entry, fake ZIP end record) through the same checks, and stops unless every forgery is rejected.
- **An empty repo is never published.** If no APK could be downloaded (for example during a GitHub outage), the run now fails and the current repo stays live, instead of publishing an index with no apps in it.

## 2026-10-17

### Security

- Each app's release signing certificate is pinned in its listing (`AllowedAPKSigningKeys`). Every downloaded APK must have a v2/v3 signature from that certificate, and its package must have a listing whose source code link is the GitHub repo it was downloaded from, so one app's release can't publish an APK for another app. Any failed check stops the run before anything is signed or published.
- APKs are saved as `<package>_<versionCode>.apk` instead of the name of the release file.
- Release notes shown as "What's new" are cleaned: HTML, links, control characters and invisible text-direction characters are removed and the length is capped.
- The repo signing key's password and alias are read from GitHub secrets/variables through the environment and are never written to disk or put on a command line. The keystore file is written with private permissions and always deleted at the end of the run.
- Workflows pin every GitHub Action to an exact commit, get no permissions by default (only the deploy job can publish to GitHub Pages), don't keep the GitHub token in the checkout, pin the F-Droid tools (fdroidserver 2.4.5) and validate every line of `apps.txt`.
- App icons are rendered with escaped attributes and plain hex colours only, and the landing page only links to `https://` source code pages.
