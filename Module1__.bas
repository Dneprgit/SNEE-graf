Option Explicit

Const MaxRealNumber = 1E+300

'Following completion codes are returned:
'-9    failure of the automatic scale evaluation : one  of  the  diagonal elements of the quadratic term is non - positive.
'    Specify variable scales manually!
'*-8    abnormal termination - infinities in function/gradient
'-5    inappropriate solver was used:
'    *QuickQP solver for problem with general linear constraints
'-4    the function is unbounded from below even under constraints, no meaningful minimum can be found.
'-3    inconsistent constraints (or, maybe, feasible point is too hard to find).
'*-2   rounding errors make further iterations impossible
'-2    IPM solver has difficulty finding primal / dual feasible point.
'    It is likely that the problem is either infeasible or unbounded, but it is difficult to determine exact reason for termination.
'    X contains best point found so far.
'> 0   success
'* 1    function change is small enough
'* 2    X(k+1)-X(k) is small enough
'* 4    gradient is small enough
'* 5    too many iterations
' 7    stopping conditions are too stringent, further improvement is impossible, X contains best point found so far.
'* 8    user requested termination, X contains best point found so far

' BLEICQPSolve решает задачу квадратичной оптимизации с двусторонними ограничениями общего вида:
' min F(x), F(x)=0.5*x'*A*x+b'*x
' с ограничениями: lb<=x<=ub
'   cl<=C'*x<=cu
' Старт с точки x0
' Масштаб x задан в s
' Матрица A должна быть симметричной.

#If Win64 Then
   Private Declare PtrSafe Function SetEnvironmentVariableA Lib "kernel32" (ByVal lpname As String, ByVal lpValue As String) As Long
   Private Declare PtrSafe Function GetEnvironmentVariableA Lib "kernel32" (ByVal lpname As String, ByVal lpBuffer As String, ByVal nSize As Long) As Long
   Private Declare PtrSafe Function BLEICQPSolve Lib "QuickQP_x64.dll" (ByRef x() As Double, ByRef A() As Double, ByRef b() As Double, _
      ByRef C() As Double, ByRef cl() As Double, ByRef cu() As Double, ByRef lb() As Double, ByRef ub() As Double, _
      ByRef s() As Double, ByRef x0() As Double) As Long
#Else
   Private Declare Function SetEnvironmentVariableA Lib "kernel32" (ByVal lpname As String, ByVal lpValue As String) As Long
   Private Declare Function GetEnvironmentVariableA Lib "kernel32" (ByVal lpname As String, ByVal lpBuffer As String, ByVal nSize As Long) As Long
   Private Declare Function BLEICQPSolve Lib "QuickQP_x86.dll" (ByRef x() As Double, ByRef A() As Double, ByRef b() As Double, _
      ByRef C() As Double, ByRef cl() As Double, ByRef cu() As Double, ByRef lb() As Double, ByRef ub() As Double, _
      ByRef s() As Double, ByRef x0() As Double) As Long

#End If

Private Function SetEnvironmentVariable(name As String, value As String) As Boolean
    SetEnvironmentVariable = SetEnvironmentVariableA(name, value)
End Function

Private Function GetEnvironmentVariable(name As String) As String
Dim L As Long
Dim Buf As String
    L = GetEnvironmentVariableA(name, vbNullString, 0)
    If L > 0 Then
        Buf = Space$(L)
        L = GetEnvironmentVariableA(name, Buf, Len(Buf))
        GetEnvironmentVariable = Mid$(Buf, 1, L)
    End If
End Function

Public Function InitDLLPath(Optional ByVal dllPath As String = "") As Boolean
Static bEnvChanged As Boolean
Dim Path As String

    If Len(dllPath) = 0 Then
        dllPath = Application.Path
    End If
    On Error Resume Next
    If Not bEnvChanged Then
        bEnvChanged = True
        Path = GetEnvironmentVariable("PATH")
        If InStr(1, Path & ";", dllPath & ";", vbTextCompare) = 0 Then
            SetEnvironmentVariable "PATH", dllPath & ";" & Path
        End If
    End If
End Function

Private Function MinDbl(ByVal x, ByVal y) As Double
   MinDbl = IIf(x > y, y, x)
End Function

Private Function MaxDbl(ByVal x, ByVal y) As Double
   MaxDbl = IIf(x > y, x, y)
End Function

Private Function CheckInitPoint(ByRef x0() As Double, ByRef C() As Double, ByRef cl() As Double, ByRef cu() As Double, ByRef lb() As Double, ByRef ub() As Double, Optional ByVal ctol As Double = 0.000001) As Long
Dim i As Long, j As Long, n As Long, m As Long
Dim s As Double
   Debug.Assert ctol > 0
   n = UBound(x0)
   m = UBound(cl)
   ReDim cx(1 To m) As Double
   For i = 1 To n
      If x0(i) < lb(i) - ctol Then
         Debug.Assert 0
      End If
      If x0(i) > ub(i) + ctol Then
         Debug.Assert 0
      End If
   Next i
   For i = 1 To m
      s = 0
      For j = 1 To n
         s = s + C(i, j) * x0(j)
      Next j
      If s < cl(i) - ctol Then
         Debug.Assert 0
      End If
      If s > cu(i) + ctol Then
         Debug.Assert 0
      End If
   Next i

