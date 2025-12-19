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

' BLEICQPSolve решает задачу квадратичной оптимизации с двусторонними ограничени€ми общего вида:
' min F(x), F(x)=0.5*x'*A*x+b'*x
' с ограничени€ми: lb<=x<=ub
'   cl<=C'*x<=cu
' —тарт с точки x0
' ћасштаб x задан в s
' ћатрица A должна быть симметричной.

#If VBA7 Then
   Private Declare PtrSafe Function SetEnvironmentVariableA Lib "kernel32" (ByVal lpname As String, ByVal lpValue As String) As Long
   Private Declare PtrSafe Function GetEnvironmentVariableA Lib "kernel32" (ByVal lpname As String, ByVal lpBuffer As String, ByVal nSize As Long) As Long
   Private Declare PtrSafe Function BLEICQPSolve Lib "QuickQP.dll" (ByRef x() As Double, ByRef A() As Double, ByRef b() As Double, _
      ByRef C() As Double, ByRef cl() As Double, ByRef cu() As Double, ByRef lb() As Double, ByRef ub() As Double, _
      ByRef s() As Double, ByRef x0() As Double) As Long
#Else
   Private Declare Function SetEnvironmentVariableA Lib "kernel32" (ByVal lpname As String, ByVal lpValue As String) As Long
   Private Declare Function GetEnvironmentVariableA Lib "kernel32" (ByVal lpname As String, ByVal lpBuffer As String, ByVal nSize As Long) As Long
   Private Declare Function BLEICQPSolve Lib "QuickQP.dll" (ByRef x() As Double, ByRef A() As Double, ByRef b() As Double, _
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
   ' веса дл€ 'x':
   For i = 1 To im * 3
      b(i) = 0
   Next i
   For i = im * 3 + 1 To im * 4
      b(i) = 0.04
   Next i
   b(im * 4 + 1) = 1
   b(im * 4 + 2) = 0.0016
   ' ограничени€:
   ' св€зь 'x' и 'y':
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
   ' ограничени€ на диапазон 'x':
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
   Debug.Assert Abs(dblVal) < 0.001 ' зар€д-разр€д подсистемы накопител€ сбалансированы
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
   ' веса дл€ 'x':
   For i = 1 To im * 3
      b(i) = 0
   Next i
   b(im * 3 + 1) = 1
   b(im * 3 + 2) = 0.02
   b(im * 3 + 3) = 0.02
   b(im * 3 + 4) = 0.0008
   
   ' ограничени€:
   ' св€зь 'x' и 'y':
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
   ' ограничени€ на диапазон 'x':
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
   InitDLLPath ThisWorkbook.Path ' указываем место расположени€ DLL - в одном каталоге с книгой
   im = 24
   Set oWS = ThisWorkbook.Worksheets("√рафик")
   
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
   InitDLLPath ThisWorkbook.Path ' указываем место расположени€ DLL - в одном каталоге с книгой
   im = 24
   Set oWS = ThisWorkbook.Worksheets("ћинимум")
   
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

