import pandas as pd
import numpy as np


def get_strats(df: pd.DataFrame):
    """Возвращает страты объектов.
    
    :return (list | np.array | pd.Series): список страт объектов размера len(df).
    """
    # YOUR_CODE_HERE
    for i in df.index:
        if df['x4'][i] == 0 and df['x8'][i] == 0:
            df.loc[i, 'strat'] = 1
        elif df['x4'][i] == 0 and df['x8'][i] == 1:
            df.loc[i, 'strat'] = 2
        elif df['x4'][i] == 1 and df['x8'][i] == 0:
            df.loc[i, 'strat'] = 3
        elif df['x4'][i] == 1 and df['x8'][i] == 1:
            df.loc[i, 'strat'] = 4
        elif df['x4'][i] == 2 and df['x8'][i] == 0:
            df.loc[i, 'strat'] = 5
        elif df['x4'][i] == 2 and df['x8'][i] == 1:
            df.loc[i, 'strat'] = 6

        return df['strat']


def calculate_strat_var(df):
    """Вычисляет стратифицированную дисперсию популяции."""
    strat_vars = df.groupby('strat')['y'].var()
    weights = df['strat'].value_counts(normalize=True)
    stratified_var = (strat_vars * weights).sum()
    return stratified_var


if __name__ == "__main__":
    bound = 50000
    df = pd.read_csv('data/stratification_task_data_public.csv')
    strats = get_strats(df.drop('y', axis=1))
    assert len(strats) == len(df), "Неверный размер списка страт"
    min_part = pd.Series(strats).value_counts(normalize=True).min()
    assert min_part >= 0.05, "Минимальная доля одной из страт меньше 5%"
    df['strat'] = strats
    strat_var = calculate_strat_var(df)
    err_msg = f"Дисперсия равна {strat_var:0.1f}, её нужно снизить до {bound}"
    assert strat_var <= bound, err_msg
    print(f'Отлично! Дисперсия равна {strat_var:0.1f}, меньше порога {bound}')