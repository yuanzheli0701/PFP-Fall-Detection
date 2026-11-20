<#
.SYNOPSIS
    Run the QUIDA fall-detection pipeline end to end.

.DESCRIPTION
    Uses the Anaconda Python installation (D:\Anaconda\python.exe) and runs the
    current phase in order:

        build_clean_dataset.py --overwrite
        verify_clean_dataset.py
        compare_four_models.py --protocol both
        report_four_models.py
        make_cleaning_figures.py --theme light

    Every step is logged to results\pipeline_<timestamp>.log.
    The historical preliminary baselines are not rerun by this script.

.PARAMETER SkipBuild
    Reuse the existing data_processed files instead of rebuilding them.

.PARAMETER SkipTraining
    Skip the 60-model comparison and only verify/report/plot existing results.

.PARAMETER SkipFigures
    Skip figure regeneration.

.EXAMPLE
    .\run_pipeline.ps1

.EXAMPLE
    .\run_pipeline.ps1 -SkipBuild -SkipTraining
#>
param(
    [switch]$SkipBuild,
    [switch]$SkipTraining,
    [switch]$SkipFigures
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$exp = Join-Path $root '02_Experiments\Current_Phase_Data_Cleaning_and_Baselines'
$python = 'D:\Anaconda\python.exe'
if (-not (Test-Path $python)) {
    $python = (Get-Command python -ErrorAction Stop).Source
}

$logDir = Join-Path $exp 'results'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ('pipeline_{0}.log' -f (Get-Date -Format 'yyyyMMdd_HHmmss'))

function Invoke-PythonStep {
    param(
        [string]$Label,
        [string[]]$StepArgs
    )
    Write-Host "`n=== $Label ===" -ForegroundColor Cyan
    & $python @StepArgs 2>&1 | Tee-Object -FilePath $log -Append
    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE. See $log"
    }
}

Push-Location $exp
try {
    Write-Host "QUIDA pipeline - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
    "QUIDA pipeline $(Get-Date -Format s)" | Tee-Object -FilePath $log
    "python: $python" | Tee-Object -FilePath $log -Append
    & $python -c "import sys, torch, sklearn, numpy; print('env:', sys.version.split()[0], 'torch', torch.__version__, 'sklearn', sklearn.__version__, 'numpy', numpy.__version__)" 2>&1 |
        Tee-Object -FilePath $log -Append

    $rawReady = Test-Path (Join-Path $exp 'data_raw\falls.csv')
    if (-not $SkipBuild -and -not $rawReady) {
        Write-Warning 'data_raw/ is not present (for example in a fresh clone); skipping the dataset build.'
        $SkipBuild = $true
    }
    if (-not $SkipBuild) {
        Invoke-PythonStep 'Build cleaned dataset' @('code\build_clean_dataset.py', '--overwrite')
    }
    Invoke-PythonStep 'Verify cleaned dataset' @('code\verify_clean_dataset.py')
    if (-not $SkipTraining) {
        Invoke-PythonStep 'Four-model comparison (window + LOSO)' @('code\compare_four_models.py', '--protocol', 'both')
    }
    Invoke-PythonStep 'Regenerate benchmark report' @('code\report_four_models.py')
    if (-not $SkipFigures) {
        Invoke-PythonStep 'Regenerate figures' @('code\make_cleaning_figures.py', '--theme', 'light')
    }

    Write-Host "`nPIPELINE OK" -ForegroundColor Green
    Write-Host "Log: $log"
}
finally {
    Pop-Location
}

