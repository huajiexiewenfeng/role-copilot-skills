param(
    [Parameter(Mandatory)][string]$BaseRoot,
    [string]$OutputPath = '',
    [string]$GeneratedAt = ([DateTimeOffset]::Now.ToString('o'))
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$resolvedBaseRoot = (Resolve-Path -LiteralPath $BaseRoot).Path
$manifestPath = Join-Path $resolvedBaseRoot '.llm-wiki\base-graph\manifest.json'
if (-not (Test-Path -LiteralPath $manifestPath)) {
    throw "Not a Base Graph root: missing $manifestPath"
}

$manifest = Get-Content -Raw -Encoding UTF8 -LiteralPath $manifestPath | ConvertFrom-Json
if ([string]$manifest.graph_role -ne 'base') {
    throw "Not a Base Graph root: graph_role must be 'base'."
}

$skillRoot = Split-Path -Parent $PSScriptRoot
$modulePath = Join-Path $PSScriptRoot 'GraphVisualization.psm1'
$templatePath = Join-Path $skillRoot 'assets\template.html'
if (-not $OutputPath) {
    $OutputPath = Join-Path $resolvedBaseRoot '.llm-wiki\base-graph\graph.html'
}
elseif (-not [IO.Path]::IsPathRooted($OutputPath)) {
    $OutputPath = Join-Path $resolvedBaseRoot $OutputPath
}

Import-Module $modulePath -Force
$snapshot = Get-GraphSnapshot `
    -BaseRoot $resolvedBaseRoot `
    -GeneratedAt ([DateTimeOffset]$GeneratedAt)
Assert-GraphSnapshot -Snapshot $snapshot

$json = $snapshot | ConvertTo-Json -Depth 20 -Compress
$json = $json.Replace('</script', '<\/script')
$template = Get-Content -Raw -Encoding UTF8 -LiteralPath $templatePath
$graphName = [string]$snapshot.base.name
$output = $template.
    Replace('__GRAPH_DATA__', $json).
    Replace('__GENERATED_AT__', $snapshot.meta.generatedAt).
    Replace('__GRAPH_NAME__', $graphName)

$outputDirectory = Split-Path -Parent $OutputPath
if (-not (Test-Path -LiteralPath $outputDirectory)) {
    [void](New-Item -ItemType Directory -Force -Path $outputDirectory)
}
[IO.File]::WriteAllText($OutputPath, $output, [Text.UTF8Encoding]::new($false))

[pscustomobject]@{
    output_path = $OutputPath
    projects = $snapshot.projects.Count
    confirmed_edges = $snapshot.edges.Count
    candidates = $snapshot.candidates.Count
    proposals = $snapshot.proposals.Count
    missing_graph_projects = @($snapshot.projects | Where-Object graphStatus -eq 'missing').Count
}
