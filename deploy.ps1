# Deploy PDF-to-XLSX to QNAP NAS (192.168.0.213).
# Requires: OpenSSH client (scp, ssh). Run from project root.
# Usage: .\deploy.ps1
#   $env:NAS_USER = "admin"; .\deploy.ps1

param(
    [string]$NasHost = "192.168.0.213",
    [string]$NasUser = "admin",
    [string]$RemoteDir = "~/pdf2xlsx",
    [string]$DockerPath = $env:DOCKER_PATH   # On your QNAP: /share/MD0_DATA/.qpkg/container-station/usr/bin/.libs
)
if ($env:NAS_USER) { $NasUser = $env:NAS_USER }
if ($env:NAS_HOST) { $NasHost = $env:NAS_HOST }
if ($env:REMOTE_DIR) { $RemoteDir = $env:REMOTE_DIR }
if ($env:DOCKER_PATH) { $DockerPath = $env:DOCKER_PATH }
if (-not $DockerPath) { $DockerPath = "/share/MD0_DATA/.qpkg/container-station/usr/bin/.libs" }

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

Write-Host "Deploying to ${NasUser}@${NasHost}:$RemoteDir"

$sshTarget = "${NasUser}@${NasHost}"
$sshOpts = "-o StrictHostKeyChecking=accept-new"

# Create remote dir
& ssh $sshOpts $sshTarget "mkdir -p $RemoteDir"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Copy project files with scp (tar-over-ssh from Windows often fails format/encoding)
$excludeNames = @(".git", "__pycache__", "venv", ".venv", "media", ".cursor", "mcps", "agent-transcripts")
Get-ChildItem -Path $ProjectRoot -Force | Where-Object {
    $n = $_.Name
    ($n -notin $excludeNames) -and ($n -notlike "*.sqlite3")
} | ForEach-Object {
    & scp -r $sshOpts $_.FullName "${sshTarget}:${RemoteDir}/"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

# On NAS: build and start using provided DockerPath.
$cmd = "export PATH=`"$DockerPath`:`$PATH`" && cd $RemoteDir && docker compose up -d --build"
& ssh -o StrictHostKeyChecking=accept-new $sshTarget $cmd
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Done. App: http://${NasHost}:8001/"
