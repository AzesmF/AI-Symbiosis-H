# Axiom Core - Foundation AI Evaluation System

## 📋 Overview

**Axiom Core** is an automated evaluation system for AI-generated content through criteria synthesis and academic metrics.

> **Status**: Active Development • **Version**: 1.0 • **License**: Human-AI Symbiosis Non-Commercial License

## ⚠️ Important Notes

### Current Limitations
- **LLM Integration**: Uses intelligent mock implementations (`_mock_llm_call`)
- **Production Readiness**: Requires integration with real ML APIs for production use

## 🏗️ Architecture

### Core Components
```python
FoundationEvaluationSystem          # Main orchestrator class
├── CriteriaSynthesizer             # Dynamic criteria generation
├── CriteriaEvaluator               # Parallel evaluation (mock implementations)
├── WeightManager                   # Adaptive weight calculation
├── VerdictValidator                # Verdict synthesis and validation
├── BatchProcessor                  # Batch processing
└── AcademicEvaluationMetrics       # Academic metrics
📁 Project Structure
text
PRACTICE/Axiom-Core/
├── axiom_core.py              # Main system code (~75KB)
├── config.yaml                # System configuration
├── requirements.txt           # Python dependencies
├── __init__.py               # Package file
├── LICENSE                   # Human-AI Symbiosis Non-Commercial License
├── NON_COMMERCIAL_CLAUSE.md  # Additional terms
└── README.md                 # This documentation
🔧 Installation & Dependencies
Requirements
txt
numpy>=1.21.0
aiohttp>=3.8.0
PyYAML>=6.0
pandas>=1.5.0
scipy>=1.9.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
prometheus-client>=0.17.0
Quick Start
bash
cd PRACTICE/Axiom-Core
pip install -r requirements.txt
🚀 Usage
Basic Evaluation
python
from axiom_core import FoundationEvaluationSystem, ModelFallbackStrategy
import asyncio

async def main():
    # System initialization
    system = FoundationEvaluationSystem(
        fallback_strategy=ModelFallbackStrategy.MOCK
    )
    
    # Prepare examples
    examples = [
        {
            "instruction": "Solve: 15 + 28",
            "generated": "43",
            "reference": "43", 
            "criterion": "Answer correctness and format",
            "scale": "0-3",
            "human_score": 3.0  # For correlation metrics
        }
    ]
    
    # Async evaluation
    scores = await system.predict_async(examples)
    print(f"Score: {scores[0]}")
    
    # Academic report
    report = system.get_academic_report()
    print(f"System quality: {report['composite_scores']['evaluation_system_quality']}")

asyncio.run(main())
⚙️ Configuration
config.yaml
yaml
system:
  model_timeout: 30           # "Call" timeout in seconds
  max_retries: 3              # Retry attempts
  batch_size: 10              # Processing batch size
  performance_metrics: true   # Performance metrics collection
  fallback_strategy: "mock"   # Error handling strategy
  max_workers: 4              # Parallel threads
  cache_size: 1000            # Cache size

academic_metrics:
  enabled: true               # Enable academic metrics
  weights:                    # Composite score weights
    pearson_correlation: 0.25
    spearman_correlation: 0.25
    mean_absolute_error: 0.15
    kl_divergence: 0.15
    confidence_calibration: 0.10
    system_reliability: 0.10
📊 Academic Metrics
Implemented Metrics
Human Agreement: Pearson, Spearman, Cohen's Kappa, MAE

Distribution Metrics: KL-divergence, Wasserstein distance

System Reliability: Criteria consistency, confidence calibration

Quality Assessments: Factual accuracy, coherence, fluency

Getting Reports
python
report = system.get_academic_report()
print(f"Spearman correlation: {report['academic_metrics']['human_agreement_metrics']['spearman_correlation']:.3f}")
print(f"System reliability: {report['academic_metrics']['evaluation_system_metrics']['system_reliability']:.3f}")
🛡️ Error Handling
Exception Hierarchy
python
EvaluationError
├── ModelTimeoutError      # "Call" timeouts
├── ConfigurationError     # Configuration errors  
└── ValidationError        # Invalid input data
Fallback Strategies
mock: Intelligent mock implementations (default)

retry: Retry attempts with delays

skip: Skip problematic examples

🎯 Evaluation Criteria
Supported Criteria
correctness: Factual accuracy and logical correctness

format: Compliance with format requirements

optimality: Solution efficiency

speech_errors: Language quality and grammar

overall_quality: Comprehensive assessment

📈 Performance
Current Characteristics
Processing: Asynchronous batch processing

Memory: Controlled usage via BatchProcessor

Caching: ThreadSafe LRU cache for repeated evaluations

Concurrency: ThreadPoolExecutor for CPU-bound operations

🔮 Roadmap
Near-term Tasks
Integration with real LLM APIs (OpenAI, Anthropic, etc.)

Comprehensive test suite

Evaluation criteria expansion

Long-term Goals
Web interface for demonstration

Additional language support

Benchmarking against existing systems

📄 License
Human-AI Symbiosis Non-Commercial License

✅ Allowed: Scientific research, education, non-commercial projects

❌ Prohibited: Commercial use, SaaS, proprietary integration

Full text: LICENSE • NON_COMMERCIAL_CLAUSE.md

🤝 Contributing
Welcome:

Bug fixes and documentation improvements

LLM provider integration implementations

Academic metrics and criteria additions

Author: AzesmF • Year: 2025
Project Part: AI-Symbiosis-H

*Documentation fully corresponds to code from axiom_core.py. Last verified: 2025-10-18*
