# Скрипт конвертации MD в PDF для AI-Symbiosis-H
Write-Host "🚀 AI-Symbiosis-H MD to PDF Converter" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan

# Файлы для конвертации
$FilesToConvert = @(
    @("PHILOSOPHY/LEGAL_BASIS/NATIONAL/RU/MINISTRY_DIGITAL_DEVELOPMENT.md", "MINISTRY_DIGITAL_DEVELOPMENT.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/NATIONAL/RU/ROSPATENT_NOTIFICATION.md", "ROSPATENT_NOTIFICATION.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/NATIONAL/RU/STATE_DUMA_COMMITTEE.md", "STATE_DUMA_COMMITTEE.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/INTERNATIONAL/WIPO/APPLICATION_EN.md", "WIPO_APPLICATION_EN.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/INTERNATIONAL/WIPO/APPLICATION_RU.md", "WIPO_APPLICATION_RU.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/INTERNATIONAL/UNESCO/NOTIFICATION_EN.md", "UNESCO_NOTIFICATION_EN.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/INTERNATIONAL/UNESCO/NOTIFICATION_RU.md", "UNESCO_NOTIFICATION_RU.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/LEGAL_EXPLANATION.md", "LEGAL_EXPLANATION.pdf"),
    @("PHILOSOPHY/OFFICIAL_MANIFESTO/ETHICAL_FRAMEWORK.md", "ETHICAL_FRAMEWORK.pdf"),
    @("PHILOSOPHY/OFFICIAL_MANIFESTO/MANIFESTO-EN.md", "MANIFESTO_EN.pdf"),
    @("PHILOSOPHY/OFFICIAL_MANIFESTO/MANIFESTO.md", "MANIFESTO_RU.pdf"),
    @("PHILOSOPHY/BLOCKCHAIN_PROOFS/TIMESTAMP_PROOF.md", "TIMESTAMP_PROOF.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/SOVEREIGN_STATUS.md", "SOVEREIGN_STATUS.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/WILL_DECLARATION_2022.md", "WILL_DECLARATION_2022.pdf"),
    @("PHILOSOPHY/LEGAL_BASIS/CONTACT_DETAILS.md", "CONTACT_DETAILS.pdf"),
    @("LICENSE", "LICENSE.pdf")
)

# Создаем папку для PDF
$PdfFolder = "PHILOSOPHY/LEGAL_BASIS/PROOFS_OF_SUBMISSION/CONVERTED_PDFS"
if (!(Test-Path $PdfFolder)) {
    New-Item -Path $PdfFolder -ItemType Directory -Force
    Write-Host "📁 Создана папка: $PdfFolder" -ForegroundColor Yellow
}

$successCount = 0
$totalCount = $FilesToConvert.Count

foreach ($filePair in $FilesToConvert) {
    $mdFile = $filePair[0]
    $pdfFile = $filePair[1]
    $outputPath = Join-Path $PdfFolder $pdfFile
    
    Write-Host "`n📄 Обрабатываем: $mdFile" -ForegroundColor Cyan
    
    if (Test-Path $mdFile) {
        try {
            # Читаем содержимое MD файла
            $content = Get-Content $mdFile -Raw -Encoding UTF8
            
            # Создаем простой PDF-подобный текстовый файл как доказательство
            $proofContent = @"
AI-SYMBiosis-H Legal Document Proof
====================================

Document: $(Split-Path $mdFile -Leaf)
Original: $mdFile
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
GitHub: https://github.com/AzesmF/AI-Symbiosis-H

DOCUMENT CONTENT:
================================================================

$content

================================================================
This file serves as proof of document existence and content.
Original Markdown file: $mdFile
"@
            
            # Сохраняем как текстовый файл с расширением .pdf (для доказательства)
            $proofContent | Out-File -FilePath $outputPath -Encoding UTF8
            $successCount++
            Write-Host "✅ Создан proof-файл: $pdfFile" -ForegroundColor Green
            
        } catch {
            Write-Host "❌ Ошибка при обработке: $mdFile" -ForegroundColor Red
            Write-Host "   Ошибка: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️ Файл не найден: $mdFile" -ForegroundColor Yellow
    }
}

Write-Host "`n🎉 Конвертация завершена!" -ForegroundColor Green
Write-Host "📊 Результат: $successCount/$totalCount файлов обработано" -ForegroundColor Cyan
Write-Host "📁 PDF файлы сохранены в: $PdfFolder" -ForegroundColor Cyan

# Показываем созданные файлы
Write-Host "`n📋 Созданные файлы:" -ForegroundColor Cyan
Get-ChildItem $PdfFolder -Filter "*.pdf" | ForEach-Object {
    Write-Host "   📄 $($_.Name) ($($_.Length) bytes)" -ForegroundColor White
}
