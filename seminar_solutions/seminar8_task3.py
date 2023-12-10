import numpy as np
import pandas as pd
from pydantic import BaseModel
from scipy import stats


class Design(BaseModel):
    """Дата-класс с описание параметров эксперимента.

    statistical_test - тип статтеста. ['ttest', 'bootstrap']
    effect - размер эффекта в процентах
    alpha - уровень значимости
    beta - допустимая вероятность ошибки II рода
    stratification - постстратификация. 'on' - использовать постстратификация, 'off - не использовать.
    """
    statistical_test: str = 'ttest'
    effect: float = 3.
    alpha: float = 0.05
    beta: float = 0.1
    stratification: str = 'off'


class ExperimentsService:

    def _ttest_strat(self, metrics_strat_a_group, metrics_strat_b_group):
        """Применяет постстратификацию, возвращает pvalue.

        Веса страт считаем по данным обеих групп.
        Предполагаем, что эксперимент проводится на всей популяции.
        Веса страт нужно считать по данным всей популяции.

        :param metrics_strat_a_group (np.ndarray): значения метрик и страт группы A.
            shape = (n, 2), первый столбец - метрики, второй столбец - страты.
        :param metrics_strat_b_group (np.ndarray): значения метрик и страт группы B.
            shape = (n, 2), первый столбец - метрики, второй столбец - страты.
        :param design (Design): объект с данными, описывающий параметры эксперимента
        :return (float): значение p-value
        """
        # YOUR_CODE_HERE
        a = pd.DataFrame(metrics_strat_a_group, columns=['metric', 'strat'])
        b = pd.DataFrame(metrics_strat_b_group, columns=['metric', 'strat'])
        df = pd.concat([a, b], ignore_index=False)
        weights = df['strat'].value_counts(normalize=True)
        
        # Stratified mean - a
        a_strat_mean = a.groupby('strat')['metric'].mean()
        a_means_weights = pd.merge(
            a_strat_mean,
            pd.Series(weights, name='weight'),
            how='inner',
            left_index=True,
            right_index=True
        )

        a_means_weights['weight'] = a_means_weights['weight'] / a_means_weights['weight'].sum()
        a_mean_final = (a_means_weights['weight'] * a_means_weights['metric']).sum()
        
        # Stratified var - a
        a_strat_var = a.groupby('strat')['metric'].var()
        a_vars_weights = pd.merge(
            a_strat_var,
            pd.Series(weights, name='weight'),
            how='inner',
            left_index=True,
            right_index=True
        )

        a_vars_weights['weight'] = a_vars_weights['weight'] / a_vars_weights['weight'].sum()
        a_var_final = (a_vars_weights['weight'] * a_vars_weights['metric']).sum()
        
        # Stratified mean - b
        b_strat_mean = b.groupby('strat')['metric'].mean()
        b_means_weights = pd.merge(
            b_strat_mean,
            pd.Series(weights, name='weight'),
            how='inner',
            left_index=True,
            right_index=True
        )

        b_means_weights['weight'] = b_means_weights['weight'] / b_means_weights['weight'].sum()
        b_mean_final = (b_means_weights['weight'] * b_means_weights['metric']).sum()
        
        # Stratified var - b
        b_strat_var = b.groupby('strat')['metric'].var()
        b_vars_weights = pd.merge(
            b_strat_var,
            pd.Series(weights, name='weight'),
            how='inner',
            left_index=True,
            right_index=True
        )

        b_vars_weights['weight'] = b_vars_weights['weight'] / b_vars_weights['weight'].sum()
        b_var_final = (b_vars_weights['weight'] * b_vars_weights['metric']).sum()
        
        # Stratified t-test
        se = (a_var_final / len(a) + b_var_final / len(b)) ** 0.5
        t = (a_mean_final - b_mean_final) / se
        pvalue = (1 - stats.norm.cdf(np.abs(t))) * 2
        # print(pvalue)
        return pvalue
        

    def get_pvalue(self, metrics_strat_a_group, metrics_strat_b_group, design):
        """Применяет статтест, возвращает pvalue.

        :param metrics_strat_a_group (np.ndarray): значения метрик и страт группы A.
            shape = (n, 2), первый столбец - метрики, второй столбец - страты.
        :param metrics_strat_b_group (np.ndarray): значения метрик и страт группы B.
            shape = (n, 2), первый столбец - метрики, второй столбец - страты.
        :param design (Design): объект с данными, описывающий параметры эксперимента
        :return (float): значение p-value
        """
        if design.statistical_test == 'ttest':
            if design.stratification == 'off':
                _, pvalue = stats.ttest_ind(metrics_strat_a_group[:, 0], metrics_strat_b_group[:, 0])
                return pvalue
            elif design.stratification == 'on':
                return self._ttest_strat(metrics_strat_a_group, metrics_strat_b_group)
            else:
                raise ValueError('Неверный design.stratification')
        else:
            raise ValueError('Неверный design.statistical_test')


if __name__ == '__main__':
    metrics_strat_a_group = np.zeros((10, 2,))
    metrics_strat_a_group[:, 0] = np.arange(10)
    metrics_strat_a_group[:, 1] = (np.arange(10) < 4).astype(float)
    metrics_strat_b_group = np.zeros((10, 2,))
    metrics_strat_b_group[:, 0] = np.arange(1, 11)
    metrics_strat_b_group[:, 1] = (np.arange(10) < 5).astype(float)
    design = Design(stratification='on')
    ideal_pvalue = 0.037056

    experiments_service = ExperimentsService()
    pvalue = experiments_service.get_pvalue(metrics_strat_a_group, metrics_strat_b_group, design)

    np.testing.assert_almost_equal(ideal_pvalue, pvalue, decimal=4, err_msg='Неверное значение pvalue')
    print('simple test passed')
