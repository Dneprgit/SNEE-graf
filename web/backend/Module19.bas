Attribute VB_Name = "Module1"
Option Explicit

Type sStat
   ' показатели емкости
   dblNetMaxCapacity As Double ' доступная и востребованная емкость сети
   dblNetCapacity As Double    ' доступная и востребованная емкость сети с учетом мощности инвертора
   dblUsedCapacity As Double   ' используемая емкость батареи
   ' показатели мощности
   dblMaxCharge As Double      ' максимальная мощность заряда
   dblMaxDischarge As Double   ' максимальная мощность разряда
   ' показатели работы со СНЭЭ
   dblDefMaxPowerWithEESS As Double ' максимальный дефицит мощности с учетом работы СНЭЭ
   dblDefEnergyWithEESS As Double   ' дефицит энергии с учетом работы СНЭЭ
   dblDefMaxPower As Double    ' максимальный дефицит мощности
   dblDefEnergy As Double      ' дефицит энергии
End Type

Private Function MaxDbl(ByVal x As Double, ByVal y As Double) As Double
   MaxDbl = IIf(x < y, y, x)
End Function

Private Function MinDbl(ByVal x As Double, ByVal y As Double) As Double
   MinDbl = IIf(x < y, x, y)
End Function

Private Function GetRoundNumber(ByVal x As Double, ByVal d As Integer) As Double
Dim dblMan As Double
   Debug.Assert x > 0
   Debug.Assert d > 0
   dblMan = Log(x) / Log(10)
   dblMan = Round(dblMan - d + 0.5)
   GetRoundNumber = Round(x * (10 ^ (-dblMan)) + 0.5) * (10 ^ dblMan)
End Function

Private Sub CSort(ByRef dblList() As Double, ByRef lList() As Long)
Dim i As Long, i0 As Long, imax As Long, j As Long
Dim bSwap As Boolean, bSwapped As Boolean
Dim lGap As Long
Dim dbltemp As Double, ltemp As Double
   i0 = LBound(dblList, 1)
   imax = UBound(dblList, 1)
   lGap = imax - i0 + 1
   bSwapped = True
   While lGap > 1 Or bSwapped
      If lGap > 1 Then lGap = Int(lGap / 1.24733095010398)
      i = i0
      bSwapped = False
      While i + lGap <= imax
         j = i + lGap
         bSwap = False
         If dblList(i) > dblList(j) Then
            bSwap = True
         ElseIf dblList(i) = dblList(j) Then
            If lList(j) > lList(i) Then bSwap = True
         End If
         If bSwap = True Then
            dbltemp = dblList(i)
            dblList(i) = dblList(j)
            dblList(j) = dbltemp
            ltemp = lList(i)
            lList(i) = lList(j)
            lList(j) = ltemp
            bSwapped = True
         End If
         i = i + 1
      Wend
   Wend
End Sub

Private Function GetLevelBounded(ByRef dblLB() As Double, ByRef dblUB() As Double, ByVal dblDirFactor As Double, ByVal dblArea As Double, ByRef dblLevel As Double) As Long
' заливка в пределах диапазона
Dim i As Long, im As Long, j As Long, jm As Long
Dim dblOrdered() As Double, lFactor() As Long
Dim dblSum As Double, lCount As Long
   im = UBound(dblLB)
   jm = 2 * im
   ReDim dblOrdered(1 To jm) As Double
   ReDim lFactor(1 To jm) As Long
   dblDirFactor = IIf(dblDirFactor > 0, 1, -1)
   ' копирование
   For i = 1 To im
      dblOrdered(i) = dblLB(i) * dblDirFactor
      lFactor(i) = dblDirFactor
      dblOrdered(i + im) = dblUB(i) * dblDirFactor
      lFactor(i + im) = -dblDirFactor
   Next i
   ' сортировка
   Call CSort(dblOrdered, lFactor)
   ' выборка
   dblSum = 0
   lCount = 0
   dblLevel = dblOrdered(1)
   For i = 1 To jm
      If dblLevel < dblOrdered(i) Then Exit For
      dblSum = dblSum + dblOrdered(i) * lFactor(i)
      lCount = lCount + lFactor(i)
      If lCount > 0 Then
         dblLevel = (dblSum + dblArea) / lCount
      Else
         If i < im Then
            dblLevel = dblOrdered(i + 1)
         Else
            dblLevel = dblOrdered(im)
         End If
      End If
   Next i
   Erase lFactor
   Erase dblOrdered
   dblLevel = dblLevel * dblDirFactor ' уровень
   GetLevelBounded = lCount ' количество активных точек
