from pydantic import BaseModel
from hashlib import md5


class Experiment(BaseModel):
    """
    id - идентификатор эксперимента.
    salt - соль эксперимента (для случайного распределения пользователей на контрольную/пилотную группы)
    """
    id: int
    salt: str


class SplittingService:

    def __init__(self, buckets_count, bucket_salt, buckets=None, id2experiment=None):
        """Класс для распределения экспериментов и пользователей по бакетам.

        :param buckets_count (int): количество бакетов.
        :param bucket_salt (str): соль для разбиения пользователей по бакетам.
            При одной соли каждый пользователь должен всегда попадать в один и тот же бакет.
            Если изменить соль, то распределение людей по бакетам должно измениться.
        :param buckets (list[list[int]]) - список бакетов, в каждом бакете перечислены идентификаторы
            эксперименты, которые в нём проводятся.
        :param id2experiment (dict[int, Experiment]) - словарь пар: идентификатор эксперимента - эксперимент.
        """
        self.buckets_count = buckets_count
        self.bucket_salt = bucket_salt
        if buckets:
            self.buckets = buckets
        else:
            self.buckets = [[] for _ in range(buckets_count)]
        if id2experiment:
            self.id2experiment = id2experiment
        else:
            self.id2experiment = {}


    def get_bucket(self, value: str, n: int, salt: str=''):
        """Определяет бакет по id.

        value - уникальный идентификатор объекта.
        n - количество бакетов.
        salt - соль для перемешивания.
        """
        hash_value = int(md5((value + salt).encode()).hexdigest(), 16)
        return hash_value % n
    

    def process_user(self, user_id):
        """Определяет в какие эксперименты попадает пользователь.

        Сначала нужно определить бакет пользователя.
        Затем для каждого эксперимента в этом бакете выбрать пилотную или контрольную группу.

        :param user_id (str): идентификатор пользователя
        :return bucket_id, experiment_groups:
            - bucket_id (int) - номер бакета (индекс элемента в self.buckets)
            - experiment_groups (list[tuple]) - список пар: id эксперимента, группа.
                Группы: 'A', 'B'.
            Пример: (8, [(194, 'A'), (73, 'B')])
        """
        # YOUR_CODE_HERE
        bucket_id = self.get_bucket(user_id, self.buckets_count, self.bucket_salt)
        
        experiment_groups_num = []
        for exp_id in self.buckets[bucket_id]:
            experiment_groups_num.append((self.id2experiment[exp_id].id, self.get_bucket(user_id, 2, self.id2experiment[exp_id].salt)))
            
        mapping = {0: 'A', 1: 'B'}

        experiment_groups = [(x[0], mapping[x[1]]) for x in experiment_groups_num]
        
        return (bucket_id, experiment_groups)

if __name__ == '__main__':
    id2experiment = {
        0: Experiment(id=0, salt='0'),
        1: Experiment(id=1, salt='1')
    }
    buckets = [[0, 1], [1], [], []]
    buckets_count = len(buckets)
    bucket_salt = 'a2N4'

    splitting_service = SplittingService(buckets_count, bucket_salt, buckets, id2experiment)
    user_ids = [str(x) for x in range(1000)]
    for user_id in user_ids:
        bucket_id, experiment_groups = splitting_service.process_user(user_id)
        assert bucket_id in [0, 1, 2, 3], 'Неверный bucket_id'
        assert len(experiment_groups) == len(buckets[bucket_id]), 'Неверное количество экспериментов в бакете'
        for exp_id, group in experiment_groups:
            assert exp_id in id2experiment, 'Неверный experiment_id'
            assert group in ['A', 'B'], 'Неверная group'
    print('simple test passed')
