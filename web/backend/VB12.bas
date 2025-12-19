Attribute VB_Name = "Module1"
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
Private Declare Function BLEICQPSolve Lib "QuickQP.dll" (ByRef x() As Double, ByRef A() As Double, ByRef b() As Double, _
    ByRef C() As Double, ByRef cl() As Double, ByRef cu() As Double, ByRef lb() As Double, ByRef ub() As Double, _
    ByRef s() As Double, ByRef x0() As Double) As Long

Private Function MaxDbl(ByVal x As Double, ByVal y As Double) As Double
   MaxDbl = IIf(x >= y, x, y)
End Function


Private Function GetEESSOptimalLoad(ByRef dblSystemLoad() As Double, _
   ByVal dblEfficiency As Double, ByVal dblNIn As Double, ByVal dblNOut As Double, ByVal dblCapacity As Double, _
   ByRef dblEENSEnergyAvailable() As Double, ByRef dblEENSLoad() As Double, _
   ByRef dblSystemWithENSSLoadDeficite As Double, ByRef dblSystemWithENSSLoadReserve As Double) As Long
Dim i As Long, im As Long, j As Long, k As Long, n As Long
Dim x() As Double, A() As Double, b() As Double, lb() As Double, ub() As Double, s() As Double, x0() As Double
Dim dblDmaxWeight As Double, dblDWeight As Double, dblRmaxWeight As Double
Dim dblVal As Double
   ' настройки
   dblDmaxWeight = 1 ' максимальный дефицит мощности
   dblDWeight = dblDmaxWeight / 25 ' дефицит мощность (25 = 24 часа + 1)
   dblRmaxWeight = dblDWeight / 25 ' максимальный резерв мощности (25 = 24 часа + 1)
   ' ---
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
      b(i) = dblDWeight
   Next i
   b(im * 4 + 1) = dblDmaxWeight ' Dmax
   b(im * 4 + 2) = dblRmaxWeight ' Rmax
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
      ub(i) = dblCapacity ' L[]
      ub(i + im) = dblNIn * dblEfficiency ' CC[]
      ub(i + im * 2) = dblNOut ' DD[]
      ub(i + im * 3) = MaxDbl(0, dblSystemLoad(i)) ' D[]
   Next i
   ub(1 + im * 4) = MaxRealNumber ' Dmax
   ub(2 + im * 4) = MaxRealNumber ' Rmax
   ' масштаб переменных: =1
   For i = 1 To n
      s(i) = 1
   Next i
   ' начальное приближение: x0=lb+s
   For i = 1 To n
      x0(i) = IIf(ub(i) - s(i) >= lb(i) + s(i), lb(i) + s(i), 0.5 * lb(i) + 0.5 * ub(i))
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
Dim dblDmaxWeight As Double, dblDWeight As Double, dblNmaxWeight As Double, dblCapacityWeight As Double
Dim dblVal As Double, dblMaxVal As Double
   ' настройки
   dblDmaxWeight = 1 ' максимальный дефицит мощности
   dblNmaxWeight = dblDmaxWeight * 0.5 / 25 ' мощность (25 = 24 часа + 1)
   dblCapacityWeight = dblNmaxWeight / 25 ' емкость (25 = 24 часа + 1)
   dblDWeight = dblNmaxWeight / 25 ' дефицит (25 = 24 часа + 1)
   ' ---
   Debug.Assert dblEfficiency > 0 And dblEfficiency <= 1
   im = UBound(dblSystemLoad, 1)
   Debug.Assert im = 24 ' 24 часа
   ReDim dblEENSEnergyAvailable(1 To im) As Double
   ReDim dblENSSLoad(1 To im) As Double
   n = im * 4 + 4
   k = im * 6
   ' ---
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
   For i = 1 + im * 3 To im * 4
      b(i) = dblDWeight
   Next i
   ' !!! добавить веса для D
   b(im * 4 + 1) = dblDmaxWeight ' дефицит мощности
   b(im * 4 + 2) = dblNmaxWeight ' входная мощность
   b(im * 4 + 3) = dblNmaxWeight ' выходная мощность
   b(im * 4 + 4) = dblCapacityWeight ' емкость
   
   ' ограничения:
   ' связь 'x' и 'y':
   For i = 1 To k
      For j = 1 To n
         C(i, j) = 0
      Next j
   Next i
   For i = 1 To im ' rL[i]=L[i]-L[i-1]-CC[i]+CD[i], rL[i]=0
      j = IIf(i > 1, i - 1, im)
      C(i, i) = 1 ' dL[]
      C(i, j) = -1 ' dL[]
      C(i, i + im) = -1 ' CC[]
      C(i, i + im * 2) = 1 ' CD[]
      ' D[]
      ' Dmax
      ' Nin
      ' Nout
      ' C
     cl(i) = 0
     cu(i) = 0
   Next i
   For i = 1 To im ' rD[i]=-CC[i]/eta+CD[i]+D[i], S[i]<=rD[i]
      ' dL[]
      C(i + im, i + im) = -1 / dblEfficiency ' CC[]
      C(i + im, i + im * 2) = 1 ' CD[]
      C(i + im, i + im * 3) = 1 ' D[]
      ' Dmax
      ' Nin
      ' Nout
      ' C
     cl(i + im) = dblSystemLoad(i)
     cu(i + im) = MaxRealNumber
   Next i
   For i = 1 To im ' rC[i]=-L[i]+C, rC[i]>=0
      C(i + im * 2, i) = -1 ' dL[]
      ' CC[]
      ' CD[]
      ' D[]
      ' Dmax
      ' Nin
      ' Nout
      C(i + im * 2, 4 + im * 4) = 1 ' C
      cl(i + im * 2) = 0
      cu(i + im * 2) = MaxRealNumber
   Next i
   For i = 1 To im ' rNi[i]=-CC[i]/eta+Nin[i], rNi[i]>=0
      ' dL[]
      C(i + im * 3, i + im) = -1 / dblEfficiency ' CC[]
      ' CD[]
      ' D[]
      ' Dmax
      C(i + im * 3, 2 + im * 4) = 1 ' Nin
      ' Nout
      ' C
      cl(i + im * 3) = 0
      cu(i + im * 3) = MaxRealNumber
   Next i
   For i = 1 To im ' rNo[i]=-CD[i]+Nout[i], rNo[i]>=0
      ' dL[]
      ' CC[]
      C(i + im * 4, i + im * 2) = -1 ' CD[]
      ' D[]
      ' Dmax
      ' Nin
      C(i + im * 4, 3 + im * 4) = 1 ' Nout
      ' C
      cl(i + im * 4) = 0
      cu(i + im * 4) = MaxRealNumber
   Next i
   For i = 1 To im ' rDmax[i]=-D[i]+Dmax, rDmax[i]>=0
      ' dL[]
      ' CC[]
      ' CD[]
      C(i + im * 5, i + im * 3) = -1 ' D[]
      C(i + im * 5, 1 + im * 4) = 1 ' Dmax
      ' Nin
      ' Nout
      ' C
      cl(i + im * 5) = 0
      cu(i + im * 5) = MaxRealNumber
   Next i
   ' ограничения на диапазон 'x':
   For i = 1 To n
      lb(i) = 0
   Next i
   For i = 1 To im
      ub(i) = MaxRealNumber ' L[]
      ub(i + im) = MaxRealNumber ' CC[]
      ub(i + im * 2) = MaxRealNumber ' CD[]
   Next i
   For i = 1 To im
      ub(i + im * 3) = MaxDbl(0, dblSystemLoad(i)) ' D[]
   Next i
   For i = im * 4 + 1 To n
      ub(i) = MaxRealNumber ' Dmax, Nin, Nout, C
   Next i
   ' масштаб переменных: =1
   For i = 1 To n
      s(i) = 1 ' scale
   Next i