End Function

Private Function GetEESSOptimalLoad_new2(ByRef dblSystemLoad() As Double, _
   ByVal dblEfficiency As Double, ByVal dblNIn As Double, ByVal dblNOut As Double, ByVal dblCapacity As Double, _
   ByRef dblEENSEnergyAvailable() As Double, ByRef dblEENSLoad() As Double, _
   ByRef dblSystemWithENSSLoadDeficite As Double, ByRef dblSystemWithENSSLoadReserve As Double) As Long
Dim i As Long, im As Long, j As Long, k As Long, n As Long
Dim x() As Double, x0() As Double, lb() As Double, ub() As Double
Dim A() As Double, b() As Double, s() As Double
Dim C() As Double, cl() As Double, cu() As Double
Dim dblS() As Double, dblP As Double
Dim dblSmin As Double, dblSmax As Double, dblWSmin As Double, dblWSmax As Double
Dim dblVal As Double
Dim dblW0 As Double, dblWCap As Double, dblWEC As Double, dblDmax As Double, dblRmax As Double, dblDsum As Double
   Debug.Assert dblEfficiency > 0 And dblEfficiency <= 1
   Debug.Assert dblNIn >= 0
   Debug.Assert dblNOut >= 0
   Debug.Assert dblCapacity >= 0
   im = UBound(dblSystemLoad, 1)
   Debug.Assert im = 24
   ReDim dblEENSEnergyAvailable(1 To im) As Double
   ReDim dblENSSLoad(1 To im) As Double
   ' размеры задачи оптимизации
   n = im * 2 + 2
   k = im * 2
   ' настройки
   dblW0 = 1E-20
   dblWCap = 0.000000001 ' емкость
   dblWEC = 0.000000001 ' обменная мощность
   dblDmax = 1 ' максимальный дефицит мощности
   dblDsum = dblDmax / (im + 1) ' максимальный дефицит энергии
   dblRmax = dblDsum / (im + 1) ' максимальный избыток мощности
   ' доопределение
   dblP = 10 ' !!! значение для тестов
   dblP = 0.01 * MaxDbl(dblNIn, dblNOut) ' !!! значение для тестов
   ' распределение памяти
   ReDim A(1 To n, 1 To n) As Double
   ReDim b(1 To n) As Double
   ReDim C(1 To k, 1 To n) As Double
   ReDim cl(1 To k) As Double
   ReDim cu(1 To k) As Double
   ReDim x(1 To n) As Double
   ReDim x0(1 To n) As Double
   ReDim lb(1 To n) As Double
   ReDim ub(1 To n) As Double
   ReDim s(1 To n) As Double
   ' приведение к задаче без потерь
   dblNIn = dblNIn * dblEfficiency
   dblS = dblSystemLoad
   For i = 1 To im
      dblS(i) = IIf(dblS(i) < 0, dblEfficiency, 1) * dblS(i)
   Next i
   ' экстремумы графика
   dblSmin = 0
   dblSmax = 0
   For i = 1 To im
      dblSmin = MinDbl(dblSmin, dblS(i))
      dblSmax = MaxDbl(dblSmax, dblS(i))
   Next i
   ' ---
   ' минимальное диагональное усиление нулевой матрицы
   For i = 1 To n
      A(i, i) = dblW0
   Next i
   ' дообуславливание при прочих равных
   ' максимизация уровня заряда
   For i = 1 To im
      A(i, i) = A(i, i) + dblWCap
      b(i + im * 0) = b(i + im * 0) - 2 * dblCapacity * dblWCap
   Next i
   ' минимизация уровня обменной мощности
   For i = 1 To im
      A(i + im, i + im) = A(i + im, i + im) + dblWEC
   Next i
   ' основная целевая функция
   ' L[]
   For i = 1 To im
      b(i + im * 0) = b(i + im * 0) + 0
   Next i
   ' EC[]
   For i = 1 To im ' максимальная выдача в часы дефицита
      b(i + im * 1) = b(i + im * 1) - dblDsum * IIf(dblS(i) > 0, 1, 0) ' проверить корректность для P<>0
   Next i
   b(im * 2 + 1) = b(im * 2 + 1) + dblDmax ' Dmax
   b(im * 2 + 2) = b(im * 2 + 2) + dblRmax ' Rmax
   ' ограничения:
   ' связь 'x' и 'y':
   For i = 1 To k
      For j = 1 To n
         C(i, j) = 0
      Next j
   Next i
   For i = 1 To im ' rL
      j = IIf(i > 1, i - 1, im)
      C(i, i) = 1      ' L[]
      C(i, j) = -1     ' L[]
      C(i, i + im) = 1 ' EC[]
      ' Dmax
      ' Rmax
     cl(i) = -dblP ' -P[]
     cu(i) = -dblP ' -P[]
   Next i
   For i = 1 To im ' rD
      ' dL[]
      If dblS(i) > 0 Then
         C(i + im, i + im) = -1   ' EC[i]
         C(i + im, im * 2 + 1) = -1 ' Dmax
