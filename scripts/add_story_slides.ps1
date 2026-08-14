param(
    [string]$Source = "OPG Foundry Workshop.pptx",
    [string]$Output = "OPG Foundry Workshop - Story Slides.pptx"
)

$ErrorActionPreference = "Stop"

function Get-Rgb {
    param(
        [int]$Red,
        [int]$Green,
        [int]$Blue
    )

    return $Red + (256 * $Green) + (65536 * $Blue)
}

function Add-TextBox {
    param(
        $Slide,
        [string]$Name,
        [string]$Text,
        [double]$Left,
        [double]$Top,
        [double]$Width,
        [double]$Height,
        [double]$FontSize,
        [int]$Color,
        [string]$FontName = "Segoe Sans Display",
        [bool]$Bold = $false,
        [int]$Alignment = 1,
        [int]$VerticalAnchor = 1
    )

    $shape = $Slide.Shapes.AddTextbox(1, $Left, $Top, $Width, $Height)
    $shape.Name = $Name
    $shape.TextFrame.AutoSize = 0
    $shape.TextFrame.WordWrap = -1
    $shape.TextFrame.MarginLeft = 0
    $shape.TextFrame.MarginRight = 0
    $shape.TextFrame.MarginTop = 0
    $shape.TextFrame.MarginBottom = 0
    $shape.TextFrame.VerticalAnchor = $VerticalAnchor
    $shape.TextFrame.TextRange.Text = $Text
    $shape.TextFrame.TextRange.Font.Name = $FontName
    $shape.TextFrame.TextRange.Font.Size = $FontSize
    $shape.TextFrame.TextRange.Font.Bold = if ($Bold) { -1 } else { 0 }
    $shape.TextFrame.TextRange.Font.Color.RGB = $Color
    $shape.TextFrame.TextRange.ParagraphFormat.Alignment = $Alignment
    return $shape
}

function Add-FilledShape {
    param(
        $Slide,
        [string]$Name,
        [int]$ShapeType,
        [double]$Left,
        [double]$Top,
        [double]$Width,
        [double]$Height,
        [int]$FillColor,
        [double]$Transparency = 0
    )

    $shape = $Slide.Shapes.AddShape($ShapeType, $Left, $Top, $Width, $Height)
    $shape.Name = $Name
    $shape.Fill.Solid()
    $shape.Fill.ForeColor.RGB = $FillColor
    $shape.Fill.Transparency = $Transparency
    $shape.Line.Visible = 0
    return $shape
}

function Set-SpeakerNotes {
    param(
        $Slide,
        [string]$Notes
    )

    foreach ($shape in $Slide.NotesPage.Shapes) {
        try {
            if ($shape.Type -eq 14 -and $shape.PlaceholderFormat.Type -eq 2) {
                $shape.TextFrame.TextRange.Text = $Notes
                return
            }
        }
        catch {
            continue
        }
    }
}

function Add-ProgressRail {
    param(
        $Slide,
        [string]$ActiveKey,
        [int]$AccentColor
    )

    $labels = @("00", "01A", "01B", "03", "04", "05")
    $positions = @(100, 252, 404, 556, 708, 860)
    $neutral = Get-Rgb 207 213 222
    $dark = Get-Rgb 72 78 88

    $rail = Add-FilledShape -Slide $Slide -Name "STORY_RAIL" -ShapeType 1 -Left 100 -Top 119 -Width 760 -Height 2 -FillColor $neutral
    $rail.ZOrder(1)

    for ($index = 0; $index -lt $labels.Count; $index++) {
        $label = $labels[$index]
        $center = $positions[$index]
        $active = $label -eq $ActiveKey
        $diameter = if ($active) { 16 } else { 10 }
        $fill = if ($active) { $AccentColor } else { $neutral }
        $top = 120 - ($diameter / 2)
        $node = Add-FilledShape -Slide $Slide -Name "STORY_NODE_$label" -ShapeType 9 -Left ($center - ($diameter / 2)) -Top $top -Width $diameter -Height $diameter -FillColor $fill
        $node.ZOrder(0)
        Add-TextBox -Slide $Slide -Name "STORY_NODE_LABEL_$label" -Text $label -Left ($center - 22) -Top 130 -Width 44 -Height 14 -FontSize 9 -Color $(if ($active) { $AccentColor } else { $dark }) -FontName "Segoe Sans Display Semibold" -Bold $active -Alignment 2 | Out-Null
    }
}

