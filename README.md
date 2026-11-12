# CtrlF-Droid

**The VKNXWorks Ctrl series in one F-Droid repo.**

Add this repo to F-Droid, Droid-ify or Neo Store and get every Ctrl app with automatic updates.

Every Ctrl app is **Google-free, de-Googled** and **telemetry-free**: no Google Play services, Firebase or other Google services, no analytics, no crash reporting, no usage stats. They work the same on de-Googled phones (GrapheneOS, CalyxOS, /e/OS, LineageOS without Google apps). The apps for your own servers only talk to the servers you add (LijnCtrl talks to De Lijn's API with your own key), the offline apps (phone, texts, contacts, calendar, clock, recorder, calculator, photo and video editor, camera, gallery, home screen, keep-awake, vehicle log and TV remote) have no internet permission at all, the apps for your own devices (Tapo plugs, Canon cameras, Cardo intercoms, JBL audio) only talk to those devices on your network or over Bluetooth, apart from one anonymous firmware check where noted, MapsCtrl only goes online to download maps, and apps with push notifications use ntfy.

👉 **[Add the repo](https://voidedkn0x.github.io/CtrlF-Droid/)** (open on your phone, or scan the QR code there)

## New to F-Droid?

F-Droid is an app store for free and open-source Android apps. You don't need a Google account.

1. Install [F-Droid](https://f-droid.org), [Droid-ify](https://github.com/Droid-ify/client) or [Neo Store](https://github.com/NeoApplications/Neo-Store) on your phone. Android will ask you to allow installing apps from your browser; that's normal.
2. On your phone, open the [CtrlF-Droid page](https://voidedkn0x.github.io/CtrlF-Droid/) and tap **Add to F-Droid**. Your store app opens and asks to add the repo; confirm.
3. Nothing happened? In your store app, go to **Settings › Repositories**, tap **+**, and paste the repo address shown on that page.
4. The Ctrl apps now show up in your store. Install the ones you want; updates arrive automatically.

## Can I trust it?

- **Open source.** Every app's full code is public on GitHub under the GPL-3.0 licence.
- **Built in the open.** Each app's releases are built from that public code by GitHub Actions, not on a personal computer, and signed with that app's own release key.
- **Checked before publishing.** This repo pins every app to its release signing key. An APK signed by any other key, or an APK that doesn't belong to the repo it came from, is refused and nothing is published (details in [How it works](#how-it-works)).
- **Signed repo.** The repo index is signed with the CtrlF-Droid key. Your store app checks it against the fingerprint in the address on the [CtrlF-Droid page](https://voidedkn0x.github.io/CtrlF-Droid/), so nobody can quietly swap the apps.
- **Honest about how it's made.** The Ctrl series is a one-person project by VoidedKN0X (VKNXWorks). Much of the code is written with the help of AI (Claude, by Anthropic). I decide what each app does, review the changes and use the apps myself. Every app has a changelog, and a **Security** tab where problems can be reported privately.

## Apps

| App | What it's for |
| --- | --- |
| [AdCtrl](https://github.com/VoidedKN0X/AdCtrl) | Control your AdGuard Home DNS server |
| [ArrCtrl](https://github.com/VoidedKN0X/ArrCtrl) | Radarr, Sonarr, Prowlarr, Bazarr, qBittorrent, autobrr and Cleanuparr in one app |
| [BeamCtrl](https://github.com/VoidedKN0X/BeamCtrl) | TV remote for phones with an IR blaster |
| [CallCtrl](https://github.com/VoidedKN0X/CallCtrl) | Offline phone app: dialer, call history and call screen |
| [CameraCtrl](https://github.com/VoidedKN0X/CameraCtrl) | Private camera with RAW (DNG) on every lens |
| [ChatCtrl](https://github.com/VoidedKN0X/ChatCtrl) | Matrix chat client for matrix.org and self-hosted Synapse |
| [ClockCtrl](https://github.com/VoidedKN0X/ClockCtrl) | Offline alarms, world clock, timers and stopwatch |
| [ContactCtrl](https://github.com/VoidedKN0X/ContactCtrl) | Offline contacts app for your phone and sync accounts |
| [CraftyCtrl](https://github.com/VoidedKN0X/CraftyCtrl) | Manage Minecraft servers on Crafty Controller |
| [DateCtrl](https://github.com/VoidedKN0X/DateCtrl) | Offline calendar for your phone and sync accounts |
| [FilesCtrl](https://github.com/VoidedKN0X/FilesCtrl) | File manager with NFS, SMB, SFTP, FTP and WebDAV |
| [FrigateCtrl](https://github.com/VoidedKN0X/FrigateCtrl) | Watch and review your Frigate NVR cameras |
| [GalleryCtrl](https://github.com/VoidedKN0X/GalleryCtrl) | Private, offline gallery with an encrypted vault |
| [ImmichCtrl](https://github.com/VoidedKN0X/ImmichCtrl) | Photos and backup for your Immich server |
| [JellyCtrl](https://github.com/VoidedKN0X/JellyCtrl) | Movies, shows, music and Live TV from Jellyfin |
| [LauncherCtrl](https://github.com/VoidedKN0X/LauncherCtrl) | Minimal, private home screen |
| [LijnCtrl](https://github.com/VoidedKN0X/LijnCtrl) | Live De Lijn bus and tram departures for your stops |
| [LumenCtrl](https://github.com/VoidedKN0X/LumenCtrl) | Private, offline photo and video editor |
| [MailCtrl](https://github.com/VoidedKN0X/MailCtrl) | Email for Gmail, Proton Mail and any IMAP account |
| [MapsCtrl](https://github.com/VoidedKN0X/MapsCtrl) | Private, offline maps and navigation |
| [MemoCtrl](https://github.com/VoidedKN0X/MemoCtrl) | Notes on your Memos server |
| [NaviCtrl](https://github.com/VoidedKN0X/NaviCtrl) | Music player for Navidrome servers |
| [PaperCtrl](https://github.com/VoidedKN0X/PaperCtrl) | Scan and browse documents on Paperless-ngx |
| [PrintCtrl](https://github.com/VoidedKN0X/PrintCtrl) | Bambu Lab printers through Bambuddy, and Spoolman spools |
| [ProxCtrl](https://github.com/VoidedKN0X/ProxCtrl) | Manage your Proxmox VE server |
| [RecorderCtrl](https://github.com/VoidedKN0X/RecorderCtrl) | Offline voice recorder with private storage |
| [RideCtrl](https://github.com/VoidedKN0X/RideCtrl) | Offline maintenance, fuel and mod log for your vehicles |
| [SeerrCtrl](https://github.com/VoidedKN0X/SeerrCtrl) | Request movies and shows on Seerr / Jellyseerr |
| [ShutterCtrl](https://github.com/VoidedKN0X/ShutterCtrl) | Wi-Fi remote and photo transfer for Canon cameras |
| [SoundCtrl](https://github.com/VoidedKN0X/SoundCtrl) | JBL headphones and speakers, without the account |
| [SumCtrl](https://github.com/VoidedKN0X/SumCtrl) | Offline calculator, unit converter and work tools |
| [SynapseCtrl](https://github.com/VoidedKN0X/SynapseCtrl) | Administer your Matrix Synapse server |
| [TalkCtrl](https://github.com/VoidedKN0X/TalkCtrl) | Cardo intercom settings, FM radio and firmware updates |
| [TapoCtrl](https://github.com/VoidedKN0X/TapoCtrl) | Tapo plugs and bulbs on your home network |
| [TextCtrl](https://github.com/VoidedKN0X/TextCtrl) | Texts and picture messages (SMS and MMS), with no internet |
| [TrueCtrl](https://github.com/VoidedKN0X/TrueCtrl) | Monitor and manage your TrueNAS server |
| [WakeCtrl](https://github.com/VoidedKN0X/WakeCtrl) | Keep the screen awake, per app or while charging |
| [WrtCtrl](https://github.com/VoidedKN0X/WrtCtrl) | Manage your OpenWrt router |

## How it works

Every 3 hours (and on every push), a GitHub Actions workflow:

1. Downloads the latest release APK of each app listed in [`apps.txt`](apps.txt), and turns its release notes into the app's "What's new".
2. Checks every APK before it goes in: its package must belong to the repo it came from, and its signature must verify with Google's `apksigner` and come from that app's own release key (pinned in `AllowedAPKSigningKeys`). A built-in self-test checks that forged APKs are rejected. If any check fails, nothing is published and the current repo stays live.
3. Runs `fdroid update` from the official [F-Droid tools](https://gitlab.com/fdroid/fdroidserver) to build and sign the repo index.
4. Publishes the repo and the landing page to GitHub Pages. The landing page lists every app in the signed index, with the number of apps next to the Apps heading.

The APKs are the same signed builds as on each app's Releases page.

## Maintaining

- **Add an app:** add its `owner/repo` to `apps.txt` and a store listing in `metadata/<package name>.yml`, including `SourceCode: https://github.com/<owner>/<repo>` and `AllowedAPKSigningKeys` with the SHA-256 of the app's release certificate (`python scripts/apk_signers.py <app>.apk` prints it).
- **An app's signing key changed:** the update run fails on purpose. Put the new SHA-256 in that app's `AllowedAPKSigningKeys`.
- **Update now:** Actions → *Update F-Droid repo* → *Run workflow*.
- **Signing:** the repo index is signed with the key in the `REPO_KEYSTORE_BASE64` and `REPO_KEYSTORE_PASSWORD` secrets and the `REPO_KEY_ALIAS` variable. Never change this key, or users have to re-add the repo.

## Support

The Ctrl apps are free and open source. If they're useful to you, you can [support development on GitHub Sponsors](https://github.com/sponsors/VoidedKN0X).

A problem with an app? Open an issue in that app's repo. A security problem? Please report it privately; see [SECURITY.md](SECURITY.md).

The Ctrl apps are independent and aren't made by or affiliated with the projects whose servers they connect to.