'         C(i + im, im * 2 + 2) = 0 ' Rmax
         cl(i + im) = -MaxRealNumber
         cu(i + im) = -dblS(i)
      Else
         C(i + im, i + im) = 1   ' EC[i]
'         C(i + im, im * 2 + 1) = 0 ' Dmax
         C(i + im, im * 2 + 2) = -1 ' Rmax
         cl(i + im) = -MaxRealNumber
         cu(i + im) = dblS(i)
      End If
   Next i
   ' ограничения на диапазон 'x':
   For i = 1 To im
      ' SOC
      lb(i) = 0
      ub(i) = dblCapacity
      ' EC
      If dblS(i) > 0 Then
         lb(i + im) = 0
         ub(i + im) = MinDbl(dblNOut, dblS(i))
      Else
         lb(i + im) = MaxDbl(-dblNIn, dblS(i))
         ub(i + im) = 0
      End If
   Next i
   ' Dmax
   lb(im * 2 + 1) = 0
'   ub(im * 2 + 1) = MaxRealNumber ' если для расчетчика не требуется ограничение
   ub(im * 2 + 1) = dblSmax ' если требуется конечное ограничение
   ' Rmax
   lb(im * 2 + 2) = 0 ' проверить корректность для случая P<>0!
'   ub(im * 2 + 2) = MaxRealNumber ' если для расчетчика не требуется ограничение
   ub(im * 2 + 2) = -dblSmin ' если требуется конечное ограничение
   ' масштаб переменных: =1
   For i = 1 To n
      s(i) = 1
   Next i
   ' начальное приближение:
   ' по L
   dblSmin = 0
   dblSmax = 0
   For i = 1 To im
      dblSmin = dblSmin + lb(i + im) + dblP
      dblSmax = dblSmax + ub(i + im) + dblP
   Next i
   If dblSmin > 0 Then ' заряд невозможен
      Debug.Assert 0
   End If
   If dblSmax < 0 Then ' разряд невостребован
      Debug.Assert 0
   End If
   dblWSmin = dblSmax / (dblSmax - dblSmin)
   dblWSmax = -dblSmin / (dblSmax - dblSmin)
   dblSmin = 0
   dblSmax = 0
   dblVal = 0
   For i = 1 To im
      dblVal = dblVal + lb(i + im) * dblWSmin + ub(i + im) * dblWSmax + dblP
      x0(i) = dblVal
      dblSmin = MinDbl(dblSmin, dblVal)
      dblSmax = MaxDbl(dblSmax, dblVal)
   Next i
   Debug.Assert dblCapacity >= dblSmax - dblSmin
   dblVal = dblCapacity + dblSmin
   For i = 1 To im
      x0(i) = dblVal - x0(i)
   Next i
   ' по ЕС
   dblVal = x0(im)
   For i = 1 To im
      x0(i + im) = dblVal - x0(i) - dblP
      dblVal = x0(i)
   Next i
   ' по Dmax, Rmax
   x0(im * 2 + 1) = ub(im * 2 + 1)
   x0(im * 2 + 2) = ub(im * 2 + 2)
   Call CheckInitPoint(x0, C, cl, cu, lb, ub)
   ' расчет
   i = BLEICQPSolve(x, A, b, C, cl, cu, lb, ub, s, x0)
   GetEESSOptimalLoad_new2 = i
   Select Case i
   Case 2
      ' ок, сходимость по x к минимуму
   Case 4
      ' ок, сходимость к минимуму по y
   Case 1, 5, 7, 8
      Debug.Print "Exit code = " & i ' успешное завершение с иным критерием
   Case Else ' отказ, либо неизвестный код возврата
      Debug.Print "Exit code = " & i
   End Select
   ' тестовый возврат начального приближения
   If 0 Then
      For i = 1 To n
         x(i) = x0(i)
      Next i
   End If
   ' контроль
   dblVal = dblP * im
   For i = 1 To im
      dblVal = dblVal + x(i + im)
   Next i
   Debug.Assert Abs(dblVal) < 0.001 ' заряд-разряд подсистемы накопителя сбалансирован
   ' результат
   For i = 1 To im
      dblEENSEnergyAvailable(i) = x(i)
      dblEENSLoad(i) = x(i + im) * IIf(x(i + im) >= 0, 1, 1 / dblEfficiency)
   Next i
   dblSystemWithENSSLoadDeficite = x(1 + im * 2)
   dblSystemWithENSSLoadReserve = x(2 + im * 2) / dblEfficiency
