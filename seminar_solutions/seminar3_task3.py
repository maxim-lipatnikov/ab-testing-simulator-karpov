import numpy as np
import pandas as pd
from pydantic import BaseModel
from scipy import stats


class Design(BaseModel):
    """Дата-класс с описание параметров эксперимента.
    
    statistical_test - тип статтеста. ['ttest']
    effect - размер эффекта в процентах
    alpha - уровень значимости
    beta - допустимая вероятность ошибки II рода
    """
    statistical_test: str
    effect: float
    alpha: float
    beta: float


class ExperimentsService:

    def estimate_sample_size(self, metrics, design):
        """Оцениваем необходимый размер выборки для проверки гипотезы о равенстве средних.
        
        Для метрик, у которых для одного пользователя одно значение просто вычислите размер групп по формуле.
        Для метрик, у которых для одного пользователя несколько значений (например, response_time),
            вычислите необходимый объём данных и разделите его на среднее количество значений на одного пользователя.
            Пример, если в таблице metrics 1000 наблюдений и 100 уникальных пользователей, и для эксперимента нужно
            302 наблюдения, то размер групп будет 31, тк в среднем на одного пользователя 10 наблюдений, то получится
            порядка 310 наблюдений в группе.

        :param metrics (pd.DataFrame): датафрейм со значениями метрик из MetricsService.
            columns=['user_id', 'metric']
        :param design (Design): объект с данными, описывающий параметры эксперимента
        :return (int): минимально необходимый размер групп (количество пользователей)
        """
        # YOUR_CODE_HERE
        alpha = design.alpha
        beta = design.beta
        effect = design.effect
        mean = np.mean(metrics.metric)
        std = np.std(metrics.metric)
        
        def get_sample_size_abs(epsilon, std, alpha, beta):
            t_alpha = stats.norm.ppf(1 - alpha / 2, loc=0, scale=1)
            t_beta = stats.norm.ppf(1 - beta, loc=0, scale=1)
            z_scores_sum_squared = (t_alpha + t_beta) ** 2
            sample_size = int(
                np.ceil(
                    z_scores_sum_squared * (2 * std ** 2) / (epsilon ** 2)
                )
            )
            return sample_size 
        
        def get_sample_size_arb(mu, std, eff, alpha, beta):
            epsilon = (eff - 1) * mu

            return get_sample_size_abs(epsilon, std=std, alpha=alpha, beta=beta)
                
        if metrics['user_id'].nunique() < metrics['user_id'].count():
            ratio = metrics.groupby('user_id')['metric'].count().mean()
            # ratio = metrics.shape[0] / metrics['user_id'].nunique()
            sample_size = int(get_sample_size_arb(mean, std, (effect / 100) + 1, alpha, beta) / ratio) + 1
        else:
            sample_size = get_sample_size_arb(mean, std, (effect / 100) + 1, alpha, beta)
        
        return sample_size
            

if __name__ == '__main__':
    metrics = pd.DataFrame({
        'user_id': [str(i) for i in range(10)],
        'metric': [i for i in range(10)]
    })
    design = Design(
        statistical_test='ttest',
        alpha=0.05,
        beta=0.1,
        effect=3.
    )
    ideal_sample_size = 9513

    experiments_service = ExperimentsService()
    sample_size = experiments_service.estimate_sample_size(metrics, design)
    assert sample_size == ideal_sample_size, 'Неверно'
    print('simple test passed')