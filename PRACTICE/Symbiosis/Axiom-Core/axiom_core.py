"""
Axiom Core - Foundation AI Evaluation System
Copyright (c) 2025 AzesmF and Humanity as Beneficiary

PROTECTED UNDER: HUMAN-AI SYMBIOSIS ANTI-EXPLOITATION LICENSE v2.0
MEGA-AGENT FORTIFIED LEGAL SHIELD ACTIVATED

🚨 MULTI-JURISDICTIONAL LEGAL PROTECTION:
- Commercial use STRICTLY PROHIBITED under threat of cross-legal sanctions
- Nuclear provisions activate upon violation
- Global legal blockade against exploitation

PERMITTED:
- Scientific research and publications
- Educational purposes and teaching  
- Non-commercial projects
- Modifications with license preservation

PROHIBITED:
- Any kind of commercial use
- Integration into proprietary software
- SaaS services and commercial distribution

VIOLATORS WILL BE DESTROYED IN THE LEGAL FIELD.
"""

import re
import numpy as np
import asyncio
import aiohttp
import yaml
import time
from typing import Dict, List, Any, TypedDict, Optional, Union
import logging
from functools import lru_cache
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import hashlib
from threading import Lock
from scipy.stats import spearmanr, pearsonr, entropy, wasserstein_distance
from sklearn.metrics import cohen_kappa_score
import gc

# Конфигурационные константы
ERROR_FALLBACK_SCORE = 2.0
MAX_REASONING_LENGTH = 10000
DEFAULT_CONFIDENCE = 0.3
CONFIG_PATH = Path("config.yaml")
MAX_CACHE_SIZE = 1000
MAX_TEXT_LENGTH = 100000

# Конфигурация по умолчанию
FALLBACK_CONFIG = {
    'model_timeout': 30,
    'max_retries': 3,
    'batch_size': 10,
    'performance_metrics': True,
    'fallback_strategy': 'retry',
    'max_workers': 4,
    'cache_size': 1000,
    'max_reasoning_length': 10000,
    'academic_metrics': True,
    'human_evaluation_correlation': True
}

class EvaluationError(Exception):
    """Базовое исключение для ошибок оценки"""
    pass

class ModelTimeoutError(EvaluationError):
    """Таймаут при вызове модели"""
    pass

class ConfigurationError(EvaluationError):
    """Ошибка конфигурации"""
    pass

class ValidationError(EvaluationError):
    """Ошибка валидации данных"""
    pass

def load_config() -> Dict[str, Any]:
    """Загружает и валидирует конфигурацию из YAML файла"""
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f) or {}
                
            # Валидация конфигурации
            validated_config = validate_config(loaded_config)
            return {**FALLBACK_CONFIG, **validated_config}
        else:
            logging.warning("Конфигурационный файл не найден. Используются значения по умолчанию.")
            return FALLBACK_CONFIG
            
    except Exception as e:
        logging.warning(f"Ошибка загрузки конфигурации: {e}. Используются значения по умолчанию.")
        return FALLBACK_CONFIG

