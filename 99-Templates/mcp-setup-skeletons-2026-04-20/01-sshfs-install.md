# SSHFS Mount Setup for Windows

## Option A — Native Windows (recommended)

### Install WinFsp + sshfs-win

1. Install WinFsp: https://winfsp.dev/rel/ (latest MSI)
2. Install sshfs-win: https://github.com/winfsp/sshfs-win/releases (latest MSI)
3. Reboot if prompted

### Mount homeserver

```powershell
# Via Explorer (GUI):
# Open File Explorer → Map Network Drive
# Folder: \\sshfs\piet@homeserver\home\piet
# Use SSH key: set via sshfs-win config

# Via command-line:
net use Z: \\sshfs.k\piet@homeserver\home\piet /PERSISTENT:YES

# Or via PowerShell + New-PSDrive (less persistent):
New-PSDrive -Name "Home" -PSProvider FileSystem -Root "\\sshfs\piet@homeserver\home\piet"
```

### Verify

```powershell
dir Z:\vault\03-Agents\*.md | select -first 5
# Should show: plan-2026-04-20.md, end-of-day-report-2026-04-19.md, etc.
```

## Option B — WSL2 (if you prefer Linux tooling on Windows)

```bash
sudo apt install sshfs
mkdir -p ~/homeserver
sshfs homeserver:/home/piet ~/homeserver \
  -o IdentityFile=~/.ssh/id_ed25519,reconnect,ServerAliveInterval=15,allow_other

# Add to /etc/fstab for auto-mount at boot:
homeserver:/home/piet  /home/<user>/homeserver  fuse.sshfs  _netdev,reconnect,IdentityFile=/home/<user>/.ssh/id_ed25519,allow_other  0  0
```

## Path-mapping reference

| Homeserver native | Windows via SSHFS | WSL2 via SSHFS |
|---|---|---|
| `/home/piet/vault` | `\\sshfs\piet@homeserver\home\piet\vault` | `~/homeserver/vault` |
| `/home/piet/.openclaw/workspace` | `\\sshfs\piet@homeserver\home\piet\.openclaw\workspace` | `~/homeserver/.openclaw/workspace` |

## Troubleshooting

- **"Access denied"**: Check SSH key. Run `ssh homeserver ls ~` from cmd first to verify auth.
- **"Network path not found"**: WinFsp service not running. `sc start WinFsp.Launcher`.
- **Slow reads**: Add `-o cache=yes,kernel_cache,big_writes` to sshfs mount options.
- **Disconnects**: Add `-o ServerAliveInterval=15,reconnect,ConnectTimeout=10`.
