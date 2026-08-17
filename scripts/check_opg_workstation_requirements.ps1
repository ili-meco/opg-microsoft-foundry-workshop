Write-Host "===================================================="
Write-Host " OPG Microsoft Foundry Workshop - Workstation Check"
Write-Host "===================================================="
Write-Host ""

$failed = $false

function Pass($message) {
    Write-Host "[PASS] $message"
}

function Fail($message, $fix = "") {
    $script:failed = $true
    Write-Host "[FAIL] $message"
    if ($fix) {
        Write-Host "       FIX: $fix"
    }
}

# Visual Studio Code
if (Get-Command code -ErrorAction SilentlyContinue) {
    $version = (& code --version 2>$null | Select-Object -First 1)
    Pass "Visual Studio Code $version"
} else {
    Fail "Visual Studio Code not found" "Install the current stable version of VS Code."
}

# Python 3.11+
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python -c "import sys; print('.'.join(map(str, sys.version_info[:3])))"
    $pythonOkay = python -c "import sys; print(sys.version_info >= (3,11))"

    if ($pythonOkay -eq "True") {
        Pass "Python $pythonVersion"
    } else {
        Fail "Python $pythonVersion" "Python 3.11 or newer is required. Python 3.12 is recommended."
    }
} else {
    Fail "Python not found" "Install Python 3.11 or newer."
}

# Git
if (Get-Command git -ErrorAction SilentlyContinue) {
    Pass "$(git --version)"
} else {
    Fail "Git not found" "Install Git."
}

# Azure CLI
if (Get-Command az -ErrorAction SilentlyContinue) {
    Pass "Azure CLI"
} else {
    Fail "Azure CLI not found" "Install Azure CLI."
}

# Azure Developer CLI
if (Get-Command azd -ErrorAction SilentlyContinue) {
    $azdVersion = (azd version 2>$null | Select-Object -First 1)
    Pass "$azdVersion"
} else {
    Fail "Azure Developer CLI (azd) not found" "Install Azure Developer CLI (azd)."
}

# PowerShell 7
if (Get-Command pwsh -ErrorAction SilentlyContinue) {
    $psVersion = & pwsh -NoLogo -NoProfile -Command '$PSVersionTable.PSVersion.ToString()'
    Pass "PowerShell $psVersion"
} else {
    Fail "PowerShell 7 not found" "Install PowerShell 7."
}

# Workshop repository access
$repoUrl = "https://github.com/ili-meco/opg-microsoft-foundry-workshop.git"

if (Get-Command git -ErrorAction SilentlyContinue) {
    $repoCheck = git ls-remote $repoUrl HEAD 2>$null

    if ($LASTEXITCODE -eq 0 -and $repoCheck) {
        Pass "Workshop Git repository is accessible"
    } else {
        Fail "Workshop Git repository cannot be accessed" "Confirm GitHub/network access to the workshop repository."
    }
}

# VS Code Extensions
if (Get-Command code -ErrorAction SilentlyContinue) {

    $extensionOutput = & code --list-extensions --show-versions 2>$null

    if ($LASTEXITCODE -eq 0 -and $extensionOutput) {

        $extensions = @{}

        foreach ($line in $extensionOutput) {
            if ($line -match '^([^@]+)@(.+)$') {
                $extensions[$matches[1].ToLower()] = $matches[2]
            }
        }

        $requiredExtensions = @(
            @{
                Id = "ms-python.python"
                Name = "Microsoft Python extension"
            },
            @{
                Id = "ms-python.vscode-pylance"
                Name = "Pylance"
            },
            @{
                Id = "ms-azuretools.vscode-azureresourcegroups"
                Name = "Azure Resources extension"
            },
            @{
                Id = "ms-windows-ai-studio.windows-ai-studio"
                Name = "Microsoft Foundry Toolkit"
            }
        )

        foreach ($ext in $requiredExtensions) {

            $id = $ext.Id.ToLower()

            if ($extensions.ContainsKey($id)) {
                Pass "$($ext.Name) $($extensions[$id])"
            } else {
                Fail "$($ext.Name) not installed" "Install VS Code extension: $($ext.Id)"
            }
        }

    } else {
        Fail "Could not check VS Code extensions" "Open VS Code once, restart the terminal, and run the check again."
    }
}

# Port 4317 for Foundry Toolkit / OpenTelemetry
try {
    $listener = [System.Net.Sockets.TcpListener]::new(
        [System.Net.IPAddress]::Loopback,
        4317
    )

    $listener.Start()
    $listener.Stop()

    Pass "Port 4317 is available for Foundry Toolkit OpenTelemetry traces"
}
catch {
    # If something is already listening on 4317, that may also be valid
    $existing = Get-NetTCPConnection -LocalPort 4317 -State Listen -ErrorAction SilentlyContinue

    if ($existing) {
        Pass "Port 4317 is currently in use by a local listener"
    } else {
        Fail "Port 4317 is unavailable" "Check whether another application or security policy is blocking port 4317."
    }
}

Write-Host ""
Write-Host "===================================================="

if ($failed) {
    Write-Host "RESULT: NOT READY FOR THE WORKSHOP"
    Write-Host "Fix the FAIL items above before attending."
    exit 1
}
else {
    Write-Host "RESULT: READY FOR THE WORKSHOP"
    Write-Host "All required workstation tools are installed."
    Write-Host "Python packages will be handled inside the workshop virtual environment."
    exit 0
}
