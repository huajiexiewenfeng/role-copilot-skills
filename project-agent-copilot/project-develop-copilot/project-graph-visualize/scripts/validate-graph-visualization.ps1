param(
    [Parameter(Mandatory)][string]$BaseRoot,
    [Parameter(Mandatory)][string]$HtmlPath
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$resolvedBaseRoot = (Resolve-Path -LiteralPath $BaseRoot).Path
$resolvedHtmlPath = (Resolve-Path -LiteralPath $HtmlPath).Path
$modulePath = Join-Path $PSScriptRoot 'GraphVisualization.psm1'

Import-Module $modulePath -Force
$snapshot = Get-GraphSnapshot `
    -BaseRoot $resolvedBaseRoot `
    -GeneratedAt ([DateTimeOffset]::Now)
Assert-GraphSnapshot -Snapshot $snapshot

$html = Get-Content -Raw -Encoding UTF8 -LiteralPath $resolvedHtmlPath
$bytes = [IO.File]::ReadAllBytes($resolvedHtmlPath)
$errors = [Collections.Generic.List[string]]::new()

function Add-ErrorIf {
    param([bool]$Condition, [string]$Message)
    if ($Condition) {
        $errors.Add($Message)
    }
}

Add-ErrorIf ($bytes.Length -lt 1024) 'HTML output is unexpectedly small.'
Add-ErrorIf ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) 'HTML contains a UTF-8 BOM.'
Add-ErrorIf ($html.Contains('__GRAPH_DATA__')) 'Graph data placeholder was not replaced.'
Add-ErrorIf ($html.Contains('__GENERATED_AT__')) 'Generated-at placeholder was not replaced.'
Add-ErrorIf ($html.Contains('__GRAPH_NAME__')) 'Graph-name placeholder was not replaced.'
Add-ErrorIf ($html.Contains('fetch(')) 'HTML must not use fetch.'
Add-ErrorIf ($html.Contains('XMLHttpRequest')) 'HTML must not use XMLHttpRequest.'
Add-ErrorIf ($html.Contains('WebSocket')) 'HTML must not use WebSocket.'
Add-ErrorIf (-not $html.Contains('"partialView":true')) 'HTML must declare partialView=true.'
Add-ErrorIf (-not $html.Contains('function setView(')) 'HTML is missing view switching.'
Add-ErrorIf (-not $html.Contains('function getVisibleRelations(')) 'HTML is missing relation filtering.'

$registryPath = Join-Path $resolvedBaseRoot '.llm-wiki\registry.local.json'
$registry = Get-Content -Raw -Encoding UTF8 -LiteralPath $registryPath | ConvertFrom-Json
foreach ($property in $registry.projects.psobject.Properties) {
    Add-ErrorIf ($html.Contains([string]$property.Value)) "Local path leaked for project $($property.Name)."
}

$dataMatch = [regex]::Match(
    $html,
    '(?s)const graphData = (?<json>\{.*\});\s+const svg ='
)
Add-ErrorIf (-not $dataMatch.Success) 'Inline graph data could not be located.'

if ($dataMatch.Success) {
    $jsonText = $dataMatch.Groups['json'].Value
    $actual = $jsonText | ConvertFrom-Json

    foreach ($propertyName in @('projects', 'edges', 'candidates', 'proposals', 'overviewFlows')) {
        $expectedItems = @($snapshot[$propertyName])
        $actualItems = @($actual.$propertyName)
        Add-ErrorIf ($actualItems.Count -ne $expectedItems.Count) "Snapshot count mismatch for $propertyName."
    }

    $expectedEdgeKeys = @($snapshot.edges | ForEach-Object { "$($_.ownerProject)|$($_.id)" } | Sort-Object)
    $actualEdgeKeys = @($actual.edges | ForEach-Object { "$($_.ownerProject)|$($_.id)" } | Sort-Object)
    Add-ErrorIf (($expectedEdgeKeys -join "`n") -ne ($actualEdgeKeys -join "`n")) 'Confirmed edge identities do not match source data.'
}

if ($errors.Count -gt 0) {
    throw ($errors -join [Environment]::NewLine)
}

[pscustomobject]@{
    status = 'PASS'
    html_path = $resolvedHtmlPath
    projects = $snapshot.projects.Count
    confirmed_edges = $snapshot.edges.Count
    candidates = $snapshot.candidates.Count
    proposals = $snapshot.proposals.Count
    missing_graph_projects = @($snapshot.projects | Where-Object graphStatus -eq 'missing').Count
}