End Function

Private Sub GetEnergyStorageInfo(ByRef dblLoadProfile() As Double, ByRef dblRatedPower As Double, ByRef dblRatedCapacity As Double, _
   ByRef dblEff As Double, ByRef dblLoad() As Double, ByRef sLoadStat As sStat)
' прямой расчет диспетчеркого графика СНЭЭ, скорость 540k расчетов/мин
Dim i As Long, im As Long, j As Long, it As Long, itmax As Long
Dim dblPF As Double
Dim dblMaxCharge() As Double, dblMaxDischarge() As Double, dblMaxChargeRate, dblMaxDischargeRate As Double
Dim dblMaxChargeCapacity As Double, dblMaxDischargeCapacity As Double, dblUsedCapacity As Double
Dim dblNetCapacity As Double, dblNetMaxCapacity As Double, dblImportCapacityFromNet As Double, dblExportCapacityToNet As Double
Dim dblVal As Double, dblCapacity As Double, dblCharge As Double, dblDischarge As Double
Dim dblLB() As Double, dblUB() As Double
Dim dblChargeLevel As Double, dblDischargeLevel As Double
Dim dblTol As Double
   ' 0. подготовка
   ' 0.1. проверки
   Debug.Assert dblRatedPower >= 0
   Debug.Assert dblRatedCapacity >= 0
   Debug.Assert dblEff > 0 And dblEff <= 1
   im = UBound(dblLoadProfile, 1)
   Debug.Assert im = 24
   ' 0.2. распределение памяти
   ReDim dblMaxCharge(1 To im) As Double
   ReDim dblMaxDischarge(1 To im) As Double
   ReDim dblLB(1 To im) As Double
   ReDim dblUB(1 To im) As Double
   ' 0.3. задание параметров
   dblTol = 0.00000001 ' допустимая погрешность
   itmax = 100 ' максимальное количество итераций
   dblPF = Sqr(dblEff) ' кпд полуцикла
   ' 1. передача мощности мощности от сети до батареи
   dblMaxChargeCapacity = 0
   dblImportCapacityFromNet = 0
   ' в результате выполняется: dblImportCapacityFromNet > dblMaxChargeCapacity
   For i = 1 To im
      dblVal = MaxDbl(dblLoadProfile(i), 0)  ' максимальная отдаваемая мощность сети
      dblImportCapacityFromNet = dblImportCapacityFromNet + dblVal ' емкость сети на выдачу
      dblVal = MinDbl(dblVal, dblRatedPower) * dblPF ' максимальная принимаемая мощность на заряд с учетом кпд и мощности инвертора
      dblMaxCharge(i) = dblVal
      dblMaxChargeCapacity = dblMaxChargeCapacity + dblVal ' доступная для заряда емкость
   Next i
   ' 2. передача мощности от батареи до сети
   dblMaxDischargeCapacity = 0
   dblExportCapacityToNet = 0
   ' в результате выполняется: dblExportCapacityToNet > dblMaxDischargeCapacity
   For i = 1 To im
      dblVal = MaxDbl(-dblLoadProfile(i), 0) ' максимальная принимаемая мощность сети с учетом кпд
      dblExportCapacityToNet = dblExportCapacityToNet + dblVal ' емкость сети на прием
      dblVal = MinDbl(dblVal / dblPF, dblRatedPower) ' максимальная отдаваемая мощность на разряд с учетом кпд и мощности инвертора
      dblMaxDischarge(i) = dblVal
      dblMaxDischargeCapacity = dblMaxDischargeCapacity + dblVal ' доступная для разряда емкость
   Next i
   ' 3. емкость сети
   dblNetMaxCapacity = MinDbl(dblImportCapacityFromNet, dblExportCapacityToNet) ' доступная и востребованная емкость сети
   dblNetCapacity = MinDbl(dblMaxChargeCapacity, dblMaxDischargeCapacity) ' доступная и востребованная емкость сети с учетом мощности инвертора
   ' в результате выполняется: dblNetMaxCapacity >= dblNetCapacity
   dblUsedCapacity = MinDbl(dblNetCapacity, dblRatedCapacity) ' используемая емкость батареи
   
   ' 4. информация по емкости
   ' !!! dblRatedCapacity < dblNetMaxCapacity - недостаток емкости
   ' !!! dblNetCapacity < dblNetMaxCapacity - недостаток мощности
   
   ' 5. подбор диспетчерских графиков заряда/разряда накопителя
   ' 5.1. уровень для заряда
   For i = 1 To 24
      dblUB(i) = dblLoadProfile(i)
      dblLB(i) = dblUB(i) - dblMaxCharge(i) / dblPF
   Next i
   Call GetLevelBounded(dblLB, dblUB, -1, dblUsedCapacity / dblPF, dblChargeLevel)
   ' 5.2. уровень для разряда
   For i = 1 To 24
      dblLB(i) = dblLoadProfile(i)
      dblUB(i) = dblLB(i) + dblMaxDischarge(i) * dblPF
   Next i
   Call GetLevelBounded(dblLB, dblUB, 1, dblUsedCapacity * dblPF, dblDischargeLevel)
   ' 5.3. расчет графика и контроль
   dblCapacity = 0
   sLoadStat.dblMaxCharge = 0
   sLoadStat.dblMaxDischarge = 0
   For i = 1 To im
      dblCharge = MinDbl(dblMaxCharge(i), MaxDbl(dblLoadProfile(i) - dblChargeLevel, 0) * dblPF) ' заряд
      dblDischarge = MinDbl(dblMaxDischarge(i), MaxDbl(dblDischargeLevel - dblLoadProfile(i), 0) / dblPF) ' разряд
      dblVal = dblDischarge - dblCharge
      dblLoad(i) = dblVal * IIf(dblVal > 0, dblPF, 1 / dblPF)
      dblCapacity = dblCapacity + dblVal
      ' расчет статистики
      sLoadStat.dblMaxCharge = MaxDbl(sLoadStat.dblMaxCharge, dblCharge)
      sLoadStat.dblMaxDischarge = MaxDbl(sLoadStat.dblMaxDischarge, dblDischarge)
   Next i
   Debug.Assert Abs(dblCapacity) < dblTol * im ' контроль баланса
   ' 6. расчет статистики
   sLoadStat.dblNetMaxCapacity = dblNetMaxCapacity
   sLoadStat.dblNetCapacity = dblNetCapacity
   sLoadStat.dblUsedCapacity = dblUsedCapacity
   sLoadStat.dblDefMaxPowerWithEESS = 0
   sLoadStat.dblDefEnergyWithEESS = 0
   sLoadStat.dblDefMaxPower = 0
   sLoadStat.dblDefEnergy = 0
   For i = 1 To im
      dblVal = -MinDbl(dblLoadProfile(i), 0)
      sLoadStat.dblDefMaxPower = MaxDbl(sLoadStat.dblDefMaxPower, dblVal)
      sLoadStat.dblDefEnergy = sLoadStat.dblDefEnergy + dblVal
      dblVal = -MinDbl(dblLoad(i) + dblLoadProfile(i), 0)
      sLoadStat.dblDefMaxPowerWithEESS = MaxDbl(sLoadStat.dblDefMaxPowerWithEESS, dblVal)
      sLoadStat.dblDefEnergyWithEESS = sLoadStat.dblDefEnergyWithEESS + dblVal
   Next i
   ' 7. освобождение памяти
   Erase dblMaxDischarge
   Erase dblMaxCharge