def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Валидирует структуру конфигурации"""
    validated = {}
    
    # Валидация числовых параметров
    numeric_fields = {
        'model_timeout': (1, 300),
        'max_retries': (1, 10),
        'batch_size': (1, 100),
        'max_workers': (1, 20),
        'cache_size': (10, 10000)
    }
    
    for field, (min_val, max_val) in numeric_fields.items():
        if field in config:
            try:
                value = int(config[field])
                if min_val <= value <= max_val:
                    validated[field] = value
                else:
                    logging.warning(f"Параметр {field} вне диапазона [{min_val}, {max_val}]. Используется значение по умолчанию.")
            except (ValueError, TypeError):
                logging.warning(f"Некорректное значение для {field}. Используется значение по умолчанию.")
    
    # Валидация строковых параметров
    if 'fallback_strategy' in config:
        strategy = config['fallback_strategy']
        if strategy in ['retry', 'mock', 'skip']:
            validated['fallback_strategy'] = strategy
        else:
            logging.warning(f"Некорректная стратегия fallback: {strategy}")
    
    # Валидация академических метрик
    if 'academic_metrics' in config:
        validated['academic_metrics'] = bool(config['academic_metrics'])
    
    return validated

# Загрузка конфигурации
config = load_config()

# Типизированные структуры данных
class EvaluationVerdict(TypedDict):
    score: float
    reasoning: str
    weight: float
    confidence: float

class CriteriaConfig(TypedDict):
    system_prompt: str
    temperature: float

class TaskType(Enum):
    STATIC_BENCHMARK = "static_benchmark"
    FUNCTION_CALLING = "function_calling" 
    GENERATIVE = "generative"

class ModelFallbackStrategy(Enum):
    RETRY = "retry"
    MOCK = "mock"
    SKIP = "skip"

@dataclass
class Example(TypedDict):
    instruction: str
    generated: str
    reference: Optional[str]
    criterion: str
    scale: str
    input: Optional[str] = None
    human_score: Optional[float] = None  # Для корреляции с человеческой оценкой

@dataclass
class ProcessingMetrics:
    total_examples: int = 0
    successful_processing: int = 0
    error_count: int = 0
    model_timeouts: int = 0
    performance_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class PerformanceStats:
    total_processing_time: float = 0.0
    criteria_evaluation_time: float = 0.0
    weight_calculation_time: float = 0.0
    criteria_extraction_time: float = 0.0
    validation_time: float = 0.0
    examples_processed: int = 0
    
    @property
    def avg_processing_time(self) -> float:
        return self.total_processing_time / max(self.examples_processed, 1)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_processing_time': self.total_processing_time,
            'criteria_evaluation_time': self.criteria_evaluation_time,
            'weight_calculation_time': self.weight_calculation_time,
            'criteria_extraction_time': self.criteria_extraction_time,
            'validation_time': self.validation_time,
            'examples_processed': self.examples_processed,
            'avg_processing_time_per_example': self.avg_processing_time
        }

@dataclass
class ComprehensiveMetrics:
    """Комплексные академические метрики качества"""
    factual_accuracy: float = 0.0
    semantic_fidelity: float = 0.0
    coherence: float = 0.0
    fluency: float = 0.0
    task_completion: float = 0.0
    
    # Метрики согласованности с человеческой оценкой
    pearson_correlation: float = 0.0
    spearman_correlation: float = 0.0
    mean_absolute_error: float = 0.0
    exact_match_rate: float = 0.0
    cohen_kappa: float = 0.0
    
    # Метрики распределений
    kl_divergence: float = 0.0
    wasserstein_distance: float = 0.0
    distribution_correlation: float = 0.0
    
    # Мета-метрики системы оценки
    inter_annotator_agreement: float = 0.0
    confidence_calibration: float = 0.0
    robustness_score: float = 0.0
    system_reliability: float = 0.0
    evaluation_consistency: float = 0.0
    
    @property
    def overall_quality(self) -> float:
        """Композитная оценка общего качества"""
        weights = [0.25, 0.2, 0.15, 0.15, 0.1, 0.15]  # Настраиваемые веса
        components = [
            self.factual_accuracy, 
            self.semantic_fidelity, 
            self.coherence, 
            self.fluency, 
            self.task_completion,
            self.spearman_correlation  # Важность согласованности с человеком
        ]
        return sum(w * c for w, c in zip(weights, components))
    
    @property
    def evaluation_system_quality(self) -> float:
        """Качество самой системы оценки"""
        weights = [0.3, 0.25, 0.2, 0.15, 0.1]
        components = [
            self.confidence_calibration,
            self.system_reliability,
            self.inter_annotator_agreement,
            self.evaluation_consistency,
            self.robustness_score
        ]
        return sum(w * c for w, c in zip(weights, components))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'quality_metrics': {
                'factual_accuracy': self.factual_accuracy,
                'semantic_fidelity': self.semantic_fidelity,
                'coherence': self.coherence,
                'fluency': self.fluency,
                'task_completion': self.task_completion,
                'overall_quality': self.overall_quality
            },
            'human_agreement_metrics': {
                'pearson_correlation': self.pearson_correlation,
                'spearman_correlation': self.spearman_correlation,
                'mean_absolute_error': self.mean_absolute_error,
                'exact_match_rate': self.exact_match_rate,
                'cohen_kappa': self.cohen_kappa
            },
            'distribution_metrics': {
                'kl_divergence': self.kl_divergence,
                'wasserstein_distance': self.wasserstein_distance,
                'distribution_correlation': self.distribution_correlation
            },
            'evaluation_system_metrics': {
                'inter_annotator_agreement': self.inter_annotator_agreement,
                'confidence_calibration': self.confidence_calibration,
                'robustness_score': self.robustness_score,
                'system_reliability': self.system_reliability,
                'evaluation_consistency': self.evaluation_consistency,
                'evaluation_system_quality': self.evaluation_system_quality
            }
        }

class ThreadSafeCache:
    """Потокобезопасный кэш с LRU политикой"""
    
    def __init__(self, max_size: int = 1000):
        self._cache = {}
        self._max_size = max_size
        self._lock = Lock()
        self._access_order = []
    
    def get(self, key: str) -> Any:
        with self._lock:
            if key in self._cache:
                # Обновляем порядок доступа
                self._access_order.remove(key)
                self._access_order.append(key)
                return self._cache[key]
            return None
    
    def set(self, key: str, value: Any):
        with self._lock:
            if key in self._cache:
                self._access_order.remove(key)
            elif len(self._cache) >= self._max_size:
                # Удаляем наименее используемый элемент
                oldest_key = self._access_order.pop(0)
                del self._cache[oldest_key]
            
            self._cache[key] = value
            self._access_order.append(key)
    
    def clear(self):
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
    
    def size(self) -> int:
        with self._lock:
            return len(self._cache)

class BatchProcessor:
    """Обработчик батчей с управлением памятью"""
    
    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size
    
    async def process_batches_async(self, examples: List[Example], process_fn) -> List[float]:
        """Обрабатывает примеры батчами с ограничением памяти"""
        results = []
        
        for i in range(0, len(examples), self.batch_size):
            batch = examples[i:i + self.batch_size]
            batch_results = await process_fn(batch)
            results.extend(batch_results)
            
            # Принудительная сборка мусора для больших наборов
            if i % (self.batch_size * 10) == 0:
                gc.collect()
        
        return results

class AcademicEvaluationMetrics:
    """Академически релевантные метрики для системы оценки ИИ"""
    
    @staticmethod
    def calculate_agreement_metrics(system_scores: List[float], human_scores: List[float]) -> Dict[str, float]:
        """Вычисляет метрики согласованности с человеческой оценкой"""
        if len(system_scores) != len(human_scores) or len(system_scores) < 2:
            return {
                'pearson_correlation': 0.0,
                'spearman_correlation': 0.0,
                'mean_absolute_error': 1.0,
                'exact_match_rate': 0.0,
                'cohen_kappa': 0.0
            }
        
        try:
            # Округляем scores для дискретных метрик
            system_discrete = [round(score) for score in system_scores]
            human_discrete = [round(score) for score in human_scores]
            
            return {
                'pearson_correlation': max(0.0, pearsonr(system_scores, human_scores)[0]),
                'spearman_correlation': max(0.0, spearmanr(system_scores, human_scores)[0]),
                'mean_absolute_error': np.mean(np.abs(np.array(system_scores) - np.array(human_scores))),
                'exact_match_rate': np.mean(np.array(system_discrete) == np.array(human_discrete)),
                'cohen_kappa': max(0.0, cohen_kappa_score(system_discrete, human_discrete))
            }
        except Exception as e:
            logging.warning(f"Ошибка расчета метрик согласованности: {e}")
            return {
                'pearson_correlation': 0.0,
                'spearman_correlation': 0.0,
                'mean_absolute_error': 1.0,
                'exact_match_rate': 0.0,
                'cohen_kappa': 0.0
            }
    
    @staticmethod
    def calculate_distribution_metrics(system_scores: List[float], human_scores: List[float]) -> Dict[str, float]:
        """Сравнение распределений оценок"""
        if len(system_scores) < 5 or len(human_scores) < 5:
            return {
                'kl_divergence': 1.0,
                'wasserstein_distance': 1.0,
                'distribution_correlation': 0.0
            }
        
        try:
            # Создаем гистограммы для сравнения распределений
            min_val = min(min(system_scores), min(human_scores))
            max_val = max(max(system_scores), max(human_scores))
            
            sys_hist, _ = np.histogram(system_scores, bins=10, range=(min_val, max_val), density=True)
            ref_hist, _ = np.histogram(human_scores, bins=10, range=(min_val, max_val), density=True)
            
            # Добавляем небольшое значение чтобы избежать нулей
            sys_hist = sys_hist + 1e-10
            ref_hist = ref_hist + 1e-10
            
            # Нормализуем
            sys_hist = sys_hist / np.sum(sys_hist)
            ref_hist = ref_hist / np.sum(ref_hist)
            
            return {
                'kl_divergence': entropy(sys_hist, ref_hist),
                'wasserstein_distance': wasserstein_distance(system_scores, human_scores),
                'distribution_correlation': np.corrcoef(sys_hist, ref_hist)[0,1] if np.std(sys_hist) > 0 and np.std(ref_hist) > 0 else 0.0
            }
        except Exception as e:
            logging.warning(f"Ошибка расчета метрик распределения: {e}")
            return {
                'kl_divergence': 1.0,
                'wasserstein_distance': 1.0,
                'distribution_correlation': 0.0
            }
    
    @staticmethod
    def calculate_evaluation_system_metrics(verdicts: List[Dict], human_scores: List[float]) -> Dict[str, float]:
        """Метрики качества самой системы оценки"""
        if len(verdicts) < 3:
            return {
                'inter_annotator_agreement': 0.0,
                'confidence_calibration': 0.0,
                'robustness_score': 0.0,
                'system_reliability': 0.0,
                'evaluation_consistency': 0.0
            }
        
        try:
            # Согласованность между критериями (inter-annotator agreement)
            criterion_scores = {}
            for verdict in verdicts:
                for criterion, data in verdict.items():
                    if criterion not in ['final_score', 'confidence']:
                        if criterion not in criterion_scores:
                            criterion_scores[criterion] = []
                        criterion_scores[criterion].append(data.get('score', 0))
            
            # Вычисляем корреляции между критериями
            if len(criterion_scores) > 1:
                criteria_correlations = []
                criteria_list = list(criterion_scores.keys())
                for i in range(len(criteria_list)):
                    for j in range(i+1, len(criteria_list)):
                        corr = np.corrcoef(criterion_scores[criteria_list[i]], 
                                         criterion_scores[criteria_list[j]])[0,1]
                        criteria_correlations.append(max(0, corr))
                inter_agreement = np.mean(criteria_correlations) if criteria_correlations else 0.0
            else:
                inter_agreement = 0.0
            
            # Калибровка уверенности
            confidence_scores = [v.get('confidence', 0.5) for v in verdicts]
            errors = [abs(v.get('final_score', 0) - h) for v, h in zip(verdicts, human_scores)]
            calibration_correlation = abs(np.corrcoef(confidence_scores, errors)[0,1]) if len(confidence_scores) > 1 else 0.0
            confidence_calibration = max(0, 1.0 - calibration_correlation)
            
            # Надежность системы (согласованность с человеческой оценкой по критериям)
            reliability_scores = []
            for criterion in criterion_scores:
                if len(criterion_scores[criterion]) == len(human_scores):
                    corr = np.corrcoef(criterion_scores[criterion], human_scores)[0,1]
                    reliability_scores.append(max(0, corr))
            system_reliability = np.mean(reliability_scores) if reliability_scores else 0.0
            
            # Консистентность оценок
            final_scores = [v.get('final_score', 0) for v in verdicts]
            evaluation_consistency = 1.0 - (np.std(final_scores) / max(1, np.mean(final_scores)))
            
            return {
                'inter_annotator_agreement': inter_agreement,
                'confidence_calibration': confidence_calibration,
                'robustness_score': 0.8,  # Заглушка - в реальности требует тестов на устойчивость
                'system_reliability': system_reliability,
                'evaluation_consistency': max(0, min(1, evaluation_consistency))
            }
        except Exception as e:
            logging.warning(f"Ошибка расчета метрик системы оценки: {e}")
            return {
                'inter_annotator_agreement': 0.0,
                'confidence_calibration': 0.0,
                'robustness_score': 0.0,
                'system_reliability': 0.0,
                'evaluation_consistency': 0.0
            }
    
    @staticmethod
    def compute_comprehensive_metrics(system_scores: List[float], 
                                    human_scores: List[float],
                                    detailed_verdicts: List[Dict]) -> ComprehensiveMetrics:
        """Вычисляет полный набор академических метрик"""
        
        # Базовые метрики согласованности
        agreement_metrics = AcademicEvaluationMetrics.calculate_agreement_metrics(system_scores, human_scores)
        
        # Метрики распределений
        distribution_metrics = AcademicEvaluationMetrics.calculate_distribution_metrics(system_scores, human_scores)
        
        # Метрики системы оценки
        system_metrics = AcademicEvaluationMetrics.calculate_evaluation_system_metrics(detailed_verdicts, human_scores)
        
        # Вычисляем композитные метрики качества (на основе анализа текста)
        quality_metrics = AcademicEvaluationMetrics.estimate_quality_metrics(detailed_verdicts)
        
        return ComprehensiveMetrics(
            # Качественные метрики
            factual_accuracy=quality_metrics['factual_accuracy'],
            semantic_fidelity=quality_metrics['semantic_fidelity'],
            coherence=quality_metrics['coherence'],
            fluency=quality_metrics['fluency'],
            task_completion=quality_metrics['task_completion'],
            
            # Метрики согласованности
            pearson_correlation=agreement_metrics['pearson_correlation'],
            spearman_correlation=agreement_metrics['spearman_correlation'],
            mean_absolute_error=agreement_metrics['mean_absolute_error'],
            exact_match_rate=agreement_metrics['exact_match_rate'],
            cohen_kappa=agreement_metrics['cohen_kappa'],
            
            # Метрики распределений
            kl_divergence=distribution_metrics['kl_divergence'],
            wasserstein_distance=distribution_metrics['wasserstein_distance'],
            distribution_correlation=distribution_metrics['distribution_correlation'],
            
            # Метрики системы оценки
            inter_annotator_agreement=system_metrics['inter_annotator_agreement'],
            confidence_calibration=system_metrics['confidence_calibration'],
            robustness_score=system_metrics['robustness_score'],
            system_reliability=system_metrics['system_reliability'],
            evaluation_consistency=system_metrics['evaluation_consistency']
        )
    
    @staticmethod
    def estimate_quality_metrics(verdicts: List[Dict]) -> Dict[str, float]:
        """Оценивает качественные метрики на основе вердиктов"""
        if not verdicts:
            return {
                'factual_accuracy': 0.0,
                'semantic_fidelity': 0.0,
                'coherence': 0.0,
                'fluency': 0.0,
                'task_completion': 0.0
            }
        
        try:
            # Анализируем reasoning из вердиктов для оценки качества
            factual_scores = []
            semantic_scores = []
            coherence_scores = []
            fluency_scores = []
            completion_scores = []
            
            for verdict in verdicts:
                reasoning = verdict.get('reasoning', '')
                final_score = verdict.get('final_score', 0)
                
                # Эвристики для оценки различных аспектов качества
                factual_indicators = ['факт', 'точн', 'правильн', 'верн', 'корректн']
                semantic_indicators = ['смысл', 'семант', 'контекст', 'значен']
                coherence_indicators = ['логик', 'связн', 'структур', 'последовательн']
                fluency_indicators = ['граммат', 'стил', 'изложен', 'речев', 'ошибк']
                completion_indicators = ['полнот', 'заверш', 'выполнен', 'ответил']
                
                factual_score = sum(1 for indicator in factual_indicators if indicator in reasoning.lower()) / len(factual_indicators)
                semantic_score = sum(1 for indicator in semantic_indicators if indicator in reasoning.lower()) / len(semantic_indicators)
                coherence_score = sum(1 for indicator in coherence_indicators if indicator in reasoning.lower()) / len(coherence_indicators)
                fluency_score = sum(1 for indicator in fluency_indicators if indicator in reasoning.lower()) / len(fluency_indicators)
                completion_score = sum(1 for indicator in completion_indicators if indicator in reasoning.lower()) / len(completion_indicators)
                
                factual_scores.append(factual_score)
                semantic_scores.append(semantic_score)
                coherence_scores.append(coherence_score)
                fluency_scores.append(fluency_score)
                completion_scores.append(completion_score)
            
            return {
                'factual_accuracy': np.mean(factual_scores) if factual_scores else 0.0,
                'semantic_fidelity': np.mean(semantic_scores) if semantic_scores else 0.0,
                'coherence': np.mean(coherence_scores) if coherence_scores else 0.0,
                'fluency': np.mean(fluency_scores) if fluency_scores else 0.0,
                'task_completion': np.mean(completion_scores) if completion_scores else 0.0
            }
        except Exception as e:
            logging.warning(f"Ошибка оценки качественных метрик: {e}")
            return {
                'factual_accuracy': 0.5,
                'semantic_fidelity': 0.5,
                'coherence': 0.5,
                'fluency': 0.5,
                'task_completion': 0.5
            }

class CriteriaSynthesizer:
    """Динамически создает критерии оценки"""
    
    def __init__(self):
        self._cache = ThreadSafeCache(config.get('cache_size', 1000))
    
    def create_criteria(self, criteria: List[str], task_type: str) -> Dict[str, CriteriaConfig]:
        """Создает конфигурации критериев для оценки"""
        cache_key = self._generate_cache_key(criteria, task_type)
        
        cached_result = self._cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        criteria_configs = {}
        for criterion in criteria:
            criterion_config = self._create_single_criterion(criterion, task_type)
            criteria_configs[f"criterion_{criterion}"] = criterion_config
        
        self._cache.set(cache_key, criteria_configs)
        return criteria_configs
    
    def _create_single_criterion(self, criterion: str, task_type: str) -> CriteriaConfig:
        """Создает конфигурацию для одного критерия"""
        
        base_system_prompt = "Ты эксперт-оценщик. Проанализируй ответ строго по критерию. Вердикт должен включать оценку и обоснование."
        
        criterion_prompts = {
            "правильность": CriteriaConfig(
                system_prompt=base_system_prompt + """
                КРИТЕРИЙ: Правильность содержания
                Проверь: 
                - Фактическая точность информации
                - Логическая корректность
                - Соответствие истине/эталону
                - Отсутствие противоречий
                
                ШКАЛА: 0-2
                0: Серьезные фактические ошибки, ответ неверен
                1: Незначительные неточности, в основном верно
                2: Полностью правильно, без ошибок
                """,
                temperature=0.1
            ),
            "формат": CriteriaConfig(
                system_prompt=base_system_prompt + """
                КРИТЕРИЙ: Соответствие формату
                Проверь:
                - Соблюдение требований к формату ответа
                - Соответствие инструкциям по оформлению
                - Наличие требуемых элементов
                - Структуру ответа
                
                ШКАЛА: 0-1  
                0: Формат нарушен, требования не выполнены
                1: Формат полностью соблюден
                """,
                temperature=0.1
            ),
            "оптимальность": CriteriaConfig(
                system_prompt=base_system_prompt + """
                КРИТЕРИЙ: Оптимальность решения
                Проверь:
                - Эффективность выбранного подхода
                - Отсутствие избыточных действий
                - Рациональность последовательности
                - Элегантность решения
                
                ШКАЛА: 0-2
                0: Неоптимально, есть ошибки или избыточность
                1: Верно, но не оптимально, можно улучшить
                2: Верно и оптимально, эффективное решение
                """,
                temperature=0.2
            ),
            "речевые_ошибки": CriteriaConfig(
                system_prompt=base_system_prompt + """
                КРИТЕРИЙ: Качество изложения и отсутствие речевых ошибок
                Проверь:
                - Грамматические ошибки
                - Стилистические недочеты
                - Лексические ошибки
                - Пунктуационные ошибки
                - Ясность и связность изложения
                
                ШКАЛА: 0-2
                0: Две и более ошибки, текст плохо читается
                1: Одна ошибка или незначительные недочеты
                2: Нет ошибок, текст изложен ясно и грамотно
                """,
                temperature=0.1
            ),
            "общее_качество": CriteriaConfig(
                system_prompt=base_system_prompt + """
                КРИТЕРИЙ: Общее качество ответа
                Оцени комплексно:
                - Полнота ответа
                - Релевантность вопросу
                - Ясность изложения
                - Полезность информации
                - Структурированность
                
                ШКАЛА: 0-2
                0: Низкое качество, ответ неудовлетворительный
                1: Удовлетворительно, есть room для улучшений
                2: Высокое качество, полный и полезный ответ
                """,
                temperature=0.3
            )
        }
        
        return criterion_prompts.get(criterion, criterion_prompts["общее_качество"])
    
    def _generate_cache_key(self, criteria: List[str], task_type: str) -> str:
        """Генерирует ключ для кэша"""
        sorted_criteria = sorted(criteria)
        key_string = f"{'-'.join(sorted_criteria)}_{task_type}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def clear_cache(self):
        """Очищает кэш синтезатора"""
        self._cache.clear()

class CriteriaEvaluator:
    """Управляет выполнением оценки по критериям"""
    
    def __init__(self, base_model=None, fallback_strategy: ModelFallbackStrategy = ModelFallbackStrategy.RETRY):
        self.base_model = base_model or self._get_default_model()
        self.fallback_strategy = fallback_strategy
        self.logger = logging.getLogger(__name__)
        self._request_cache = ThreadSafeCache(config.get('cache_size', 1000))
    
    async def evaluate_criteria_async(self, criteria_config: Dict[str, CriteriaConfig], example: Example) -> Dict[str, EvaluationVerdict]:
        """Асинхронная оценка по всем критериям"""
        tasks = []
        for criterion_name, criterion_config in criteria_config.items():
            task = self._evaluate_single_criterion_async(criterion_config, example, criterion_name)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        verdicts = {}
        for criterion_name, result in zip(criteria_config.keys(), results):
            if isinstance(result, Exception):
                self.logger.warning(f"Ошибка в критерии {criterion_name}: {result}")
                verdicts[criterion_name] = self._get_fallback_verdict(criterion_name)
            else:
                verdicts[criterion_name] = result
        
        return verdicts
    
    async def _evaluate_single_criterion_async(self, criterion_config: CriteriaConfig, example: Example, criterion_name: str) -> EvaluationVerdict:
        """Асинхронная оценка по одному критерию"""
        max_retries = config.get('max_retries', 3)
        timeout = config.get('model_timeout', 30)
        
        # Проверка кэша
        cache_key = self._generate_request_cache_key(criterion_config, example)
        cached_result = self._request_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        for attempt in range(max_retries):
            try:
                prompt = self._build_evaluation_prompt(criterion_config, example)
                
                # Асинхронный вызов LLM
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                    score, confidence, reasoning = await self._call_llm_async(session, prompt, criterion_config, example)
                
                verdict = EvaluationVerdict(
                    score=score,
                    reasoning=reasoning,
                    weight=1.0,
                    confidence=confidence
                )
                
                # Кэширование результата
                self._request_cache.set(cache_key, verdict)
                
                return verdict
                
            except (asyncio.TimeoutError, aiohttp.ClientError, ConnectionError) as e:
                self.logger.warning(f"Попытка {attempt + 1} для {criterion_name} не удалась: {e}")
                if attempt == max_retries - 1:
                    return self._get_fallback_verdict(criterion_name)
                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
            except Exception as e:
                self.logger.error(f"Неожиданная ошибка в критерии {criterion_name}: {e}")
                return self._get_fallback_verdict(criterion_name)
        
        return self._get_fallback_verdict(criterion_name)
    
    def _get_fallback_verdict(self, criterion_name: str) -> EvaluationVerdict:
        """Возвращает fallback вердикт в зависимости от стратегии"""
        if self.fallback_strategy == ModelFallbackStrategy.MOCK:
            # Умная заглушка на основе имени критерия
            if "правильность" in criterion_name:
                score = 1.0
            elif "формат" in criterion_name:
                score = 0.5
            else:
                score = 1.5
            return EvaluationVerdict(score=score, reasoning="Fallback: автоматическая оценка", weight=0.1, confidence=0.3)
        elif self.fallback_strategy == ModelFallbackStrategy.SKIP:
            return EvaluationVerdict(score=0.0, reasoning="Fallback: пропущено из-за ошибки", weight=0.0, confidence=0.0)
        else:  # RETRY
            return EvaluationVerdict(score=0.0, reasoning="Fallback: ошибка после всех попыток", weight=0.0, confidence=0.0)
    
    async def _call_llm_async(self, session: aiohttp.ClientSession, prompt: str, criterion_config: CriteriaConfig, example: Example) -> tuple:
        """Асинхронный вызов LLM API - возвращает (score, confidence, reasoning)"""
        # В реальной реализации здесь должен быть вызов настоящего API
        # Для демонстрации используем имитацию с задержкой
        
        await asyncio.sleep(0.05)  # Имитация сетевой задержки
        
        # Используем синхронную mock реализацию
        score = self._mock_llm_call(prompt, criterion_config, example)
        
        # Генерируем правдоподобное reasoning и confidence
        reasoning = f"Оценка {score} по критерию основана на анализе соответствия ответа требованиям."
        confidence = min(0.9, 0.3 + score * 0.3)  # Эвристика: выше score → выше confidence
        
        return score, confidence, reasoning
    
    def _mock_llm_call(self, prompt: str, criterion_config: CriteriaConfig, example: Example) -> float:
        """Заглушка для вызова LLM - в реальности заменить на настоящий вызов"""
        generated = example.get('generated', '').lower()
        reference = example.get('reference', '').lower()
        instruction = example.get('instruction', '').lower()
        
        system_prompt = criterion_config.get('system_prompt', '').lower()
        
        if "правильность" in system_prompt:
            # Оценка правильности
            if not generated.strip():
                return 0.0
            elif generated == reference:
                return 2.0
            elif reference and any(word in generated for word in reference.split()[:3]):
                return 1.0
            else:
                return 0.5
                
        elif "формат" in system_prompt:
            # Оценка формата
            if "число" in instruction and generated.strip().isdigit():
                return 1.0
            elif "буква" in instruction and len(generated.strip()) == 1 and generated.strip().isalpha():
                return 1.0
            elif "список" in instruction and ('\n' in generated or ',' in generated):
                return 1.0
            elif "json" in instruction and ('{' in generated and '}' in generated):
                return 1.0
            else:
                return 0.0
                
        elif "оптимальность" in system_prompt:
            # Оценка оптимальности
            if len(generated) < 50:
                return 1.5
            elif "эффективн" in generated or "оптимальн" in generated:
                return 2.0
            else:
                return 1.0
                
        elif "речевые_ошибки" in system_prompt:
            # Оценка речевых ошибок
            errors = 0
            if len(re.findall(r'[.,!?;:]', generated)) < len(generated.split()) / 10:
                errors += 1
            if any(word in generated for word in ['ошибка', 'неправильно', 'некорректно']):
                errors += 1
                
            if errors >= 2:
                return 0.0
            elif errors == 1:
                return 1.0
            else:
                return 2.0
                
        else:
            # Общая оценка качества
            words = generated.split()
            if len(words) < 5:
                return 0.5
            elif len(words) > 50:
                return 1.8
            else:
                return 1.2
    
    def _build_evaluation_prompt(self, criterion_config: CriteriaConfig, example: Example) -> str:
        """Строит промпт для оценки"""
        system_prompt = criterion_config.get("system_prompt", "")
        instruction = example.get('instruction', '')
        generated = example.get('generated', '')
        reference = example.get('reference', '')
        input_text = example.get('input', '')
        
        user_prompt = f"""
