import xalglib
import math
import cmath
import sys
import random
import traceback
import numpy as np

_TotalResult = True
sys.stdout.write("Python-ALGLIB X-tests:\n")
try:
    _TestResult = True
    test_name = "dummy test"
    try:
        pass
    except RuntimeError as e:
        sys.stdout.write("RuntimeError during %s: '" % (test_name,))
        sys.stdout.write(str(e))
        sys.stdout.write("'\n")
        _TestResult = False
    except ValueError as e:
        sys.stdout.write("ValueError during %s: '" % (test_name,))
        sys.stdout.write(str(e))
        sys.stdout.write("'\n")
        _TestResult = False
    except:
        raise
    sys.stdout.write("%-32s %s\n" % (test_name,"OK" if _TestResult else "FAILED"))
    sys.stdout.flush()
    _TotalResult = _TotalResult and _TestResult
    
    #
    # numpy 1D as input
    #
    _TestResult = True
    test_name = "numpy 1D as input"
    try:
        # bool
        v = np.array([False,True,True,True,False], dtype='bool')
        _TestResult = _TestResult and (xalglib.xdebugb1count(v)==3)
        v = np.array([0,1,1,0,0], dtype='bool')
        _TestResult = _TestResult and (xalglib.xdebugb1count(v)==2)
        v = np.array([0,1,1,2,1], dtype='int32')
        _TestResult = _TestResult and (xalglib.xdebugb1count(v)==4)
        v = np.array([0,1,1,1,0], dtype='bool')
        _TestResult = _TestResult and (xalglib.xdebugb1count(v[::2])==1)
        
        # int
        v = np.array([0,7,6,34], dtype='int8')
        _TestResult = _TestResult and (xalglib.xdebugi1sum(v)==47)
        v = np.array([99,1,54], dtype='uint16')
        _TestResult = _TestResult and (xalglib.xdebugi1sum(v)==154)
        v = np.array([3,4,-5], dtype='int32')
        _TestResult = _TestResult and (xalglib.xdebugi1sum(v)==2)
        v = np.array([0,1,2,3,4,5,6,7], dtype='int32')
        _TestResult = _TestResult and (xalglib.xdebugi1sum(v[::2])==12)
        
        # float
        v = np.array([0,7,6,34], dtype='float32')
        _TestResult = _TestResult and (xalglib.xdebugr1sum(v)==47)
        v = np.array([99,1,54], dtype='float64')
        _TestResult = _TestResult and (xalglib.xdebugr1sum(v)==154)
        v = np.array([3,4,-5], dtype='float64')
        _TestResult = _TestResult and (xalglib.xdebugr1sum(v)==2)
        v = np.array([0,1,2.5,3,4,5,6,7], dtype='float32')
        _TestResult = _TestResult and (xalglib.xdebugr1sum(v[::2])==12.5)
        v = np.array([0,1,2.5,3,4.5,5,6,7], dtype='float64')
        _TestResult = _TestResult and (xalglib.xdebugr1sum(v[::2])==13.0)
        
        # complex
        v = np.array([0+1j,7+2j,6+3j,34+4j], dtype='complex64')
        _TestResult = _TestResult and (xalglib.xdebugc1sum(v)==47+10j)
        v = np.array([99+5j,1-4j,54-1j], dtype='complex128')
        _TestResult = _TestResult and (xalglib.xdebugc1sum(v)==154)
        v = np.array([3+3j,4+4j,-5+5j], dtype='complex128')
        _TestResult = _TestResult and (xalglib.xdebugc1sum(v)==2+12j)
        v = np.array([1j,1,2,3,4,5,6,7+2j], dtype='complex64')
        _TestResult = _TestResult and (xalglib.xdebugc1sum(v[::2])==12+1j)
        v = np.array([0,1,2+2j,3+8j,4,5,6,7], dtype='complex128')
        _TestResult = _TestResult and (xalglib.xdebugc1sum(v[::2])==12+2j)
    except RuntimeError as e:
        sys.stdout.write("RuntimeError during %s: '" % (test_name,))
        sys.stdout.write(str(e))
        sys.stdout.write("'\n")
        _TestResult = False
    except ValueError as e:
        sys.stdout.write("ValueError during %s: '" % (test_name,))
        sys.stdout.write(str(e))
        sys.stdout.write("'\n")
        _TestResult = False
    except:
        raise
    sys.stdout.write("%-32s %s\n" % (test_name,"OK" if _TestResult else "FAILED"))
    sys.stdout.flush()
    _TotalResult = _TotalResult and _TestResult
    
    #
    # numpy 1D as inplace input/output
    #
    _TestResult = True
    test_name = "numpy 1D as inplace"
    try:
        # bool
        v = np.array([False,True,True,False], dtype='bool')
        xalglib.xdebugb1not(v)
        _TestResult = _TestResult and (len(v)==4) and (v[0]==True) and (v[1]==False) and (v[2]==False) and (v[3]==True)
        v = np.array([0,1,1,0,0], dtype='int32')
        xalglib.xdebugb1not(v)
        _TestResult = _TestResult and (len(v)==5) and (v[0]==1) and (v[1]==0) and (v[2]==0) and (v[3]==1) and (v[4]==1)
        v = np.array([0,1,1,1,0], dtype='int8')
        xalglib.xdebugb1not(v[::2])
        _TestResult = _TestResult and (len(v)==5) and (v[0]==1) and (v[1]==1) and (v[2]==0) and (v[3]==1) and (v[4]==1)
        #_TestResult = _TestResult and (xalglib.xdebugb1count(v[::2])==1)
        v = np.array([[0,1,1],[1,0,1]], dtype='float64')
        xalglib.xdebugb1not(v[1,::2])
        _TestResult = _TestResult and (v.shape==(2,3)) and (v[0,0]==0) and (v[0,1]==1) and (v[0,2]==1) and (v[1,0]==0) and (v[1,1]==0) and (v[1,2]==0)
        v = np.array([[1,1,1],[0,0,0]], dtype='float64')
        xalglib.xdebugb1not(v[0:2,1])
        _TestResult = _TestResult and (v.shape==(2,3)) and (v[0,0]==1) and (v[0,1]==0) and (v[0,2]==1) and (v[1,0]==0) and (v[1,1]==1) and (v[1,2]==0)
        
        # int
        v = np.array([6,-2,-6,5], dtype='int32')
        xalglib.xdebugi1neg(v)
        _TestResult = _TestResult and (len(v)==4) and (v[0]==-6) and (v[1]==2) and (v[2]==6) and (v[3]==-5)
        v = np.array([0,1,1,0,0], dtype='int8')
        xalglib.xdebugi1neg(v)
        _TestResult = _TestResult and (len(v)==5) and (v[0]==0) and (v[1]==-1) and (v[2]==-1) and (v[3]==0) and (v[4]==0)
        v = np.array([[0,1,1],[1,2,1]], dtype='intp')
        xalglib.xdebugi1neg(v[1,::2])
        _TestResult = _TestResult and (v.shape==(2,3)) and (v[0,0]==0) and (v[0,1]==1) and (v[0,2]==1) and (v[1,0]==-1) and (v[1,1]==2) and (v[1,2]==-1)
        v = np.array([[1,1,1],[2,2,2]], dtype='int8')
        xalglib.xdebugi1neg(v[0:2,1])
        _TestResult = _TestResult and (v.shape==(2,3)) and (v[0,0]==1) and (v[0,1]==-1) and (v[0,2]==1) and (v[1,0]==2) and (v[1,1]==-2) and (v[1,2]==2)
        
        # real
        v = np.array([6,-2,-6,5], dtype='float32')
        xalglib.xdebugr1neg(v)
        _TestResult = _TestResult and (len(v)==4) and (v[0]==-6) and (v[1]==2) and (v[2]==6) and (v[3]==-5)
        v = np.array([0,1,1,0,0], dtype='float64')
        xalglib.xdebugr1neg(v)
        _TestResult = _TestResult and (len(v)==5) and (v[0]==0) and (v[1]==-1) and (v[2]==-1) and (v[3]==0) and (v[4]==0)
        v = np.array([[0,1,1],[1,2,1]], dtype='float32')
        xalglib.xdebugr1neg(v[1,::2])
        _TestResult = _TestResult and (v.shape==(2,3)) and (v[0,0]==0) and (v[0,1]==1) and (v[0,2]==1) and (v[1,0]==-1) and (v[1,1]==2) and (v[1,2]==-1)
        v = np.array([[1,1,1],[2,2,2]], dtype='float64')
        xalglib.xdebugr1neg(v[0:2,1])
        _TestResult = _TestResult and (v.shape==(2,3)) and (v[0,0]==1) and (v[0,1]==-1) and (v[0,2]==1) and (v[1,0]==2) and (v[1,1]==-2) and (v[1,2]==2)
                
        # complex
        v = np.array([6+1j,-2-5j], dtype='complex64')
        xalglib.xdebugc1neg(v)
        _TestResult = _TestResult and (len(v)==2) and (v[0]==-6-1j) and (v[1]==2+5j)
        v = np.array([0,1,1j,2+2j], dtype='complex128')
        xalglib.xdebugc1neg(v)
        _TestResult = _TestResult and (len(v)==4) and (v[0]==0) and (v[1]==-1) and (v[2]==-1j) and (v[3]==-2-2j)
        v = np.array([[0,1,1],[1,2,1j]], dtype='complex128')
        xalglib.xdebugc1neg(v[1,::2])
        _TestResult = _TestResult and (v.shape==(2,3)) and (v[0,0]==0) and (v[0,1]==1) and (v[0,2]==1) and (v[1,0]==-1) and (v[1,1]==2) and (v[1,2]==-1j)
        v = np.array([[1,1,1],[2,2j,2]], dtype='complex64')
        xalglib.xdebugc1neg(v[0:2,1])
        _TestResult = _TestResult and (v.shape==(2,3)) and (v[0,0]==1) and (v[0,1]==-1) and (v[0,2]==1) and (v[1,0]==2) and (v[1,1]==-2j) and (v[1,2]==2)
    except RuntimeError as e:
        sys.stdout.write("RuntimeError during %s: '" % (test_name,))
        sys.stdout.write(str(e))
        sys.stdout.write("'\n")
        _TestResult = False
    except ValueError as e:
        sys.stdout.write("ValueError during %s: '" % (test_name,))
        sys.stdout.write(str(e))
        sys.stdout.write("'\n")
        _TestResult = False
    except:
        raise
    sys.stdout.write("%-32s %s\n" % (test_name,"OK" if _TestResult else "FAILED"))
    sys.stdout.flush()
    _TotalResult = _TotalResult and _TestResult
    
    #
    # numpy 2D as input
    #
    _TestResult = True
    test_name = "numpy 2D as input"
    try:
        
        # bool
        v = np.array([[False,True,False],[True,True,False]], dtype='bool')
        _TestResult = _TestResult and (xalglib.xdebugb2count(v)==3)
        v = np.array([[0,1],[1,0],[1,1]], dtype='bool')
        _TestResult = _TestResult and (xalglib.xdebugb2count(v)==4)
        v = np.array([[0,1],[1,0],[0,1]], dtype='int32')
        _TestResult = _TestResult and (xalglib.xdebugb2count(v)==3)
        v = np.array([[[0,1],[1,0]],[[0,0],[0,0]],[[1,1],[1,1]]], dtype='int32')
        _TestResult = _TestResult and (xalglib.xdebugb2count(v[0,0:2,0:2])==2)
        _TestResult = _TestResult and (xalglib.xdebugb2count(v[0:2,0:2,0])==1)
        _TestResult = _TestResult and (xalglib.xdebugb2count(v[0:3,0:2,0])==3)
        
        # int
        v = np.array([[1,2,3],[-3,-4,-5]], dtype='int8')
        _TestResult = _TestResult and (xalglib.xdebugi2sum(v)==-6)
        v = np.array([[0,1],[1,0],[1,1]], dtype='int32')
        _TestResult = _TestResult and (xalglib.xdebugi2sum(v)==4)
        v = np.array([[0,1],[1,0],[0,1]], dtype='intp')
        _TestResult = _TestResult and (xalglib.xdebugi2sum(v)==3)
        v = np.array([[[0,1],[1,0]],[[0,0],[0,0]],[[1,1],[1,1]]], dtype='int32')
        _TestResult = _TestResult and (xalglib.xdebugi2sum(v[0,0:2,0:2])==2)
        _TestResult = _TestResult and (xalglib.xdebugi2sum(v[0:2,0:2,0])==1)
        _TestResult = _TestResult and (xalglib.xdebugi2sum(v[0:3,0:2,0])==3)
        
        # real
        v = np.array([[1,2,3],[-3,-4,-5]], dtype='float32')
        _TestResult = _TestResult and (xalglib.xdebugr2sum(v)==-6)
        v = np.array([[0,1.5],[1,0],[1.5,1.5]], dtype='float64')
        _TestResult = _TestResult and (xalglib.xdebugr2sum(v)==5.5)
        v = np.array([[0,1],[1,0.5],[-0.5,1]], dtype='float64')
        _TestResult = _TestResult and (xalglib.xdebugr2sum(v)==3)
        v = np.array([[[0,1],[1,0]],[[0,0],[0,0]],[[1,1],[1,1]]], dtype='float64')
        _TestResult = _TestResult and (xalglib.xdebugr2sum(v[0,0:2,0:2])==2)
        _TestResult = _TestResult and (xalglib.xdebugr2sum(v[0:2,0:2,0])==1)
        _TestResult = _TestResult and (xalglib.xdebugr2sum(v[0:3,0:2,0])==3)
        
        # complex
        v = np.array([[1,2j,3],[-3,-4j,-5]], dtype='complex64')
        _TestResult = _TestResult and (xalglib.xdebugc2sum(v)==-4-2j)
        v = np.array([[0,1.5],[1,0],[1.5j,1.5]], dtype='complex128')
        _TestResult = _TestResult and (xalglib.xdebugc2sum(v)==4+1.5j)
        v = np.array([[1j,1],[1,0.5j],[-0.5,1]], dtype='complex128')
        _TestResult = _TestResult and (xalglib.xdebugc2sum(v)==2.5+1.5j)
        v = np.array([[[0,1],[1,0]],[[0,0],[0,0]],[[0.5j,1.5j],[1j,1j]]], dtype='complex128')
        _TestResult = _TestResult and (xalglib.xdebugc2sum(v[0,0:2,0:2])==2)
        _TestResult = _TestResult and (xalglib.xdebugc2sum(v[0:2,0:2,0])==1)
        _TestResult = _TestResult and (xalglib.xdebugc2sum(v[0:3,0:2,0])==1+1.5j)
    except RuntimeError as e:
        sys.stdout.write("RuntimeError during %s: '" % (test_name,))
        sys.stdout.write(str(e))
        sys.stdout.write("'\n")
        _TestResult = False
    except ValueError as e:
        sys.stdout.write("ValueError during %s: '" % (test_name,))
        sys.stdout.write(str(e))
        sys.stdout.write("'\n")
        _TestResult = False
    except:
        raise
    sys.stdout.write("%-32s %s\n" % (test_name,"OK" if _TestResult else "FAILED"))
    sys.stdout.flush()
    _TotalResult = _TotalResult and _TestResult
    
    #
    # numpy 2D as inplace input/output
    #
    _TestResult = True
    test_name = "numpy 2D as inplace"
    try:
        
        # bool
        v = np.array([[False,True,False],[True,True,False]], dtype='bool')
        xalglib.xdebugb2not(v)
        _TestResult = _TestResult and (v.shape==(2,3)) and (v[0,0]==True) and (v[0,1]==False) and (v[0,2]==True) and (v[1,0]==False) and (v[1,1]==False) and (v[1,2]==True)
        v= np.array([[[0,1],[1,0]],[[0,0],[0,0]],[[1,1],[1,1]]], dtype='bool')
        xalglib.xdebugb2not(v[0,0:2,0:2])
        _TestResult = _TestResult and (v.shape==(3,2,2))
        _TestResult = _TestResult and (v[0,0,0]==True)  and (v[0,0,1]==False) and (v[0,1,0]==False) and (v[0,1,1]==True)
        _TestResult = _TestResult and (v[1,0,0]==False) and (v[1,0,1]==False) and (v[1,1,0]==False) and (v[1,1,1]==False)
        _TestResult = _TestResult and (v[2,0,0]==True)  and (v[2,0,1]==True)  and (v[2,1,0]==True)  and (v[2,1,1]==True)
        xalglib.xdebugb2not(v[0:2,0:2,0])
        _TestResult = _TestResult and (v.shape==(3,2,2))
        _TestResult = _TestResult and (v[0,0,0]==False) and (v[0,0,1]==False) and (v[0,1,0]==True)  and (v[0,1,1]==True)
        _TestResult = _TestResult and (v[1,0,0]==True)  and (v[1,0,1]==False) and (v[1,1,0]==True)  and (v[1,1,1]==False)
        _TestResult = _TestResult and (v[2,0,0]==True)  and (v[2,0,1]==True)  and (v[2,1,0]==True)  and (v[2,1,1]==True)
        xalglib.xdebugb2not(v[0:3,0,0:2])
        _TestResult = _TestResult and (v.shape==(3,2,2))
        _TestResult = _TestResult and (v[0,0,0]==True)  and (v[0,0,1]==True)  and (v[0,1,0]==True)  and (v[0,1,1]==True)
        _TestResult = _TestResult and (v[1,0,0]==False) and (v[1,0,1]==True)  and (v[1,1,0]==True)  and (v[1,1,1]==False)
        _TestResult = _TestResult and (v[2,0,0]==False) and (v[2,0,1]==False) and (v[2,1,0]==True)  and (v[2,1,1]==True)
        
        # int
        v = np.array([[0,1,3],[-6,8,-9]], dtype='int8')
        xalglib.xdebugi2neg(v)
        _TestResult = _TestResult and (v.shape==(2,3)) and (v[0,0]==0) and (v[0,1]==-1) and (v[0,2]==-3) and (v[1,0]==6) and (v[1,1]==-8) and (v[1,2]==9)
        v = np.array([[0,1,3],[-6,88,-9]], dtype='int64')
        xalglib.xdebugi2neg(v)
        _TestResult = _TestResult and (v.shape==(2,3)) and (v[0,0]==0) and (v[0,1]==-1) and (v[0,2]==-3) and (v[1,0]==6) and (v[1,1]==-88) and (v[1,2]==9)
        v= np.array([[[0,3],[-1,0]],[[0,6],[5,0]],[[4,-4],[5,-7]]], dtype='intp')
        xalglib.xdebugi2neg(v[0,0:2,0:2])
        _TestResult = _TestResult and (v.shape==(3,2,2))
        _TestResult = _TestResult and (v[0,0,0]==+0) and (v[0,0,1]==-3) and (v[0,1,0]==+1) and (v[0,1,1]==+0)
        _TestResult = _TestResult and (v[1,0,0]==+0) and (v[1,0,1]==+6) and (v[1,1,0]==+5) and (v[1,1,1]==+0)
        _TestResult = _TestResult and (v[2,0,0]==+4) and (v[2,0,1]==-4) and (v[2,1,0]==+5) and (v[2,1,1]==-7)
        xalglib.xdebugi2neg(v[0:2,0:2,0])
        _TestResult = _TestResult and (v.shape==(3,2,2))
        _TestResult = _TestResult and (v[0,0,0]==+0) and (v[0,0,1]==-3) and (v[0,1,0]==-1) and (v[0,1,1]==+0)
        _TestResult = _TestResult and (v[1,0,0]==+0) and (v[1,0,1]==+6) and (v[1,1,0]==-5) and (v[1,1,1]==+0)
        _TestResult = _TestResult and (v[2,0,0]==+4) and (v[2,0,1]==-4) and (v[2,1,0]==+5) and (v[2,1,1]==-7)
        xalglib.xdebugi2neg(v[0:3,0,0:2])
        _TestResult = _TestResult and (v.shape==(3,2,2))
        _TestResult = _TestResult and (v[0,0,0]==+0) and (v[0,0,1]==+3) and (v[0,1,0]==-1) and (v[0,1,1]==+0)
        _TestResult = _TestResult and (v[1,0,0]==+0) and (v[1,0,1]==-6) and (v[1,1,0]==-5) and (v[1,1,1]==+0)
        _TestResult = _TestResult and (v[2,0,0]==-4) and (v[2,0,1]==+4) and (v[2,1,0]==+5) and (v[2,1,1]==-7)
        """
        _TestResult = _TestResult and (xalglib.xdebugb2count(v[0,0:2,0:2])==2)
        _TestResult = _TestResult and (xalglib.xdebugb2not(v[0:2,0:2,0])==1)
        _TestResult = _TestResult and (xalglib.xdebugb2count(v[0:3,0:2,0])==3)
        
        # int
        v = np.array([[1,2,3],[-3,-4,-5]], dtype='int8')
        _TestResult = _TestResult and (xalglib.xdebugi2sum(v)==-6)
        v = np.array([[0,1],[1,0],[1,1]], dtype='int32')
        _TestResult = _TestResult and (xalglib.xdebugi2sum(v)==4)
        v = np.array([[0,1],[1,0],[0,1]], dtype='intp')
        _TestResult = _TestResult and (xalglib.xdebugi2sum(v)==3)
        v = np.array([[[0,1],[1,0]],[[0,0],[0,0]],[[1,1],[1,1]]], dtype='int32')
        _TestResult = _TestResult and (xalglib.xdebugi2sum(v[0,0:2,0:2])==2)
        _TestResult = _TestResult and (xalglib.xdebugi2sum(v[0:2,0:2,0])==1)
        _TestResult = _TestResult and (xalglib.xdebugi2sum(v[0:3,0:2,0])==3)
        
        # real
        v = np.array([[1,2,3],[-3,-4,-5]], dtype='float32')
        _TestResult = _TestResult and (xalglib.xdebugr2sum(v)==-6)
        v = np.array([[0,1.5],[1,0],[1.5,1.5]], dtype='float64')
        _TestResult = _TestResult and (xalglib.xdebugr2sum(v)==5.5)
        v = np.array([[0,1],[1,0.5],[-0.5,1]], dtype='float64')
        _TestResult = _TestResult and (xalglib.xdebugr2sum(v)==3)
        v = np.array([[[0,1],[1,0]],[[0,0],[0,0]],[[1,1],[1,1]]], dtype='float64')
        _TestResult = _TestResult and (xalglib.xdebugr2sum(v[0,0:2,0:2])==2)
        _TestResult = _TestResult and (xalglib.xdebugr2sum(v[0:2,0:2,0])==1)
        _TestResult = _TestResult and (xalglib.xdebugr2sum(v[0:3,0:2,0])==3)
        
        # complex
        v = np.array([[1,2j,3],[-3,-4j,-5]], dtype='complex64')
        _TestResult = _TestResult and (xalglib.xdebugc2sum(v)==-4-2j)
        v = np.array([[0,1.5],[1,0],[1.5j,1.5]], dtype='complex128')
        _TestResult = _TestResult and (xalglib.xdebugc2sum(v)==4+1.5j)
        v = np.array([[1j,1],[1,0.5j],[-0.5,1]], dtype='complex128')
        _TestResult = _TestResult and (xalglib.xdebugc2sum(v)==2.5+1.5j)
        v = np.array([[[0,1],[1,0]],[[0,0],[0,0]],[[0.5j,1.5j],[1j,1j]]], dtype='complex128')
        _TestResult = _TestResult and (xalglib.xdebugc2sum(v[0,0:2,0:2])==2)
        _TestResult = _TestResult and (xalglib.xdebugc2sum(v[0:2,0:2,0])==1)
        _TestResult = _TestResult and (xalglib.xdebugc2sum(v[0:3,0:2,0])==1+1.5j)
        """
    except RuntimeError as e:
        sys.stdout.write("RuntimeError during %s: '" % (test_name,))
        sys.stdout.write(str(e))
        sys.stdout.write("'\n")
        _TestResult = False
    except ValueError as e:
        sys.stdout.write("ValueError during %s: '" % (test_name,))
        sys.stdout.write(str(e))
        sys.stdout.write("'\n")
        _TestResult = False
    except:
        raise
    sys.stdout.write("%-32s %s\n" % (test_name,"OK" if _TestResult else "FAILED"))
    sys.stdout.flush()
    _TotalResult = _TotalResult and _TestResult
    
except Exception as e:
    sys.stdout.write("Unhandled exception was raised!\n")
    sys.stdout.write("MESSAGE: ")
    sys.stdout.write(str(e))
    sys.stdout.write("\n")
    traceback.print_exc()
    sys.exit(1)
if _TotalResult:
    sys.exit(0)
else:
    sys.exit(1)