End Sub

Private Sub VariatePowerAndVolume(ByRef dblNetLoad() As Double, ByVal dblPF As Double, ByVal lMeshXSize As Double, ByVal lMeshYSize As Double, _
   ByRef dblXScale() As Double, ByRef dblYScale() As Double, ByRef dblPower() As Double, ByRef dblEnergy() As Double, _
   Optional ByVal dblXMax As Double = -1, Optional ByVal dblYMax As Double = -1)
Dim i As Long, im As Long, j As Long
Dim dblRatedPowerMW As Double, dblRatedPowerMWMax As Double, dblRatedCapacityMWh As Double, dblRatedCapacityMWhMax As Double
Dim dblMaxChargeCapacity As Double, dblMaxDischargeCapacity As Double
Dim dblENSSLoad() As Double
Dim dblVal As Double, dblRatedPowerStep As Double, dblRatedCapacityStep As Double
Dim sLoadStat As sStat
   im = UBound(dblNetLoad, 1)
   Debug.Assert im = 24
   ReDim dblENSSLoad(1 To im) As Double
   ' определяем масштаб
   dblRatedPowerMWMax = 0
   dblRatedCapacityMWhMax = 0
   dblMaxChargeCapacity = 0
   dblMaxDischargeCapacity = 0
   For i = 1 To im
      dblVal = dblNetLoad(i)