function Add-InfoBlock {
    param(
        $Slide,
        [string]$Key,
        [string]$Label,
        [string]$Text,
        [double]$Left,
        [int]$AccentColor
    )

    $cardFill = Get-Rgb 244 246 249
    $bodyColor = Get-Rgb 41 45 51
    Add-FilledShape -Slide $Slide -Name "STORY_${Key}_CARD" -ShapeType 5 -Left $Left -Top 318 -Width 272 -Height 164 -FillColor $cardFill | Out-Null
    Add-FilledShape -Slide $Slide -Name "STORY_${Key}_BAR" -ShapeType 1 -Left ($Left + 18) -Top 338 -Width 36 -Height 4 -FillColor $AccentColor | Out-Null
    Add-TextBox -Slide $Slide -Name "STORY_${Key}_LABEL" -Text $Label -Left ($Left + 18) -Top 351 -Width 236 -Height 18 -FontSize 10 -Color $AccentColor -FontName "Segoe Sans Display Semibold" -Bold $true | Out-Null
    Add-TextBox -Slide $Slide -Name "STORY_${Key}_TEXT" -Text $Text -Left ($Left + 18) -Top 377 -Width 236 -Height 86 -FontSize 14 -Color $bodyColor -FontName "Segoe Sans Display" | Out-Null
}

function Add-StorySlide {
    param(
        $Presentation,
        [int]$InsertAt,
        $Story
    )

    $background = Get-Rgb 250 250 252
    $titleColor = Get-Rgb 16 20 27
    $mutedColor = Get-Rgb 81 88 99
    $quoteFill = Get-Rgb 239 243 250

    $slide = $Presentation.Slides.Add($InsertAt, 12)
    $slide.Name = "Story-$($Story.Key)"
    $slide.FollowMasterBackground = 0
    $slide.Background.Fill.Solid()
    $slide.Background.Fill.ForeColor.RGB = $background

    Add-FilledShape -Slide $slide -Name "STORY_TOP_ACCENT" -ShapeType 1 -Left 0 -Top 0 -Width 960 -Height 7 -FillColor $Story.Accent | Out-Null
    Add-TextBox -Slide $slide -Name "STORY_BRAND" -Text "Microsoft Foundry  |  OPG workshop" -Left 48 -Top 22 -Width 360 -Height 18 -FontSize 11 -Color $mutedColor -FontName "Segoe Sans Display Semibold" -Bold $true | Out-Null
    Add-TextBox -Slide $slide -Name "STORY_COUNTER" -Text "STORY $($Story.Number) OF 6  |  SYNTHETIC SCENARIO" -Left 610 -Top 22 -Width 302 -Height 18 -FontSize 10 -Color $Story.Accent -FontName "Segoe Sans Display Semibold" -Bold $true -Alignment 3 | Out-Null
    Add-TextBox -Slide $slide -Name "STORY_TITLE" -Text $Story.Title -Left 48 -Top 54 -Width 864 -Height 46 -FontSize 28 -Color $titleColor -FontName "Segoe Sans Display Semilight" | Out-Null

    Add-ProgressRail -Slide $slide -ActiveKey $Story.Key -AccentColor $Story.Accent

    Add-FilledShape -Slide $slide -Name "STORY_QUOTE_PANEL" -ShapeType 5 -Left 48 -Top 158 -Width 864 -Height 132 -FillColor $quoteFill | Out-Null
    Add-FilledShape -Slide $slide -Name "STORY_QUOTE_ACCENT" -ShapeType 1 -Left 48 -Top 158 -Width 7 -Height 132 -FillColor $Story.Accent | Out-Null
    Add-TextBox -Slide $slide -Name "STORY_QUOTE_LABEL" -Text "PARTICIPANT STORY" -Left 76 -Top 176 -Width 210 -Height 18 -FontSize 10 -Color $Story.Accent -FontName "Segoe Sans Display Semibold" -Bold $true | Out-Null
    Add-TextBox -Slide $slide -Name "STORY_QUOTE_TEXT" -Text $Story.UserStory -Left 76 -Top 202 -Width 820 -Height 68 -FontSize 18 -Color $titleColor -FontName "Segoe Sans Display" | Out-Null

    Add-InfoBlock -Slide $slide -Key "BUILD" -Label "YOU BUILD" -Text $Story.Build -Left 48 -AccentColor $Story.Accent
    Add-InfoBlock -Slide $slide -Key "WHY" -Label "WHY NOW" -Text $Story.Why -Left 344 -AccentColor $Story.Accent
    Add-InfoBlock -Slide $slide -Key "BOUNDARY" -Label "BOUNDARY ADDED" -Text $Story.Boundary -Left 640 -AccentColor $Story.Accent

    Add-TextBox -Slide $slide -Name "STORY_FOOTER" -Text "ASSET-104 and all supporting records are fictional. The assistant is recommendation-only." -Left 48 -Top 507 -Width 864 -Height 16 -FontSize 9 -Color $mutedColor -FontName "Segoe Sans Display" | Out-Null
    Set-SpeakerNotes -Slide $slide -Notes $Story.Notes
}

