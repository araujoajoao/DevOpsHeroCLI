# <img src="assets/logo.png" width="44" height="44" alt="DevOpsHero logo" /> DevOpsHeroCLI

<div align="center">

<img src="assets/logo.png" width="220" height="220" alt="DevOpsHero logo" />

[![GitHub release](https://img.shields.io/github/v/release/araujoajoao/DevOpsHeroCLI?color=blue)](https://github.com/araujoajoao/DevOpsHeroCLI/releases)
[![CI](https://github.com/araujoajoao/DevOpsHeroCLI/actions/workflows/ci.yml/badge.svg)](https://github.com/araujoajoao/DevOpsHeroCLI/actions/workflows/ci.yml)
[![Release](https://github.com/araujoajoao/DevOpsHeroCLI/actions/workflows/release.yml/badge.svg)](https://github.com/araujoajoao/DevOpsHeroCLI/actions/workflows/release.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![80 Missions](https://img.shields.io/badge/Missions-80-orange.svg)](#en-tracks)

**Learn Linux, SysAdmin, Git, Docker, Kubernetes, AWS, Terraform and Datadog by typing real commands in a gamified interactive terminal.**<br/>
**Aprenda Linux, SysAdmin, Git, Docker, Kubernetes, AWS, Terraform e Datadog digitando comandos reais em um terminal interativo com gamificação.**

### [🇺🇸 English](#english) · [🇧🇷 Português](#portugues)

<br/>

<img src="assets/terminal_preview.png" width="100%" alt="DevOpsHeroCLI Terminal Lab Preview" />

</div>

---

<a id="english"></a>

# 🇺🇸 English

*No cloud account, no bills, and no risk of breaking your own machine.*

[Quick start](#en-run) •
[macOS app](#en-macos) •
[Updates & versions](#en-releases) •
[Mobile apps](#en-mobile) •
[Tracks & missions](#en-tracks) •
[Gamification](#en-gamification) •
[Shortcuts](#en-shortcuts) •
[Docker](#en-docker) •
[Tests](#en-tests)

<a id="en-what"></a>
## 💡 What is DevOpsHeroCLI?

Unlike multiple-choice quizzes or static tutorials, **DevOpsHeroCLI** simulates a complete operating environment in memory:

- **Virtual File System (VFS)**: if you create `/app/logs/access.log`, it really exists for other commands (`ls`, `grep`, `tar`, `rm`).
- **Daemons & services (`systemctl`)**: manage service state (`status`, `restart`, `enable`).
- **Container engine (`docker`)**: simulates the lifecycle of containers, images, dedicated networks and volumes.
- **Cluster orchestrator (`kubectl`)**: manage Pods, Deployments, replicas, Services and ConfigMaps.
- **Realistic observability (`datadog-agent`)**: disk/docker checks, component status and unified service tags (`DD_ENV`, `DD_SERVICE`, `DD_VERSION`).

---

<a id="en-run"></a>
## 🚀 Run it locally in 1 minute

### ⚡ Recommended: run directly (no clone)

If you just want to play and learn without downloading the whole repository:

```bash
# With pipx (creates an isolated environment and runs instantly):
pipx run --spec git+https://github.com/araujoajoao/DevOpsHeroCLI.git dh

# Or install with pip:
pip install git+https://github.com/araujoajoao/DevOpsHeroCLI.git
dh              # Full visual interface
dh r            # Quick REPL mode
```

### 📂 From the Git repository (step by step per OS)

If you prefer to clone the source code to run locally or contribute:

```bash
# Shallow clone (current state only, without the full history)
git clone --depth=1 https://github.com/araujoajoao/DevOpsHeroCLI.git
cd DevOpsHeroCLI
```

Then follow the steps for your operating system.

#### <img src="assets/icons/linux.svg" width="20" height="20" alt="Linux" /> 1. Linux (Ubuntu, Debian, Fedora, Arch) or WSL

##### Option 1.1: run in the terminal (recommended)
Open your terminal (**Bash** or **Zsh**) and run the official launcher:

```bash
./dh            # Full TUI
./dh r          # Quick REPL prompt (no split panes)
./dh s          # Profile stats and earned XP
./dh l          # Catalog of all 80 missions
./dh d          # OS and terminal compatibility check
./dh update     # Update to the latest version (fast-forward only)
```

> [!NOTE]
> On first run, `./dh` creates the `.venv` virtual environment and installs dependencies automatically. If the environment is broken (for example, copied from another OS), `./dh` recreates it. On Debian/Ubuntu without `python3-venv`, it falls back to [`uv`](https://docs.astral.sh/uv/) when available.

##### Option 1.2: native Debian / Ubuntu package (.deb)
On **Ubuntu, Debian, Linux Mint or Pop!_OS**, install the official package with a menu shortcut and native icon:

```bash
# Download the latest version from GitHub Releases:
curl -fLO https://github.com/araujoajoao/DevOpsHeroCLI/releases/latest/download/DevOpsHero.deb

# (Recommended) Verify integrity with the SHA256SUMS.txt from the same release:
curl -fLO https://github.com/araujoajoao/DevOpsHeroCLI/releases/latest/download/SHA256SUMS.txt
sha256sum --ignore-missing -c SHA256SUMS.txt

# Install from the terminal (or double-click the file in your file manager):
sudo apt install ./DevOpsHero.deb

# (Optional) Build the .deb from source (creates dist/DevOpsHero.deb):
make deb
```

> **Updating**: install the `.deb` from the latest release over the current version. The TUI's `Update` pill tells you when a new version is available.

##### Option 1.3: add a menu shortcut (any distribution)
For GNOME, KDE, XFCE or Cinnamon:
```bash
make install-linux   # Creates an app menu shortcut and adds 'dh' to PATH
```

<a id="en-macos"></a>
#### <img src="assets/icons/apple.svg" width="20" height="20" alt="Apple" /> 2. macOS (MacBook, iMac, Mac mini)

##### Option 2.1 (recommended): native app (.dmg)
The graphical installer is built automatically for every version and published on **[GitHub Releases](https://github.com/araujoajoao/DevOpsHeroCLI/releases/latest)**:

```bash
# 1. Download the latest version:
curl -fLO https://github.com/araujoajoao/DevOpsHeroCLI/releases/latest/download/DevOpsHero.dmg

# (Recommended) Verify integrity with the SHA256SUMS.txt from the same release:
curl -fLO https://github.com/araujoajoao/DevOpsHeroCLI/releases/latest/download/SHA256SUMS.txt
shasum -a 256 --ignore-missing -c SHA256SUMS.txt

# 2. Open the disk image in Finder:
open DevOpsHero.dmg

# (Optional) Build the installer from source (creates dist/DevOpsHero.dmg):
make dmg
```

> **Installing**: open the disk image and drag **DevOpsHero** into **Applications**. It then shows up in **Launchpad**, **Spotlight** and the **Dock**.

##### Option 2.2: from the terminal
```bash
./dh            # Full interface in your current terminal
./dh r          # Quick REPL prompt
```

#### <img src="assets/icons/windows.svg" width="20" height="20" alt="Windows" /> 3. Windows (10 and 11)

> **Download without Git**: get [`DevOpsHero-windows.zip`](https://github.com/araujoajoao/DevOpsHeroCLI/releases/latest/download/DevOpsHero-windows.zip) from the latest release, extract it, and run the commands below inside the `DevOpsHero` folder. To update, download the newest `.zip`.

##### Option 3.1: PowerShell (recommended)
```powershell
.\dh.ps1        # Full TUI
.\dh.ps1 r      # Quick REPL prompt
.\dh.ps1 s      # Profile stats and XP
.\dh.ps1 l      # Catalog of all 80 missions
.\dh.ps1 d      # OS and compatibility check
```

##### Option 3.2: desktop and Start menu shortcuts
To pin DevOpsHero to the desktop and Start menu with the official `.ico`:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_windows.ps1
```

##### Option 3.3: classic Command Prompt (CMD)
```cmd
dh.bat          # Full interface
dh.bat r        # Quick REPL mode
```

> [!TIP]
> **WSL users**: open your Linux terminal (Ubuntu/Debian) and run `./dh`.

#### <img src="assets/icons/python.svg" width="20" height="20" alt="Python" /> 4. Global install with pip (any OS)

To make **`dh`** available from any folder:

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\Activate.ps1
pip install -e .

dh              # Run the interface from any folder
dh r            # Quick interactive prompt
dh s            # Profile stats and XP
dh d            # OS and compatibility check
```

---

<a id="en-releases"></a>
## <img src="assets/icons/github.svg" width="20" height="20" alt="GitHub" /> Updates, versions & releases

- **One source of truth**: the version lives in `devopsherocli/__init__.py` (`__version__`) and in `pyproject.toml`. A test checks that both match, and the Linux, macOS and Windows packages read the version from there.
- **Checking for updates**: the TUI shows the `Update` pill **only** when your copy is behind `origin/main` or when a newer version is published. It never appears when you are ahead with unpushed commits.
- **Applying updates**:
  - Git checkout (Linux, macOS, WSL): `dh update` or `F6` in the TUI runs `git pull --ff-only` and reinstalls the package. It never creates merge commits on your machine.
  - `.deb` / `.dmg` / Windows `.zip` installs: download the latest package from [Releases](https://github.com/araujoajoao/DevOpsHeroCLI/releases/latest). `dh update` shows the right link for your OS.
- **Publishing a release** (maintainers): bump the version in `devopsherocli/__init__.py` and `pyproject.toml`, then:
  ```bash
  git tag vX.Y.Z && git push origin vX.Y.Z
  ```
  The [`release.yml`](.github/workflows/release.yml) workflow checks that the tag matches the code and runs the tests. It then builds the `.deb` (Ubuntu), the `.dmg` (macOS) and the Windows `.zip`, and attaches them, along with `SHA256SUMS.txt`, to the GitHub Release.

---

<a id="en-mobile"></a>
## <img src="assets/icons/ios.svg" width="20" height="20" alt="iOS" /> <img src="assets/icons/expo.svg" width="20" height="20" alt="Expo" /> Mobile apps

The same 80 missions are available on mobile, generated from the CLI tracks:

| Project | Stack | Run |
|---|---|---|
| <img src="assets/icons/expo.svg" width="16" height="16" alt="Expo" /> [`devopshero-mobile`](devopshero-mobile) | React Native (Expo SDK 58, TypeScript) | `make mobile` or `cd devopshero-mobile && npx expo start` |
| <img src="assets/icons/swift.svg" width="16" height="16" alt="Swift" /> [`devopshero-ios-swiftui`](devopshero-ios-swiftui) | Native SwiftUI (Xcode) | `make swift` (macOS) |

To sync missions after changing the CLI tracks:
```bash
.venv/bin/python devopshero-mobile/scripts/export_mobile_dataset.py
```
This rewrites `missions.json` for both apps.

---

<a id="en-commands"></a>
## 🧭 CLI commands

| Shortcut | Full command | Description |
|---|---|---|
| **`dh`** | `./dh` or `devopshero` | **Full TUI**: multi-pane interactive terminal with Console Home, mission explorer, XP bar, streak and Terminal Lab. |
| **`dh r`** | `./dh r` or `devopshero repl` | **Quick prompt**: practice directly on the command line with arrow-key history and autocomplete. |
| **`dh l`** | `./dh l` or `devopshero list` | **Mission catalog**: lists all **80 missions** and whether each is done. |
| **`dh s`** | `./dh s` or `devopshero stats` | **Profile & stats**: your level, total XP, streak and history. |
| **`dh v`** | `./dh v` or `devopshero verify` | **Integrity check**: runs a sandboxed self-test of all **80 missions**. |
| **`dh d`** | `./dh d` or `devopshero doctor` | **OS & terminal check**: compatibility (Linux, macOS, Windows, WSL), UTF-8 and the active terminal. |
| **`dh update`** | `./dh update` or `devopshero update` | **Update**: fast-forward to the latest version (git installs) or show the installer link. |
| **`dh reset`** | `./dh reset` or `devopshero reset` | **Reset progress**: start your journey from scratch. |
| **`dh -v`** | `devopshero --version` | Shows the installed version. |

### ⚡ One-letter shortcuts in REPL mode

| Key | Long command | Action |
|:---:|---|---|
| **`d`** | `dica` / `hint` | Get a hint for the current mission (-XP) |
| **`s`** | `solucao` / `gabarito` | Reveal the solution (zero XP, breaks the streak) |
| **`n`** | `proxima` / `next` | Go to the next available challenge |
| **`r`** | `reset` | Restore the current mission's lab environment |
| **`c`** | `clear` | Clear the terminal |
| **`q`** | `sair` / `exit` | Save progress and quit |

---

<a id="en-docker"></a>
## <img src="assets/icons/docker.svg" width="20" height="20" alt="Docker" /> Run with Docker (no Python needed)

```bash
# Docker Compose with persistent progress:
docker compose -f docker/docker-compose.yml run --rm devopshero

# Or via Makefile:
make docker

# Or build the image manually:
docker build -f docker/Dockerfile -t devopshero .
docker run -it --rm devopshero
```

The image runs as an unprivileged `devops` user.

---

<a id="en-tracks"></a>
## 🗺️ Learning tracks (80 missions)

### <img src="assets/icons/linux.svg" width="20" height="20" alt="Linux" /> 1. Linux Essentials (10 missions)
1. **Basic navigation**: find and print the current working directory.
2. **Detailed listing**: list permissions, owners and sizes, including hidden files.
3. **Creating directories and files**: create nested structures and empty log files.
4. **Investigating logs**: filter critical errors in audit files with pipelines.
5. **Security permissions**: lock down permissions on private SSH keys.
6. **Inspecting and killing processes**: find resource-hungry processes and stop them.
7. **Output redirection**: save port inventories and append headers without overwriting.
8. **Backing up critical files**: copy production configuration files.
9. **Resource diagnostics**: check free disk space and available RAM.
10. **Safe cleanup**: remove temporary files safely.

### <img src="assets/icons/gnubash.svg" width="20" height="20" alt="Bash" /> 2. Sysadmin Basics (10 missions)
1. **Diagnosing systemd services**: check the health and PID of the Nginx web server.
2. **Restarting database services**: apply new credentials by restarting PostgreSQL.
3. **Starting on boot**: enable essential services to start with the OS.
4. **Auditing ports and sockets**: check listening TCP ports with `ss`.
5. **Creating system users**: create accounts with a home directory and bash shell.
6. **Scheduling with crontab**: inspect recurring automation and backup jobs.
7. **Compressing directories with tar**: create `.tar.gz` archives of system directories.
8. **Auditing logs with journalctl**: query centralized systemd daemon logs.
9. **System load and uptime**: monitor uptime and load average.
10. **Admin privileges (sudo)**: grant superuser rights by adding members to the sudo group.

### <img src="assets/icons/git.svg" width="20" height="20" alt="Git" /> 3. Git Version Control (10 missions)
1. **Initializing the repository**: create a clean Git repository for the application.
2. **Inspecting state**: check the working tree status and pending files.
3. **Staging area**: stage modified files before committing.
4. **Recording commits**: create restore points with descriptive messages.
5. **Commit history**: inspect previous commits, authors and SHAs.
6. **Branch isolation**: create and switch to feature branches.
7. **Merging changes**: merge finished features into the main branch.
8. **Remote repositories**: connect the local repository to remotes such as GitHub.
9. **Temporary stash**: stash pending changes to switch context quickly.
10. **Version tags**: create immutable tags for official production releases.

### <img src="assets/icons/docker.svg" width="20" height="20" alt="Docker" /> 4. Docker & Containers (10 missions)
1. **First web container**: run web servers in the background with port mapping.
2. **Auditing running containers**: list running containers with IDs and ports.
3. **Inspecting application logs**: watch stdout/stderr of running microservices.
4. **Interactive exec**: run diagnostic commands inside production containers.
5. **Graceful stop**: stop containers safely with SIGTERM.
6. **Dedicated networks**: connect several services on an isolated bridge.
7. **Data persistence**: create dedicated volumes for durable database data.
8. **Building images**: build custom Docker images from Dockerfiles.
9. **Resource metrics**: watch CPU and memory usage live with `docker stats`.
10. **Cleanup**: remove stale containers to free host resources.

### <img src="assets/icons/kubernetes.svg" width="20" height="20" alt="Kubernetes" /> 5. Kubernetes Orchestration (10 missions)
1. **Inspecting cluster nodes**: check the status and roles of control-plane and worker nodes.
2. **Standalone Pods**: create quick Pods for connectivity tests.
3. **All namespaces at a glance**: list workloads across every namespace.
4. **Resilient Deployments**: create managed Deployments with declared replicas.
5. **Horizontal scaling**: scale replicas to handle traffic spikes.
6. **Exposing with Services**: expose workloads through ClusterIP Services.
7. **Injecting configuration**: create ConfigMaps from literals for environment variables.
8. **Detailed troubleshooting**: investigate Pod events, failures and warnings with `describe`.
9. **Collecting Pod logs**: read startup and request logs in Kubernetes.
10. **Clean deletion**: stop and remove stale Pods and resources safely.

### <img src="assets/icons/aws.svg" width="20" height="20" alt="AWS" /> 6. AWS Cloud & Infrastructure (10 missions)
1. **Identity audit**: confirm your account and authenticated user with AWS STS.
2. **Listing S3 buckets**: inspect the available object storage buckets.
3. **Creating buckets**: provision new S3 buckets for backups and logs.
4. **Uploading artifacts**: copy local release packages to cloud buckets.
5. **EC2 inventory**: describe virtual instances and their public and private IPs.
6. **Starting servers**: start EC2 instances on demand for batch workloads.
7. **Stopping idle servers**: stop EC2 instances, keeping their volumes, to cut costs.
8. **Auditing IAM identities**: list the users registered in the account.
9. **Provisioning service accounts**: create new IAM identities for CI/CD pipelines.
10. **Lambda inventory**: list active serverless functions in the AWS region.

### <img src="assets/icons/terraform.svg" width="20" height="20" alt="Terraform" /> 7. Terraform Infrastructure as Code (10 missions)
1. **Initializing the project**: install providers and configure backends.
2. **Code formatting**: reformat HCL manifests to the official HashiCorp style.
3. **Static validation**: validate syntax and arguments before touching cloud resources.
4. **Planning changes**: preview the execution plan (`+`, `~`, `-`) with `terraform plan`.
5. **Provisioning with apply**: apply declared changes to create resources and update state.
6. **Inspecting state**: show the state file in a readable format with `terraform show`.
7. **Resource inventory**: list the managed resource addresses with `state list`.
8. **Resource details**: inspect the attributes of a single resource stored in state.
9. **Reading outputs**: extract useful output values produced by provisioning.
10. **Controlled destroy**: remove all managed resources to stop test costs.

### <img src="assets/icons/datadog.svg" width="20" height="20" alt="Datadog" /> 8. Datadog Observability (10 missions)
1. **Agent diagnostics**: check the overall health of collectors, metrics and APM.
2. **Daemon health check**: run quick integrity tests of the monitoring process.
3. **Version audit**: identify the exact Datadog Agent version installed.
4. **Disk integration check**: run the storage plugin diagnostics.
5. **Docker integration check**: validate container metrics and socket collection.
6. **Support flare**: collect encrypted diagnostics and logs for support.
7. **Unified service tagging (environment)**: set the standard `DD_ENV` tag.
8. **Unified service tagging (service)**: set the standard `DD_SERVICE` tag.
9. **Unified service tagging (version)**: set the standard `DD_VERSION` tag.
10. **Configuration audit**: inspect the agent's consolidated configuration.

---

<a id="en-gamification"></a>
## 🎮 Gamification

- **⚡ Anti-cheat speed rule**:
  - **100% of points**: awarded **only** when the command is run **without hints** within the **first 5 seconds** (`<= 5.0s`). This shows real retention rather than looking it up online or asking an AI.
  - **More than 5 seconds (no hints)**: 70% of the base points.
  - **Progressive hint penalty**: each hint (F3 or the `dica` command) lowers your score:
    - 💡 **1 hint**: 40% of XP
    - 💡 **2 hints**: 20% of XP
    - 💡 **3+ hints**: 10% of XP (a minimum, to encourage finishing)
  - **👁️ Solution revealed (F4 / `solucao`)**: zero XP for the mission and the streak resets to 0.
- **XP and levels (10 ranks)**:
  - 🌱 **Level 1 · DevOps Recruit** (0–249 XP)
  - <img src="assets/icons/gnubash.svg" width="16" height="16" alt="Bash" /> **Level 2 · Sysadmin Basics** (250–599 XP)
  - <img src="assets/icons/linux.svg" width="16" height="16" alt="Linux" /> **Level 3 · Linux Explorer** (600–1099 XP)
  - <img src="assets/icons/git.svg" width="16" height="16" alt="Git" /> **Level 4 · Git Codecrafter** (1100–1699 XP)
  - <img src="assets/icons/docker.svg" width="16" height="16" alt="Docker" /> **Level 5 · Container Captain** (1700–2499 XP)
  - <img src="assets/icons/kubernetes.svg" width="16" height="16" alt="Kubernetes" /> **Level 6 · Cluster Commander** (2500–3499 XP)
  - <img src="assets/icons/aws.svg" width="16" height="16" alt="AWS" /> **Level 7 · Cloud Architect** (3500–4699 XP)
  - <img src="assets/icons/terraform.svg" width="16" height="16" alt="Terraform" /> **Level 8 · IaC Master** (4700–6199 XP)
  - <img src="assets/icons/datadog.svg" width="16" height="16" alt="Datadog" /> **Level 9 · Observability Guru** (6200–7999 XP)
  - ⚡ **Level 10 · DevOps Titan** (8000+ XP)
- **Streak 🔥**: consecutive correct answers without revealing the solution give up to **+50% bonus XP**.
- **Automatic local save**: progress is stored in `~/.devopsherocli/progress.json`.

---

<a id="en-shortcuts"></a>
## ⌨️ Keyboard shortcuts

| Key | Action |
|---|---|
| `F1` | Help and command summary |
| `F2` | Open the track and mission picker |
| `F3` | Show or hide the current mission's hint |
| `F4` | Reveal the solution (resets the streak) |
| `F5` | Reset the lab to the mission's initial state |
| `F6` | Check for and apply updates |
| `Ctrl + L` | Clear the terminal log |
| `Ctrl + Q` | Quit safely |

---

<a id="en-icons"></a>
## 🎨 Visual identity & icons

<img src="assets/logo.png" width="96" height="96" alt="DevOpsHero logo" />

The official DevOpsHero logo (graduation cap, laptop and the DevOps ∞ loop) is [assets/logo.png](assets/logo.png): the mobile app icon with a transparent background. The full app icon with its rounded background is [devopshero-mobile/assets/icon.png](devopshero-mobile/assets/icon.png), identical to the SwiftUI app's `AppIcon-1024.png`.

Technology and platform logos used in this README live in [assets/icons/](assets/icons) as brand-colored SVGs (from [Simple Icons](https://simpleicons.org), CC0; AWS from [Devicon](https://devicon.dev), MIT; Windows drawn from its four-pane mark). Black marks are drawn in neutral gray so they stay visible in light and dark themes. Each logo is a trademark of its owner.

Native desktop icons (macOS Dock/Launchpad and the Windows shortcut) are generated from the vector [assets/icon.svg](assets/icon.svg), following Apple's macOS Human Interface Guidelines:
- **Geometry**: continuous superellipse (an 824×824 *squircle* centered on a 1024×1024 canvas).
- **Pure alpha**: a fully transparent outer background (`alpha = 0`), so no unwanted plate appears in the Dock or Launchpad.
- **Native Swift pipeline**: [`scripts/build_icons.sh`](scripts/build_icons.sh) builds the derived formats with `AppKit` (`NSGraphicsContext`):
  - `assets/DevOpsHero.icns` (10 Retina sizes, 16px to 1024px)
  - `assets/DevOpsHero.ico` (multi-size, for Windows)

To rebuild every desktop icon from the SVG (macOS):
```bash
make icons
```

---

<a id="en-tests"></a>
## <img src="assets/icons/python.svg" width="20" height="20" alt="Python" /> Automated tests

```bash
make test
# Or the full integrity check of all 80 missions:
make verify
# Or directly with Python:
.venv/bin/python -m unittest discover tests
```

CI runs the suite on Linux, macOS and Windows with Python 3.9 to 3.13.

---

<a id="en-ai-review"></a>
## <img src="assets/icons/githubactions.svg" width="20" height="20" alt="GitHub Actions" /> Automated AI review on GitHub

Every pull request goes through an automated GitHub Actions pipeline ([`ai_code_review.yml`](.github/workflows/ai_code_review.yml)) that checks:
- 🔒 **AppSec**: exposed credentials, command/SQL injection, path traversal and excessive permissions.
- 📐 **Code quality**: clean code, typing, exception handling and readability in any language.
- 🌿 **Git standards**: Conventional Commits and change scope.
- 💬 **Feedback on the PR**: an automated verdict (`LGTM` or `Changes required`) with inline suggestions.

---

<a id="en-contributing"></a>
## 🤝 Contributing

Contributions are very welcome!

1. Read the guide in [CONTRIBUTING.md](.github/CONTRIBUTING.md).
2. Create a topic branch from `main` (`git checkout -b feat/new-track` or `fix/bug-name`).
3. Follow Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`).
4. Run the tests locally (`make test`).
5. Open a pull request using the [template](.github/pull_request_template.md).

---

## 📄 License

Released under the **MIT** license. See [LICENSE](LICENSE) for details.

Built by **[João Araújo](https://github.com/araujoajoao)**.

<div align="right"><a href="#">⬆ Back to top</a></div>

---

<a id="portugues"></a>

# 🇧🇷 Português

*Sem precisar de nuvem, sem pagar contas e sem risco de quebrar sua máquina.*

[Como rodar](#pt-run) •
[App macOS](#pt-macos) •
[Atualizações e versões](#pt-releases) •
[Apps mobile](#pt-mobile) •
[Trilhas e missões](#pt-tracks) •
[Gamificação](#pt-gamification) •
[Atalhos](#pt-shortcuts) •
[Docker](#pt-docker) •
[Testes](#pt-tests)

<a id="pt-what"></a>
## 💡 O que é o DevOpsHeroCLI?

Diferente de quizzes de múltipla escolha ou tutoriais estáticos, o **DevOpsHeroCLI** simula um ambiente operacional completo em memória:

- **Sistema de Arquivos Virtual (VFS)**: se você cria `/app/logs/access.log`, ele passa a existir de verdade para outros comandos (`ls`, `grep`, `tar`, `rm`).
- **Daemons e serviços (`systemctl`)**: gerencie o estado de serviços (`status`, `restart`, `enable`).
- **Mecanismo de contêineres (`docker`)**: simula o ciclo de vida de contêineres, imagens, redes dedicadas e volumes.
- **Orquestrador de clusters (`kubectl`)**: gerencie Pods, Deployments, réplicas, Services e ConfigMaps.
- **Observabilidade realista (`datadog-agent`)**: checks de disco/docker, status de componentes e tags unificadas de serviço (`DD_ENV`, `DD_SERVICE`, `DD_VERSION`).

---

<a id="pt-run"></a>
## 🚀 Como rodar localmente em 1 minuto

### ⚡ Recomendado: execução direta (sem clonar)

Se você quer apenas jogar e aprender sem baixar o repositório completo:

```bash
# Usando pipx (cria ambiente isolado e executa na hora):
pipx run --spec git+https://github.com/araujoajoao/DevOpsHeroCLI.git dh

# Ou instalando via pip:
pip install git+https://github.com/araujoajoao/DevOpsHeroCLI.git
dh              # Interface visual completa
dh r            # Modo REPL rápido
```

### 📂 Pelo repositório Git (passo a passo por sistema operacional)

Se preferir clonar o código-fonte para rodar localmente ou contribuir:

```bash
# Clone leve (apenas o estado atual, sem o histórico completo)
git clone --depth=1 https://github.com/araujoajoao/DevOpsHeroCLI.git
cd DevOpsHeroCLI
```

Depois siga os passos do seu sistema operacional.

#### <img src="assets/icons/linux.svg" width="20" height="20" alt="Linux" /> 1. Linux (Ubuntu, Debian, Fedora, Arch) ou WSL

##### Opção 1.1: executar no terminal (recomendado)
Abra seu terminal (**Bash** ou **Zsh**) e execute o launcher oficial:

```bash
./dh            # Interface TUI completa
./dh r          # Prompt REPL rápido (sem divisão de tela)
./dh s          # Estatísticas do perfil e XP acumulado
./dh l          # Catálogo das 80 missões
./dh d          # Diagnóstico do SO e compatibilidade do terminal
./dh update     # Atualiza para a versão mais recente (somente fast-forward)
```

> [!NOTE]
> Na primeira execução, o `./dh` cria o ambiente virtual `.venv` e instala as dependências automaticamente. Se o ambiente estiver quebrado (por exemplo, copiado de outro SO), o `./dh` o recria. No Debian/Ubuntu sem `python3-venv`, ele usa o [`uv`](https://docs.astral.sh/uv/) quando disponível.

##### Opção 1.2: pacote nativo Debian / Ubuntu (.deb)
No **Ubuntu, Debian, Linux Mint ou Pop!_OS**, instale o pacote oficial com atalho no menu e ícone nativo:

```bash
# Baixe a versão mais recente publicada nos GitHub Releases:
curl -fLO https://github.com/araujoajoao/DevOpsHeroCLI/releases/latest/download/DevOpsHero.deb

# (Recomendado) Confira a integridade com o SHA256SUMS.txt do mesmo release:
curl -fLO https://github.com/araujoajoao/DevOpsHeroCLI/releases/latest/download/SHA256SUMS.txt
sha256sum --ignore-missing -c SHA256SUMS.txt

# Instale via terminal (ou dê duplo clique no arquivo pelo gerenciador de arquivos):
sudo apt install ./DevOpsHero.deb

# (Opcional) Para compilar o .deb a partir do código-fonte (gera dist/DevOpsHero.deb):
make deb
```

> **Atualização**: instale o `.deb` do release mais recente por cima da versão atual. A pílula `Update` da TUI avisa quando houver uma nova versão.

##### Opção 1.3: atalho no menu (qualquer distribuição)
Para GNOME, KDE, XFCE ou Cinnamon:
```bash
make install-linux   # Cria atalho no menu de aplicativos e adiciona 'dh' ao PATH
```

<a id="pt-macos"></a>
#### <img src="assets/icons/apple.svg" width="20" height="20" alt="Apple" /> 2. macOS (MacBook, iMac, Mac mini)

##### Opção 2.1 (recomendada): aplicativo nativo (.dmg)
O instalador gráfico é gerado automaticamente a cada versão e publicado nos **[GitHub Releases](https://github.com/araujoajoao/DevOpsHeroCLI/releases/latest)**:

```bash
# 1. Baixe a versão mais recente:
curl -fLO https://github.com/araujoajoao/DevOpsHeroCLI/releases/latest/download/DevOpsHero.dmg

# (Recomendado) Confira a integridade com o SHA256SUMS.txt do mesmo release:
curl -fLO https://github.com/araujoajoao/DevOpsHeroCLI/releases/latest/download/SHA256SUMS.txt
shasum -a 256 --ignore-missing -c SHA256SUMS.txt

# 2. Abra a imagem de disco no Finder:
open DevOpsHero.dmg

# (Opcional) Para compilar o instalador a partir do código-fonte (gera dist/DevOpsHero.dmg):
make dmg
```

> **Instalação**: abra a imagem de disco e arraste o **DevOpsHero** para **Applications**. Ele passa a aparecer no **Launchpad**, no **Spotlight** e no **Dock**.

##### Opção 2.2: pelo terminal
```bash
./dh            # Interface completa no terminal atual
./dh r          # Prompt REPL rápido
```

#### <img src="assets/icons/windows.svg" width="20" height="20" alt="Windows" /> 3. Windows (10 e 11)

> **Download sem Git**: baixe o [`DevOpsHero-windows.zip`](https://github.com/araujoajoao/DevOpsHeroCLI/releases/latest/download/DevOpsHero-windows.zip) do release mais recente, extraia e rode os comandos abaixo dentro da pasta `DevOpsHero`. Para atualizar, baixe o `.zip` mais novo.

##### Opção 3.1: PowerShell (recomendado)
```powershell
.\dh.ps1        # Interface TUI completa
.\dh.ps1 r      # Prompt REPL rápido
.\dh.ps1 s      # Estatísticas do perfil e XP
.\dh.ps1 l      # Catálogo das 80 missões
.\dh.ps1 d      # Diagnóstico do SO e compatibilidade
```

##### Opção 3.2: atalhos na Área de Trabalho e no Menu Iniciar
Para fixar o DevOpsHero na Área de Trabalho e no Menu Iniciar com o `.ico` oficial:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_windows.ps1
```

##### Opção 3.3: Prompt de Comando clássico (CMD)
```cmd
dh.bat          # Interface completa
dh.bat r        # Modo REPL rápido
```

> [!TIP]
> **Usuários de WSL**: abra seu terminal Linux (Ubuntu/Debian) e rode `./dh`.

#### <img src="assets/icons/python.svg" width="20" height="20" alt="Python" /> 4. Instalação global via pip (qualquer SO)

Para que o comando **`dh`** funcione em qualquer pasta:

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\Activate.ps1
pip install -e .

dh              # Executa a interface de qualquer pasta
dh r            # Prompt interativo rápido
dh s            # Estatísticas do perfil e XP
dh d            # Diagnóstico de SO e compatibilidade
```

---

<a id="pt-releases"></a>
## <img src="assets/icons/github.svg" width="20" height="20" alt="GitHub" /> Atualizações, versões e releases

- **Fonte única de versão**: a versão fica em `devopsherocli/__init__.py` (`__version__`) e no `pyproject.toml`. Um teste garante que as duas batem, e os pacotes de Linux, macOS e Windows leem a versão de lá.
- **Verificação de updates**: a TUI mostra a pílula `Update` **somente** quando sua cópia está atrás do `origin/main` ou quando existe uma versão publicada mais nova. Ela nunca aparece quando você está à frente, com commits ainda não enviados.
- **Aplicando a atualização**:
  - Checkout Git (Linux, macOS, WSL): `dh update` ou `F6` na TUI executa `git pull --ff-only` e reinstala o pacote. Nunca cria merge commits na sua máquina.
  - Instalações `.deb` / `.dmg` / `.zip` do Windows: baixe o pacote mais recente em [Releases](https://github.com/araujoajoao/DevOpsHeroCLI/releases/latest). O `dh update` mostra o link certo para o seu SO.
- **Publicando um release** (mantenedores): atualize a versão em `devopsherocli/__init__.py` e `pyproject.toml` e depois rode:
  ```bash
  git tag vX.Y.Z && git push origin vX.Y.Z
  ```
  O workflow [`release.yml`](.github/workflows/release.yml) confere se a tag bate com o código e roda os testes. Em seguida, gera o `.deb` (Ubuntu), o `.dmg` (macOS) e o `.zip` do Windows e os anexa ao GitHub Release, junto com o `SHA256SUMS.txt`.

---

<a id="pt-mobile"></a>
## <img src="assets/icons/ios.svg" width="20" height="20" alt="iOS" /> <img src="assets/icons/expo.svg" width="20" height="20" alt="Expo" /> Apps mobile

As mesmas 80 missões estão disponíveis no mobile, geradas a partir das trilhas da CLI:

| Projeto | Stack | Como rodar |
|---|---|---|
| <img src="assets/icons/expo.svg" width="16" height="16" alt="Expo" /> [`devopshero-mobile`](devopshero-mobile) | React Native (Expo SDK 58, TypeScript) | `make mobile` ou `cd devopshero-mobile && npx expo start` |
| <img src="assets/icons/swift.svg" width="16" height="16" alt="Swift" /> [`devopshero-ios-swiftui`](devopshero-ios-swiftui) | SwiftUI nativo (Xcode) | `make swift` (macOS) |

Para sincronizar as missões depois de alterar as trilhas da CLI:
```bash
.venv/bin/python devopshero-mobile/scripts/export_mobile_dataset.py
```
Isso regrava o `missions.json` dos dois apps.

---

<a id="pt-commands"></a>
## 🧭 Comandos da CLI

| Atalho | Comando completo | Descrição |
|---|---|---|
| **`dh`** | `./dh` ou `devopshero` | **Interface TUI completa**: terminal interativo multi-painel com Console Home, explorer de missões, barra de XP, streak e Terminal Lab. |
| **`dh r`** | `./dh r` ou `devopshero repl` | **Prompt rápido**: pratique direto na linha de comando com histórico pelas setas e autocomplete. |
| **`dh l`** | `./dh l` ou `devopshero list` | **Catálogo de missões**: lista as **80 missões** e o status de cada uma. |
| **`dh s`** | `./dh s` ou `devopshero stats` | **Perfil e estatísticas**: nível, XP acumulado, sequência (streak) e histórico. |
| **`dh v`** | `./dh v` ou `devopshero verify` | **Diagnóstico de integridade**: autoteste em sandbox de todas as **80 missões**. |
| **`dh d`** | `./dh d` ou `devopshero doctor` | **Diagnóstico de SO e terminal**: compatibilidade (Linux, macOS, Windows, WSL), UTF-8 e terminal ativo. |
| **`dh update`** | `./dh update` ou `devopshero update` | **Atualização**: avança para a versão mais recente (instalações via git) ou mostra o link do instalador. |
| **`dh reset`** | `./dh reset` ou `devopshero reset` | **Reset de progresso**: recomeça a jornada do zero. |
| **`dh -v`** | `devopshero --version` | Mostra a versão instalada. |

### ⚡ Atalhos de 1 letra no modo REPL

| Tecla | Comando longo | Ação |
|:---:|---|---|
| **`d`** | `dica` / `hint` | Pede uma dica da missão atual (-XP) |
| **`s`** | `solucao` / `gabarito` | Revela a solução (zera o XP e quebra o streak) |
| **`n`** | `proxima` / `next` | Avança para o próximo desafio disponível |
| **`r`** | `reset` | Restaura o laboratório da missão atual |
| **`c`** | `clear` | Limpa a tela do terminal |
| **`q`** | `sair` / `exit` | Salva o progresso e encerra |

---

<a id="pt-docker"></a>
## <img src="assets/icons/docker.svg" width="20" height="20" alt="Docker" /> Executando com Docker (sem instalar Python)

```bash
# Docker Compose com persistência de progresso:
docker compose -f docker/docker-compose.yml run --rm devopshero

# Ou via Makefile:
make docker

# Ou construindo a imagem manualmente:
docker build -f docker/Dockerfile -t devopshero .
docker run -it --rm devopshero
```

A imagem roda com o usuário sem privilégios `devops`.

---

<a id="pt-tracks"></a>
## 🗺️ Trilhas de aprendizado (80 missões)

### <img src="assets/icons/linux.svg" width="20" height="20" alt="Linux" /> 1. Linux Essencial (10 missões)
1. **Navegação básica**: descubra e exiba o diretório de trabalho atual.
2. **Listagem detalhada**: liste permissões, donos e tamanhos, incluindo arquivos ocultos.
3. **Criação de diretórios e arquivos**: crie estruturas aninhadas e arquivos de log vazios.
4. **Investigação de logs**: filtre erros críticos em arquivos de auditoria com pipelines.
5. **Permissões de segurança**: restrinja as permissões de chaves SSH privadas.
6. **Inspeção e encerramento de processos**: identifique processos com alto consumo e finalize-os.
7. **Redirecionamento de saída**: salve inventários de portas e adicione cabeçalhos sem sobrescrever.
8. **Backup de arquivos críticos**: copie arquivos de configuração de produção.
9. **Diagnóstico de recursos**: analise o espaço livre em disco e a RAM disponível.
10. **Remoção segura**: elimine arquivos temporários com segurança.

### <img src="assets/icons/gnubash.svg" width="20" height="20" alt="Bash" /> 2. Sysadmin Básico (10 missões)
1. **Diagnóstico de serviços systemd**: verifique a saúde e o PID do servidor web Nginx.
2. **Reinício de serviços de banco**: aplique novas credenciais reiniciando o PostgreSQL.
3. **Persistência no boot**: habilite serviços essenciais para iniciar com o SO.
4. **Auditoria de portas e sockets**: verifique portas TCP em escuta com `ss`.
5. **Criação de usuários de sistema**: crie contas com diretório home e shell bash.
6. **Agendamento com crontab**: inspecione rotinas periódicas de automação e backup.
7. **Compactação com tar**: crie arquivos `.tar.gz` de diretórios do sistema.
8. **Auditoria de logs com journalctl**: consulte logs centralizados dos daemons do systemd.
9. **Carga e uptime**: monitore o tempo de atividade e o load average.
10. **Privilégios administrativos (sudo)**: conceda poderes de superusuário adicionando membros ao grupo sudo.

### <img src="assets/icons/git.svg" width="20" height="20" alt="Git" /> 3. Git Controle de Versão (10 missões)
1. **Inicializando o repositório**: crie um repositório Git limpo para a aplicação.
2. **Inspecionando o estado**: consulte o status da árvore de trabalho e os arquivos pendentes.
3. **Área de staging**: mova arquivos modificados para a staging area antes do commit.
4. **Gravando commits**: registre pontos de restauração com mensagens descritivas.
5. **Histórico de commits**: inspecione commits anteriores, autores e SHAs.
6. **Isolamento em branches**: crie e ative branches de feature.
7. **Mesclando alterações**: faça merge de funcionalidades prontas na branch principal.
8. **Repositórios remotos**: conecte o repositório local a remotos como o GitHub.
9. **Stash temporário**: guarde alterações pendentes no stash para trocar de contexto.
10. **Tags de versão**: crie tags imutáveis para releases oficiais de produção.

### <img src="assets/icons/docker.svg" width="20" height="20" alt="Docker" /> 4. Docker & Contêineres (10 missões)
1. **Primeiro contêiner web**: execute servidores web em background mapeando portas.
2. **Auditoria de contêineres ativos**: liste contêineres em execução com IDs e portas.
3. **Inspeção de logs da aplicação**: acompanhe stdout/stderr de microsserviços em execução.
4. **Execução interativa**: rode comandos de diagnóstico dentro de contêineres em produção.
5. **Parada graciosa**: interrompa contêineres com SIGTERM de forma segura.
6. **Redes dedicadas**: conecte vários serviços em uma bridge isolada.
7. **Persistência de dados**: crie volumes dedicados para dados duráveis de banco.
8. **Build de imagens**: construa imagens Docker personalizadas a partir de Dockerfiles.
9. **Métricas de recursos**: acompanhe CPU e memória em tempo real com `docker stats`.
10. **Limpeza**: remova contêineres obsoletos para liberar recursos do host.

### <img src="assets/icons/kubernetes.svg" width="20" height="20" alt="Kubernetes" /> 5. Kubernetes Orquestração (10 missões)
1. **Inspeção dos nós do cluster**: verifique o status e o papel dos nós control-plane e worker.
2. **Pods standalone**: crie Pods rápidos para testes de conectividade.
3. **Visão de todos os namespaces**: liste cargas de trabalho em todos os namespaces.
4. **Deployments resilientes**: crie Deployments gerenciados com réplicas declaradas.
5. **Escalonamento horizontal**: escale réplicas para suportar picos de tráfego.
6. **Exposição com Services**: exponha cargas de trabalho com Services ClusterIP.
7. **Injeção de configurações**: crie ConfigMaps a partir de literais para variáveis de ambiente.
8. **Troubleshooting detalhado**: investigue eventos, falhas e alertas de Pods com `describe`.
9. **Coleta de logs de Pods**: leia logs de inicialização e de requisições no Kubernetes.
10. **Remoção limpa**: encerre e remova Pods e recursos obsoletos com segurança.

### <img src="assets/icons/aws.svg" width="20" height="20" alt="AWS" /> 6. AWS Cloud & Infraestrutura (10 missões)
1. **Auditoria de identidade**: confirme sua conta e o usuário autenticado com o AWS STS.
2. **Listagem de buckets S3**: inspecione os buckets de armazenamento disponíveis.
3. **Criação de buckets**: provisione novos buckets S3 para backups e logs.
4. **Upload de artefatos**: envie pacotes de release locais para buckets na nuvem.
5. **Inventário EC2**: descreva instâncias virtuais e seus IPs públicos e privados.
6. **Iniciando servidores**: inicie instâncias EC2 sob demanda para cargas batch.
7. **Parando servidores ociosos**: pare instâncias EC2, preservando os volumes, para reduzir custos.
8. **Auditoria de identidades IAM**: liste os usuários cadastrados na conta.
9. **Provisionando contas de serviço**: crie novas identidades IAM para esteiras de CI/CD.
10. **Inventário Lambda**: liste as funções serverless ativas na região AWS.

### <img src="assets/icons/terraform.svg" width="20" height="20" alt="Terraform" /> 7. Terraform Infraestrutura como Código (10 missões)
1. **Inicialização do projeto**: instale provedores e configure backends.
2. **Padronização de código**: reformate manifestos HCL no padrão oficial da HashiCorp.
3. **Validação estática**: valide sintaxe e argumentos antes de tocar nos recursos de nuvem.
4. **Planejamento de mudanças**: preveja o plano de execução (`+`, `~`, `-`) com `terraform plan`.
5. **Provisionamento com apply**: aplique as mudanças declaradas para criar recursos e atualizar o estado.
6. **Inspeção do estado**: exiba o arquivo de estado em formato legível com `terraform show`.
7. **Inventário de recursos**: liste os endereços dos recursos gerenciados com `state list`.
8. **Detalhamento de recurso**: inspecione os atributos de um recurso salvo no estado.
9. **Consultando outputs**: extraia os valores de saída gerados pelo provisionamento.
10. **Destruição controlada**: remova todos os recursos gerenciados para zerar custos de teste.

### <img src="assets/icons/datadog.svg" width="20" height="20" alt="Datadog" /> 8. Datadog Observabilidade (10 missões)
1. **Diagnóstico do Agent**: verifique a saúde geral de coletores, métricas e APM.
2. **Health check do daemon**: rode testes rápidos de integridade do processo de monitoramento.
3. **Auditoria de versão**: identifique a versão exata do Datadog Agent instalada.
4. **Check de integração de disco**: rode o diagnóstico do plugin de armazenamento.
5. **Check de integração Docker**: valide a coleta de métricas de contêineres e sockets.
6. **Flare de suporte**: colete diagnósticos e logs criptografados para o suporte.
7. **Unified service tagging (ambiente)**: configure a tag padronizada `DD_ENV`.
8. **Unified service tagging (serviço)**: configure a tag padronizada `DD_SERVICE`.
9. **Unified service tagging (versão)**: configure a tag padronizada `DD_VERSION`.
10. **Auditoria de configurações**: inspecione a configuração consolidada do agente.

---

<a id="pt-gamification"></a>
## 🎮 Gamificação

- **⚡ Regra anti-cola de velocidade**:
  - **100% dos pontos**: concedidos **apenas** quando o comando é executado **sem dicas** nos **primeiros 5 segundos** (`<= 5.0s`). Isso comprova a fixação do conteúdo em vez de consultas a pesquisas ou IA.
  - **Mais de 5 segundos (sem dicas)**: 70% dos pontos base.
  - **Penalidade progressiva por dicas**: cada dica (F3 ou o comando `dica`) reduz a pontuação:
    - 💡 **1 dica**: 40% do XP
    - 💡 **2 dicas**: 20% do XP
    - 💡 **3+ dicas**: 10% do XP (mínimo garantido para incentivar a conclusão)
  - **👁️ Gabarito revelado (F4 / `solucao`)**: zera o XP da missão e o streak volta a 0.
- **XP e níveis (10 patentes)**:
  - 🌱 **Nível 1 · Recruta DevOps** (0–249 XP)
  - <img src="assets/icons/gnubash.svg" width="16" height="16" alt="Bash" /> **Nível 2 · Sysadmin Básico** (250–599 XP)
  - <img src="assets/icons/linux.svg" width="16" height="16" alt="Linux" /> **Nível 3 · Linux Explorer** (600–1099 XP)
  - <img src="assets/icons/git.svg" width="16" height="16" alt="Git" /> **Nível 4 · Git Codecrafter** (1100–1699 XP)
  - <img src="assets/icons/docker.svg" width="16" height="16" alt="Docker" /> **Nível 5 · Container Captain** (1700–2499 XP)
  - <img src="assets/icons/kubernetes.svg" width="16" height="16" alt="Kubernetes" /> **Nível 6 · Cluster Commander** (2500–3499 XP)
  - <img src="assets/icons/aws.svg" width="16" height="16" alt="AWS" /> **Nível 7 · Cloud Architect** (3500–4699 XP)
  - <img src="assets/icons/terraform.svg" width="16" height="16" alt="Terraform" /> **Nível 8 · IaC Master** (4700–6199 XP)
  - <img src="assets/icons/datadog.svg" width="16" height="16" alt="Datadog" /> **Nível 9 · Observability Guru** (6200–7999 XP)
  - ⚡ **Nível 10 · DevOps Titan** (8000+ XP)
- **Sequência (streak 🔥)**: acertos seguidos sem revelar o gabarito dão até **+50% de bônus de XP**.
- **Salvamento local automático**: o progresso fica em `~/.devopsherocli/progress.json`.

---

<a id="pt-shortcuts"></a>
## ⌨️ Atalhos do teclado

| Tecla | Ação |
|---|---|
| `F1` | Ajuda e resumo dos comandos |
| `F2` | Abre o seletor de trilhas e missões |
| `F3` | Mostra ou oculta a dica da missão atual |
| `F4` | Revela o gabarito (zera o streak) |
| `F5` | Restaura o laboratório para o estado inicial da missão |
| `F6` | Verifica e aplica atualizações |
| `Ctrl + L` | Limpa o log do terminal |
| `Ctrl + Q` | Encerra com segurança |

---

<a id="pt-icons"></a>
## 🎨 Identidade visual e ícones

<img src="assets/logo.png" width="96" height="96" alt="DevOpsHero logo" />

O logo oficial do DevOpsHero (capelo, laptop e o laço ∞ do DevOps) é o [assets/logo.png](assets/logo.png): o ícone do app mobile com fundo transparente. O ícone completo do app, com fundo arredondado, é o [devopshero-mobile/assets/icon.png](devopshero-mobile/assets/icon.png), idêntico ao `AppIcon-1024.png` do app SwiftUI.

Os logos de tecnologias e plataformas usados neste README ficam em [assets/icons/](assets/icons), como SVGs nas cores oficiais das marcas (do [Simple Icons](https://simpleicons.org), CC0; AWS do [Devicon](https://devicon.dev), MIT; Windows desenhado a partir da marca de quatro painéis). Marcas pretas são desenhadas em cinza neutro para continuarem visíveis nos temas claro e escuro. Cada logo é marca registrada do respectivo dono.

Os ícones nativos de desktop (Dock/Launchpad no macOS e atalho no Windows) são gerados a partir do vetor [assets/icon.svg](assets/icon.svg), seguindo as Human Interface Guidelines da Apple para macOS:
- **Geometria**: superelipse contínua (*squircle* de 824×824 centralizado em canvas de 1024×1024).
- **Alfa puro**: fundo externo 100% transparente (`alpha = 0`), sem placa ou moldura indesejada no Dock e no Launchpad.
- **Pipeline nativo em Swift**: o [`scripts/build_icons.sh`](scripts/build_icons.sh) gera os formatos derivados com `AppKit` (`NSGraphicsContext`):
  - `assets/DevOpsHero.icns` (10 resoluções Retina, de 16px a 1024px)
  - `assets/DevOpsHero.ico` (múltiplas resoluções, para Windows)

Para recompilar todos os ícones de desktop a partir do SVG (macOS):
```bash
make icons
```

---

<a id="pt-tests"></a>
## <img src="assets/icons/python.svg" width="20" height="20" alt="Python" /> Testes automatizados

```bash
make test
# Ou o diagnóstico completo de integridade das 80 missões:
make verify
# Ou diretamente via Python:
.venv/bin/python -m unittest discover tests
```

O CI roda a suíte em Linux, macOS e Windows com Python 3.9 a 3.13.

---

<a id="pt-ai-review"></a>
## <img src="assets/icons/githubactions.svg" width="20" height="20" alt="GitHub Actions" /> Revisão automática por IA no GitHub

Todo pull request passa por uma esteira automatizada no GitHub Actions ([`ai_code_review.yml`](.github/workflows/ai_code_review.yml)) que verifica:
- 🔒 **AppSec**: credenciais expostas, injeção de comando/SQL, path traversal e permissões indevidas.
- 📐 **Qualidade de código**: clean code, tipagem, tratamento de exceções e legibilidade em qualquer linguagem.
- 🌿 **Padrões Git**: Conventional Commits e escopo das alterações.
- 💬 **Feedback no PR**: parecer automatizado (`LGTM` ou `Alterações necessárias`) com sugestões inline.

---

<a id="pt-contributing"></a>
## 🤝 Contribuições

Contribuições são muito bem-vindas!

1. Leia o guia em [CONTRIBUTING.md](.github/CONTRIBUTING.md).
2. Crie uma branch temática a partir da `main` (`git checkout -b feat/nova-trilha` ou `fix/nome-do-bug`).
3. Siga o padrão Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`).
4. Rode os testes localmente (`make test`).
5. Abra um pull request usando o [modelo padrão](.github/pull_request_template.md).

---

## 📄 Licença

Distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais informações.

Desenvolvido por **[João Araújo](https://github.com/araujoajoao)**.

<div align="right"><a href="#">⬆ Voltar ao topo</a></div>