'      dblRatedPowerMWMax = MaxDbl(dblRatedPowerMWMax, Abs(dblVal))
      dblRatedPowerMWMax = MaxDbl(dblRatedPowerMWMax, -dblVal)
      dblMaxChargeCapacity = dblMaxChargeCapacity + MaxDbl(dblVal, 0)
      dblMaxDischargeCapacity = dblMaxDischargeCapacity + MaxDbl(-dblVal, 0)
   Next i
   dblRatedCapacityMWhMax = MinDbl(dblMaxChargeCapacity, dblMaxDischargeCapacity)
   Debug.Assert dblRatedPowerMWMax >= 0
   Debug.Assert dblRatedCapacityMWhMax >= 0
   dblRatedPowerMWMax = dblRatedPowerMWMax * 1.2
   dblRatedCapacityMWhMax = dblRatedCapacityMWhMax * 1.2
   dblRatedPowerMWMax = IIf(dblXMax > 0, dblXMax, dblRatedPowerMWMax)
   dblRatedCapacityMWhMax = IIf(dblYMax > 0, dblYMax, dblRatedCapacityMWhMax)
   dblRatedPowerMWMax = GetRoundNumber(dblRatedPowerMWMax, 2)
   dblRatedCapacityMWhMax = GetRoundNumber(dblRatedCapacityMWhMax, 2)
   ' определяем шаг
   dblRatedPowerStep = dblRatedPowerMWMax / lMeshXSize
   dblRatedCapacityStep = dblRatedCapacityMWhMax / lMeshYSize
   ' расчет
   ReDim dblXScale(0 To lMeshXSize) As Double
   ReDim dblYScale(0 To lMeshYSize) As Double
   ReDim dblPower(0 To lMeshXSize, 0 To lMeshYSize) As Double
   ReDim dblEnergy(0 To lMeshXSize, 0 To lMeshYSize) As Double
   For i = 0 To lMeshXSize
      dblXScale(i) = i * dblRatedPowerStep
   Next i
   For i = 0 To lMeshYSize
      dblYScale(i) = i * dblRatedCapacityStep
   Next i
   For i = 0 To lMeshXSize
      For j = 0 To lMeshYSize
         dblRatedPowerMW = dblXScale(i)
         dblRatedCapacityMWh = dblYScale(j)
         Call GetEnergyStorageInfo(dblNetLoad, dblRatedPowerMW, dblRatedCapacityMWh, dblPF, dblENSSLoad, sLoadStat)
         dblPower(i, j) = sLoadStat.dblDefMaxPowerWithEESS
         dblEnergy(i, j) = sLoadStat.dblDefEnergyWithEESS
      Next j
   Next i
End Sub