End Function

Private Function GetEESSOptimalLoad_new(ByRef dblSystemLoad() As Double, _
   ByVal dblEfficiency As Double, ByVal dblNIn As Double, ByVal dblNOut As Double, ByVal dblCapacity As Double, _
   ByRef dblEENSEnergyAvailable() As Double, ByRef dblEENSLoad() As Double, _
   ByRef dblSystemWithENSSLoadDeficite As Double, ByRef dblSystemWithENSSLoadReserve As Double) As Long
Dim i As Long, im As Long, j As Long, k As Long, n As Long
Dim x() As Double, x0() As Double, lb() As Double, ub() As Double
Dim A() As Double, b() As Double, s() As Double
Dim C() As Double, cl() As Double, cu() As Double
Dim dblSmin As Double, dblSmax As Double, dblWSmin As Double, dblWSmax As Double
Dim dblVal As Double
   Debug.Assert dblEfficiency > 0 And dblEfficiency <= 1
   Debug.Assert dblNIn >= 0
   Debug.Assert dblNOut >= 0
   Debug.Assert dblCapacity >= 0
   im = UBound(dblSystemLoad, 1)
   Debug.Assert im = 24
   ReDim dblEENSEnergyAvailable(1 To im) As Double
   ReDim dblENSSLoad(1 To im) As Double
   ' размеры задачи оптимизации
   n = im * 2 + 2
   k = im * 2
   ' распределение памяти
   ReDim A(1 To n, 1 To n) As Double
   ReDim b(1 To n) As Double
   ReDim C(1 To k, 1 To n) As Double
   ReDim cl(1 To k) As Double
   ReDim cu(1 To k) As Double
   ReDim x(1 To n) As Double
   ReDim x0(1 To n) As Double
   ReDim lb(1 To n) As Double
   ReDim ub(1 To n) As Double
   ReDim s(1 To n) As Double
   ' экстремумы графика
   dblSmin = 0
   dblSmax = 0
   For i = 1 To im
      dblSmin = MinDbl(dblSmin, dblSystemLoad(i))
      dblSmax = MaxDbl(dblSmax, dblSystemLoad(i))
   Next i
   dblSmin = dblSmin * dblEfficiency
   '
   ' ---
   ' минимальное диагональное усиление нулевой матрицы
   For i = 1 To n
      For j = 1 To n
         A(i, j) = IIf(i = j, 1, 0) * 0.00000001
      Next j
   Next i
   ' веса для 'x':
   For i = 1 To im ' L[]
      b(i + im * 0) = 0
   Next i
   For i = 1 To im ' EC[]
      b(i + im * 1) = -0.04 * IIf(dblSystemLoad(i) > 0, 1, 0) ' проверить корректности для P<>0
   Next i
   b(im * 2 + 1) = 1      ' Dmax
   b(im * 2 + 2) = 0.0016 ' Rmax
   ' ограничения:
   ' связь 'x' и 'y':
   For i = 1 To k
      For j = 1 To n
         C(i, j) = 0
      Next j
   Next i
   For i = 1 To im ' rL
      j = IIf(i > 1, i - 1, im)
      C(i, i) = 1      ' L[]
      C(i, j) = -1     ' L[]
      C(i, i + im) = 1 ' EC[]
      ' Dmax
      ' Rmax
     cl(i) = -0 ' -P[]
     cu(i) = -0 ' -P[]
   Next i
   For i = 1 To im ' rD
      ' dL[]
      If dblSystemLoad(i) > 0 Then
         C(i + im, i + im) = -1   ' EC[i]
         C(i + im, im * 2 + 1) = -1 ' Dmax
'         C(i + im, im * 2 + 2) = 0 ' Rmax
         cl(i + im) = -MaxRealNumber
         cu(i + im) = -dblSystemLoad(i)
      Else
         C(i + im, i + im) = 1   ' EC[i]
'         C(i + im, im * 2 + 1) = 0 ' Dmax
         C(i + im, im * 2 + 2) = -1 ' Rmax
         cl(i + im) = -MaxRealNumber
         cu(i + im) = dblSystemLoad(i) * dblEfficiency
      End If
   Next i
   ' ограничения на диапазон 'x':
   For i = 1 To im
      ' SOC
      lb(i) = 0
      ub(i) = dblCapacity
      ' EC
      If dblSystemLoad(i) > 0 Then
         lb(i + im) = 0
         ub(i + im) = MinDbl(dblNOut, dblSystemLoad(i))
      Else
         lb(i + im) = MaxDbl(-dblNIn, dblSystemLoad(i) * dblEfficiency)
         ub(i + im) = 0
      End If
   Next i
   ' Dmax
   lb(im * 2 + 1) = 0
