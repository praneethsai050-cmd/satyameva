# ==============================================================================
# Satyameva Aegis - Windows Desktop Shortcut Creator
# ==============================================================================
$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$vbsLauncher = Join-Path $projectDir "launch_app.vbs"
$icoPath = Join-Path $projectDir "satyameva.ico"

# Target desktop locations
$desktopLocations = @(
    [Environment]::GetFolderPath('Desktop'),
    "C:\Users\hp\OneDrive\Desktop",
    "C:\Users\hp\Desktop"
) | Select-Object -Unique | Where-Object { Test-Path $_ }

$WshShell = New-Object -ComObject WScript.Shell

foreach ($desktopPath in $desktopLocations) {
    $shortcutPath = Join-Path $desktopPath "Satyameva Aegis.lnk"
    $shortcut = $WshShell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = "wscript.exe"
    $shortcut.Arguments = "`"$vbsLauncher`""
    $shortcut.WorkingDirectory = $projectDir
    $shortcut.IconLocation = "$icoPath,0"
    $shortcut.Description = "Satyameva Aegis - Blockchain Credential Verification System"
    $shortcut.WindowStyle = 1
    $shortcut.Save()
    Write-Host "Created Desktop Shortcut: $shortcutPath"
}

Write-Host "Desktop shortcut creation completed successfully!"