Private Sub VariatePowerAndVolume2(ByRef dblNetLoad() As Double, ByVal dblPF As Double, ByRef dblPower As Double, ByRef dblEnergy As Double)
Dim i As Long, im As Long, j As Long
Dim dblENSSLoad() As Double
Dim dblRatedPowerMW As Double, dblRatedPowerMWMax As Double, dblRatedPowerMWOpt As Double
Dim dblRatedCapacityMWh As Double, dblRatedCapacityMWhMax As Double, dblRatedCapacityMWhOpt As Double
Dim dblMaxChargeCapacity As Double, dblMaxDischargeCapacity As Double
Dim dblDefMaxPowerWithEESS As Double, dblMinDefMaxPowerWithEESS As Double
Dim dblDefEnergyWithEESS As Double, dblMinDefEnergyWithEESS As Double
Dim dblVal As Double, dblLB As Double, dblUB As Double, dblXTol As Double, dblYTol As Double
Dim sLoadStat As sStat
   dblXTol = 0.000001 ' погрешность расчета по x
   dblYTol = 0.001 ' погрешность расчета по y
   im = UBound(dblNetLoad, 1)
   Debug.Assert im = 24
   ReDim dblENSSLoad(1 To im) As Double
   ' определяем масштаб
   dblRatedPowerMWMax = 0
   dblRatedCapacityMWhMax = 0
   dblMaxChargeCapacity = 0
   dblMaxDischargeCapacity = 0
   For i = 1 To im
      dblVal = dblNetLoad(i)
      dblRatedPowerMWMax = MaxDbl(dblRatedPowerMWMax, Abs(dblVal))
      dblMaxChargeCapacity = dblMaxChargeCapacity + MaxDbl(dblVal, 0)
      dblMaxDischargeCapacity = dblMaxDischargeCapacity + MaxDbl(-dblVal, 0)
   Next i
   dblRatedCapacityMWhMax = MaxDbl(dblMaxChargeCapacity, dblMaxDischargeCapacity)
   Debug.Assert dblRatedPowerMWMax >= 0
   Debug.Assert dblRatedCapacityMWhMax >= 0
   dblRatedPowerMWMax = dblRatedPowerMWMax * 1.1
   dblRatedCapacityMWhMax = dblRatedCapacityMWhMax * 1.1
   ' определяем минимальный объем ограничений
   dblRatedPowerMW = dblRatedPowerMWMax
   dblRatedCapacityMWh = dblRatedCapacityMWhMax
   Call GetEnergyStorageInfo(dblNetLoad, dblRatedPowerMW, dblRatedCapacityMWh, dblPF, dblENSSLoad, sLoadStat)
   dblMinDefMaxPowerWithEESS = sLoadStat.dblDefMaxPowerWithEESS
   dblMinDefEnergyWithEESS = sLoadStat.dblDefEnergyWithEESS
   ' определяем минимальную емкость
   dblLB = 0
   dblUB = dblRatedCapacityMWhMax
   While dblUB - dblLB > dblXTol
      dblRatedPowerMW = dblRatedPowerMWMax
      dblRatedCapacityMWh = 0.5 * dblLB + 0.5 * dblUB
      Call GetEnergyStorageInfo(dblNetLoad, dblRatedPowerMW, dblRatedCapacityMWh, dblPF, dblENSSLoad, sLoadStat)
      dblDefMaxPowerWithEESS = sLoadStat.dblDefMaxPowerWithEESS
      dblDefEnergyWithEESS = sLoadStat.dblDefEnergyWithEESS
      If (dblDefEnergyWithEESS - dblMinDefEnergyWithEESS) + im * (dblDefMaxPowerWithEESS - dblMinDefMaxPowerWithEESS) < im * dblYTol Then
         dblUB = dblRatedCapacityMWh
      Else
         dblLB = dblRatedCapacityMWh
      End If
   Wend
   dblRatedCapacityMWhOpt = dblUB
   ' определяем минимальную мощность
   dblLB = 0
   dblUB = dblRatedPowerMWMax
   While dblUB - dblLB > dblXTol
      dblRatedPowerMW = 0.5 * dblLB + 0.5 * dblUB
      dblRatedCapacityMWh = dblRatedCapacityMWhMax
      Call GetEnergyStorageInfo(dblNetLoad, dblRatedPowerMW, dblRatedCapacityMWh, dblPF, dblENSSLoad, sLoadStat)
      dblDefMaxPowerWithEESS = sLoadStat.dblDefMaxPowerWithEESS
      dblDefEnergyWithEESS = sLoadStat.dblDefEnergyWithEESS
      If (dblDefEnergyWithEESS - dblMinDefEnergyWithEESS) + im * (dblDefMaxPowerWithEESS - dblMinDefMaxPowerWithEESS) < im * dblYTol Then
         dblUB = dblRatedPowerMW
      Else
         dblLB = dblRatedPowerMW
      End If
   Wend
   dblRatedPowerMWOpt = dblUB
   ' расчет общей точки
   ' определяем минимальную мощность
   dblRatedPowerMW = dblRatedPowerMWOpt
   dblRatedCapacityMWh = dblRatedCapacityMWhOpt
   Call GetEnergyStorageInfo(dblNetLoad, dblRatedPowerMW, dblRatedCapacityMWh, dblPF, dblENSSLoad, sLoadStat)
   If (dblDefEnergyWithEESS - dblMinDefEnergyWithEESS) + im * (dblDefMaxPowerWithEESS - dblMinDefMaxPowerWithEESS) < 2 * im * dblYTol Then
      ' точка на минимуме
   Else
      Debug.Assert 0
      ' точка не на минимуме
   End If
   dblPower = dblRatedPowerMWOpt
   dblEnergy = dblRatedCapacityMWhOpt