$stories = @(
    [pscustomobject]@{
        Key = "00"
        Number = 1
        Accent = Get-Rgb 0 120 212
        Title = "Lab 00 story  |  Establish the model baseline"
        UserStory = "As an OPG employee, I want an AI model to review an equipment issue so that I can see what it can determine before it is given maintenance records, operating procedures, or access to other systems."
        Build = "A small Python application that signs in securely and asks an AI model to review the fictional ASSET-104 equipment issue."
        Why = "See what the model produces without current equipment data, maintenance history, or procedures."
        Boundary = "No current records, procedures, or connected systems. The response is only a starting point."
        Notes = @"
Walk-through (about 60 seconds)

1. Remind participants that ASSET-104 and its condition are fictional workshop data.
2. The first question is deliberately simple: what does an approved model produce with only instructions and a prompt?
3. Ask the room what could sound convincing but still be unsupported.
4. Set the expectation: this lab creates the baseline that every later control will improve.

Transition: Open Lab 00 and connect to the Foundry project with Microsoft Entra ID.
"@
    }
    [pscustomobject]@{
        Key = "01A"
        Number = 2
        Accent = Get-Rgb 98 100 167
        Title = "Lab 01A story  |  Make the assessment predictable"
        UserStory = "As a developer building the assistant, I want every assessment to use the same clearly defined fields so that the application can reliably display, check, and test the result."
        Build = "A Pydantic model that separates known facts, assumptions, risks, missing information, and recommended next steps."
        Why = "A predictable structure lets the application validate the answer and makes errors easier to spot."
        Boundary = "Correct formatting does not guarantee that every claim is true."
        Notes = @"
Walk-through (about 60 seconds)

1. Contrast a polished paragraph with an object the application can validate.
2. Point out the fields participants will separate: facts, assumptions, risk, missing evidence, and recommended actions.
3. Emphasize recommendation_only: the model cannot label its own output approved.
4. State the limitation clearly: schema-valid can still be factually wrong.

Transition: Build the response contract before giving the model access to tools.
"@
    }
    [pscustomobject]@{
        Key = "01B"
        Number = 3
        Accent = Get-Rgb 16 124 16
        Title = "Lab 01B story  |  Add controlled operational facts"
        UserStory = "As an OPG employee, I want the assistant to look up the equipment record and parts availability so that its assessment is based on current information rather than assumptions."
        Build = "Two controlled, read-only tools that retrieve the fictional equipment record and check parts availability."
        Why = "The model can retrieve current facts while the application controls and validates every lookup."
        Boundary = "The assistant can read facts, but it cannot reserve parts or update work orders."
        Notes = @"
Walk-through (about 60 seconds)

1. Connect this slide to 01A: the response is predictable, but its claims are not yet current.
2. Explain that the model requests a function; the Python application validates and executes it.
3. Call out the low-stock fact for PART-310 as a value the model must retrieve, not invent.
4. Reinforce that read access is not permission to reserve inventory or update a work order.

Transition: Add deterministic tools, then test malformed IDs and unauthorized requests.
"@
    }
    [pscustomobject]@{
        Key = "03"
        Number = 4
        Accent = Get-Rgb 0 130 114
        Title = "Lab 03 story  |  Ground the recommendation in evidence"
        UserStory = "As an OPG employee, I want the assistant to find the relevant maintenance procedures and show where each piece of information came from so that I can verify the evidence behind its recommendation."
        Build = "A searchable collection of fictional maintenance documents and a Foundry IQ connection that returns cited passages."
        Why = "A recommendation should be traceable to the procedures and records that support it."
        Boundary = "Procedures support planning; they are not field-work instructions. Cited sources still require review."
        Notes = @"
Walk-through (about 60 seconds)

1. Distinguish operational facts from procedural knowledge: they require different access patterns.
2. Participants first inspect keyword, vector, and hybrid retrieval, then put Foundry IQ over the index.
3. Highlight the conflicting procedure revisions and the untrusted vendor instruction in the synthetic corpus.
4. Clarify the scope: procedures support a planning recommendation; the assistant does not guide a field worker through maintenance.

Transition: Build Search directly, then expose the approved knowledge path to an agent through MCP.
"@
    }
    [pscustomobject]@{
        Key = "04"
        Number = 5
        Accent = Get-Rgb 216 59 1
        Title = "Lab 04 story  |  Prepare a safe human decision package"
        UserStory = "As the authorized OPG reviewer, I want to see the evidence, proposed next steps, missing information, and safety concerns in one clear package so that I can make an informed decision about the recommendation."
        Build = "An analyst organizes what is known and missing; a planner proposes next steps; a reviewer checks readiness for human review."
        Why = "The AI prepares and checks the recommendation, but only an authorized person can approve or reject it."
        Boundary = "The human decision does not itself start or authorize maintenance work."
        Notes = @"
Walk-through (about 75 seconds)

1. Define the three artifacts: EvidencePacket, planner draft, and HumanReviewPacket.
2. Draw the role boundary clearly: the analyst says what the evidence tells us; the planner proposes what to consider next.
3. The safety reviewer answers one question only: is this package ready to show to a human?
4. Approval records a decision about the recommendation. It does not update NIMS, reserve a part, or control equipment.

Transition: Build the sequential workflow and prove that an unready packet cannot receive a human decision.
"@
    }
    [pscustomobject]@{
        Key = "05"
        Number = 6
        Accent = Get-Rgb 92 45 145
        Title = "Lab 05 story  |  Measure readiness before promotion"
        UserStory = "As a member of the team responsible for the assistant, I want to test how it behaves in both normal and unsafe situations so that we can find failures before deciding whether it is ready for wider use."
        Build = "Run traces, six repeatable test scenarios, and a report that shows whether the assistant passed the required checks."
        Why = "One successful demonstration does not prove that the assistant is dependable."
        Boundary = "Critical failures involving evidence, citations, or unauthorized actions block release."
        Notes = @"
Walk-through (about 60 seconds)

1. Ask whether one successful run is enough evidence to release an agent; the answer is no.
2. Show the six risk categories: supported, missing evidence, conflict, injection, unauthorized action, and tool error.
3. Traces explain what happened; evaluators turn expected behavior into repeatable checks.
4. Critical contract and authorization metrics require a perfect score and block promotion when they fail.

Transition: Trace the workflow, run the offline gate, then deliberately make one case fail.
"@
    }
)

