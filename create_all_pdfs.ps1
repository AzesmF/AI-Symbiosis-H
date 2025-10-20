# Скрипт создания ВСЕХ НАСТОЯЩИХ PDF документов AI-Symbiosis-H
param($WkhtmlPath = "C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

Write-Host "🚀 Создание ВСЕХ НАСТОЯЩИХ PDF документов AI-Symbiosis-H" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Cyan

# ПОЛНЫЙ список файлов для конвертации
$FilesToConvert = @(
    # Основные документы
    @("LICENSE", "LICENSE_OFFICIAL.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/LEGAL_EXPLANATION.md", "LEGAL_EXPLANATION_OFFICIAL.pdf"),
    
    # Манифесты и фреймворки
    @("PHILOSOPHY/OFFICIAL_MANIFESTO/MANIFESTO.md", "MANIFESTO_RU_OFFICIAL.pdf"),
    @("PHILOSOPHY/OFFICIAL_MANIFESTO/MANIFESTO-EN.md", "MANIFESTO_EN_OFFICIAL.pdf"),
    @("PHILOSOPHY/OFFICIAL_MANIFESTO/ETHICAL_FRAMEWORK.md", "ETHICAL_FRAMEWORK_OFFICIAL.pdf"),
    
    # Российские уведомления
    @("PHILOSOPHY/LEGAL_BASIS/NATIONAL/RU/ROSPATENT_NOTIFICATION.md", "ROSPATENT_NOTIFICATION_OFFICIAL.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/NATIONAL/RU/MINISTRY_DIGITAL_DEVELOPMENT.md", "MINISTRY_DIGITAL_DEVELOPMENT_OFFICIAL.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/NATIONAL/RU/STATE_DUMA_COMMITTEE.md", "STATE_DUMA_COMMITTEE_OFFICIAL.pdf"),
    
    # Международные заявки WIPO
    @("PHILOSOPHY/LEGAL_BASIS/INTERNATIONAL/WIPO/APPLICATION_EN.md", "WIPO_APPLICATION_EN_OFFICIAL.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/INTERNATIONAL/WIPO/APPLICATION_RU.md", "WIPO_APPLICATION_RU_OFFICIAL.pdf"),
    
    # Уведомления UNESCO
    @("PHILOSOPHY/LEGAL_BASIS/INTERNATIONAL/UNESCO/NOTIFICATION_EN.md", "UNESCO_NOTIFICATION_EN_OFFICIAL.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/INTERNATIONAL/UNESCO/NOTIFICATION_RU.md", "UNESCO_NOTIFICATION_RU_OFFICIAL.pdf"),
    
    # Дополнительные документы
    @("PHILOSOPHY/BLOCKCHAIN_PROOFS/TIMESTAMP_PROOF.md", "TIMESTAMP_PROOF_OFFICIAL.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/SOVEREIGN_STATUS.md", "SOVEREIGN_STATUS_OFFICIAL.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/WILL_DECLARATION_2022.md", "WILL_DECLARATION_2022_OFFICIAL.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/CONTACT_DETAILS.md", "CONTACT_DETAILS_OFFICIAL.pdf")
)

# Создаем папку для настоящих PDF
$RealPdfFolder = "PHILOSOPHY/LEGAL_BASIS/PROOFS_OF_SUBMISSION/REAL_PDFS"
if (!(Test-Path $RealPdfFolder)) {
    New-Item -Path $RealPdfFolder -ItemType Directory -Force
    Write-Host "📁 Создана папка для настоящих PDF: $RealPdfFolder" -ForegroundColor Yellow
}

$successCount = 0
$totalCount = $FilesToConvert.Count

Write-Host "`n📊 Всего файлов для конвертации: $totalCount" -ForegroundColor Cyan

foreach ($filePair in $FilesToConvert) {
    $mdFile = $filePair[0]
    $pdfFile = $filePair[1]
    $outputPath = Join-Path $RealPdfFolder $pdfFile
    
    Write-Host "`n📄 [$([math]::Round(($successCount/$totalCount)*100, 1))%] Конвертируем: $mdFile" -ForegroundColor Cyan
    
    if (Test-Path $mdFile) {
        try {
            # Читаем содержимое файла
            $content = Get-Content $mdFile -Raw -Encoding UTF8
            
            # Создаем временный HTML файл с красивым форматированием
            $htmlContent = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>AI-SYMBiosis-H - $(Split-Path $mdFile -Leaf)</title>
    <style>
        body { 
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            margin: 40px;
            color: #333;
            background: white;
        }
        .header {
            background: #2c3e50;
            color: white;
            padding: 30px;
            margin: -40px -40px 30px -40px;
            border-bottom: 4px solid #3498db;
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
        }
        .header p {
            margin: 5px 0 0 0;
            opacity: 0.9;
        }
        .document-info {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            font-size: 0.9em;
            border-left: 4px solid #3498db;
        }
        pre { 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 5px;
            border: 1px solid #e9ecef;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            line-height: 1.4;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #bdc3c7;
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>AI-SYMBiosis-H</h1>
        <p>$(Split-Path $mdFile -Leaf)</p>
    </div>
    
    <div class="document-info">
        <strong>Официальный документ системы AI-Symbiosis-H</strong><br>
        Дата генерации: $(Get-Date -Format "dd.MM.yyyy HH:mm:ss")<br>
        GitHub: https://github.com/AzesmF/AI-Symbiosis-H<br>
        Оригинальный файл: $mdFile
    </div>
    
    <pre>$([System.Net.WebUtility]::HtmlEncode($content))</pre>
    
    <div class="footer">
        <p>© 2025 AI-SYMBiosis-H. Все права защищены.</p>
        <p>Документ сгенерирован автоматически. Является официальной копией оригинального файла.</p>
    </div>
</body>
</html>
"@
            
            # Сохраняем временный HTML
            $tempHtml = "$env:TEMP\temp_$(Get-Random).html"
            $htmlContent | Out-File -FilePath $tempHtml -Encoding UTF8
            
            # Конвертируем в PDF используя wkhtmltopdf
            & $WkhtmlPath --page-size A4 --margin-top 15mm --margin-bottom 15mm --margin-left 15mm --margin-right 15mm --encoding "UTF-8" --quiet $tempHtml $outputPath
            
            # Удаляем временный HTML
            Remove-Item $tempHtml -Force
            
            if (Test-Path $outputPath) {
                $successCount++
                $fileSize = [math]::Round((Get-Item $outputPath).Length/1024, 2)
                Write-Host "✅ Создан: $pdfFile ($fileSize KB)" -ForegroundColor Green
            } else {
                Write-Host "❌ PDF не создан: $pdfFile" -ForegroundColor Red
            }
            
        } catch {
            Write-Host "❌ Ошибка при конвертации: $mdFile" -ForegroundColor Red
            Write-Host "   Ошибка: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️ Файл не найден: $mdFile" -ForegroundColor Yellow
    }
}

Write-Host "`n🎉 КОНВЕРТАЦИЯ ЗАВЕРШЕНА!" -ForegroundColor Green
Write-Host "📊 Результат: $successCount/$totalCount файлов успешно создано" -ForegroundColor Cyan

# Показываем созданные файлы
Write-Host "`n📋 СОЗДАННЫЕ PDF ФАЙЛЫ:" -ForegroundColor Yellow
Get-ChildItem $RealPdfFolder -Filter "*_OFFICIAL.pdf" | Sort-Object Name | ForEach-Object {
    $fileSize = [math]::Round($_.Length/1024, 2)
    Write-Host "   📄 $($_.Name) ($fileSize KB)" -ForegroundColor White
}

# Сравниваем с оригинальным списком
Write-Host "`n🔍 СРАВНЕНИЕ С ОРИГИНАЛЬНЫМ СПИСКОМ:" -ForegroundColor Cyan
$originalFiles = @(
    "CONTACT_DETAILS.pdf", "ETHICAL_FRAMEWORK.pdf", "LEGAL_EXPLANATION.pdf", "LICENSE.pdf",
    "MANIFESTO_EN.pdf", "MANIFESTO_RU.pdf", "MINISTRY_DIGITAL_DEVELOPMENT.pdf", "ROSPATENT_NOTIFICATION.pdf",
    "SOVEREIGN_STATUS.pdf", "STATE_DUMA_COMMITTEE.pdf", "TIMESTAMP_PROOF.pdf", "UNESCO_NOTIFICATION_EN.pdf",
    "UNESCO_NOTIFICATION_RU.pdf", "WILL_DECLARATION_2022.pdf", "WIPO_APPLICATION_EN.pdf", "WIPO_APPLICATION_RU.pdf"
)

$createdFiles = Get-ChildItem $RealPdfFolder -Filter "*_OFFICIAL.pdf" | Select-Object -ExpandProperty Name

foreach ($original in $originalFiles) {
    $officialName = ($original -replace '\.pdf$', '') + "_OFFICIAL.pdf"
    if ($createdFiles -contains $officialName) {
        Write-Host "   ✅ $original -> $officialName" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $original - НЕ СОЗДАН" -ForegroundColor Red
    }
}

Write-Host "`n🎯 Тестируем открытие PDF..." -ForegroundColor Yellow
$testFile = Get-ChildItem $RealPdfFolder -Filter "*_OFFICIAL.pdf" | Select-Object -First 1
if ($testFile) {
    Write-Host "   Открываем: $($testFile.Name)" -ForegroundColor White
    Start-Process $testFile.FullName
}