End Sub

Private Sub GetEnergyStorageLimitsInfo(ByRef dblLoadProfile() As Double, ByRef dblRatedPower As Double, ByRef dblRatedCapacity As Double, ByRef dblEff As Double, _
   ByRef dblNetChargeCapacityLimit As Double, ByRef dblNetDischargeCapacityLimit As Double, ByRef dblChargeCapacityLimit As Double, ByRef dblDischargeCapacityLimit As Double)
Dim i As Long, im As Long
Dim dblPF As Double
Dim dblUsedCapacity As Double, dblNetCapacity As Double, dblNetMaxCapacity As Double
Dim dblVal As Double
   ' 0. подготовка
   ' 0.1. проверки
   Debug.Assert dblRatedPower >= 0
   Debug.Assert dblRatedCapacity >= 0
   Debug.Assert dblEff > 0 And dblEff <= 1
   im = UBound(dblLoadProfile, 1)
   Debug.Assert im = 24
   ' 0.2. задание параметров
   dblPF = Sqr(dblEff) ' кпд полуцикла
   ' 1. передача мощности мощности от сети до батареи
   dblNetChargeCapacityLimit = 0
   dblChargeCapacityLimit = 0
   For i = 1 To im
      dblVal = MaxDbl(dblLoadProfile(i), 0)  ' максимальная отдаваемая мощность сети
      dblNetChargeCapacityLimit = dblNetChargeCapacityLimit + dblVal ' емкость сети на выдачу
      dblVal = MinDbl(dblVal, dblRatedPower) * dblPF ' максимальная принимаемая мощность на заряд с учетом кпд и мощности инвертора
      dblChargeCapacityLimit = dblChargeCapacityLimit + dblVal ' доступная для заряда емкость
   Next i
   ' 2. передача мощности от батареи до сети
   dblNetDischargeCapacityLimit = 0
   dblDischargeCapacityLimit = 0
   For i = 1 To im
      dblVal = MaxDbl(-dblLoadProfile(i), 0) ' максимальная принимаемая мощность сети с учетом кпд
      dblNetDischargeCapacityLimit = dblNetDischargeCapacityLimit + dblVal ' емкость сети на прием
      dblVal = MinDbl(dblVal / dblPF, dblRatedPower) ' максимальная отдаваемая мощность на разряд с учетом кпд и мощности инвертора
      dblDischargeCapacityLimit = dblDischargeCapacityLimit + dblVal ' доступная для разряда емкость
   Next i
   ' 3. емкость сети
   dblNetMaxCapacity = MinDbl(dblNetChargeCapacityLimit, dblNetDischargeCapacityLimit) ' доступная и востребованная емкость сети
   dblNetCapacity = MinDbl(dblChargeCapacityLimit, dblDischargeCapacityLimit) ' доступная и востребованная емкость сети с учетом мощности инвертора
   dblUsedCapacity = MinDbl(dblNetCapacity, dblRatedCapacity) ' используемая емкость батареи
   
End Sub

'-------------------------------------------------------------------------------
' функция, вызываемая пользователем с листа
Public Function ДиспетчерскийГрафикРаботыСНЭЭ(ByRef oNetLoadMWRange As Range, ByVal dblRatedPowerMW As Double, ByVal dblRatedCapacityMWh As Double, ByVal dblPF As Double) As Variant
Dim i As Long, im As Long, istep As Long, j As Long, jm As Long, jstep As Long, k As Long, km As Long
Dim arr As Variant
Dim dblNetLoad() As Double, dblLoad() As Double
Dim sLoadStat As sStat
   Debug.Assert dblRatedPowerMW >= 0
   Debug.Assert dblRatedCapacityMWh >= 0
   arr = oNetLoadMWRange
   im = UBound(arr, 1)
   jm = UBound(arr, 2)
   Debug.Assert (im = 1 And jm = 24) Or (jm = 1 And im = 24)
   If im = 1 Then
      istep = 0
      jstep = 1
   ElseIf jm = 1 Then
      istep = 1
      jstep = 0
   Else
   End If
   km = IIf(im < jm, jm, im)
   Debug.Assert km = 24
   ReDim dblNetLoad(1 To km) As Double
   ReDim dblLoad(1 To km) As Double
   i = 1
   j = 1
   For k = 1 To km
      dblNetLoad(k) = arr(1 + (k - 1) * istep, 1 + (k - 1) * jstep)
   Next k
   Call GetEnergyStorageInfo(dblNetLoad, dblRatedPowerMW, dblRatedCapacityMWh, dblPF, dblLoad, sLoadStat)
   i = 1
   j = 1
   For k = 1 To km
      arr(1 + (k - 1) * istep, 1 + (k - 1) * jstep) = dblLoad(k)
   Next k
   ДиспетчерскийГрафикРаботыСНЭЭ = arr ' нагрузка на шинах