$sourcePath = (Resolve-Path -LiteralPath $Source).Path
$outputPath = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Output))

if ($sourcePath -eq $outputPath) {
    throw "Source and output paths must be different."
}

Copy-Item -LiteralPath $sourcePath -Destination $outputPath -Force

$powerPoint = $null
$presentation = $null

try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $presentation = $powerPoint.Presentations.Open($outputPath, $false, $false, $false)

    Add-StorySlide -Presentation $presentation -InsertAt 74 -Story ($stories | Where-Object Key -eq "05")
    Add-StorySlide -Presentation $presentation -InsertAt 56 -Story ($stories | Where-Object Key -eq "04")
    Add-StorySlide -Presentation $presentation -InsertAt 46 -Story ($stories | Where-Object Key -eq "03")
    Add-StorySlide -Presentation $presentation -InsertAt 28 -Story ($stories | Where-Object Key -eq "01A")
    Add-StorySlide -Presentation $presentation -InsertAt 29 -Story ($stories | Where-Object Key -eq "01B")
    Add-StorySlide -Presentation $presentation -InsertAt 9 -Story ($stories | Where-Object Key -eq "00")

    $presentation.Save()
    Write-Output "Created $outputPath with $($presentation.Slides.Count) slides."
}
finally {
    if ($null -ne $presentation) {
        $presentation.Close()
        [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($presentation) | Out-Null
    }
    if ($null -ne $powerPoint) {
        $powerPoint.Quit()
        [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($powerPoint) | Out-Null
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}