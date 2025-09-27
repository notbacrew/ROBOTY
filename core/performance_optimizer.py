# -*- coding: utf-8 -*-
"""
Модуль оптимизации производительности для больших нагрузок
"""

import gc
import os
import sys
import multiprocessing
import numpy as np
from typing import Dict, Any, Optional, List
import logging

# Попытка импорта psutil с fallback
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class PerformanceOptimizer:
    """Класс для оптимизации производительности системы"""
    
    def __init__(self):
        self.logger = logging.getLogger("ROBOTY.performance")
        self.original_settings = {}
        self.optimizations_applied = []
    
    def apply_system_optimizations(self) -> Dict[str, Any]:
        """Применяет системные оптимизации"""
        optimizations = {}
        
        try:
            # 1. Настройка приоритета процесса
            if hasattr(os, 'nice'):
                try:
                    os.nice(-5)  # Повышаем приоритет
                    optimizations['process_priority'] = 'high'
                    self.optimizations_applied.append('process_priority')
                except PermissionError:
                    self.logger.warning("Не удалось повысить приоритет процесса (требуются права администратора)")
            
            # 2. Настройка NumPy
            try:
                # Отключаем предупреждения для скорости
                np.seterr(all='ignore')
                # Используем все доступные ядра
                np.seterr(divide='ignore', invalid='ignore')
                optimizations['numpy_optimized'] = True
                self.optimizations_applied.append('numpy_optimized')
            except Exception as e:
                self.logger.error(f"Ошибка оптимизации NumPy: {e}")
            
            # 3. Настройка сборщика мусора
            try:
                # Более агрессивная сборка мусора
                gc.set_threshold(700, 10, 10)
                optimizations['gc_optimized'] = True
                self.optimizations_applied.append('gc_optimized')
            except Exception as e:
                self.logger.error(f"Ошибка оптимизации сборщика мусора: {e}")
            
            # 4. Настройка переменных окружения
            try:
                # Оптимизация для NumPy
                os.environ['OMP_NUM_THREADS'] = str(multiprocessing.cpu_count())
                os.environ['MKL_NUM_THREADS'] = str(multiprocessing.cpu_count())
                os.environ['NUMEXPR_NUM_THREADS'] = str(multiprocessing.cpu_count())
                optimizations['environment_optimized'] = True
                self.optimizations_applied.append('environment_optimized')
            except Exception as e:
                self.logger.error(f"Ошибка настройки переменных окружения: {e}")
            
            # 5. Настройка Python
            try:
                # Увеличиваем размер буфера для stdout/stderr
                sys.stdout.reconfigure(line_buffering=False)
                sys.stderr.reconfigure(line_buffering=False)
                optimizations['python_optimized'] = True
                self.optimizations_applied.append('python_optimized')
            except Exception as e:
                self.logger.error(f"Ошибка оптимизации Python: {e}")
            
            self.logger.info(f"Применено оптимизаций: {len(self.optimizations_applied)}")
            
        except Exception as e:
            self.logger.error(f"Ошибка применения системных оптимизаций: {e}")
        
        return optimizations
    
    def get_system_info(self) -> Dict[str, Any]:
        """Возвращает информацию о системе"""
        try:
            cpu_count = multiprocessing.cpu_count()
            
            if PSUTIL_AVAILABLE:
                memory = psutil.virtual_memory()
                cpu_usage = psutil.cpu_percent(interval=0.1)
                
                return {
                    'cpu_cores': cpu_count,
                    'cpu_usage': cpu_usage,
                    'memory_total_gb': memory.total / (1024**3),
                    'memory_available_gb': memory.available / (1024**3),
                    'memory_usage_percent': memory.percent,
                    'process_count': len(psutil.pids()),
                    'python_version': sys.version,
                    'platform': sys.platform
                }
            else:
                # Fallback без psutil
                return {
                    'cpu_cores': cpu_count,
                    'cpu_usage': 0.0,
                    'memory_total_gb': 0.0,
                    'memory_available_gb': 0.0,
                    'memory_usage_percent': 0.0,
                    'process_count': 0,
                    'python_version': sys.version,
                    'platform': sys.platform
                }
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о системе: {e}")
            return {}
    
    def optimize_for_scene_size(self, n_robots: int, n_operations: int) -> Dict[str, Any]:
        """Оптимизирует настройки в зависимости от размера сцены"""
        optimizations = {}
        
        try:
            # Определяем сложность сцены
            scene_complexity = n_robots * n_operations
            
            if scene_complexity <= 50:
                # Малая сцена
                optimizations.update({
                    'max_anim_frames': 200,
                    'anim_time_stride': 0.05,
                    'arm_segments': 5,
                    'use_3d_models': True,
                    'collision_check_density': 0.02,
                    'genetic_population': 30,
                    'genetic_generations': 50
                })
            elif scene_complexity <= 200:
                # Средняя сцена
                optimizations.update({
                    'max_anim_frames': 120,
                    'anim_time_stride': 0.1,
                    'arm_segments': 3,
                    'use_3d_models': True,
                    'collision_check_density': 0.05,
                    'genetic_population': 50,
                    'genetic_generations': 100
                })
            elif scene_complexity <= 500:
                # Большая сцена
                optimizations.update({
                    'max_anim_frames': 80,
                    'anim_time_stride': 0.15,
                    'arm_segments': 2,
                    'use_3d_models': False,
                    'collision_check_density': 0.1,
                    'genetic_population': 30,
                    'genetic_generations': 50
                })
            else:
                # Очень большая сцена
                optimizations.update({
                    'max_anim_frames': 40,
                    'anim_time_stride': 0.2,
                    'arm_segments': 1,
                    'use_3d_models': False,
                    'collision_check_density': 0.2,
                    'genetic_population': 20,
                    'genetic_generations': 30
                })
            
            self.logger.info(f"Оптимизация для сцены: {n_robots} роботов, {n_operations} операций")
            
        except Exception as e:
            self.logger.error(f"Ошибка оптимизации для размера сцены: {e}")
        
        return optimizations
    
    def monitor_memory_usage(self) -> Dict[str, float]:
        """Мониторит использование памяти"""
        try:
            if PSUTIL_AVAILABLE:
                process = psutil.Process()
                memory_info = process.memory_info()
                system_memory = psutil.virtual_memory()
                
                return {
                    'process_memory_mb': memory_info.rss / (1024**2),
                    'process_memory_percent': process.memory_percent(),
                    'system_memory_percent': system_memory.percent,
                    'available_memory_gb': system_memory.available / (1024**3)
                }
            else:
                # Fallback без psutil
                return {
                    'process_memory_mb': 0.0,
                    'process_memory_percent': 0.0,
                    'system_memory_percent': 0.0,
                    'available_memory_gb': 0.0
                }
        except Exception as e:
            self.logger.error(f"Ошибка мониторинга памяти: {e}")
            return {}
    
    def force_garbage_collection(self):
        """Принудительная сборка мусора"""
        try:
            collected = gc.collect()
            self.logger.debug(f"Собрано объектов: {collected}")
            return collected
        except Exception as e:
            self.logger.error(f"Ошибка сборки мусора: {e}")
            return 0
    
    def optimize_numpy_arrays(self, arrays: List[np.ndarray]) -> List[np.ndarray]:
        """Оптимизирует NumPy массивы"""
        try:
            optimized_arrays = []
            for arr in arrays:
                # Конвертируем в оптимальный тип данных
                if arr.dtype == np.float64:
                    arr = arr.astype(np.float32)
                elif arr.dtype == np.int64:
                    arr = arr.astype(np.int32)
                
                # Убеждаемся, что массив непрерывный
                if not arr.flags['C_CONTIGUOUS']:
                    arr = np.ascontiguousarray(arr)
                
                optimized_arrays.append(arr)
            
            return optimized_arrays
        except Exception as e:
            self.logger.error(f"Ошибка оптимизации массивов: {e}")
            return arrays
    
    def get_performance_recommendations(self) -> List[str]:
        """Возвращает рекомендации по производительности"""
        recommendations = []
        
        try:
            system_info = self.get_system_info()
            
            # Рекомендации по CPU
            if system_info.get('cpu_cores', 0) < 4:
                recommendations.append("Рекомендуется использовать систему с 4+ ядрами для лучшей производительности")
            
            # Рекомендации по памяти (только если psutil доступен)
            if PSUTIL_AVAILABLE:
                memory_gb = system_info.get('memory_total_gb', 0)
                if memory_gb < 8:
                    recommendations.append("Рекомендуется 8+ ГБ RAM для работы с большими сценами")
                elif memory_gb < 16:
                    recommendations.append("16+ ГБ RAM рекомендуется для очень больших сцен")
                
                # Рекомендации по использованию
                if system_info.get('memory_usage_percent', 0) > 80:
                    recommendations.append("Высокое использование памяти - закройте другие приложения")
                
                if system_info.get('cpu_usage', 0) > 90:
                    recommendations.append("Высокая нагрузка на CPU - дождитесь завершения текущих задач")
            else:
                recommendations.append("Установите psutil для расширенного мониторинга системы: pip install psutil")
            
        except Exception as e:
            self.logger.error(f"Ошибка получения рекомендаций: {e}")
        
        return recommendations
    
    def cleanup_resources(self):
        """Очищает ресурсы и откатывает оптимизации"""
        try:
            # Принудительная сборка мусора
            self.force_garbage_collection()
            
            # Сброс настроек NumPy
            try:
                np.seterr(all='warn')
            except Exception:
                pass
            
            # Сброс настроек сборщика мусора
            try:
                gc.set_threshold(700, 10, 10)  # Стандартные значения
            except Exception:
                pass
            
            self.logger.info("Ресурсы очищены, оптимизации откачены")
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки ресурсов: {e}")


# Глобальный экземпляр оптимизатора
performance_optimizer = PerformanceOptimizer()


def apply_performance_optimizations() -> Dict[str, Any]:
    """Применяет оптимизации производительности"""
    return performance_optimizer.apply_system_optimizations()


def get_system_performance_info() -> Dict[str, Any]:
    """Возвращает информацию о производительности системы"""
    return performance_optimizer.get_system_info()


def optimize_for_scene(n_robots: int, n_operations: int) -> Dict[str, Any]:
    """Оптимизирует настройки для конкретной сцены"""
    return performance_optimizer.optimize_for_scene_size(n_robots, n_operations)


def monitor_memory() -> Dict[str, float]:
    """Мониторит использование памяти"""
    return performance_optimizer.monitor_memory_usage()


def cleanup_performance_resources():
    """Очищает ресурсы производительности"""
    performance_optimizer.cleanup_resources()