End Function

Public Function ЕмкостьСистемы(ByRef oNetLoadMWRange As Range, ByVal dblRatedPowerMW As Double, ByVal dblRatedCapacityMWh As Double, ByVal dblPF As Double) As Variant
Dim i As Long, im As Long, istep As Long, j As Long, jm As Long, jstep As Long, k As Long, km As Long
Dim arr As Variant
Dim dblNetLoad() As Double
Dim dblNetChargeCapacityLimit As Double, dblNetDischargeCapacityLimit As Double, dblChargeCapacityLimit As Double, dblDischargeCapacityLimit As Double
   Debug.Assert dblRatedPowerMW >= 0
   Debug.Assert dblRatedCapacityMWh >= 0
   arr = oNetLoadMWRange
   im = UBound(arr, 1)
   jm = UBound(arr, 2)
   Debug.Assert (im = 1 And jm = 24) Or (jm = 1 And im = 24)
   If im = 1 Then
      istep = 0
      jstep = 1
   ElseIf jm = 1 Then
      istep = 1
      jstep = 0
   Else
   End If
   km = IIf(im < jm, jm, im)
   Debug.Assert km = 24
   ReDim dblNetLoad(1 To km) As Double
   ReDim dblLoad(1 To km) As Double
   i = 1
   j = 1
   For k = 1 To km
      dblNetLoad(k) = arr(1 + (k - 1) * istep, 1 + (k - 1) * jstep)
   Next k
   ' расчет емкости
   Call GetEnergyStorageLimitsInfo(dblNetLoad, dblRatedPowerMW, dblRatedCapacityMWh, dblPF, dblNetChargeCapacityLimit, dblNetDischargeCapacityLimit, dblChargeCapacityLimit, dblDischargeCapacityLimit)
   ' выгрузка результата
   ReDim arr(1 To 3, 1 To 1)
   arr(1, 1) = dblNetChargeCapacityLimit ' максимальная энергия, которую может дать система
   arr(2, 1) = dblNetDischargeCapacityLimit ' максимальная энергия, котрая требуется системе
   arr(3, 1) = dblChargeCapacityLimit ' максимальная энергия заряда накопителя - может дать система и можно передать через инвертор
   ЕмкостьСистемы = arr
End Function