'   ' начальное приближение: x0=lb+s
'   For i = 1 To n
'      x0(i) = IIf(ub(i) - s(i) >= lb(i) + s(i), lb(i) + s(i), 0.5 * lb(i) + 0.5 * ub(i))
'   Next i
   ' начальное приближение, специфичное задаче, является:
   ' - допустимым на диапазон переменных, кроме переменных дефицита мощности, с запасом не менее scale
   ' - допустимым на диапазон переменных дефицита мощности с запасом не менее максимума из величины scale и полуширины допустимого интервала
   ' - допустимым по ограничению типа равенство
   ' - допустимым на диапазон неравенств, кроме дефицита мощности, с запасом не менее scale
   ' - для диапазона неравенств дефицита мощности:
   ' -- допустимо с запасом не менее scale для (s*eta/scale)<=-1
   ' -- допустимо с запасом менее scale для -1<=(s*eta/scale)<eta-1
   ' -- недопустимо (s*eta/scale)>=eta-1
   ' начальное приближение емкость
   dblMaxVal = 0
   For i = 1 To im
      dblMaxVal = MaxDbl(lb(i) + s(i), dblMaxVal + Abs(dblSystemLoad(i)))
   Next i
   For i = 1 To im ' уровень заряда [L]
      x0(i) = dblMaxVal
   Next i
   x0(im * 4 + 4) = MaxDbl(lb(im * 4 + 4), dblMaxVal) + s(im * 4 + 4)   ' емкость
   ' начальное приближение мощность заряда-разряда
   For i = 1 To im
      dblVal = MaxDbl(lb(i + im) + s(i + im), lb(i + im * 2) + s(i + im * 2)) ' мощность заряда [CC] = мощность разряда [CD]
      x0(i + im) = dblVal
      x0(i + im * 2) = dblVal
   Next i
   ' начальное приближение дефицит мощности
   For i = 1 To im
      dblVal = MaxDbl(lb(i + im * 3), dblSystemLoad(i) + x0(i + im) / dblEfficiency - x0(i + im * 2))
      x0(i + im * 3) = dblVal + s(i + im * 3)
   Next i
   ' начальное приближение максимальный дефицит мощности
   dblMaxVal = lb(im * 4 + 1)
   For i = 1 To im
      dblMaxVal = MaxDbl(dblMaxVal, x0(i + im * 3))
   Next i
   x0(im * 4 + 1) = dblMaxVal + s(im * 4 + 1) ' максимальный дефицит мощности
   ' начальное приближение входная мощность
   dblMaxVal = lb(im * 4 + 2)
   For i = 1 To im
      dblMaxVal = MaxDbl(dblMaxVal, x0(i + im))
   Next i
   x0(im * 4 + 2) = dblMaxVal + s(im * 4 + 2)  ' входная мощность
   ' начальное приближение выходная мощность
   dblMaxVal = lb(im * 4 + 3)
   For i = 1 To im
      dblMaxVal = MaxDbl(dblMaxVal, x0(i + im * 2))
   Next i
   x0(im * 4 + 3) = dblMaxVal + s(im * 4 + 3) ' выходная мощность
   ' расчет
   i = BLEICQPSolve(x, A, b, C, cl, cu, lb, ub, s, x0) ' не справляется со стандартным начальным приближением, которое недопустимо по ограничениям типа равенство, использовать специфичное задаче
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
      Debug.Assert 0
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
   dblSystemWithENSSLoadDeficite = x(1 + im * 4)
   dblNIn = x(2 + im * 4)
   dblNOut = x(3 + im * 4)
   dblCapacity = x(4 + im * 4)
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
   lRes = GetEESSOptimalLoad(dblSystemLoad, dblEfficiency, dblNIn, dblNOut, dblCapacity, dblEENSEnergyAvailable, dblEENSLoad, dblSystemWithENSSLoadDeficite, dblSystemWithENSSLoadReserve)
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

