param(
    [Parameter(Mandatory)][string]$BaseRoot
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$skillRoot = Split-Path -Parent $PSScriptRoot
$outputPath = Join-Path $env:TEMP 'project-graph-visualize-skill-smoke.html'
$assertions = 0

function Assert-True {
    param([bool]$Condition, [string]$Message)
    $script:assertions++
    if (-not $Condition) {
        throw "ASSERTION FAILED: $Message"
    }
}

function Assert-Contains {
    param([string]$Text, [string]$Needle, [string]$Message)
    Assert-True -Condition $Text.Contains($Needle) -Message $Message
}

$requiredFiles = @(
    'SKILL.md',
    'scripts\build-graph-visualization.ps1',
    'scripts\GraphVisualization.psm1',
    'scripts\validate-graph-visualization.ps1',
    'assets\template.html',
    'evals\evals.json'
)

foreach ($relativePath in $requiredFiles) {
    Assert-True `
        -Condition (Test-Path -LiteralPath (Join-Path $skillRoot $relativePath)) `
        -Message "Skill contains $relativePath"
}

$skillText = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $skillRoot 'SKILL.md')
Assert-Contains $skillText 'name: project-graph-visualize' 'Skill name is stable'
Assert-Contains $skillText 'Use when' 'Description has trigger language'
Assert-Contains $skillText 'Mechanical generation mode' 'Skill declares mechanical generation mode'
Assert-Contains $skillText 'Do not create Change Brief' 'Skill prevents lifecycle-document expansion'

& (Join-Path $skillRoot 'scripts\build-graph-visualization.ps1') `
    -BaseRoot $BaseRoot `
    -OutputPath $outputPath | Out-Null

& (Join-Path $skillRoot 'scripts\validate-graph-visualization.ps1') `
    -BaseRoot $BaseRoot `
    -HtmlPath $outputPath | Out-Null

$html = Get-Content -Raw -Encoding UTF8 -LiteralPath $outputPath
$manifest = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $BaseRoot '.llm-wiki\base-graph\manifest.json') |
    ConvertFrom-Json
$registry = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $BaseRoot '.llm-wiki\registry.local.json') |
    ConvertFrom-Json

Assert-Contains $html ([string]$manifest.name) 'Generated title comes from Base manifest'
Assert-True (-not $html.Contains('__GRAPH_DATA__')) 'Graph data placeholder is resolved'
Assert-True (-not $html.Contains('__GRAPH_NAME__')) 'Graph name placeholder is resolved'
Assert-True (-not $html.Contains('fetch(')) 'Generated HTML is offline'
foreach ($property in $registry.projects.psobject.Properties) {
    Assert-True `
        -Condition (-not $html.Contains([string]$property.Value)) `
        -Message "Generated HTML hides local path for $($property.Name)"
}

Write-Output "PASS: $assertions project-graph-visualize skill assertions"