'   ub(im * 2 + 1) = MaxRealNumber ' если для расчетчика не требуется ограничение
   ub(im * 2 + 1) = dblSmax ' если требуется ограничение
   ' Rmax
   lb(im * 2 + 2) = 0 ' проверить корректность для случая P<>0!
'   ub(im * 2 + 2) = MaxRealNumber ' если для расчетчика не требуется ограничение
   ub(im * 2 + 2) = -dblSmin ' если требуется ограничение
   ' масштаб переменных: =1
   For i = 1 To n
      s(i) = 1
   Next i
   ' начальное приближение:
   ' по L
   dblSmin = 0
   dblSmax = 0
   For i = 1 To im
      dblSmin = dblSmin + lb(i + im)
      dblSmax = dblSmax + ub(i + im)
   Next i
   If dblSmin > 0 Then ' заряд невозможен
      Debug.Assert 0
   End If
   If dblSmax < 0 Then ' разряд невостребован
      Debug.Assert 0
   End If
   dblWSmin = dblSmax / (dblSmax - dblSmin)
   dblWSmax = -dblSmin / (dblSmax - dblSmin)
   dblSmin = 0
   dblSmax = 0
   dblVal = 0
   For i = 1 To im
      dblVal = dblVal + lb(i + im) * dblWSmin + ub(i + im) * dblWSmax
      x0(i) = dblVal
      dblSmin = MinDbl(dblSmin, dblVal)
      dblSmax = MaxDbl(dblSmax, dblVal)
   Next i
   Debug.Assert dblCapacity >= dblSmax - dblSmin
   dblVal = dblCapacity + dblSmin
   For i = 1 To im
      x0(i) = dblVal - x0(i)
   Next i
   ' по ЕС
   dblVal = x0(im)
   For i = 1 To im
      x0(i + im) = dblVal - x0(i)
      dblVal = x0(i)
   Next i
   ' по Dmax, Rmax
   x0(im * 2 + 1) = ub(im * 2 + 1)
   x0(im * 2 + 2) = ub(im * 2 + 2)
   Call CheckInitPoint(x0, C, cl, cu, lb, ub)
   ' расчет
   i = BLEICQPSolve(x, A, b, C, cl, cu, lb, ub, s, x0)
   GetEESSOptimalLoad_new = i
   Select Case i
   Case 2
      ' ок, сходимость по x к минимуму
   Case 4
      ' ок, сходимость к минимуму по y
   Case 1, 5, 7, 8
      Debug.Print "Exit code = " & i ' успешное завершение с иным критерием
   Case Else ' отказ, либо неизвестный код возврата
      Debug.Print "Exit code = " & i
   End Select
   ' тестовый возврат начального приближения
   If 0 Then
      For i = 1 To n
         x(i) = x0(i)
      Next i
   End If
   ' контроль
   dblVal = 0
   For i = 1 To im
      dblVal = dblVal + x(i + im)
   Next i
   Debug.Assert Abs(dblVal) < 0.001 ' заряд-разряд подсистемы накопителя сбалансирован
   ' результат
   For i = 1 To im
      dblEENSEnergyAvailable(i) = x(i)
      dblEENSLoad(i) = x(i + im) * IIf(x(i + im) >= 0, 1, 1 / dblEfficiency)
   Next i
   dblSystemWithENSSLoadDeficite = x(1 + im * 2)
   dblSystemWithENSSLoadReserve = x(2 + im * 2) / dblEfficiency
End Function


Private Function GetEESSOptimalLoad(ByRef dblSystemLoad() As Double, _
   ByVal dblEfficiency As Double, ByVal dblNIn As Double, ByVal dblNOut As Double, ByVal dblCapacity As Double, _
   ByRef dblEENSEnergyAvailable() As Double, ByRef dblEENSLoad() As Double, _
   ByRef dblSystemWithENSSLoadDeficite As Double, ByRef dblSystemWithENSSLoadReserve As Double) As Long
