# git-commit.ps1 — workaround for Windows Defender locking .git/index
#
# Usage:
#   .\git-commit.ps1 "your commit message" [file1] [file2] ...
#   .\git-commit.ps1 "your commit message" -all
#
# Root cause: Windows Defender scans .git/index when git tries to atomically
# rename index.lock -> index, causing MoveFileEx to return ACCESS_DENIED.
# Permanent fix (run once as Admin): Add-MpPreference -ExclusionPath "<repo>\.git"
#
param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Message,

    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Files,

    [switch]$All
)

$ErrorActionPreference = "Stop"
$repo = $PSScriptRoot
$tmpIndex = [System.IO.Path]::GetTempFileName()

try {
    # 1. Copy current index to temp location
    Copy-Item "$repo\.git\index" $tmpIndex -Force

    # 2. Stage files using the temp index
    if ($All) {
        $env:GIT_INDEX_FILE = $tmpIndex
        git -C $repo add -A
        $env:GIT_INDEX_FILE = $null
    } elseif ($Files.Count -gt 0) {
        $env:GIT_INDEX_FILE = $tmpIndex
        git -C $repo add @Files
        $env:GIT_INDEX_FILE = $null
    } else {
        Write-Host "No files specified. Pass file paths or -All to stage everything." -ForegroundColor Yellow
        exit 1
    }

    # 3. Write the tree from the temp index
    $env:GIT_INDEX_FILE = $tmpIndex
    $tree = git -C $repo write-tree
    $env:GIT_INDEX_FILE = $null

    if (-not $tree) { throw "write-tree failed" }

    # 4. Create the commit object
    $commitHash = git -C $repo commit-tree $tree -p HEAD -m $Message
    if (-not $commitHash) { throw "commit-tree failed" }

    # 5. Update the branch ref directly (avoids update-ref's rename)
    $branch = git -C $repo rev-parse --abbrev-ref HEAD
    $refPath = "$repo\.git\refs\heads\$branch"
    [System.IO.File]::WriteAllText($refPath, "$commitHash`n")

    Write-Host ""
    git -C $repo log --oneline -3
    Write-Host ""
    Write-Host "Committed: $($commitHash.Substring(0,7)) $Message" -ForegroundColor Green
    Write-Host ""
    Write-Host "To push: git -C '$repo' push origin $branch" -ForegroundColor Cyan

} finally {
    $env:GIT_INDEX_FILE = $null
    if (Test-Path $tmpIndex) { Remove-Item $tmpIndex -Force -ErrorAction SilentlyContinue }
}
