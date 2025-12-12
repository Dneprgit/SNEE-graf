"""
FastAPI Backend для СНЭЭ Graf
Веб-версия системы расчета диспетчерского графика СНЭЭ
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import sys
import os
import numpy as np
import pandas as pd
from io import BytesIO

from energy_storage_calculator import EnergyStorageCalculator, calculate_optimal_parameters
from data_manager import DataManager
from ppw_calculator import PPWCalculator

app = FastAPI(
    title="СНЭЭ Graf API",
    description="API для расчета диспетчерского графика системы накопления электрической энергии",
    version="2.0.0"
)

# CORS middleware для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретный домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Модели данных
class CalculationRequest(BaseModel):
    """Запрос на расчет графика СНЭЭ"""
    load_profile: List[float] = Field(..., min_items=24, max_items=24, 
                                      description="Суточный профиль баланса мощности (24 часа)")
    rated_power_mw: float = Field(..., gt=0, description="Мощность инвертора в МВт")
    rated_capacity_mwh: float = Field(..., gt=0, description="Емкость батареи в МВтч")
    efficiency: float = Field(..., gt=0, le=1, description="КПД цикла (0-1)")

    class Config:
        json_schema_extra = {
            "example": {
                "load_profile": [
                    1320, 1515, 1623, 1769, 1854, 1791, 1409, 860, 227, -261,
                    -618, -779, -845, -927, -927, -927, -862, -799, -669, -535,
                    -638, -370, 59, 963
                ],
                "rated_power_mw": 500,
                "rated_capacity_mwh": 2000,
                "efficiency": 0.95
            }
        }


class CalculationResponse(BaseModel):
    """Ответ с результатами расчета"""
    eess_schedule: List[float] = Field(..., description="График работы СНЭЭ (+ разряд, - заряд)")
    resulting_balance: List[float] = Field(..., description="Результирующий баланс мощности")
    soc: List[float] = Field(..., description="Состояние заряда батареи (SOC)")
    summary: dict = Field(..., description="Сводная информация о работе СНЭЭ")


# Эндпоинты
@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "СНЭЭ Graf API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/api/v1/health")
async def health_check():
    """Проверка работоспособности API"""
    return {"status": "healthy", "service": "SNEE Graf API"}


@app.get("/api/v1/default-profile")
async def get_default_profile():
    """Получить профиль баланса по умолчанию"""
    return {
        "load_profile": DataManager.get_default_profile(),
        "description": "Профиль баланса мощности из примера задания"
    }


@app.post("/api/v1/calculate", response_model=CalculationResponse)
async def calculate_dispatch_schedule(request: CalculationRequest):
    """
    Расчет диспетчерского графика работы СНЭЭ
    
    Принимает профиль баланса мощности и параметры СНЭЭ,
    возвращает оптимальный график работы и статистику
    """
    try:
        # Создание калькулятора
        calculator = EnergyStorageCalculator(
            rated_power_mw=request.rated_power_mw,
            rated_capacity_mwh=request.rated_capacity_mwh,
            efficiency=request.efficiency
        )
        
        # Расчет графика
        eess_schedule = calculator.calculate_dispatch_schedule(request.load_profile)
        
        # Расчет результирующего баланса
        resulting_balance = [
            request.load_profile[i] + eess_schedule[i] 
            for i in range(24)
        ]
        
        # Расчет SOC (состояния заряда)
        soc = calculate_soc(eess_schedule, request.rated_capacity_mwh)
        
        # Получение сводной информации
        summary = calculator.get_summary(request.load_profile, eess_schedule)
        
        return CalculationResponse(
            eess_schedule=eess_schedule.tolist(),
            resulting_balance=resulting_balance,
            soc=soc,
            summary=summary
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при расчете: {str(e)}")


@app.post("/api/v1/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    """
    Загрузка профиля баланса из Excel файла
    
    Файл должен содержать 24 числовых значения в одной строке или столбце
    """
    try:
        # Проверка типа файла
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400, 
                detail="Поддерживаются только файлы Excel (.xlsx, .xls)"
            )
        
        # Чтение файла
        contents = await file.read()
        
        # Временное сохранение
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(contents)
        
        # Импорт данных
        load_profile = DataManager.import_from_excel(temp_path)
        
        # Удаление временного файла
        os.remove(temp_path)
        
        if load_profile is None:
            raise HTTPException(
                status_code=400,
                detail="Не удалось найти 24 числовых значения в файле"
            )
        
        return {
            "success": True,
            "load_profile": load_profile,
            "message": f"Успешно загружено {len(load_profile)} значений"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке файла: {str(e)}")


@app.post("/api/v1/validate-profile")
async def validate_profile(load_profile: List[float]):
    """
    Валидация профиля баланса мощности
    
    Проверяет корректность входных данных
    """
    try:
        if len(load_profile) != 24:
            return {
                "valid": False,
                "error": f"Профиль должен содержать 24 значения, получено: {len(load_profile)}"
            }
        
        # Проверка на NaN и бесконечности
        if any(not np.isfinite(val) for val in load_profile):
            return {
                "valid": False,
                "error": "Профиль содержит некорректные значения (NaN или Infinity)"
            }
        
        # Статистика по профилю
        arr = np.array(load_profile)
        stats = {
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "mean": float(np.mean(arr)),
            "total_surplus": float(np.sum(arr[arr > 0])),
            "total_deficit": float(-np.sum(arr[arr < 0])),
        }
        
        return {
            "valid": True,
            "statistics": stats
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": f"Ошибка при валидации: {str(e)}"
        }


class OptimalParametersRequest(BaseModel):
    """Запрос на расчет оптимальных параметров СНЭЭ"""
    load_profile: List[float] = Field(..., min_items=24, max_items=24, 
                                      description="Суточный профиль баланса мощности (24 часа)")
    efficiency: float = Field(..., gt=0, le=1, description="КПД цикла (0-1)")

    class Config:
        json_schema_extra = {
            "example": {
                "load_profile": [
                    1320, 1515, 1623, 1769, 1854, 1791, 1409, 860, 227, -261,
                    -618, -779, -845, -927, -927, -927, -862, -799, -669, -535,
                    -638, -370, 59, 963
                ],
                "efficiency": 0.95
            }
        }


@app.post("/api/v1/calculate-optimal-parameters")
async def calculate_optimal_params(request: OptimalParametersRequest):
    """
    Расчет оптимальных параметров мощности инвертора и емкости батареи
    
    Реализует алгоритм VariatePowerAndVolume2 из VBA кода.
    Находит минимальные значения мощности и емкости, при которых
    дефицит энергии и мощности минимизируются.
    """
    try:
        optimal_power, optimal_capacity = calculate_optimal_parameters(
            request.load_profile,
            request.efficiency
        )
        
        return {
            "optimal_power_mw": optimal_power,
            "optimal_capacity_mwh": optimal_capacity,
            "message": "Оптимальные параметры успешно рассчитаны"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при расчете оптимальных параметров: {str(e)}")


# ============================================================================
# PPW Variant API (Второй вариант с квадратичной оптимизацией)
# ============================================================================

class PPWCalculateLoadRequest(BaseModel):
    """Запрос на расчет графика СНЭЭ для PPW варианта"""
    system_load: List[float] = Field(..., min_items=24, max_items=24,
                                     description="Суточный баланс мощности энергосистемы (24 часа)")
    rated_power_in_mw: float = Field(..., gt=0, description="Номинальная активная входная мощность в МВт")
    rated_power_out_mw: float = Field(..., gt=0, description="Номинальная активная выходная мощность в МВт")
    capacity_mwh: float = Field(..., gt=0, description="Энергия, фактически отдаваемая в рабочем диапазоне в МВтч")
    efficiency: float = Field(..., gt=0, le=1, description="КПД цикла (0-1)")

    class Config:
        json_schema_extra = {
            "example": {
                "system_load": [
                    27, 38, 84, 137.54, 21.33, -115.19, -166.18, -185.59, -130.30, -48.17,
                    37.55, 152, 103, 175, 99, 49, -47, 7, -130, -176, -117, -222, -205, -166
                ],
                "rated_power_in_mw": 95,
                "rated_power_out_mw": 140,
                "capacity_mwh": 360,
                "efficiency": 0.95
            }
        }


class PPWCalculateLoadResponse(BaseModel):
    """Ответ с результатами расчета графика СНЭЭ для PPW варианта"""
    eess_energy_available: List[float] = Field(..., description="Энергия в батарее на каждый час (МВтч)")
    eess_load: List[float] = Field(..., description="График нагрузки СНЭЭ (+ разряд, - заряд)")
    resulting_balance: List[float] = Field(..., description="Результирующий баланс мощности")
    soc: List[float] = Field(..., description="Состояние заряда батареи (SOC)")
    summary: dict = Field(..., description="Сводная информация о работе СНЭЭ")
    system_load_deficit: float = Field(..., description="Дефицит мощности с учетом СНЭЭ")
    system_load_reserve: float = Field(..., description="Резерв мощности с учетом СНЭЭ")
    termination_code: int = Field(..., description="Код завершения оптимизации")


class PPWOptimalParametersRequest(BaseModel):
    """Запрос на расчет оптимальных параметров СНЭЭ для PPW варианта"""
    system_load: List[float] = Field(..., min_items=24, max_items=24,
                                     description="Суточный баланс мощности энергосистемы (24 часа)")
    efficiency: float = Field(..., gt=0, le=1, description="КПД цикла (0-1)")

    class Config:
        json_schema_extra = {
            "example": {
                "system_load": [
                    27, 38, 84, 137.54, 21.33, -115.19, -166.18, -185.59, -130.30, -48.17,
                    37.55, 152, 103, 175, 99, 49, -47, 7, -130, -176, -117, -222, -205, -166
                ],
                "efficiency": 0.95
            }
        }


class PPWOptimalParametersResponse(BaseModel):
    """Ответ с оптимальными параметрами СНЭЭ для PPW варианта"""
    rated_power_in_mw: float = Field(..., description="Оптимальная номинальная активная входная мощность (МВт)")
    rated_power_out_mw: float = Field(..., description="Оптимальная номинальная активная выходная мощность (МВт)")
    capacity_mwh: float = Field(..., description="Оптимальная энергия в рабочем диапазоне (МВтч)")
    eess_energy_available: List[float] = Field(..., description="Энергия в батарее на каждый час (МВтч)")
    eess_load: List[float] = Field(..., description="График нагрузки СНЭЭ")
    resulting_balance: List[float] = Field(..., description="Результирующий баланс мощности")
    soc: List[float] = Field(..., description="Состояние заряда батареи (SOC)")
    summary: dict = Field(..., description="Сводная информация")
    system_load_deficit: float = Field(..., description="Дефицит мощности с учетом СНЭЭ")
    termination_code: int = Field(..., description="Код завершения оптимизации")


@app.post("/api/v1/ppw/calculate-load", response_model=PPWCalculateLoadResponse)
async def calculate_ppw_load(request: PPWCalculateLoadRequest):
    """
    Расчет графика работы СНЭЭ для заданных параметров (второй вариант PPW)
    
    Использует квадратичную оптимизацию (IPM метод) для расчета
    оптимального графика нагрузки СНЭЭ при заданных параметрах.
    """
    try:
        # Создание калькулятора
        calculator = PPWCalculator(efficiency=request.efficiency)
        
        # Расчет графика
        eess_energy_available, eess_load, system_load_deficit, system_load_reserve, termination_code = \
            calculator.calculate_optimal_load(
                system_load=request.system_load,
                rated_power_in=request.rated_power_in_mw,
                rated_power_out=request.rated_power_out_mw,
                capacity=request.capacity_mwh
            )
        
        # Расчет результирующего баланса
        resulting_balance = [
            request.system_load[i] + eess_load[i]
            for i in range(24)
        ]
        
        # Расчет SOC
        soc = calculate_soc(eess_load, request.capacity_mwh)
        
        # Получение сводной информации
        summary = calculator.get_summary(request.system_load, eess_load)
        
        return PPWCalculateLoadResponse(
            eess_energy_available=eess_energy_available.tolist(),
            eess_load=eess_load.tolist(),
            resulting_balance=resulting_balance,
            soc=soc,
            summary=summary,
            system_load_deficit=float(system_load_deficit),
            system_load_reserve=float(system_load_reserve),
            termination_code=int(termination_code)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при расчете графика PPW: {str(e)}")


@app.post("/api/v1/ppw/calculate-optimal-parameters", response_model=PPWOptimalParametersResponse)
async def calculate_ppw_optimal_parameters(request: PPWOptimalParametersRequest):
    """
    Расчет оптимальных параметров мощности и емкости СНЭЭ (второй вариант PPW)
    
    Использует квадратичную оптимизацию для нахождения минимальных значений
    номинальной входной/выходной мощности и емкости, при которых дефицит
    энергии и мощности минимизируются.
    """
    try:
        # Создание калькулятора
        calculator = PPWCalculator(efficiency=request.efficiency)
        
        # Расчет оптимальных параметров
        rated_power_in, rated_power_out, capacity, eess_energy_available, eess_load, system_load_deficit, termination_code = \
            calculator.calculate_optimized_parameters(system_load=request.system_load)
        
        # Расчет результирующего баланса
        resulting_balance = [
            request.system_load[i] + eess_load[i]
            for i in range(24)
        ]
        
        # Расчет SOC
        soc = calculate_soc(eess_load, capacity)
        
        # Получение сводной информации
        summary = calculator.get_summary(request.system_load, eess_load)
        
        return PPWOptimalParametersResponse(
            rated_power_in_mw=round(float(rated_power_in), 2),
            rated_power_out_mw=round(float(rated_power_out), 2),
            capacity_mwh=round(float(capacity), 2),
            eess_energy_available=eess_energy_available.tolist(),
            eess_load=eess_load.tolist(),
            resulting_balance=resulting_balance,
            soc=soc,
            summary=summary,
            system_load_deficit=float(system_load_deficit),
            termination_code=int(termination_code)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при расчете оптимальных параметров PPW: {str(e)}")


# ============================================================================
# Вспомогательные функции
# ============================================================================

def calculate_soc(eess_schedule: np.ndarray, rated_capacity: float) -> List[float]:
    """
    Расчет состояния заряда батареи в течение суток
    
    Args:
        eess_schedule: График работы СНЭЭ (+ разряд, - заряд)
        rated_capacity: Емкость батареи
    
    Returns:
        Список значений SOC для каждого часа
    """
    soc = [0.0]  # Начинаем с разряженной батареи
    
    for i in range(24):
        # Положительное значение = разряд (уменьшает SOC)
        # Отрицательное значение = заряд (увеличивает SOC)
        energy_change = -eess_schedule[i]
        new_soc = soc[-1] + energy_change
        
        # Ограничиваем в пределах [0, rated_capacity]
        new_soc = max(0, min(new_soc, rated_capacity))
        soc.append(new_soc)
    
    return soc[1:]  # Возвращаем без начального нуля


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=False)