Dim i As Long, im As Long, j As Long, k As Long, n As Long
Dim x() As Double, A() As Double, b() As Double, lb() As Double, ub() As Double, s() As Double, x0() As Double
Dim dblVal As Double
   Debug.Assert dblEfficiency > 0 And dblEfficiency <= 1
   Debug.Assert dblNIn >= 0
   Debug.Assert dblNOut >= 0
   Debug.Assert dblCapacity >= 0
   im = UBound(dblSystemLoad, 1)
   Debug.Assert im = 24
   ReDim dblEENSEnergyAvailable(1 To im) As Double
   ReDim dblENSSLoad(1 To im) As Double
   n = im * 4 + 2
   k = im * 4

   ReDim A(1 To n, 1 To n) As Double
   ReDim b(1 To n) As Double
   ReDim C(1 To k, 1 To n) As Double
   ReDim cl(1 To k) As Double
   ReDim cu(1 To k) As Double
   ReDim x(1 To n) As Double
   ReDim x0(1 To n) As Double
   ReDim lb(1 To n) As Double
   ReDim ub(1 To n) As Double
   ReDim s(1 To n) As Double
   ' ---
   ' минимальное диагональное усиление нулевой матрицы
   For i = 1 To n
      For j = 1 To n
         A(i, j) = IIf(i = j, 1, 0) * 0.00000001
      Next j
   Next i
   ' веса для 'x':
   For i = 1 To im * 3
      b(i) = 0
   Next i
   For i = im * 3 + 1 To im * 4
      b(i) = 0.04
   Next i
   b(im * 4 + 1) = 1
   b(im * 4 + 2) = 0.0016
   ' ограничения:
   ' связь 'x' и 'y':
   For i = 1 To k
      For j = 1 To n
         C(i, j) = 0
      Next j
   Next i
   For i = 1 To im ' rL
      j = IIf(i > 1, i - 1, im)
      C(i, i) = 1 ' dL[]
      C(i, j) = -1 ' dL[]
      C(i, i + im) = -1 ' CC[]
      C(i, i + im * 2) = 1 ' CD[]
      ' D[]
      ' Dmax
      ' Rmax
     cl(i) = 0
     cu(i) = 0
   Next i
   For i = 1 To im ' rD
      ' dL[]
      C(i + im, i + im) = -1 / dblEfficiency ' CC[]
      C(i + im, i + im * 2) = 1 ' CD[]
      C(i + im, i + im * 3) = 1 ' D[]
      ' Dmax
      ' Rmax
     cl(i + im) = dblSystemLoad(i)
     cu(i + im) = MaxRealNumber
   Next i
   For i = 1 To im ' rDmin
      ' dL[]
      C(i + im * 2, i + im) = 1 / dblEfficiency ' CC[]
      C(i + im * 2, i + im * 2) = -1 ' CD[]
      ' D[]
      ' Dmax
      C(i + im * 2, 2 + im * 4) = 1 ' Rmax
      cl(i + im * 2) = -dblSystemLoad(i)
      cu(i + im * 2) = MaxRealNumber
   Next i
   For i = 1 To im ' rDmax
      ' dL[]
      ' CC[]
      ' CD[]
      C(i + im * 3, i + im * 3) = -1 ' D[]
      C(i + im * 3, 1 + im * 4) = 1 ' Dmax
      ' Rmax
      cl(i + im * 3) = 0
      cu(i + im * 3) = MaxRealNumber
   Next i
   ' ограничения на диапазон 'x':
   For i = 1 To n
      lb(i) = 0
   Next i
   For i = 1 To im
      ub(i) = dblCapacity
      ub(i + im) = dblNIn * dblEfficiency
      ub(i + im * 2) = dblNOut
      ub(i + im * 3) = MaxRealNumber
   Next i
   ub(1 + im * 4) = MaxRealNumber
   ub(2 + im * 4) = MaxRealNumber
   ' масштаб переменных: =1
   For i = 1 To n
      s(i) = 1
   Next i
   ' начальное приближение: x0=lb+s
   For i = 1 To n
      x0(i) = lb(i) + s(i)
   Next i
   ' расчет
   i = BLEICQPSolve(x, A, b, C, cl, cu, lb, ub, s, x0)
   GetEESSOptimalLoad = i
   Select Case i
   Case 2
      ' ок, сходимость по x к минимуму
   Case 4
      ' ок, сходимость к минимуму по y
   Case 1, 5, 7, 8
      Debug.Print "Exit code = " & i ' успешное завершение с иным критерием
   Case Else ' отказ, либо неизвестный код возврата
      Debug.Print "Exit code = " & i
   End Select
   ' контроль
   dblVal = 0
   For i = 1 To im
      dblVal = dblVal + x(i + im) - x(i + im * 2)
   Next i
   Debug.Assert Abs(dblVal) < 0.001 ' заряд-разряд подсистемы накопителя сбалансированы
   ' результат
   For i = 1 To im
      dblEENSEnergyAvailable(i) = x(i)
      dblEENSLoad(i) = x(i + im * 2) - x(i + im) / dblEfficiency
   Next i
   dblSystemWithENSSLoadDeficite = x(1 + im * 4)
   dblSystemWithENSSLoadReserve = x(2 + im * 4)
End Function

Private Function GetEESSOptimizedParameters(ByRef dblSystemLoad() As Double, ByVal dblEfficiency As Double, _
   ByRef dblNIn As Double, ByRef dblNOut As Double, ByRef dblCapacity As Double, _
   ByRef dblEENSEnergyAvailable() As Double, ByRef dblEENSLoad() As Double, _
   ByRef dblSystemWithENSSLoadDeficite As Double) As Long
