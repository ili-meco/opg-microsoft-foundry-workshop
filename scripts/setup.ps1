$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Push-Location $repoRoot

try {
    if (-not (Test-Path ".venv")) {
        python -m venv .venv
    }

    $python = Join-Path $repoRoot ".venv\Scripts\python.exe"
    & $python -m pip install --upgrade pip
    & $python -m pip install -r requirements.txt

    if (-not (Test-Path ".env")) {
        Copy-Item ".env.example" ".env"
        Write-Host "Created .env. Add the instructor-provided Foundry values before Lab 00."
    }

    & $python scripts\verify_setup.py
}
finally {
    Pop-Location
}