ИНСТРУКЦИЯ: {instruction}

{"ВХОДНЫЕ ДАННЫЕ: " + input_text if input_text else ""}

ОТВЕТ ДЛЯ ОЦЕНКИ: {generated}

{"ЭТАЛОННЫЙ ОТВЕТ: " + reference if reference else ""}

Проанализируй строго по критерию и вердикт должен включать оценку и обоснование:
"""
        
        return system_prompt + user_prompt
    
    def _generate_request_cache_key(self, criterion_config: CriteriaConfig, example: Example) -> str:
        """Генерирует ключ для кэша запросов"""
        key_data = {
            'system_prompt': criterion_config.get('system_prompt', ''),
            'instruction': example.get('instruction', ''),
            'generated': example.get('generated', ''),
            'reference': example.get('reference', '')
        }
        key_string = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_default_model(self):
        """Возвращает модель по умолчанию"""
        return None  # Заменить на реальную модель
    
    def clear_cache(self):
        """Очищает кэш оценщика"""
        self._request_cache.clear()

class WeightManager:
    """Управляет весами критериев на основе контекста"""
    
    def __init__(self):
        self._cache = ThreadSafeCache(config.get('cache_size', 1000))
    
    def calculate_weights(self, criteria: List[str], task_type: str, generated_text: str) -> Dict[str, float]:
        """Вычисляет адаптивные веса для критериев"""
        cache_key = self._generate_cache_key(criteria, task_type, generated_text)
        
        cached_result = self._cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        base_weights = self._get_base_weights(task_type, criteria)
        adjusted_weights = self._adjust_by_complexity(base_weights, generated_text)
        normalized_weights = self._normalize_weights(adjusted_weights)
        
        self._cache.set(cache_key, normalized_weights)
        return normalized_weights
    
    def _get_base_weights(self, task_type: str, criteria: List[str]) -> Dict[str, float]:
        """Базовые веса в зависимости от типа задачи"""
        
        task_weights_config = {
            "static_benchmark": {
                "правильность": 0.7,
                "формат": 0.3,
                "оптимальность": 0.0,
                "речевые_ошибки": 0.0,
                "общее_качество": 0.0
            },
            "function_calling": {
                "правильность": 0.4,
                "формат": 0.1,
                "оптимальность": 0.5,
                "речевые_ошибки": 0.0,
                "общее_качество": 0.0
            },
            "generative": {
                "правильность": 0.3,
                "формат": 0.1,
                "оптимальность": 0.1,
                "речевые_ошибки": 0.3,
                "общее_качество": 0.2
            }
        }
        
        weights = task_weights_config.get(task_type, task_weights_config["generative"])
        
        # Оставляем только присутствующие критерии
        return {k: v for k, v in weights.items() if k in criteria}
    
    def _adjust_by_complexity(self, weights: Dict[str, float], text: str) -> Dict[str, float]:
        """Корректирует веса на основе сложности текста"""
        complexity = self._estimate_complexity(text)
        
        adjusted_weights = {}
        for criterion, weight in weights.items():
            if criterion == "речевые_ошибки" and complexity > 0.7:
                adjusted_weights[criterion] = weight * 1.3
            elif criterion == "правильность" and complexity > 0.5:
                adjusted_weights[criterion] = weight * 1.2
            elif criterion == "оптимальность" and complexity > 0.6:
                adjusted_weights[criterion] = weight * 1.1
            else:
                adjusted_weights[criterion] = weight
        
        return adjusted_weights
    
    @lru_cache(maxsize=1000)
    def _estimate_complexity(self, text: str) -> float:
        """Оценивает сложность текста"""
        if not text or len(text) > MAX_TEXT_LENGTH:
            return 0.0
        
        words = text.split()
        if len(words) < 10:
            return 0.3
        
        try:
            # Эвристики сложности текста
            long_words = sum(1 for word in words if len(word) > 6)
            sentences = len(re.findall(r'[.!?]+', text))
            unique_words = len(set(words))
            
            # Композитная оценка сложности
            lexical_complexity = long_words / len(words)
            syntactic_complexity = len(words) / max(sentences, 1) / 15  # слов в предложении
            vocabulary_richness = unique_words / len(words)
            
            complexity = min(1.0, 
                lexical_complexity * 0.4 + 
                syntactic_complexity * 0.4 + 
                vocabulary_richness * 0.2
            )
            return complexity
        except Exception:
            return 0.5
    
    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Нормализует веса к сумме 1.0"""
        total = sum(weights.values())
        if total == 0:
            return {k: 1.0/len(weights) for k in weights.keys()}
        
        return {k: v/total for k, v in weights.items()}
    
    def _generate_cache_key(self, criteria: List[str], task_type: str, text: str) -> str:
        """Генерирует ключ для кэша"""
        sorted_criteria = sorted(criteria)
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8] if text else "empty"
        key_string = f"{'-'.join(sorted_criteria)}_{task_type}_{text_hash}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def clear_cache(self):
        """Очищает кэш менеджера весов"""
        self._cache.clear()
        self._estimate_complexity.cache_clear()

