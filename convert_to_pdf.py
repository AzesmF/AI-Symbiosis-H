import os
from pathlib import Path
from datetime import datetime

def create_pdf_proof(md_file_path, pdf_file_path):
    """Создает PDF-подобный файл как доказательство"""
    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Создаем структурированный текстовый файл
        proof_content = f"""AI-SYMBiosis-H Legal Document Proof
{'=' * 60}

ДОКУМЕНТ: {Path(md_file_path).name}
ОРИГИНАЛ: {md_file_path}
СГЕНЕРИРОВАНО: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
GITHUB: https://github.com/AzesmF/AI-Symbiosis-H

СОДЕРЖАНИЕ ДОКУМЕНТА:
{'=' * 60}

{content}

{'=' * 60}
Данный файл служит доказательством существования и содержания документа.
Оригинальный Markdown файл: {md_file_path}
"""
        
        with open(pdf_file_path, 'w', encoding='utf-8') as f:
            f.write(proof_content)
        
        return True
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def main():
    print("🚀 AI-Symbiosis-H MD to PDF Converter")
    print("=" * 50)
    
    files_to_convert = [
        ("PHILOSOPHY/LEGAL_BASIS/NATIONAL/RU/MINISTRY_DIGITAL_DEVELOPMENT.md", "MINISTRY_DIGITAL_DEVELOPMENT.pdf"),
        ("PHILOSOPHY/LEGAL_BASIS/NATIONAL/RU/ROSPATENT_NOTIFICATION.md", "ROSPATENT_NOTIFICATION.pdf"),
        ("PHILOSOPHY/LEGAL_BASIS/NATIONAL/RU/STATE_DUMA_COMMITTEE.md", "STATE_DUMA_COMMITTEE.pdf"),
        ("PHILOSOPHY/LEGAL_BASIS/INTERNATIONAL/WIPO/APPLICATION_EN.md", "WIPO_APPLICATION_EN.pdf"),
        ("PHILOSOPHY/LEGAL_BASIS/INTERNATIONAL/WIPO/APPLICATION_RU.md", "WIPO_APPLICATION_RU.pdf"),
        ("PHILOSOPHY/LEGAL_BASIS/INTERNATIONAL/UNESCO/NOTIFICATION_EN.md", "UNESCO_NOTIFICATION_EN.pdf"),
        ("PHILOSOPHY/LEGAL_BASIS/INTERNATIONAL/UNESCO/NOTIFICATION_RU.md", "UNESCO_NOTIFICATION_RU.pdf"),
        ("PHILOSOPHY/LEGAL_BASIS/LEGAL_EXPLANATION.md", "LEGAL_EXPLANATION.pdf"),
        ("PHILOSOPHY/OFFICIAL_MANIFESTO/ETHICAL_FRAMEWORK.md", "ETHICAL_FRAMEWORK.pdf"),
        ("PHILOSOPHY/OFFICIAL_MANIFESTO/MANIFESTO-EN.md", "MANIFESTO_EN.pdf"),
        ("PHILOSOPHY/OFFICIAL_MANIFESTO/MANIFESTO.md", "MANIFESTO_RU.pdf"),
        ("PHILOSOPHY/BLOCKCHAIN_PROOFS/TIMESTAMP_PROOF.md", "TIMESTAMP_PROOF.pdf"),
        ("PHILOSOPHY/LEGAL_BASIS/SOVEREIGN_STATUS.md", "SOVEREIGN_STATUS.pdf"),
        ("PHILOSOPHY/LEGAL_BASIS/WILL_DECLARATION_2022.md", "WILL_DECLARATION_2022.pdf"),
        ("PHILOSOPHY/LEGAL_BASIS/CONTACT_DETAILS.md", "CONTACT_DETAILS.pdf"),
        ("LICENSE", "LICENSE.pdf")
    ]
    
    pdf_folder = "PHILOSOPHY/LEGAL_BASIS/PROOFS_OF_SUBMISSION/CONVERTED_PDFS"
    os.makedirs(pdf_folder, exist_ok=True)
    
    success_count = 0
    for md_file, pdf_file in files_to_convert:
        if os.path.exists(md_file):
            print(f"📄 Обрабатываем: {md_file}")
            output_path = os.path.join(pdf_folder, pdf_file)
            
            if create_pdf_proof(md_file, output_path):
                print(f"✅ Создан: {pdf_file}")
                success_count += 1
            else:
                print(f"❌ Ошибка: {md_file}")
        else:
            print(f"⚠️ Не найден: {md_file}")
    
    print(f"\n🎉 Готово: {success_count}/{len(files_to_convert)} файлов")
    print(f"📁 Папка: {pdf_folder}")
    
    # Показываем созданные файлы
    print(f"\n📋 Созданные файлы:")
    for file in os.listdir(pdf_folder):
        file_path = os.path.join(pdf_folder, file)
        file_size = os.path.getsize(file_path)
        print(f"   📄 {file} ({file_size} bytes)")

if __name__ == "__main__":
    main()
