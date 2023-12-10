# Task 1

# Реализуйте метод для распределения экспериментов по бакетам.
# Реализуйте метод add_experiment класса SplittingService.

from pydantic import BaseModel


class Experiment(BaseModel):
    """
    id - идентификатор эксперимента.
    buckets_count - необходимое количество бакетов.
    conflicts - список идентификаторов экспериментов, которые нельзя проводить
        одновременно на одних и тех же пользователях.
    """
    id: int
    buckets_count: int
    conflicts: list[int] = []


class SplittingService:

    def __init__(self, buckets_count):
        """Класс для распределения экспериментов и пользователей по бакетам.

        :param buckets_count (int): количество бакетов.
        """
        self.buckets_count = buckets_count
        self.buckets = [[] for _ in range(buckets_count)]

    def add_experiment(self, experiment):
        """Проверяет можно ли добавить эксперимент, добавляет если можно.

        :param experiment (Experiment): параметры эксперимента, который нужно запустить
        :return success, buckets:
            success (boolean) - можно ли добавить эксперимент, True - можно, иначе - False
            buckets (list[list[int]]]) - список бакетов, в каждом бакете перечислены идентификаторы экспериментов,
                которые в нём проводятся.
        """
        # YOUR_CODE_HERE
        ok_buckets = []

        for b_id in range(len(self.buckets)):
            conflicts_in_bucket = [conflict for conflict in experiment.conflicts if conflict in self.buckets[b_id]]
            if not conflicts_in_bucket:
                ok_buckets.append(b_id)

        if len(ok_buckets) < experiment.buckets_count or len(ok_buckets) == 0:
            return False, self.buckets
        else:
            for b_id in ok_buckets[:experiment.buckets_count]:
                self.buckets[b_id].append(experiment.id)

            return True, self.buckets


def check_correct_buckets(buckets, experiments):
    for experiment in experiments:
        buckets_with_exp = [b for b in buckets if experiment.id in b]
        assert experiment.buckets_count == len(buckets_with_exp), 'Неверное количество бакетов с экспериментом'
        parallel_experiments = set(sum(buckets_with_exp, []))
        err_msg = 'Несовместные эксперименты в одном бакете'
        assert len(set(experiment.conflicts) & parallel_experiments) == 0, err_msg


if __name__ == '__main__':
    experiments = [
        Experiment(id=1, buckets_count=4, conflicts=[4]),
        Experiment(id=2, buckets_count=2, conflicts=[3]),
        Experiment(id=3, buckets_count=2, conflicts=[2]),
        Experiment(id=4, buckets_count=1, conflicts=[1]),
    ]
    ideal_answers = [True, True, True, False]

    splitting_service = SplittingService(buckets_count=4)
    added_experiments = []
    for index, (experiment, ideal_answer) in enumerate(zip(experiments, ideal_answers)):
        success, buckets = splitting_service.add_experiment(experiment)
        assert success == ideal_answer, 'Сплит-система работает неоптимально или некорректно.'
        if success:
            added_experiments.append(experiment)
        check_correct_buckets(buckets, added_experiments)
    print('simple test passed')