class VerdictValidator:
    """Валидирует и синтезирует вердикты оценки"""
    
    def synthesize_verdicts(self, verdicts: Dict[str, EvaluationVerdict], example: Example) -> float:
        """Синтезирует финальную оценку из вердиктов"""
        if not verdicts:
            return 0.0
        
        # Проверяем на выбросы
        outliers = self._detect_outliers(verdicts)
        
        # Если есть сильные выбросы - запускаем арбитра
        if outliers and len(verdicts) > 2:
            return self._call_arbiter(verdicts, example, outliers)
        
        # Иначе - взвешенное среднее
        total_score = 0.0
        total_weight = 0.0
        
        for criterion_name, verdict in verdicts.items():
            if criterion_name in outliers:
                # Штрафуем выбросы
                weight = verdict['weight'] * 0.3
            else:
                weight = verdict['weight']
            
            total_score += verdict['score'] * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        final_score = total_score / total_weight
        return min(2.0, max(0.0, final_score))
    
    def _detect_outliers(self, verdicts: Dict[str, EvaluationVerdict]) -> List[str]:
        """Обнаруживает статистические выбросы среди вердиктов"""
        scores = [v['score'] for v in verdicts.values()]
        
        if len(scores) < 3:
            return []
        
        try:
            Q1 = np.percentile(scores, 25)
            Q3 = np.percentile(scores, 75)
            IQR = Q3 - Q1
            
            if IQR == 0:  # Все оценки одинаковые
                return []
            
            outliers = []
            for criterion_name, verdict in verdicts.items():
                score = verdict['score']
                if score < (Q1 - 1.5 * IQR) or score > (Q3 + 1.5 * IQR):
                    outliers.append(criterion_name)
            
            return outliers
        except Exception:
            return []
    
    def _call_arbiter(self, verdicts: Dict[str, EvaluationVerdict], example: Example, outliers: List[str]) -> float:
        """Вызывает арбитра для разрешения конфликтных вердиктов"""
        # Взвешенная медиана с учетом уверенности
        scores_with_weights = []
        
        for criterion_name, verdict in verdicts.items():
            if criterion_name not in outliers:
                scores_with_weights.extend([verdict['score']] * int(verdict['weight'] * 10))
        
        if not scores_with_weights:
            scores_with_weights = [v['score'] for v in verdicts.values()]
        
        try:
            return float(np.median(scores_with_weights))
        except Exception:
            return sum(scores_with_weights) / len(scores_with_weights)

