# 核心概念
## 简介
Granger因果关系检验基于自回归模型
## lag value
过去值,或称落后期:同一变项比当期**时间上**更早的值,如当期为$y_{10}$,落后期为$y_{i<10}$

## 基本观念
未来的时间不会对目前与过去产生因果关系,而过去的事件才可能对现在及未来产生影响.假如在控制了变量y的过去值后,变量x的过去值仍能对变量y有显著的解释能力,则称x能"Granger-cause" y

# 局限性
最初的Granger 因果测试没有纳入干扰变量的分析,无法发现真正的因果关系.

# 代码部分
```python
def grangercausalitytests(x, maxlag, addconst=True, verbose=True):
# params:
#	x: data for test whether the time series in the second column 
#          Granger causes the time series in the first column 
#	maxlag: the Granger causality test results are calculated for all lags up to maxlag
	for mxlg in range(1, maxlag + 1):
		dta = lagmat2ds(x, mxlg, trim='both', dropex=1) # lag矩阵
		# 舍弃第一列,并在数据的最后加上值为1的一列
		dtaown = add_constant(dta[:, 1:(mxlg + 1)], prepend=False)
		dtajoint = add_constant(dta[:, 1:], prepend=False)

		# 普通最小二乘法
		res2down = OLS(dta[:, 0], dtaown).fit()
        res2djoint = OLS(dta[:, 0], dtajoint).fit()

		# 利用残差平方和(ssr)进行F检验
		# df_resid: 残余自由度 n - p
		# sf: 生存函数
		fgc1 = ((res2down.ssr - res2djoint.ssr) /
                res2djoint.ssr / mxlg * res2djoint.df_resid)
		result['ssr_ftest'] = (fgc1,
                               stats.f.sf(fgc1, mxlg, res2djoint.df_resid),
                               res2djoint.df_resid, mxlg)

		# 利用残差平方和进行ch2检验
		# nobs: 观测次数
		fgc2 = res2down.nobs * (res2down.ssr - res2djoint.ssr) / res2djoint.ssr
        result['ssr_chi2test'] = (fgc2, stats.chi2.sf(fgc2, mxlg), mxlg)

		# 似然比检验
		lr = -2 * (res2down.llf - res2djoint.llf)
        result['lrtest'] = (lr, stats.chi2.sf(lr, mxlg), mxlg)

        # 外生变量的滞后系数均为0情况下的F检验
        rconstr = np.column_stack((np.zeros((mxlg, mxlg)),
                                   np.eye(mxlg, mxlg),
                                   np.zeros((mxlg, 1))))
        ftres = res2djoint.f_test(rconstr)
		result['params_ftest'] = (np.squeeze(ftres.fvalue)[()],
                                  np.squeeze(ftres.pvalue)[()],
                                  ftres.df_denom, ftres.df_num)
```
