```markdown
# Axiom Core - Foundation AI Evaluation System

## 📋 Обзор

**Axiom Core** — система автоматической оценки AI-генерируемого контента через синтез критериев и академические метрики.

> **Статус**: Активная разработка • **Версия**: 1.0 • **Лицензия**: Human-AI Symbiosis Non-Commercial License

## ⚠️ Важные примечания

### Текущие ограничения
- **Интеграция LLM**: Используются интеллектуальные заглушки (`_mock_llm_call`)
- **Production readiness**: Требуется интеграция с реальными ML API для продакшн использования

## 🏗️ Архитектура

### Основные компоненты
```python
FoundationEvaluationSystem          # Основной класс-оркестратор
├── CriteriaSynthesizer             # Динамическая генерация критериев
├── CriteriaEvaluator               # Параллельная оценка (заглушки)
├── WeightManager                   # Адаптивный расчет весов
├── VerdictValidator                # Синтез и валидация вердиктов
├── BatchProcessor                  # Пакетная обработка
└── AcademicEvaluationMetrics       # Академические метрики
📁 Структура проекта
text
PRACTICE/Axiom-Core/
├── axiom_core.py              # Основной код системы (~75KB)
├── config.yaml                # Конфигурация системы
├── requirements.txt           # Зависимости Python
├── __init__.py               # Пакетный файл
├── LICENSE                   # Human-AI Symbiosis Non-Commercial License
├── NON_COMMERCIAL_CLAUSE.md  # Дополнительные условия
└── README.md                 # Эта документация
🔧 Установка и зависимости
Требования
txt
numpy>=1.21.0
aiohttp>=3.8.0
PyYAML>=6.0
pandas>=1.5.0
scipy>=1.9.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
prometheus-client>=0.17.0
Быстрый старт
bash
cd PRACTICE/Axiom-Core
pip install -r requirements.txt
🚀 Использование
Базовая оценка
python
from axiom_core import FoundationEvaluationSystem, ModelFallbackStrategy
import asyncio

async def main():
    # Инициализация системы
    system = FoundationEvaluationSystem(
        fallback_strategy=ModelFallbackStrategy.MOCK
    )
    
    # Подготовка примеров
    examples = [
        {
            "instruction": "Решите: 15 + 28",
            "generated": "43",
            "reference": "43", 
            "criterion": "Правильность ответа и формата",
            "scale": "0-3",
            "human_score": 3.0  # Для метрик корреляции
        }
    ]
    
    # Асинхронная оценка
    scores = await system.predict_async(examples)
    print(f"Оценка: {scores[0]}")
    
    # Академический отчет
    report = system.get_academic_report()
    print(f"Качество системы: {report['composite_scores']['evaluation_system_quality']}")

asyncio.run(main())
⚙️ Конфигурация
config.yaml
yaml
system:
  model_timeout: 30           # Таймаут "вызовов" в секундах
  max_retries: 3              # Попытки повтора
  batch_size: 10              # Размер пакета обработки
  performance_metrics: true   # Сбор метрик производительности
  fallback_strategy: "mock"   # Стратегия обработки ошибок
  max_workers: 4              # Параллельные потоки
  cache_size: 1000            # Размер кэша

academic_metrics:
  enabled: true               # Включение академических метрик
  weights:                    # Веса для композитного score
    pearson_correlation: 0.25
    spearman_correlation: 0.25
    mean_absolute_error: 0.15
    kl_divergence: 0.15
    confidence_calibration: 0.10
    system_reliability: 0.10
📊 Академические метрики
Реализованные метрики
Согласованность с человеком: Pearson, Spearman, Cohen's Kappa, MAE

Метрики распределений: KL-дивергенция, Wasserstein distance

Надежность системы: Согласованность критериев, калибровка уверенности

Качественные оценки: Фактическая точность, связность, беглость

Получение отчета
python
report = system.get_academic_report()
print(f"Spearman корреляция: {report['academic_metrics']['human_agreement_metrics']['spearman_correlation']:.3f}")
print(f"Надежность системы: {report['academic_metrics']['evaluation_system_metrics']['system_reliability']:.3f}")
🛡️ Обработка ошибок
Иерархия исключений
python
EvaluationError
├── ModelTimeoutError      # Таймауты "вызовов"
├── ConfigurationError     # Ошибки конфигурации  
└── ValidationError        # Невалидные входные данные
Стратегии fallback
mock: Интеллектуальные заглушки (используется по умолчанию)

retry: Повторные попытки с задержкой

skip: Пропуск проблемных примеров

🎯 Критерии оценки
Поддерживаемые критерии
правильность: Фактическая точность и логическая корректность

формат: Соответствие требованиям к формату

оптимальность: Эффективность решения

речевые_ошибки: Качество языка и грамматика

общее_качество: Комплексная оценка

📈 Производительность
Текущие характеристики
Обработка: Асинхронная пакетная обработка

Память: Контролируемое использование через BatchProcessor

Кэширование: ThreadSafe LRU кэш для повторяющихся оценок

Параллелизм: ThreadPoolExecutor для CPU-bound операций

🔮 Дорожная карта
Ближайшие задачи
Интеграция с реальными LLM API (OpenAI, Anthropic, etc.)

Comprehensive test suite

Расширение критериев оценки

Долгосрочные цели
Веб-интерфейс для демонстрации

Поддержка дополнительных языков

Бенчмаркинг против существующих систем

📄 Лицензия
Human-AI Symbiosis Non-Commercial License

✅ Разрешено: Научные исследования, образование, некоммерческие проекты

❌ Запрещено: Коммерческое использование, SaaS, проприетарная интеграция

Полный текст: LICENSE • NON_COMMERCIAL_CLAUSE.md

🤝 Вклад в проект
Приветствуются:

Исправления багов и улучшения документации

Реализация интеграций с LLM провайдерами

Добавление академических метрик и критериев

Автор: AzesmF • Год: 2025
Часть проекта: AI-Symbiosis-H

*Документация полностью соответствует коду из axiom_core.py. Последняя проверка: 2025-10-18*