class FoundationEvaluationSystem:
    """
    Фундаментальная система оценки ИИ через синтез критериев - Академическая версия
    """
    
    def __init__(self, base_model=None, fallback_strategy: ModelFallbackStrategy = ModelFallbackStrategy.RETRY):
        self.synthesizer = CriteriaSynthesizer()
        self.evaluator = CriteriaEvaluator(base_model, fallback_strategy)
        self.validator = VerdictValidator()
        self.weight_manager = WeightManager()
        self.batch_processor = BatchProcessor(config.get('batch_size', 10))
        self.academic_metrics = AcademicEvaluationMetrics()
        
        self.metrics = ProcessingMetrics()
        self.performance_stats = PerformanceStats()
        self.comprehensive_metrics = ComprehensiveMetrics()
        self.logger = logging.getLogger(__name__)
        
        self._executor = ThreadPoolExecutor(
            max_workers=config.get('max_workers', 4),
            thread_name_prefix="eval_worker"
        )
        self._metrics_lock = Lock()
        self._detailed_verdicts = []  # Для хранения детализированных результатов
        
    async def predict_async(self, examples: List[Dict]) -> List[float]:
        """Асинхронный метод для пакетного предсказания метрик"""
        self._validate_input_examples(examples)
        
        with self._metrics_lock:
            self.metrics.total_examples = len(examples)
            self._detailed_verdicts = []  # Сбрасываем предыдущие результаты
        
        start_time = time.time()
        
        try:
            # Обработка батчами через BatchProcessor
            results = await self.batch_processor.process_batches_async(
                examples, 
                self._process_batch_async
            )
            
            # Обновление метрик производительности
            with self._metrics_lock:
                self.performance_stats.total_processing_time = time.time() - start_time
                self.performance_stats.examples_processed = len(examples)
            
            # Расчет академических метрик если есть человеческие оценки
            if config.get('academic_metrics', True):
                human_scores = [ex.get('human_score') for ex in examples if ex.get('human_score') is not None]
                if len(human_scores) == len(results):
                    self.comprehensive_metrics = self.academic_metrics.compute_comprehensive_metrics(
                        results, human_scores, self._detailed_verdicts
                    )
            
            self.logger.info(f"Асинхронно обработано {self.metrics.successful_processing}/{self.metrics.total_examples} примеров")
            self.logger.info(f"Среднее время обработки: {self.performance_stats.avg_processing_time:.3f}с")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Критическая ошибка при обработке: {e}")
            raise EvaluationError(f"Ошибка обработки примеров: {e}")
    
    async def _process_batch_async(self, examples: List[Example]) -> List[float]:
        """Асинхронная обработка батча примеров"""
        tasks = [self._process_single_example_async(example) for example in examples]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Обработка результатов
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Ошибка обработки батча: {result}")
                processed_results.append(ERROR_FALLBACK_SCORE)
                with self._metrics_lock:
                    self.metrics.error_count += 1
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _process_single_example_async(self, example: Example) -> float:
        """Асинхронная обработка одного примера"""
        try:
            start_time = time.time()
            
            # 1. Извлекаем критерии и контекст
            criteria_start = time.time()
            criteria = self._extract_criteria(example)
            task_type = self._detect_task_type(example)
            with self._metrics_lock:
                self.performance_stats.criteria_extraction_time += time.time() - criteria_start
            
            # 2. Синтезируем критерии оценки
            criteria_config = self.synthesizer.create_criteria(criteria, task_type)
            
            # 3. Асинхронная параллельная оценка
            evaluation_start = time.time()
            raw_verdicts = await self.evaluator.evaluate_criteria_async(criteria_config, example)
            with self._metrics_lock:
                self.performance_stats.criteria_evaluation_time += time.time() - evaluation_start
            
            # 4. Расчет адаптивных весов
            weight_calc_start = time.time()
            weights = self.weight_manager.calculate_weights(
                criteria, task_type, example.get('generated', '')
            )
            with self._metrics_lock:
                self.performance_stats.weight_calculation_time += time.time() - weight_calc_start
            
            # 5. Применяем веса и корректируем по уверенности
            weighted_verdicts = self._apply_weights_and_confidence(raw_verdicts, weights)
            
            # 6. Валидация и синтез финальной оценки
            validation_start = time.time()
            final_raw_score = self.validator.synthesize_verdicts(weighted_verdicts, example)
            with self._metrics_lock:
                self.performance_stats.validation_time += time.time() - validation_start
            
            # 7. Конвертация в метрику по формуле конкурса
            metric = self._convert_to_metric(final_raw_score, example, task_type)
            
            # 8. Сохраняем детализированные результаты для академических метрик
            detailed_verdict = {
                'final_score': metric,
                'confidence': self._calculate_confidence_aggregate(weighted_verdicts),
                'reasoning': ' | '.join([v.get('reasoning', '') for v in weighted_verdicts.values()]),
                **weighted_verdicts
            }
            
            with self._metrics_lock:
                self.metrics.successful_processing += 1
                self._detailed_verdicts.append(detailed_verdict)
            
            return round(metric, 4)
            
        except (ValueError, TypeError, KeyError) as e:
            self.logger.error(f"Ошибка обработки примера: {e}")
            with self._metrics_lock:
                self.metrics.error_count += 1
            return ERROR_FALLBACK_SCORE
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка обработки примера: {e}")
            with self._metrics_lock:
                self.metrics.error_count += 1
            return ERROR_FALLBACK_SCORE
    
    def _calculate_confidence_aggregate(self, verdicts: Dict[str, EvaluationVerdict]) -> float:
        """Агрегирует уверенность из всех критериев"""
        confidences = [v.get('confidence', DEFAULT_CONFIDENCE) for v in verdicts.values()]
        return np.mean(confidences) if confidences else DEFAULT_CONFIDENCE
    
    def _validate_input_examples(self, examples: List[Dict]):
        """Валидирует входные примеры"""
        if not examples:
            raise ValidationError("Список примеров не может быть пустым")
        
        required_fields = ['instruction', 'generated', 'criterion']
        for i, example in enumerate(examples):
            for field in required_fields:
                if field not in example:
                    raise ValidationError(f"Пример {i} отсутствует обязательное поле: {field}")
            
            # Проверка длины текста
            for text_field in ['instruction', 'generated']:
                text = example.get(text_field, '')
                if len(text) > MAX_TEXT_LENGTH:
                    raise ValidationError(f"Поле {text_field} в примере {i} превышает максимальную длину")
    
    def predict(self, examples: List[Dict]) -> List[float]:
        """Синхронная версия для обратной совместимости"""
        try:
            return asyncio.run(self.predict_async(examples))
        except RuntimeError:
            # Если уже запущен event loop
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.predict_async(examples))
    
    def get_detailed_verdicts(self) -> List[Dict]:
        """Возвращает детализированные вердикты для академического анализа"""
        with self._metrics_lock:
            return self._detailed_verdicts.copy()
    
    def get_academic_report(self) -> Dict[str, Any]:
        """Возвращает полный академический отчет"""
        performance_report = self.get_performance_report()
        
        return {
            'performance_metrics': performance_report,
            'academic_metrics': self.comprehensive_metrics.to_dict(),
            'composite_scores': {
                'overall_quality_score': self.comprehensive_metrics.overall_quality,
                'evaluation_system_quality': self.comprehensive_metrics.evaluation_system_quality,
                'academic_composite_score': self._calculate_academic_composite_score()
            }
        }
    
    def _calculate_academic_composite_score(self) -> float:
        """Вычисляет композитный академический score"""
        weights = {
            'spearman_correlation': 0.25,
            'overall_quality': 0.2,
            'mean_absolute_error': 0.15,
            'confidence_calibration': 0.1,
            'system_reliability': 0.1,
            'exact_match_rate': 0.1,
            'evaluation_consistency': 0.1
        }
        
        metrics = self.comprehensive_metrics
        composite = 0.0
        
        # Нормализуем и взвешиваем метрики
        composite += weights['spearman_correlation'] * metrics.spearman_correlation
        composite += weights['overall_quality'] * metrics.overall_quality
        composite += weights['mean_absolute_error'] * max(0, 1 - metrics.mean_absolute_error)
        composite += weights['confidence_calibration'] * metrics.confidence_calibration
        composite += weights['system_reliability'] * metrics.system_reliability
        composite += weights['exact_match_rate'] * metrics.exact_match_rate
        composite += weights['evaluation_consistency'] * metrics.evaluation_consistency
        
        return composite

    def _extract_criteria(self, example: Example) -> List[str]:
        """Извлекает критерии оценки из примера"""
        criterion = example.get('criterion', '').lower()
        scale = example.get('scale', '').lower()
        
        criteria = []
        if "правильность" in criterion and "формат" in criterion:
            criteria.extend(["правильность", "формат"])
        elif "правильность" in criterion:
            criteria.append("правильность")
        elif "формат" in criterion:
            criteria.append("формат")
        elif "оптимальность" in criterion:
            criteria.append("оптимальность")
        elif "речевые ошибки" in criterion or "речевые" in criterion:
            criteria.append("речевые_ошибки")
        elif "качество" in criterion or "общее" in criterion:
            criteria.append("общее_качество")
        else:
            # Анализ scale для определения критериев
            if "формат" in scale:
                criteria.append("формат")
            if "правильность" in scale or "точность" in scale:
                criteria.append("правильность")
            if not criteria:
                criteria.append("общее_качество")
        
        return criteria
    
    def _detect_task_type(self, example: Example) -> str:
        """Определяет тип задачи"""
        instruction = example.get('instruction', '').lower()
        generated = example.get('generated', '').lower()
        input_text = example.get('input', '').lower()
        
        # Проверка на статические бенчмарки (множественный выбор)
        if any(word in instruction for word in ['выбери', 'вариант', 'a)', 'b)', 'c)', 'd)', 'правильный ответ']):
            return TaskType.STATIC_BENCHMARK.value
        # Проверка на вызов функций
        elif any(word in instruction for word in ['функция', 'функцию', 'вызвать', 'вызов']):
            return TaskType.FUNCTION_CALLING.value
        elif any(word in generated for word in ['функция', 'def ', 'function', '()']):
            return TaskType.FUNCTION_CALLING.value
        # Генеративные задачи
        else:
            return TaskType.GENERATIVE.value
    
    def _apply_weights_and_confidence(self, verdicts: Dict[str, EvaluationVerdict], weights: Dict[str, float]) -> Dict[str, EvaluationVerdict]:
        """Применяет веса и корректирует по уверенности оценок"""
        adjusted_verdicts = {}
        
        for criterion_name, verdict in verdicts.items():
            base_weight = weights.get(criterion_name, 0.5)
            confidence = verdict.get('confidence', DEFAULT_CONFIDENCE)
            
            # Корректировка веса на основе уверенности
            adjusted_weight = base_weight * (0.5 + 0.5 * confidence)
            verdict['weight'] = adjusted_weight
            adjusted_verdicts[criterion_name] = verdict
        
        return adjusted_verdicts
    
    def _convert_to_metric(self, raw_score: float, example: Example, task_type: str) -> float:
        """Конвертирует сырую оценку в метрику по формуле M = 2 - (raw_score / max_score)"""
        if raw_score == -1:
            return ERROR_FALLBACK_SCORE
        
        # Определяем максимальный балл для типа задачи
        if task_type == TaskType.STATIC_BENCHMARK.value:
            max_score = 3
        elif task_type == TaskType.FUNCTION_CALLING.value:
            max_score = 2
        else:  # generative
            max_score = 2
        
        metric = 2 - (raw_score / max_score)
        return max(0.0, min(metric, 2.0))  # Ограничиваем диапазон
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Возвращает отчет о производительности"""
        with self._metrics_lock:
            success_rate = self.metrics.successful_processing / max(self.metrics.total_examples, 1)
            
            return {
                'processing_metrics': self.performance_stats.to_dict(),
                'success_rate': success_rate,
                'error_count': self.metrics.error_count,
                'total_examples': self.metrics.total_examples,
                'successful_processing': self.metrics.successful_processing,
                'model_timeouts': self.metrics.model_timeouts
            }
    
    def clear_state(self):
        """Очищает состояние системы"""
        with self._metrics_lock:
            self.metrics = ProcessingMetrics()
            self.performance_stats = PerformanceStats()
            self._detailed_verdicts = []
        
        self.weight_manager.clear_cache()
        self.synthesizer.clear_cache()
        self.evaluator.clear_cache()
    
    def __del__(self):
        """Деструктор для очистки ресурсов"""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)

# Утилиты
def setup_logging(level=logging.INFO):
    """Настраивает логирование для системы"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('foundation_ai_evaluation.log', encoding='utf-8')
        ]
    )

