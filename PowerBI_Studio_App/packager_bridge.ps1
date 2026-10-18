param(
    [Parameter(Mandatory=$true)]
    [string]$JobJsonPath
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$jobText = [System.IO.File]::ReadAllText($JobJsonPath, [System.Text.Encoding]::UTF8)
$job = $jobText | ConvertFrom-Json

$Mode = $job.Mode
$SchemaPath = $job.SchemaPath
$LayoutPath = $job.LayoutPath
$SourcePbixPath = $job.SourcePbixPath
$OutputPath = $job.OutputPath

$possibleDirs = @(
    "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.883.0_x64__8wekyb3d8bbwe\bin",
    "C:\Program Files\Microsoft Power BI Desktop\bin",
    "C:\Program Files (x86)\Microsoft Power BI Desktop\bin"
)
$appx = Get-AppxPackage -Name "*PowerBIDesktop*" -ErrorAction SilentlyContinue | Sort-Object Version -Descending
foreach ($pkg in $appx) {
    if ($pkg.InstallLocation) {
        $possibleDirs += Join-Path $pkg.InstallLocation "bin"
    }
}

$pbiBinDir = $null
foreach ($d in $possibleDirs) {
    if (Test-Path (Join-Path $d "Microsoft.PowerBI.Packaging.dll")) {
        $pbiBinDir = $d
        break
    }
}

if (-not $pbiBinDir) {
    throw "Could not find Microsoft.PowerBI.Packaging.dll in Power BI Desktop installation paths."
}

Get-ChildItem "$pbiBinDir\*.dll" | ForEach-Object {
    try { [System.Reflection.Assembly]::LoadFrom($_.FullName) | Out-Null } catch {}
}
$asm = [System.Reflection.Assembly]::LoadFrom((Join-Path $pbiBinDir "Microsoft.PowerBI.Packaging.dll"))
$s = $asm.GetType("Microsoft.PowerBI.Packaging.StreamablePowerBIPackagePartContent")
$ctorStr = $s.GetConstructor(@([string], [string]))
$ctorBytes = $s.GetConstructor(@([byte[]], [string]))

[string]$reportJson = [System.IO.File]::ReadAllText($LayoutPath, [System.Text.Encoding]::UTF8)
$reportPart = $ctorStr.Invoke(@($reportJson, [string]"application/json"))
$verPart = $ctorStr.Invoke(@([string]"1.28", [string]"text/plain"))
$settingsPart = $ctorStr.Invoke(@([string]'{"Version":4,"ReportSettings":{},"QueriesSettings":{"Version":"2.126.927.0"}}', [string]"application/json"))
$metaPart = $ctorStr.Invoke(@([string]'{"Version":5,"AutoCreatedRelationships":[],"CreatedFrom":"Cloud","CreatedFromRelease":"2024.06"}', [string]"application/json"))

$pkgType = $asm.GetType("Microsoft.PowerBI.Packaging.PowerBIPackage")
$pkgCtor = $pkgType.GetConstructors()[0]
$pkgr = $asm.GetType("Microsoft.PowerBI.Packaging.PowerBIPackager")
$saveMethod = $pkgr.GetMethods() | Where-Object { $_.Name -eq "Save" -and $_.GetParameters().Count -eq 5 }

if ($Mode -eq "pbit") {
    [string]$schemaJson = [System.IO.File]::ReadAllText($SchemaPath, [System.Text.Encoding]::UTF8)
    $schemaPart = $ctorStr.Invoke(@($schemaJson, [string]"application/json"))

    $pkg = $pkgCtor.Invoke(@(
        $null, $null, $null, $null, $schemaPart, $null, $null, $reportPart,
        $null, $metaPart, $settingsPart, $verPart, $null, $null, $null, $null,
        $null, $null, $null, $null, $null
    ))

    $fs = [System.IO.File]::Create($OutputPath)
    try {
        $saveMethod.Invoke($null, @($pkg, $fs, $true, $null, $true))
    } finally {
        $fs.Close()
    }
    Write-Output "SUCCESS_PBIT"
}
elseif ($Mode -eq "repack_pbix") {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [System.IO.Compression.ZipFile]::OpenRead($SourcePbixPath)
    try {
        $dmEntry = $zip.GetEntry("DataModel")
        if (-not $dmEntry) {
            throw "Source PBIX does not contain a DataModel entry."
        }
        $msDm = New-Object System.IO.MemoryStream
        $dmEntry.Open().CopyTo($msDm)
        [byte[]]$dmBytes = $msDm.ToArray()
        $dmPart = $ctorBytes.Invoke(@($dmBytes, [string]"application/octet-stream"))

        $dlPart = $null
        $dlEntry = $zip.GetEntry("DiagramLayout")
        if ($dlEntry) {
            $srDl = New-Object System.IO.StreamReader($dlEntry.Open(), [System.Text.Encoding]::Unicode)
            [string]$dlStr = $srDl.ReadToEnd()
            $dlPart = $ctorStr.Invoke(@($dlStr, [string]"application/json"))
        }
    } finally {
        $zip.Dispose()
    }

    $pkg = $pkgCtor.Invoke(@(
        $null, $null, $null, $dmPart, $null, $null, $dlPart, $reportPart,
        $null, $metaPart, $settingsPart, $verPart, $null, $null, $null, $null,
        $null, $null, $null, $null, $null
    ))

    $fs = [System.IO.File]::Create($OutputPath)
    try {
        $saveMethod.Invoke($null, @($pkg, $fs, $true, $null, $true))
    } finally {
        $fs.Close()
    }
    Write-Output "SUCCESS_PBIX"
}
else {
    throw "Invalid Mode: $Mode"
}
