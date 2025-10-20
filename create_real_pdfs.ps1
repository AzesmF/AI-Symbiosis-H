# Скрипт создания НАСТОЯЩИХ PDF документов AI-Symbiosis-H
param($WkhtmlPath = "C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

Write-Host "🚀 Создание НАСТОЯЩИХ PDF документов AI-Symbiosis-H" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan

# Основные файлы для конвертации
$FilesToConvert = @(
    @("LICENSE", "LICENSE_OFFICIAL.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/LEGAL_EXPLANATION.md", "LEGAL_EXPLANATION_OFFICIAL.pdf"),
    @("PHILOSOPHY/OFFICIAL_MANIFESTO/MANIFESTO.md", "MANIFESTO_RU_OFFICIAL.pdf"),
    @("PHILOSOPHY/OFFICIAL_MANIFESTO/MANIFESTO-EN.md", "MANIFESTO_EN_OFFICIAL.pdf"),
    @("PHILOSOPHY/OFFICIAL_MANIFESTO/ETHICAL_FRAMEWORK.md", "ETHICAL_FRAMEWORK_OFFICIAL.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/NATIONAL/RU/ROSPATENT_NOTIFICATION.md", "ROSPATENT_NOTIFICATION_OFFICIAL.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/NATIONAL/RU/MINISTRY_DIGITAL_DEVELOPMENT.md", "MINISTRY_DIGITAL_DEVELOPMENT_OFFICIAL.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/NATIONAL/RU/STATE_DUMA_COMMITTEE.md", "STATE_DUMA_COMMITTEE_OFFICIAL.pdf")
)

# Создаем папку для настоящих PDF
$RealPdfFolder = "PHILOSOPHY/LEGAL_BASIS/PROOFS_OF_SUBMISSION/REAL_PDFS"
if (!(Test-Path $RealPdfFolder)) {
    New-Item -Path $RealPdfFolder -ItemType Directory -Force
    Write-Host "📁 Создана папка для настоящих PDF: $RealPdfFolder" -ForegroundColor Yellow
}

$successCount = 0

foreach ($filePair in $FilesToConvert) {
    $mdFile = $filePair[0]
    $pdfFile = $filePair[1]
    $outputPath = Join-Path $RealPdfFolder $pdfFile
    
    Write-Host "`n📄 Конвертируем: $mdFile" -ForegroundColor Cyan
    
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
        h1 { 
            color: #2c3e50; 
            border-bottom: 2px solid #3498db; 
            padding-bottom: 10px;
            margin-top: 30px;
        }
        h2 { 
            color: #34495e; 
            margin-top: 25px;
            border-left: 4px solid #e74c3c;
            padding-left: 10px;
        }
        h3 { color: #16a085; }
        code { 
            background: #f8f9fa; 
            padding: 2px 6px; 
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            border: 1px solid #e9ecef;
        }
        pre { 
            background: #f8f9fa; 
            padding: 15px; 
            border-radius: 5px;
            border-left: 4px solid #3498db;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
        }
        blockquote {
            border-left: 4px solid #e74c3c;
            padding-left: 15px;
            margin-left: 0;
            color: #7f8c8d;
            font-style: italic;
            background: #fdf2f2;
            padding: 10px;
            border-radius: 0 5px 5px 0;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #bdc3c7;
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: center;
        }
        .document-info {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            font-size: 0.9em;
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
        GitHub: https://github.com/AzesmF/AI-Symbiosis-H
    </div>
    
    <pre style="white-space: pre-wrap; font-family: 'Arial', sans-serif; line-height: 1.4;">$([System.Net.WebUtility]::HtmlEncode($content))</pre>
    
    <div class="footer">
        <p>© 2025 AI-SYMBiosis-H. Все права защищены.</p>
        <p>Документ сгенерирован автоматически. Оригинал: $mdFile</p>
    </div>
</body>
</html>
"@
            
            # Сохраняем временный HTML
            $tempHtml = "$env:TEMP\temp_$(Get-Random).html"
            $htmlContent | Out-File -FilePath $tempHtml -Encoding UTF8
            
            # Конвертируем в PDF используя wkhtmltopdf
            & $WkhtmlPath --page-size A4 --margin-top 15mm --margin-bottom 15mm --margin-left 15mm --margin-right 15mm --encoding "UTF-8" $tempHtml $outputPath
            
            # Удаляем временный HTML
            Remove-Item $tempHtml -Force
            
            if (Test-Path $outputPath) {
                $successCount++
                $fileSize = [math]::Round((Get-Item $outputPath).Length/1024, 2)
                Write-Host "✅ Создан НАСТОЯЩИЙ PDF: $pdfFile ($fileSize KB)" -ForegroundColor Green
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

Write-Host "`n🎉 Конвертация завершена!" -ForegroundColor Green
Write-Host "📊 Создано настоящих PDF: $successCount/$($FilesToConvert.Count)" -ForegroundColor Cyan

# Показываем созданные файлы
Write-Host "`n📋 НАСТОЯЩИЕ PDF файлы:" -ForegroundColor Yellow
Get-ChildItem $RealPdfFolder -Filter "*_OFFICIAL.pdf" | ForEach-Object {
    $fileSize = [math]::Round($_.Length/1024, 2)
    Write-Host "   📄 $($_.Name) ($fileSize KB)" -ForegroundColor White
}

Write-Host "`n🔍 Тестируем открытие PDF..." -ForegroundColor Cyan
$testPdf = Get-ChildItem $RealPdfFolder -Filter "*.pdf" | Select-Object -First 1
if ($testPdf) {
    Write-Host "   Открываем: $($testPdf.Name)" -ForegroundColor White
    Start-Process $testPdf.FullName
}
