param(
    [string]$CodexHome = "$HOME\.codex"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$source = Join-Path $repoRoot ".codex\skills"
$dest = Join-Path $CodexHome "skills"

if (-not (Test-Path $source)) {
    throw "Project skills directory not found: $source"
}

New-Item -ItemType Directory -Force $dest | Out-Null

Get-ChildItem -Path $source -Directory | ForEach-Object {
    $target = Join-Path $dest $_.Name
    if (Test-Path $target) {
        Write-Host "Updating existing skill: $($_.Name)"
        Remove-Item -Recurse -Force $target
    } else {
        Write-Host "Installing skill: $($_.Name)"
    }
    Copy-Item -Recurse -Force $_.FullName $target
}

Write-Host "Project skills installed to $dest"
Write-Host "Restart Codex to pick up newly installed skills."

