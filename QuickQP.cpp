// QuickQP.cpp : Определяет экспортированные функции для приложения DLL.
//

#include "stdafx.h"

#include "stdafx.h"
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "optimization.h"

using namespace alglib;

/*Following completion codes are returned:
*-9    failure of the automatic scale evaluation : one  of  the  diagonal elements of the quadratic term is non - positive. 
	Specify variable scales manually!
*-5    inappropriate solver was used :
	*QuickQP solver for problem with general linear constraints
*-4    the function is unbounded from below even under constraints, no meaningful minimum can be found.
*-3    inconsistent constraints(or , maybe, feasible point is too hard to find).
*-2    IPM solver has difficulty finding primal / dual feasible point.
	It is likely that the problem is either infeasible or unbounded, but it is difficult to determine exact reason for termination.
	X contains best point found so far.
*> 0   success
* 7    stopping conditions are too stringent, further improvement is impossible, X contains best point found so far.
*/

__declspec(dllexport) int __stdcall BLEICQPSolve(SAFEARRAY **mX, SAFEARRAY **mA, SAFEARRAY **mB, SAFEARRAY **mC, SAFEARRAY **mCL, SAFEARRAY **mCU, SAFEARRAY **mBndL, SAFEARRAY **mBndU, SAFEARRAY **mS, SAFEARRAY **mX0)
{
	int ret;
	int i, j, n;
	double *dblX;
	real_2d_array a;
	real_1d_array b;
	real_2d_array c;
	real_1d_array cl;
	real_1d_array cu;
	real_1d_array x0;
	real_1d_array s;
	real_1d_array bndl;
	real_1d_array bndu;
	real_1d_array x;
	ae_int_t k;
	minqpstate state;
	minqpreport rep;

	ret = 0;
	// dimensions check
	if (((*mX)->cDims != 1) || ((*mA)->cDims != 2) || ((*mB)->cDims != 1) || ((*mC)->cDims != 2) || ((*mCL)->cDims != 1) || ((*mCU)->cDims != 1) || ((*mBndL)->cDims != 1) || ((*mBndU)->cDims != 1) || ((*mS)->cDims != 1))
	{
		ret = -101;
		return ret;
	}
	n = ((*mX)->rgsabound)[0].cElements;
	k = ((*mCU)->rgsabound)[0].cElements;
	if ((((*mA)->rgsabound)[0].cElements != n) || (((*mA)->rgsabound)[1].cElements != n) || (((*mB)->rgsabound)[0].cElements != n) || (((*mC)->rgsabound)[0].cElements != n) || (((*mC)->rgsabound)[1].cElements != k) || (((*mCL)->rgsabound)[0].cElements != k) || (((*mCU)->rgsabound)[0].cElements != k) || (((*mBndL)->rgsabound)[0].cElements != n) || (((*mBndU)->rgsabound)[0].cElements != n) || (((*mS)->rgsabound)[0].cElements != n) || (((*mX0)->rgsabound)[0].cElements != n))
	{
		ret = -102;
		return ret;
	}
	if ((((*mA)->rgsabound)[0].lLbound != 1) || (((*mA)->rgsabound)[1].lLbound != 1) || (((*mB)->rgsabound)[0].lLbound != 1) || (((*mC)->rgsabound)[0].lLbound != 1) || (((*mC)->rgsabound)[1].lLbound != 1) || (((*mCL)->rgsabound)[0].lLbound != 1) || (((*mCU)->rgsabound)[0].lLbound != 1) || (((*mBndL)->rgsabound)[0].lLbound != 1) || (((*mBndU)->rgsabound)[0].lLbound != 1) || (((*mS)->rgsabound)[0].lLbound != 1) || (((*mX0)->rgsabound)[0].lLbound != 1))
	{
		ret = -103;
		return ret;
	}

	// allocate work variables
	a.setlength(n, n);
	b.setlength(n);
	x0.setlength(n);
	c.setlength(k, n);
	cl.setlength(k);
	cu.setlength(k);
	s.setlength(n);
	bndl.setlength(n);
	bndu.setlength(n);
	x.setlength(n);

	// copy arrays with transponse
	for (i = 0; i < n; i++)
		for (j = 0; j < n; j++) a(j, i) = ((double*)((*mA)->pvData))[i * n + j];
	for (i = 0; i < n; ++i) b(i) = ((double*)((*mB)->pvData))[i];
	for (i = 0; i < n; ++i) x0(i) = ((double*)((*mX0)->pvData))[i];
	for (i = 0; i < n; i++)
		for (j = 0; j < k; j++) c(j, i) = ((double*)((*mC)->pvData))[i * k + j];
	for (i = 0; i < k; ++i) cl(i) = ((double*)((*mCL)->pvData))[i];
	for (i = 0; i < k; ++i) cu(i) = ((double*)((*mCU)->pvData))[i];
	for (i = 0; i < n; ++i) s(i) = ((double*)((*mS)->pvData))[i];
	for (i = 0; i < n; ++i) bndl(i) = ((double*)((*mBndL)->pvData))[i];
	for (i = 0; i < n; ++i) bndu(i) = ((double*)((*mBndU)->pvData))[i];

	for (i = 0; i < k; ++i) cl(i) = (cl(i) <= -ae_maxrealnumber ? fp_neginf : cl(i));
	for (i = 0; i < k; ++i) cl(i) = (cl(i) >= ae_maxrealnumber ? fp_posinf : cl(i));
	for (i = 0; i < k; ++i) cu(i) = (cu(i) <= -ae_maxrealnumber ? fp_neginf : cu(i));
	for (i = 0; i < k; ++i) cu(i) = (cu(i) >= ae_maxrealnumber ? fp_posinf : cu(i));

	// create solver, set quadratic/linear terms
	minqpcreate(n, state);
	minqpsetquadraticterm(state, a);
	minqpsetlinearterm(state, b);
	minqpsetstartingpoint(state, x0);
	minqpsetbc(state, bndl, bndu);
	minqpsetlc2dense(state, c, cl, cu, k);

	// Set scale of the parameters.
	// NOTE: for convex problems you may try using minqpsetscaleautodiag() which automatically determines variable scales.
	minqpsetscale(state, s);

	// Solve problem with BLEIC-QP solver.
	// Default stopping criteria are used, Newton phase is active.
	minqpsetalgobleic(state, 0.0, 0.0, 0.0, 0);
	minqpoptimize(state);
	minqpresults(state, x, rep);

	// save result
	dblX = (double*)((*mX)->pvData);
	for (i = 0; i < n; i++)
	{
		dblX[i] = x(i);
	}
	// exit
	return int(rep.terminationtype);
}
