Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Split-MarkdownRow {
    param([Parameter(Mandatory)][AllowEmptyString()][string]$Line)

    $value = $Line.Trim()
    if ($value.StartsWith('|')) {
        $value = $value.Substring(1)
    }
    if ($value.EndsWith('|')) {
        $value = $value.Substring(0, $value.Length - 1)
    }

    $cells = [Collections.Generic.List[string]]::new()
    $buffer = [Text.StringBuilder]::new()
    $escaped = $false

    foreach ($character in $value.ToCharArray()) {
        if ($escaped) {
            if ($character -eq '|') {
                [void]$buffer.Append('|')
            }
            else {
                [void]$buffer.Append('\')
                [void]$buffer.Append($character)
            }
            $escaped = $false
        }
        elseif ($character -eq '\') {
            $escaped = $true
        }
        elseif ($character -eq '|') {
            $cells.Add($buffer.ToString().Trim())
            [void]$buffer.Clear()
        }
        else {
            [void]$buffer.Append($character)
        }
    }

    if ($escaped) {
        [void]$buffer.Append('\')
    }
    $cells.Add($buffer.ToString().Trim())
    return $cells.ToArray()
}

function Test-MarkdownSeparator {
    param([Parameter(Mandatory)][AllowEmptyString()][string]$Line)

    $cells = @(Split-MarkdownRow -Line $Line)
    if ($cells.Count -eq 0) {
        return $false
    }
    foreach ($cell in $cells) {
        if ($cell -notmatch '^\s*:?-{3,}:?\s*$') {
            return $false
        }
    }
    return $true
}

function Read-MarkdownTable {
    param(
        [Parameter(Mandatory)][string]$Path,
        [string[]]$RequiredHeaders = @()
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return @()
    }

    $lines = @(Get-Content -LiteralPath $Path -Encoding UTF8)
    $headerIndex = -1
    $headers = @()

    for ($index = 0; $index -lt ($lines.Count - 1); $index++) {
        if ($lines[$index] -notmatch '^\s*\|') {
            continue
        }
        if (-not (Test-MarkdownSeparator -Line $lines[$index + 1])) {
            continue
        }

        $candidateHeaders = @(Split-MarkdownRow -Line $lines[$index])
        $containsRequiredHeaders = $true
        foreach ($requiredHeader in $RequiredHeaders) {
            if ($candidateHeaders -notcontains $requiredHeader) {
                $containsRequiredHeaders = $false
                break
            }
        }
        if ($containsRequiredHeaders) {
            $headerIndex = $index
            $headers = $candidateHeaders
            break
        }
    }

    if ($headerIndex -lt 0) {
        return @()
    }

    $rows = [Collections.Generic.List[object]]::new()
    for ($index = $headerIndex + 2; $index -lt $lines.Count; $index++) {
        if ($lines[$index] -notmatch '^\s*\|') {
            break
        }
        $cells = @(Split-MarkdownRow -Line $lines[$index])
        if ($cells.Count -ne $headers.Count) {
            continue
        }

        $row = [ordered]@{}
        for ($column = 0; $column -lt $headers.Count; $column++) {
            $row[$headers[$column]] = $cells[$column]
        }
        $rows.Add([pscustomobject]$row)
    }

    return $rows.ToArray()
}

function Get-PropertyValue {
    param(
        [Parameter(Mandatory)]$Object,
        [Parameter(Mandatory)][string]$Name,
        [string]$Default = ''
    )

    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return $Default
    }
    return [string]$property.Value
}

function Copy-EdgeRow {
    param(
        [Parameter(Mandatory)]$Row,
        [Parameter(Mandatory)][string]$OwnerProject
    )

    return [pscustomobject][ordered]@{
        id = Get-PropertyValue $Row 'edge_id'
        fingerprint = Get-PropertyValue $Row 'fingerprint'
        type = Get-PropertyValue $Row 'type'
        source = Get-PropertyValue $Row 'source'
        ownerProject = $OwnerProject
        fromProject = Get-PropertyValue $Row 'from_project'
        fromAnchor = Get-PropertyValue $Row 'from_anchor'
        toProject = Get-PropertyValue $Row 'to_project'
        toAnchor = Get-PropertyValue $Row 'to_anchor'
        summary = Get-PropertyValue $Row 'contract_summary'
        verificationStatus = Get-PropertyValue $Row 'verification_status'
        lastVerified = Get-PropertyValue $Row 'last_verified'
    }
}

function Copy-CandidateRow {
    param(
        [Parameter(Mandatory)]$Row,
        [Parameter(Mandatory)][string]$OwnerProject
    )

    return [pscustomobject][ordered]@{
        id = Get-PropertyValue $Row 'candidate_id'
        fingerprint = Get-PropertyValue $Row 'candidate_fingerprint'
        relation = Get-PropertyValue $Row 'relation'
        type = (Get-PropertyValue $Row 'relation').Replace('-client', '').Replace('-callback', '').Replace('-publish', '').Replace('-subscribe', '').Replace('-read', '').Replace('-write', '').Replace('-consume', '').Replace('-use', '').Replace('-similar', '')
        source = Get-PropertyValue $Row 'source'
        ownerProject = $OwnerProject
        localAnchor = Get-PropertyValue $Row 'local_anchor'
        remoteProject = Get-PropertyValue $Row 'remote_project' 'unknown'
        remoteAnchor = Get-PropertyValue $Row 'remote_anchor' 'unknown-anchor'
        evidence = Get-PropertyValue $Row 'evidence'
        confidence = Get-PropertyValue $Row 'confidence'
        status = Get-PropertyValue $Row 'status'
        edgeId = Get-PropertyValue $Row 'edge_id'
        discoveredAt = Get-PropertyValue $Row 'discovered_at'
        lastSeen = Get-PropertyValue $Row 'last_seen'
    }
}

function Copy-ProposalRow {
    param(
        [Parameter(Mandatory)]$Row,
        [Parameter(Mandatory)][string]$OwnerProject
    )

    return [pscustomobject][ordered]@{
        id = Get-PropertyValue $Row 'proposal_id'
        sourceCandidateId = Get-PropertyValue $Row 'source_candidate_id'
        proposedEdgeId = Get-PropertyValue $Row 'proposed_edge_id'
        fingerprint = Get-PropertyValue $Row 'fingerprint'
        type = Get-PropertyValue $Row 'type'
        source = Get-PropertyValue $Row 'source'
        ownerProject = $OwnerProject
        fromProject = Get-PropertyValue $Row 'from_project'
        fromAnchor = Get-PropertyValue $Row 'from_anchor'
        toProject = Get-PropertyValue $Row 'to_project'
        toAnchor = Get-PropertyValue $Row 'to_anchor'
        summary = Get-PropertyValue $Row 'contract_summary'
        verificationStatus = Get-PropertyValue $Row 'verification_status'
        verificationEvidence = Get-PropertyValue $Row 'verification_evidence'
        proposedCrossRefId = Get-PropertyValue $Row 'proposed_cross_ref_id'
        proposedLocalEntry = Get-PropertyValue $Row 'proposed_local_entry'
        proposedWhyPinned = Get-PropertyValue $Row 'proposed_why_pinned'
        humanStatus = Get-PropertyValue $Row 'human_status'
        humanNote = Get-PropertyValue $Row 'human_note'
        createdAt = Get-PropertyValue $Row 'created_at'
        updatedAt = Get-PropertyValue $Row 'updated_at'
    }
}

function Get-GraphSnapshot {
    param(
        [Parameter(Mandatory)][string]$BaseRoot,
        [Parameter(Mandatory)][DateTimeOffset]$GeneratedAt
    )

    $wikiRoot = Join-Path $BaseRoot '.llm-wiki'
    $manifestPath = Join-Path $wikiRoot 'base-graph\manifest.json'
    $catalogPath = Join-Path $wikiRoot 'base-graph\project-catalog.md'
    $overviewPath = Join-Path $wikiRoot 'base-graph\overview.md'
    $registryPath = Join-Path $wikiRoot 'registry.local.json'

    $manifest = Get-Content -Raw -Encoding UTF8 -LiteralPath $manifestPath | ConvertFrom-Json
    $registry = Get-Content -Raw -Encoding UTF8 -LiteralPath $registryPath | ConvertFrom-Json
    $catalogRows = @(Read-MarkdownTable -Path $catalogPath -RequiredHeaders @('project_id', 'display_name', 'domain'))
    $flowRows = @(Read-MarkdownTable -Path $overviewPath -RequiredHeaders @('flow', 'projects', 'summary', 'evidence'))

    $projects = [Collections.Generic.List[object]]::new()
    $overviewFlows = [Collections.Generic.List[object]]::new()
    $edges = [Collections.Generic.List[object]]::new()
    $candidates = [Collections.Generic.List[object]]::new()
    $proposals = [Collections.Generic.List[object]]::new()

    foreach ($flowRow in $flowRows) {
        $overviewFlows.Add([pscustomobject][ordered]@{
            id = 'overview-' + ($overviewFlows.Count + 1)
            name = Get-PropertyValue $flowRow 'flow'
            projects = @((Get-PropertyValue $flowRow 'projects').Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_ })
            summary = Get-PropertyValue $flowRow 'summary'
            evidence = Get-PropertyValue $flowRow 'evidence'
            layer = 'overview'
            verificationStatus = 'overview-only'
        })
    }

    foreach ($catalogRow in $catalogRows) {
        $projectId = Get-PropertyValue $catalogRow 'project_id'
        $registryProperty = $registry.projects.PSObject.Properties |
            Where-Object Name -eq $projectId |
            Select-Object -First 1
        $registryMapped = $null -ne $registryProperty
        $projectRoot = if ($registryMapped) { [string]$registryProperty.Value } else { '' }
        $projectWiki = if ($projectRoot) { Join-Path $projectRoot '.llm-wiki' } else { '' }
        $graphRoot = if ($projectWiki) { Join-Path $projectWiki 'project-graph' } else { '' }
        $wikiInitialized = [bool]($projectWiki -and (Test-Path -LiteralPath $projectWiki))
        $graphStatus = if ($graphRoot -and (Test-Path -LiteralPath $graphRoot)) { 'initialized' } else { 'missing' }

        $projectEdges = @()
        $projectCandidates = @()
        $projectProposals = @()
        if ($graphStatus -eq 'initialized') {
            $projectEdges = @(Read-MarkdownTable -Path (Join-Path $graphRoot 'edges.md') -RequiredHeaders @('edge_id', 'from_project', 'to_project'))
            $projectCandidates = @(Read-MarkdownTable -Path (Join-Path $graphRoot 'candidates.md') -RequiredHeaders @('candidate_id', 'status'))
            $projectProposals = @(Read-MarkdownTable -Path (Join-Path $graphRoot 'proposals.md') -RequiredHeaders @('proposal_id', 'human_status'))

            foreach ($row in $projectEdges) {
                $edges.Add((Copy-EdgeRow -Row $row -OwnerProject $projectId))
            }
            foreach ($row in $projectCandidates) {
                $candidates.Add((Copy-CandidateRow -Row $row -OwnerProject $projectId))
            }
            foreach ($row in $projectProposals) {
                $proposals.Add((Copy-ProposalRow -Row $row -OwnerProject $projectId))
            }
        }

        $projects.Add([pscustomobject][ordered]@{
            id = $projectId
            displayName = Get-PropertyValue $catalogRow 'display_name'
            domain = Get-PropertyValue $catalogRow 'domain'
            owner = Get-PropertyValue $catalogRow 'owner'
            repo = Get-PropertyValue $catalogRow 'repo'
            status = Get-PropertyValue $catalogRow 'status'
            notes = Get-PropertyValue $catalogRow 'notes'
            registryMapped = $registryMapped
            wikiInitialized = $wikiInitialized
            graphStatus = $graphStatus
            edgeCount = $projectEdges.Count
            candidateCount = $projectCandidates.Count
            proposalCount = $projectProposals.Count
        })
    }

    return [ordered]@{
        meta = [ordered]@{
            generatedBy = 'scripts/build-graph-visualization.ps1'
            generatedAt = $GeneratedAt.ToString('o')
            partialView = $true
            factSource = 'project-local .llm-wiki/project-graph/edges.md'
            staleDays = [int]$manifest.default_stale_days
        }
        base = [ordered]@{
            graphId = [string]$manifest.graph_id
            name = [string]$manifest.name
            graphRole = [string]$manifest.graph_role
        }
        projects = $projects.ToArray()
        overviewFlows = $overviewFlows.ToArray()
        edges = $edges.ToArray()
        candidates = $candidates.ToArray()
        proposals = $proposals.ToArray()
        quality = [ordered]@{
            skippedRows = 0
            missingGraphProjects = @($projects | Where-Object graphStatus -eq 'missing').Count
        }
    }
}

function Assert-GraphSnapshot {
    param([Parameter(Mandatory)]$Snapshot)

    $duplicateEdges = @($Snapshot.edges | Group-Object ownerProject, id | Where-Object Count -gt 1)
    if ($duplicateEdges.Count -gt 0) {
        throw 'Duplicate ownerProject/edge id values detected.'
    }

    foreach ($edge in $Snapshot.edges) {
        if (-not $edge.id -or -not $edge.fromProject -or -not $edge.toProject) {
            throw 'Confirmed edge is missing an id or endpoint.'
        }
    }

    $serialized = $Snapshot | ConvertTo-Json -Depth 20 -Compress
    if ($serialized -match '[A-Za-z]:\\\\') {
        throw 'Snapshot contains a local absolute path.'
    }
}

Export-ModuleMember -Function Read-MarkdownTable, Get-GraphSnapshot, Assert-GraphSnapshot
