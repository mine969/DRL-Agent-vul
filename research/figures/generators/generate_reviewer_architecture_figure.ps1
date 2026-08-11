$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Drawing

$outputPath = 'D:\github\DRL Agents\DQN web vul\research\D3QN_vuln_finder_reviewer_fixed.png'

$bitmap = New-Object System.Drawing.Bitmap 1600, 1000
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$graphics.Clear([System.Drawing.Color]::White)

$titleFont = New-Object System.Drawing.Font('Times New Roman', 28, [System.Drawing.FontStyle]::Bold)
$boxFont = New-Object System.Drawing.Font('Times New Roman', 22, [System.Drawing.FontStyle]::Regular)
$smallFont = New-Object System.Drawing.Font('Times New Roman', 18, [System.Drawing.FontStyle]::Regular)

$textBrush = [System.Drawing.Brushes]::Black
$fillBrush = [System.Drawing.Brushes]::White
$borderPen = New-Object System.Drawing.Pen([System.Drawing.Color]::Black, 2)
$arrowPen = New-Object System.Drawing.Pen([System.Drawing.Color]::Black, 3)
$arrowPen.EndCap = [System.Drawing.Drawing2D.LineCap]::ArrowAnchor

function Draw-Box {
    param(
        [int]$X,
        [int]$Y,
        [int]$Width,
        [int]$Height,
        [string]$Text,
        [System.Drawing.Font]$Font
    )

    $rect = New-Object System.Drawing.RectangleF($X, $Y, $Width, $Height)
    $graphics.FillRectangle($fillBrush, $rect)
    $graphics.DrawRectangle($borderPen, $X, $Y, $Width, $Height)

    $format = New-Object System.Drawing.StringFormat
    $format.Alignment = [System.Drawing.StringAlignment]::Center
    $format.LineAlignment = [System.Drawing.StringAlignment]::Center
    $graphics.DrawString($Text, $Font, $textBrush, $rect, $format)
}

$graphics.DrawString(
    'System Architecture of the Proposed RL-Based Web Vulnerability Scanner',
    $titleFont,
    $textBrush,
    80,
    25
)

Draw-Box 480 110 640 90 'Mock Web Applications: E-Commerce | Social Media | Banking | Blog | File Share' $boxFont
Draw-Box 150 300 520 220 "WebSecurityGym Environment`n`n- Crawls endpoints and forms`n- Encodes HTTP feedback into a fixed state vector`n- Executes payload actions against the target" $smallFont
Draw-Box 930 300 520 220 "Extended D3QN Agent`n`n- Double Q-learning and dueling heads`n- Prioritized replay and noisy exploration`n- Multi-step returns for delayed reward propagation" $smallFont
Draw-Box 480 620 640 110 "Phase-Based Curriculum`nReconnaissance -> Assessment -> Exploitation" $boxFont
Draw-Box 560 820 480 90 'Confirmed Findings and Scan Report' $boxFont

$graphics.DrawLine($arrowPen, 800, 200, 800, 300)
$graphics.DrawLine($arrowPen, 670, 410, 930, 410)
$graphics.DrawLine($arrowPen, 930, 430, 670, 430)
$graphics.DrawString('state, reward', $smallFont, $textBrush, 690, 360)
$graphics.DrawString('action', $smallFont, $textBrush, 760, 442)
$graphics.DrawLine($arrowPen, 410, 520, 410, 675)
$graphics.DrawLine($arrowPen, 1190, 520, 1190, 675)
$graphics.DrawLine($arrowPen, 410, 675, 480, 675)
$graphics.DrawLine($arrowPen, 1190, 675, 1120, 675)
$graphics.DrawLine($arrowPen, 800, 730, 800, 820)

$bitmap.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)

$graphics.Dispose()
$bitmap.Dispose()

Write-Output $outputPath
