from artifact import Artifact
import numpy as np

types = ["Flower", "Plume", "Sands", "Goblet", "Circlet"]
cost_for_level20 = 270475
cost_for_level4 = 5900
resin_per_domain = 20
exp_per_day = 101957  # https://wikiwiki.jp/genshinwiki/%E7%A8%BC%E3%81%8E#c1dff353
# exp_per_day += 80000  # 聖遺物拾いをやる場合


class Player:

    def __init__(self, desired_main_statuses, desired_sub_status):
        self.free_artifact_scores = np.array([32, 32, 23, 15, 15])
        self.bag = {t: [] for t in types}
        self.desired_main_statuses = desired_main_statuses
        self.desired_sub_status = desired_sub_status
        self.best_set = {t: None for t in types}

    def get_max_scores(self):
        nb_no_artifact_types = sum([i is None for i in self.best_set.values()])
        if nb_no_artifact_types > 1:  # 2箇所以上なかったとき
            return []
        elif nb_no_artifact_types == 1:  # 1箇所足りてなかったとき
            current_best_scores = []
            for i, type in enumerate(types):
                if self.best_set[type] is not None:
                    current_best_scores.append(self.best_set[type].get_score(desired_sub_status))
                else:
                    current_best_scores.append(self.free_artifact_scores[i])
            current_best_scores = np.array(current_best_scores)

        else:  # 全箇所あるときは、一番差分がでかいところを置き換える
            current_best_scores = np.array([a.get_score(desired_sub_status) for a in self.best_set.values()])

            diff = self.free_artifact_scores - current_best_scores
            index = np.argmax(diff)
            current_best_scores[index] = self.free_artifact_scores[index]
        return current_best_scores

    def spend_weeks(self, weeks):
        resin = (180 * 7 - 90 + 60) * weeks  # 自然回復 - 週ボス + 刹那樹脂
        nb_go_domain = resin // resin_per_domain
        self.go_domain(nb_go_domain)
        self.exp = exp_per_day * 7 * weeks

    def go_domain(self, nb_pull):
        artifacts = [Artifact() for _ in range(nb_pull)]
        for artifact in artifacts:
            self.bag[artifact.type].append(artifact)
        self._filter_main_status()

    def levelup_until_exp(self):
        for type in types:
            if self.best_set[type] is None:
                index = self._get_best_artifact_index(type)
                if index is None:
                    continue
                else:
                    temp_artifact = self.bag[type].pop(index)
                    temp_artifact.level_up(20)
                    self.exp -= cost_for_level20
                    self.best_set[type] = temp_artifact
        while self.exp > 0:
            type, index = self._get_next_artifact()
            next_artifact = self.bag[type].pop(index)
            next_artifact.level_up(20)
            self.exp -= cost_for_level20

            next_score = next_artifact.get_score(desired_sub_status)
            if self.best_set[type].get_score(desired_sub_status) < next_score:
                self.best_set[type] = next_artifact

    def _filter_main_status(self):
        for type, artifact_per_type in self.bag.items():
            filtered = []
            for a in artifact_per_type:
                if a.main_status == self.desired_main_statuses[type]:
                    filtered.append(a)
            self.bag[type] = filtered

    def _get_best_artifact_index(self, type):
        artifact_list = self.bag[type]
        scores = [a.get_score(self.desired_sub_status) for a in artifact_list]
        if len(scores) == 0:
            return None
        else:
            return np.argmax(scores)

    def _get_next_artifact(self):
        # 現在育成済みの最も良いやつと、育成前の聖遺物のスコアの差が最小のやつ
        score_diff = {}
        score_diff_index = {}
        for type, artifact_per_type in self.bag.items():
            if len(artifact_per_type) == 0:
                continue
            scores = np.array([a.get_score(self.desired_sub_status) for a in artifact_per_type])
            diff = -scores + self.best_set[type].get_score(self.desired_sub_status)
            score_diff[type] = np.max(diff)  # 次点とのスコアの差
            score_diff_index[type] = np.argmax(diff)
        next_artifact_type = max(score_diff)
        next_artifact_index = score_diff_index[next_artifact_type]

        return next_artifact_type, next_artifact_index


if __name__ == "__main__":
    import pylab as plt
    import seaborn as sns

    desired_main_statuses = {"Flower": "HP", "Plume": "ATK", "Sands": "ATK%", "Goblet": "PYR_DMG", "Circlet": "CR"}
    desired_sub_status = "ATK%"
    nb_travelers = 1000
    for j in range(3, 6):
        all_scores = []
        nb_failed = 0
        for i in range(nb_travelers):
            player = Player(desired_main_statuses, desired_sub_status)
            player.spend_weeks(j)
            player.levelup_until_exp()
            scores = player.get_max_scores()
            if len(scores) == 0:
                nb_failed += 1
            else:
                all_scores.append(scores)
        all_scores = np.array(all_scores)
        # hist, bins = np.histogram(all_scores.sum(axis=1))
        # print(np.cumsum(hist).shape, bins.shape)

        # plt.plot(bins[:-1], np.cumsum(hist))
        all_scores = np.sort(all_scores.sum(axis=1))
        all_scores = [np.nan] * nb_failed + list(all_scores)
        plt.plot(all_scores, label=f"{j} weeks")
        print(j, nb_failed)

    plt.xlabel("# Travelers")
    plt.ylabel("Score")
    plt.legend()

    plt.savefig("hist.png")
