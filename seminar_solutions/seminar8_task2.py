import numpy as np
import pandas as pd


def split_stratified(strats: np.array) -> np.array:
    """Распределяет объекты по группам (контрольная и экспериментальная).
    
    :param strats: массив с разбиением на страты.
    :return: массив из 0 и 1, 0 - контрольная группа, 1 - экспериментальная.
    """
    # YOUR_CODE_HERE
    strats = pd.DataFrame(strats, columns=['strat'])
    a_indexes = []
    b_indexes = []
    indexes = {}

    for strat in strats['strat'].unique():
        indexes[strat] = strats.index[strats['strat'] == strat].tolist()
    
    strats['split'] = 0
    
    for strat in indexes:
        a, b = np.random.choice(indexes[strat], (2, len(indexes[strat])//2), replace=False).tolist()
        a_indexes.append(a)
        b_indexes.append(b)

    strats.loc[[item for sublist in a_indexes for item in sublist], 'split'] = 1
    strats.loc[[item for sublist in b_indexes for item in sublist], 'split'] = 0
    
    return strats['split']


def check_split(df: pd.DataFrame):
    """Проверяет корректность разбиения на страты.
    
    :param df: датафрейм с двумя столбцами: ['strat', 'group'].
    """
    df_agg = (
        df
        .groupby(['strat', 'group'])[['group']].count()
        .rename(columns={'group': 'count'})
        .reset_index()
    )
    df_pivot = df_agg.pivot(index='strat', values='count', columns='group')
    max_delta = (df_pivot[0] - df_pivot[1]).abs().max()
    assert max_delta <= 1, "Размеры страт между группами отличаются более чем на 1."


if __name__ == "__main__":
    df = pd.DataFrame({'strat': [1, 2, 2, 2, 1, 1, 1, 3, 3]})
    df['group'] = split_stratified(df['strat'].values)
    check_split(df)
    print('simple test passed')