Dim i As Long, im As Long, j As Long, k As Long, n As Long
Dim x() As Double, A() As Double, b() As Double, lb() As Double, ub() As Double, s() As Double, x0() As Double
Dim dblVal As Double
   Debug.Assert dblEfficiency > 0 And dblEfficiency <= 1
   im = UBound(dblSystemLoad, 1)
   Debug.Assert im = 24
   ReDim dblEENSEnergyAvailable(1 To im) As Double
   ReDim dblENSSLoad(1 To im) As Double
   n = im * 3 + 4
   k = im * 5

   ReDim A(1 To n, 1 To n) As Double
   ReDim b(1 To n) As Double
   ReDim C(1 To k, 1 To n) As Double
   ReDim cl(1 To k) As Double
   ReDim cu(1 To k) As Double
   ReDim x(1 To n) As Double
   ReDim x0(1 To n) As Double
   ReDim lb(1 To n) As Double
   ReDim ub(1 To n) As Double
   ReDim s(1 To n) As Double
   ' ---
   ' минимальное диагональное усиление нулевой матрицы
   For i = 1 To n
      For j = 1 To n
         A(i, j) = IIf(i = j, 1, 0) * 0.00000001
      Next j
   Next i
   ' веса для 'x':
   For i = 1 To im * 3
      b(i) = 0
   Next i
   b(im * 3 + 1) = 1
   b(im * 3 + 2) = 0.02
   b(im * 3 + 3) = 0.02
   b(im * 3 + 4) = 0.0008
   
   ' ограничения:
   ' связь 'x' и 'y':
   For i = 1 To k
      For j = 1 To n
         C(i, j) = 0
      Next j
   Next i
   For i = 1 To im ' rL
      j = IIf(i > 1, i - 1, im)
      C(i, i) = 1 ' dL[]
      C(i, j) = -1 ' dL[]
      C(i, i + im) = -1 ' CC[]
      C(i, i + im * 2) = 1 ' CD[]
      ' Dmax
      ' Nin
      ' Nout
      ' C
     cl(i) = 0
     cu(i) = 0
   Next i
   For i = 1 To im ' rD
      ' dL[]
      C(i + im, i + im) = -1 / dblEfficiency ' CC[]
      C(i + im, i + im * 2) = 1 ' CD[]
      C(i + im, 1 + im * 3) = 1 ' Dmax
      ' Nin
      ' Nout
      ' C
     cl(i + im) = dblSystemLoad(i)
     cu(i + im) = MaxRealNumber
   Next i
   For i = 1 To im ' rC
      C(i + im * 2, i) = -1 ' dL[]
      ' CC[]
      ' CD[]
      ' Dmax
      ' Nin
      ' Nout
      C(i + im * 2, 4 + im * 3) = 1 ' C
      cl(i + im * 2) = 0
      cu(i + im * 2) = MaxRealNumber
   Next i
   For i = 1 To im ' rNi
      ' dL[]
      C(i + im * 3, i + im) = -1 / dblEfficiency ' CC[]
      ' CD[]
      ' Dmax
      C(i + im * 3, 2 + im * 3) = 1 ' Nin
      ' Nout
      ' C
      cl(i + im * 3) = 0
      cu(i + im * 3) = MaxRealNumber
   Next i
   For i = 1 To im ' rNo
      ' dL[]
      ' CC[]
      C(i + im * 4, i + im * 2) = -1 ' CD[]
      ' Dmax
      ' Nin
      C(i + im * 4, 3 + im * 3) = 1 ' Nout
      ' C
      cl(i + im * 4) = 0
      cu(i + im * 4) = MaxRealNumber
   Next i
   ' ограничения на диапазон 'x':
   For i = 1 To n
      lb(i) = 0
      ub(i) = MaxRealNumber
   Next i
   ' масштаб переменных: =1
   For i = 1 To n
      s(i) = 1
   Next i
   ' начальное приближение: x0=lb+s
   For i = 1 To n
      x0(i) = lb(i) + s(i)
   Next i
   ' расчет
   i = BLEICQPSolve(x, A, b, C, cl, cu, lb, ub, s, x0)
   GetEESSOptimizedParameters = i
   Select Case i
   Case 2
      ' ок, сходимость по x к минимуму
   Case 4
      ' ок, сходимость к минимуму по y
   Case 1, 5, 7, 8
      Debug.Print "Exit code = " & i ' успешное завершение с иным критерием
   Case Else ' отказ, либо неизвестный код возврата
      Debug.Print "Exit code = " & i
   End Select
   ' контроль
   dblVal = 0
   For i = 1 To im
      dblVal = dblVal + x(i + im) - x(i + im * 2)
   Next i
   Debug.Assert Abs(dblVal) < 0.001
   ' результат
   For i = 1 To im
      dblEENSEnergyAvailable(i) = x(i)
      dblEENSLoad(i) = x(i + im * 2) - x(i + im) / dblEfficiency
   Next i
   dblSystemWithENSSLoadDeficite = x(1 + im * 3)
   dblNIn = x(2 + im * 3)
   dblNOut = x(3 + im * 3)
   dblCapacity = x(4 + im * 3)
