# Тест QP API через PowerShell
$base_url = "http://localhost:8002"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "ТЕСТИРОВАНИЕ QP API" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Тест 1: Расчет оптимальных параметров QP
Write-Host "`n[ТЕСТ 1] Расчет оптимальных параметров QP" -ForegroundColor Yellow

$load_profile = @(27, 38, 84, 137.54, 21.33, -115.19, -166.18, -185.59, -130.30, -48.17,
    37.55, 152, 103, 175, 99, 49, -47, 7, -130, -176, -117, -222, -205, -166)

$body = @{
    load_profile = $load_profile
    efficiency = 0.95
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$base_url/api/v1/calculate-optimal-parameters-qp" -Method Post -Body $body -ContentType "application/json"
    
    Write-Host "✓ Запрос успешен" -ForegroundColor Green
    Write-Host "`nОПТИМАЛЬНЫЕ ПАРАМЕТРЫ:" -ForegroundColor Cyan
    Write-Host "  Nin (входная мощность):   $($response.nin) МВт"
    Write-Host "  Nout (выходная мощность):  $($response.nout) МВт"
    Write-Host "  Capacity (емкость):        $($response.capacity) МВтч"
    Write-Host "  Deficit (дефицит):         $($response.deficit) МВт"
    
    # Дополнительные параметры
    $discharge_time = $response.capacity / $response.nout
    $charge_energy = $response.capacity / 0.95
    $charge_time = $charge_energy / $response.nin
    
    Write-Host "`nДОПОЛНИТЕЛЬНЫЕ ПАРАМЕТРЫ:" -ForegroundColor Cyan
    Write-Host "  Время разряда:             $([math]::Round($discharge_time, 2)) ч"
    Write-Host "  Энергия заряда:            $([math]::Round($charge_energy, 2)) МВтч"
    Write-Host "  Время заряда:              $([math]::Round($charge_time, 2)) ч"
    
} catch {
    Write-Host "✗ Ошибка: $_" -ForegroundColor Red
}

# Тест 2: Расчет диспетчерского графика с заданными параметрами
Write-Host "`n[ТЕСТ 2] Расчет диспетчерского графика QP" -ForegroundColor Yellow

$body2 = @{
    load_profile = $load_profile
    nin = 95.0
    nout = 140.0
    capacity = 360.0
    efficiency = 0.95
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri "$base_url/api/v1/calculate-dispatch-qp" -Method Post -Body $body2 -ContentType "application/json"
    
    Write-Host "✓ Запрос успешен" -ForegroundColor Green
    Write-Host "`nРЕЗУЛЬТАТЫ:" -ForegroundColor Cyan
    Write-Host "  Deficit (дефицит):  $($response2.deficit) МВт"
    Write-Host "  Reserve (резерв):   $($response2.reserve) МВт"
    
    Write-Host "`nГРАФИК РАБОТЫ (первые 8 часов):" -ForegroundColor Cyan
    Write-Host "  Час | Баланс | СНЭЭ  | Результ. | SOC"
    Write-Host "  ----|--------|-------|----------|-----"
    for ($i = 0; $i -lt 8; $i++) {
        $hour = $i + 1
        $bal = $load_profile[$i]
        $eens = $response2.eens_schedule[$i]
        $result = $response2.resulting_balance[$i]
        $soc = $response2.soc[$i]
        Write-Host ("{0,5} | {1,6:F1} | {2,5:F1} | {3,8:F1} | {4,4:F1}" -f $hour, $bal, $eens, $result, $soc)
    }
    
} catch {
    Write-Host "✗ Ошибка: $_" -ForegroundColor Red
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "ТЕСТЫ ЗАВЕРШЕНЫ" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

