# Changelog

Changes to the CtrlF-Droid repo itself: how it checks, signs and publishes the Ctrl apps. Each app's own changes are in that app's changelog and show up as "What's new" in your F-Droid client.

## 2026-11-05

### Project

- **The workflows are audited.** A new check runs [zizmor](https://docs.zizmor.sh) on every workflow change, offline, with zizmor pinned by its PyPI hashes. Both workflows already start with no permissions and give each job only what it needs; the permissions now say why each one is there. Nothing changes in the repo or on the website.

### Fixed

- **The repo updates again after the GitHub security settings were tightened.** The repo now only lets GitHub Actions run when every action is pinned to an exact commit. The step that publishes the website used an older Pages action that pulled in another action by version name instead, so every update stopped before it started. It now uses the current Pages actions (upload-pages-artifact 5.0.0 and deploy-pages 5.0.1), which are pinned all the way down. Nothing changes in the repo or on the website.

### New

- **CallCtrl** is in the repo: an offline phone app that replaces your phone's dialer and call screen. Version 0.1.1 has the call screen (answer, decline with a text, mute, speaker and Bluetooth, hold, swap and conference calls), a keypad that searches your contacts as you type, Recents with a Missed filter, contacts with a number, missed call notifications, blocked numbers and two-SIM support. Calls still go through your phone's own telephony. It has no internet permission, and it's pinned to its own release signing key (80980445…c51c13).
- **ClockCtrl** is in the repo: an offline clock app with alarms that ring reliably (through Do Not Disturb, over the lock screen and after a restart), a world clock, several timers at once and a stopwatch with laps. Version 0.1.1 also takes "Set alarm" and "Set timer" from other apps and assistants. It has no internet permission, and it's pinned to its own release signing key (3531cfcd…3ede70).
- **ContactCtrl** is in the repo: an offline contacts app for the contacts on your phone and in your sync accounts (DAVx⁵, Exchange and others). Version 0.1.2 has fast search, adding and editing contacts with only the changed fields written back, favourites, .vcf import and export, and the contact pickers other apps use. It has no internet permission, and it's pinned to its own release signing key (b530d103…29b955).
- **DateCtrl** is in the repo: an offline calendar for the calendars on your phone and in your sync accounts. Version 0.1.1 has a month view, an agenda with search, repeating events, reminders with Snooze, calendars you can show, hide and add, and "Add to calendar" from other apps. It has no internet permission, and it's pinned to its own release signing key (49fe026b…4d5c07).
- **LijnCtrl** is in the repo: live De Lijn bus and tram departures for your stops, with your own free De Lijn API key. Version 0.15.4 has saved stops with live times, a departures widget, stop, trip and line pages, live vehicles on the map, bus alerts, trip guidance, disruptions and nearby stops, and a route planner with every Belgian operator. It only connects to De Lijn's API, OpenStreetMap for map tiles and, only if you turn it on, Transitous for route planning and address search. It's pinned to its own release signing key (fabac3f4…323e30).
- **MailCtrl** is in the repo: a private, Google-free email app for several accounts, talking straight to your own mail servers over IMAP and SMTP. Version 0.1.3 has a combined inbox, all your folders, safe mail reading with remote pictures blocked, writing with attachments, server-side search, swipe actions and new-mail notifications (instant with ntfy if you set it up). It works with Gmail and other providers through an app password, and with Proton Mail through hydroxide or Proton Mail Bridge. It only connects to your own mail servers, and it's pinned to its own release signing key (e80fb689…9f5065).
- **RecorderCtrl** is in the repo: an offline voice recorder that replaces your phone's recorder app. Version 0.1.1 records with a live level meter (also with the screen off), in AAC or Opus, keeps recordings in private storage until you share or save them, recovers cut-off recordings and has a player with speed control. It has no internet permission, and it's pinned to its own release signing key (5c67ddaa…ccb24f).
- **TextCtrl** is in the repo: an SMS and MMS app that becomes your phone's texting app. Version 0.6.4 has group chats, pictures and files, scheduled messages and undo send, reactions, spam and keyword filters, hidden chats, encrypted backup and restore, dual SIM and a recent chats widget. It has no internet permission: texts go out over the mobile network and picture messages through Android's own MMS service. It's pinned to its own release signing key (cf93cf96…f394b3).
- The README's app list includes all eight, so it now lists all 28 apps in the repo.

### Changed

- **Every app now needs Android 15 or newer.** Android 13 no longer gets security updates and Android 14's updates end in early 2027, so the Ctrl apps now support Android 15, 16 and 17 only. Each app's description in your F-Droid client says so. On an older phone the version you have keeps working, but your store won't offer it updates.
- **The landing page shows how many apps are in the repo.** The Apps heading has a badge with the number of apps, counted from the repo's signed index each time the page is rebuilt, so it's always the real number.
- **The repo's description** in your F-Droid client now mentions email, live De Lijn departures and the offline apps that replace your phone's dialer, texts, contacts, calendar, clock, recorder and calculator, not just apps for self-hosted servers.
- **The landing page and README say what each kind of app connects to:** apps for your own servers only talk to the servers you add (LijnCtrl to De Lijn's API), and the offline apps have no internet permission at all. The README also describes the app count on the landing page.

## 2026-11-03

### New

- **SumCtrl** is in the repo: an offline calculator, unit converter and work-tools app that replaces your phone's calculator. Version 0.1.0 has exact decimal maths with a live result, shop-style percentages, scientific keys, history, a unit converter with 13 categories, and VAT, discount, margin, instalment and percentage tools. It has no internet permission, and it's pinned to its own release signing key (a8e6376f…54a809). The README's app list includes it.

### Changed

- **The Matrix chat app is now ChatCtrl.** It's in the repo as a new app, with its own app ID (`com.vknxworks.chatctrl`) and its own release signing key (9ee0fc5f…929aba), pinned like every other app. If you used the chat app before, install **ChatCtrl**, sign in again and verify the new session with your recovery key; the earlier install no longer gets updates from this repo.
- **SynapseCtrl's listing** says to chat with ChatCtrl or another Matrix app, and the README's app list links to ChatCtrl.

## 2026-11-02

### Changed

- **Every app's listing is up to date.** Each description was checked against that app's README and code:
  - Every listing now says it needs Android 13 or newer on a 64-bit ARM phone.
  - **TrueCtrl** now describes the full app, not just monitoring: datasets, snapshots and protection tasks, SMB and NFS shares, apps, the shell, notifications, widgets and the tile, and the app lock. Its summary is now "Monitor and manage your TrueNAS server from your phone".
  - **ArrCtrl** now mentions Lidarr. **ProxCtrl**'s app-lock line now describes its own PIN with optional fingerprint.
  - **BeamCtrl** and **FilesCtrl** no longer mention theme options that were replaced by the Signal look.
  - Missing features were added to most other listings, and server requirements were added where they were missing (AdGuard Home, Memos, Immich, Synapse, OpenWrt with LuCI).
- **Every listing says how the app is made:** a one-person project by VoidedKN0X, much of it written with the help of AI (Claude), and every release built from the public code by GitHub Actions and signed with the same key.

### New

- **"Why you can trust these apps" on the repo page:** open source, built in the open, every APK checked against its app's signing key, the repo's signing fingerprint shown in full, Google-free and telemetry-free, and honest about AI use.
- **Help when the Add button does nothing** on the repo page: where to paste the repo address by hand.
- **README:** "New to F-Droid?" step-by-step instructions and a "Can I trust it?" section.
- **SECURITY.md:** how to report a problem with the repo or an app privately, and how the repo is protected.

## 2026-10-31 (later)

### Changed

- **RideCtrl** listing: describes the complete app from version 0.2.0 (garage, fuel log and premix calculator, maintenance and reminders, parts, mods, specs, temperature log, costs, backup, widget and shortcuts) and its two permissions; no longer marked as early development.

## 2026-10-31

### Changed

- **SynapseCtrl's listing is no longer "in early development"**: it now lists the Overview with health checks, users, invites, rooms, media cleanup, reports, federation, server notices, notifications, the widget and the app shortcuts, which arrived in SynapseCtrl 1.0.0.

### New

- **SynapseCtrl** is in the repo: administer your self-hosted Matrix Synapse server from your phone. Version 0.1.0 signs in with an admin account (password or access token), checks admin access and shows the Synapse version; users, invites, rooms, media, reports and health checks arrive with the next releases. It's in early development, so new parts arrive with each release.
- It's pinned to its own release signing key like every other app, and the repo's README lists it.
- **RideCtrl** is in the repo: an offline maintenance, fuel and mod log for your scooter, motorbike or car. Version 0.1.0 is the app's foundation (look, app lock, privacy switches and units); vehicles, the fuel log and premix calculator, maintenance, parts and mods, temperature log, costs and backup arrive with the next releases. It has no internet permission, and it's pinned to its own release signing key (d545bfb0…4573b8).

## 2026-10-31

### New

- **WrtCtrl** is in the repo: manage your OpenWrt router from your phone (overview with live WAN throughput, every device on your network with static leases, blocking and Wake-on-LAN, Wi-Fi and guest Wi-Fi, DHCP, port forwards, interfaces, services, package updates, logs, backups and reboot), with every risky change applied with OpenWrt's rollback. It's pinned to its own release signing key like every other app, and the repo's README lists it. It appears in the repo as soon as its first signed release is published.

### Fixed

- **The repo updates again.** WrtCtrl's listing had a colon in its one-line summary that the F-Droid tools read as a new field, so the repo update stopped with "could not parse" and no app in the repo was updated until this fix. The summary is now written without it.

## 2026-10-21

### Changed

- **AdCtrl's listing is no longer "in early development"**: it now lists the home screen widget, the app shortcuts (Pause protection, Query log, Search the query log, Blocked queries), notifications from its background checks and the app lock, which arrived in AdCtrl 0.9.0.
- **ChatCtrl's listing mentions calls**: voice and video calls through your own server (MatrixRTC/Element Call), which work with Element X and Element Web.

### New

- **AdCtrl** is in the repo: control your AdGuard Home DNS server from your phone (overview and pause, live query log with one-tap block/unblock, filters and rules, clients, Quick Settings tile). It's in early development, so new parts arrive with each release.
- **MemoCtrl** is in the repo: your self-hosted Memos on your phone, with offline sync, a full editor, widgets and an app lock.
- Both are pinned to their own release signing keys like every other app, and the repo's README lists them.

## 2026-10-20

### Changed

- **Every listing says the app is Google-free and de-Googled**, and works the same on de-Googled phones such as GrapheneOS, CalyxOS, /e/OS and LineageOS without Google apps. The repo's README says the same.
- **ArrCtrl, ProxCtrl and ChatCtrl's listings say push notifications come through ntfy**, with the app's own background checks as a fallback (they no longer mention UnifiedPush or other push apps). PaperCtrl's says Paperless pushes come through ntfy.
- **Every listing says the app is telemetry-free.** The Ctrl apps no longer have optional usage stats, so the line about them is replaced by: no analytics, crash reporting, usage stats or tracking of any kind. BeamCtrl's listing also says it has no internet permission at all. The repo's README says the same.
- **Link preview image** for the repo in `assets/social-preview.png`, with the CtrlF-Droid icon, "Every Ctrl app in one F-Droid repo, with automatic updates" and Google-free, Telemetry-free, GPL-3.0 and F-Droid tags, for when the repo is shared on Reddit, Discord or elsewhere.

## 2026-10-19

### Changed

- **ProxCtrl's listing covers the finished app** (ProxCtrl 1.0.0): the Storage, Tasks and Node tabs, editing guest resources, growing disks, clones and templates, home screen widgets and the Quick Settings tile, and the app lock and typed confirmations, which are in the app now.
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