End Function

Public Sub test_optimize_load()
Dim oWS As Worksheet, oRng As Range
Dim dblSystemLoad() As Double
Dim dblEfficiency As Double, dblNIn As Double, dblNOut As Double, dblCapacity As Double
Dim dblEENSEnergyAvailable() As Double, dblEENSLoad() As Double
Dim dblSystemWithENSSLoadDeficite As Double, dblSystemWithENSSLoadReserve As Double
Dim i As Integer, im As Integer
Dim lRes As Long
Dim arr()
   InitDLLPath ThisWorkbook.Path ' указываем место расположения DLL - в одном каталоге с книгой
   im = 24
   Set oWS = ThisWorkbook.Worksheets("График")
   
   ReDim dblSystemLoad(1 To im) As Double
   ReDim dblEENSEnergyAvailable(1 To im) As Double
   ReDim dblEENSLoad(1 To im) As Double
   ' чтение параметров
   dblEfficiency = oWS.Range("G2")
   dblNIn = oWS.Range("B2")
   dblNOut = oWS.Range("B3")
   dblCapacity = oWS.Range("B4")
   ' чтение графика нагрузки
   Set oRng = oWS.Range("B7:Y7")
   arr = oRng
   Debug.Assert UBound(arr, 2) = im
   For i = 1 To im
      dblSystemLoad(i) = arr(1, i)
   Next i
   ' расчет
'   lRes = GetEESSOptimalLoad(dblSystemLoad, dblEfficiency, dblNIn, dblNOut, dblCapacity, dblEENSEnergyAvailable, dblEENSLoad, dblSystemWithENSSLoadDeficite, dblSystemWithENSSLoadReserve)
   lRes = GetEESSOptimalLoad_new2(dblSystemLoad, dblEfficiency, dblNIn, dblNOut, dblCapacity, dblEENSEnergyAvailable, dblEENSLoad, dblSystemWithENSSLoadDeficite, dblSystemWithENSSLoadReserve)
   ' выгрузка
   oWS.Range("B13") = dblSystemWithENSSLoadDeficite
   oWS.Range("B14") = dblSystemWithENSSLoadReserve
   ReDim arr(1 To 1, 1 To im)
   For i = 1 To im
      arr(1, i) = dblEENSEnergyAvailable(i)
   Next i
   Set oRng = oWS.Range("B10:Y10")
   oRng = arr
   For i = 1 To im
      arr(1, i) = dblEENSLoad(i)
   Next i
   Set oRng = oWS.Range("B11:Y11")
   oRng = arr
End Sub

Public Sub test_optimize_parameters()
Dim oWS As Worksheet, oRng As Range
Dim dblSystemLoad() As Double
Dim dblEfficiency As Double, dblNIn As Double, dblNOut As Double, dblCapacity As Double
Dim dblEENSEnergyAvailable() As Double, dblEENSLoad() As Double
Dim dblSystemWithENSSLoadDeficite As Double, dblSystemWithENSSLoadReserve As Double
Dim i As Integer, im As Integer
Dim lRes As Long
Dim arr()
   InitDLLPath ThisWorkbook.Path ' указываем место расположения DLL - в одном каталоге с книгой
   im = 24
   Set oWS = ThisWorkbook.Worksheets("Минимум")
   
   ReDim dblSystemLoad(1 To im) As Double
   ReDim dblEENSEnergyAvailable(1 To im) As Double
   ReDim dblEENSLoad(1 To im) As Double
   ' чтение параметров
   dblEfficiency = oWS.Range("G2")
   ' чтение графика нагрузки
   Set oRng = oWS.Range("B7:Y7")
   arr = oRng
   Debug.Assert UBound(arr, 2) = im
   For i = 1 To im
      dblSystemLoad(i) = arr(1, i)
   Next i
   ' расчет
   lRes = GetEESSOptimizedParameters(dblSystemLoad, dblEfficiency, dblNIn, dblNOut, dblCapacity, dblEENSEnergyAvailable, dblEENSLoad, dblSystemWithENSSLoadDeficite)
   ' выгрузка
   oWS.Range("B2") = dblNIn
   oWS.Range("B3") = dblNOut
   oWS.Range("B4") = dblCapacity
   oWS.Range("B13") = dblSystemWithENSSLoadDeficite
   ReDim arr(1 To 1, 1 To im)
   For i = 1 To im
      arr(1, i) = dblEENSEnergyAvailable(i)
   Next i
   Set oRng = oWS.Range("B10:Y10")
   oRng = arr
   For i = 1 To im
      arr(1, i) = dblEENSLoad(i)
   Next i
   Set oRng = oWS.Range("B11:Y11")
   oRng = arr
End Sub