Public Sub ВариацияПараметровСНЭЭ()
Dim oWS As Worksheet, oRng As Range
Dim dblXScale() As Double, dblYScale() As Double
Dim dblPower() As Double, dblEnergy() As Double
Dim dblEff As Double
Dim arr As Variant
Dim i As Long, im As Long, istep As Long, j As Long, jm As Long, jstep As Long, k As Long, km As Long
Dim lMeshSize As Long
   ' настройки
   dblEff = 0.95 ' кпд
   lMeshSize = 100 ' размер сетки
   Debug.Assert lMeshSize = 100
   ' источник данных
   Set oWS = ThisWorkbook.Worksheets("График СНЭЭ")
   Set oRng = oWS.Range("B6:Y6")
   ' загрузка
   arr = oRng
   im = UBound(arr, 1)
   jm = UBound(arr, 2)
   Debug.Assert (im = 1 And jm = 24) Or (jm = 1 And im = 24)
   If im = 1 Then
      istep = 0
      jstep = 1
   ElseIf jm = 1 Then
      istep = 1
      jstep = 0
   Else
   End If
   km = IIf(im < jm, jm, im)
   Debug.Assert km = 24
   ReDim dblNetLoad(1 To km) As Double
   ReDim dblLoad(1 To km) As Double
   i = 1
   j = 1
   For k = 1 To km
      dblNetLoad(k) = arr(1 + (k - 1) * istep, 1 + (k - 1) * jstep)
   Next k
   ' расчет
   Call VariatePowerAndVolume(dblNetLoad, dblEff, lMeshSize, lMeshSize, dblXScale, dblYScale, dblPower, dblEnergy)
   ' выгрузка
   ' запись результатов
   Application.Calculation = xlCalculationManual
   Set oWS = ThisWorkbook.Worksheets("Дефицит мощности " & lMeshSize & "x" & lMeshSize)
   Set oRng = oWS.Range(oWS.Cells(2, 2), oWS.Cells(lMeshSize + 2, lMeshSize + 2))
   oRng.Cells = dblPower
   Set oWS = ThisWorkbook.Worksheets("Дефицит энергии " & lMeshSize & "x" & lMeshSize)
   Set oRng = oWS.Range(oWS.Cells(2, 2), oWS.Cells(lMeshSize + 2, lMeshSize + 2))
   oRng.Cells = dblEnergy
   ReDim arr(0 To lMeshSize, 1 To 1)
   For i = 0 To lMeshSize
      arr(i, 1) = dblXScale(i)
   Next i
   Set oWS = ThisWorkbook.Worksheets("Дефицит мощности " & lMeshSize & "x" & lMeshSize)
   Set oRng = oWS.Range(oWS.Cells(2, 1), oWS.Cells(lMeshSize + 2, 1))
   oRng.Cells = arr
   Set oWS = ThisWorkbook.Worksheets("Дефицит энергии " & lMeshSize & "x" & lMeshSize)
   Set oRng = oWS.Range(oWS.Cells(2, 1), oWS.Cells(lMeshSize + 2, 1))
   oRng.Cells = arr
   ReDim arr(1 To 1, 0 To lMeshSize)
   For i = 0 To lMeshSize
      arr(1, i) = dblYScale(i)
   Next i
   Set oWS = ThisWorkbook.Worksheets("Дефицит мощности " & lMeshSize & "x" & lMeshSize)
   Set oRng = oWS.Range(oWS.Cells(1, 2), oWS.Cells(1, lMeshSize + 2))
   oRng.Cells = arr
   Set oWS = ThisWorkbook.Worksheets("Дефицит энергии " & lMeshSize & "x" & lMeshSize)
   Set oRng = oWS.Range(oWS.Cells(1, 2), oWS.Cells(1, lMeshSize + 2))
   oRng.Cells = arr
   Application.Calculation = xlCalculationAutomatic
End Sub

Public Sub ПодборПараметровСНЭЭ()
Dim oWS As Worksheet, oRng As Range
Dim dblPower As Double, dblEnergy As Double
Dim dblEff As Double
Dim arr As Variant
Dim i As Long, im As Long, istep As Long, j As Long, jm As Long, jstep As Long, k As Long, km As Long
Dim lMeshSize As Long
   ' настройки
   dblEff = 0.95 ' кпд
   ' источник данных
   Set oWS = ThisWorkbook.Worksheets("График СНЭЭ")
   Set oRng = oWS.Range("B6:Y6")
   ' загрузка
   arr = oRng
   im = UBound(arr, 1)
   jm = UBound(arr, 2)
   Debug.Assert (im = 1 And jm = 24) Or (jm = 1 And im = 24)
   If im = 1 Then
      istep = 0
      jstep = 1
   ElseIf jm = 1 Then
      istep = 1
      jstep = 0
   Else
   End If
   km = IIf(im < jm, jm, im)
   Debug.Assert km = 24
   ReDim dblNetLoad(1 To km) As Double
   ReDim dblLoad(1 To km) As Double
   i = 1
   j = 1
   For k = 1 To km
      dblNetLoad(k) = arr(1 + (k - 1) * istep, 1 + (k - 1) * jstep)
   Next k
   ' расчет
   Call VariatePowerAndVolume2(dblNetLoad, dblEff, dblPower, dblEnergy)
   ' выгрузка
   ' запись результатов
   Application.Calculation = xlCalculationManual
   Set oWS = ThisWorkbook.Worksheets("График СНЭЭ")
   oWS.Range("AD12") = dblPower
   oWS.Range("AD13") = dblEnergy
   Application.Calculation = xlCalculationAutomatic
End Sub