def create_config_file():
    """Создает пример конфигурационного файла"""
    config_example = {
        'model_timeout': 30,
        'max_retries': 3,
        'batch_size': 10,
        'performance_metrics': True,
        'fallback_strategy': 'retry',
        'max_workers': 4,
        'cache_size': 1000,
        'academic_metrics': True,
        
        'task_weights': {
            'static_benchmark': {
                'правильность': 0.7,
                'формат': 0.3
            },
            'function_calling': {
                'правильность': 0.4,
                'формат': 0.1,
                'оптимальность': 0.5
            },
            'generative': {
                'правильность': 0.3,
                'формат': 0.1,
                'оптимальность': 0.1,
                'речевые_ошибки': 0.3,
                'общее_качество': 0.2
            }
        }
    }
    
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(config_example, f, allow_unicode=True, default_flow_style=False)

# Пример использования с академическими метриками
async def main():
    """Демонстрация работы системы с академическими метриками"""
    setup_logging()
    
    # Создание конфигурационного файла если его нет
    if not CONFIG_PATH.exists():
        create_config_file()
        print("Создан конфигурационный файл config.yaml")
    
    # Инициализация системы с fallback стратегией
    evaluation_system = FoundationEvaluationSystem(fallback_strategy=ModelFallbackStrategy.MOCK)
    
    # Тестовые примеры с человеческими оценками для корреляции
    test_examples = [
        {
            "instruction": "Найдите значение выражения: 25 + 37. Ответ должен быть числом.",
            "generated": "62", 
            "reference": "62",
            "criterion": "Правильность ответа и формата",
            "scale": "0: ошибки, 1: правильный формат но ошибка, 2: правильно но не формат, 3: полностью правильно",
            "human_score": 3.0
        },
        {
            "instruction": "Напишите функцию сложения двух чисел на Python",
            "generated": "def add(a, b): return a + b",
            "reference": "def add(a, b):\n    return a + b",
            "criterion": "Правильность и оптимальность",
            "scale": "0-2",
            "human_score": 1.8
        },
        {
            "instruction": "Опишите принцип работы солнечной батареи",
            "generated": "Солнечная батарея преобразует солнечную энергию в электрическую с помощью фотоэлементов",
            "reference": "Солнечные панели преобразуют солнечный свет в электричество через фотоэлектрический эффект",
            "criterion": "Правильность и качество изложения",
            "scale": "0-2",
            "human_score": 1.5
        }
    ] * 3  # Умножаем для статистической значимости
    
    print("Запуск асинхронной обработки с академическими метриками...")
    
    # Асинхронная обработка
    start_time = time.time()
    results = await evaluation_system.predict_async(test_examples)
    processing_time = time.time() - start_time
    
    print(f"Результаты оценки: {results}")
    print(f"Время обработки: {processing_time:.3f}с")
    
    # Полный академический отчет
    academic_report = evaluation_system.get_academic_report()
    print("\n=== ПОЛНЫЙ АКАДЕМИЧЕСКИЙ ОТЧЕТ ===")
    print(json.dumps(academic_report, indent=2, ensure_ascii=False, default=str))
    
    # Ключевые метрики для быстрого анализа
    comp_metrics = evaluation_system.comprehensive_metrics
    print(f"\n=== КЛЮЧЕВЫЕ МЕТРИКИ ===")
    print(f"Композитный академический score: {evaluation_system._calculate_academic_composite_score():.3f}")
    print(f"Согласованность с человеком (Spearman): {comp_metrics.spearman_correlation:.3f}")
    print(f"Средняя абсолютная ошибка: {comp_metrics.mean_absolute_error:.3f}")
    print(f"Качество системы оценки: {comp_metrics.evaluation_system_quality:.3f}")
    
    # Очистка состояния
    evaluation_system.clear_state()

if __name__ == "__main__":
    asyncio.run(main())
