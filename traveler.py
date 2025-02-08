import numpy as np
from artifact import Artifact, TYPES

COST_LEVEL_20 = 270475
COST_LEVEL_4 = 5900
RESIN_PER_DOMAIN = 20
EXP_PER_DAY = 101957  # https://wikiwiki.jp/genshinwiki/%E7%A8%BC%E3%81%8E#c1dff353
PROB_DROP_TWO_ARTIFACT = 0.06


class Traveler:
    def __init__(self, desired_main_statuses, desired_sub_status):
        self.resin = 0
        self.bag = {artifact_type: [] for artifact_type in TYPES}
        self.best_set = {artifact_type: None for artifact_type in TYPES}
        self.desired_main_statuses = desired_main_statuses
        self.desired_sub_status = desired_sub_status

    def __str__(self):
        result = []
        for artifact_type in TYPES:
            result.append(artifact_type)
            for artifact in self.bag[artifact_type]:
                score = artifact.get_score(self.desired_sub_status)
                result.append(f"lv.{artifact.level}: {score}")
        return "\n".join(result)

    def go_domain(self, nb_pull):
        additional_pull = sum(
            [np.random.choice([0, 1], p=[1 - PROB_DROP_TWO_ARTIFACT, PROB_DROP_TWO_ARTIFACT]) for _ in range(nb_pull)]
        )
        artifacts = [Artifact() for _ in range(nb_pull + additional_pull)]
        for artifact in artifacts:
            # Filter by artifact type (assumes index 1 is undesired type)
            if np.random.randint(2) == 1:
                continue
            self.bag[artifact.type].append(artifact)
        self._filter_main_status()

    def _filter_main_status(self):
        for artifact_type, artifacts in self.bag.items():
            self.bag[artifact_type] = [
                a for a in artifacts if a.main_status == self.desired_main_statuses[artifact_type]
            ]

    def spend_weeks(self, weeks):
        weekly_resin = (180 * 7 - 90 + 60) * weeks  # Natural resin recovery - Weekly boss cost + Transient Resin
        self.resin += weekly_resin
        nb_go_domain = self.resin // RESIN_PER_DOMAIN
        self.resin -= nb_go_domain * RESIN_PER_DOMAIN

        self.go_domain(nb_go_domain)
        self.exp = EXP_PER_DAY * 7 * weeks

    def get_artifact_score(self, x):
        return x.get_score(self.desired_sub_status)

    def levelup_4(self, percentage):
        for artifact_type in TYPES:
            artifacts = self.bag[artifact_type]

            temp_artifacts = sorted(artifacts, key=self.get_artifact_score, reverse=True)
            self.bag[artifact_type] = temp_artifacts

            if len(temp_artifacts) < 3:
                nb_levelup = len(temp_artifacts)
                # 2つ以下なら全部4まで強化する
            else:
                nb_levelup = int(np.ceil(len(temp_artifacts) * percentage / 100))

            for a in temp_artifacts[:nb_levelup]:
                a.level_up(4)
                self.exp -= COST_LEVEL_4

    def _get_max_diff_artifact(self):
        diffs = {artifact_type: 1000 for artifact_type in TYPES}
        max_diff_artifacts = {artifact_type: None for artifact_type in TYPES}

        for artifact_type in TYPES:
            artifacts = self.bag[artifact_type]
            if len(artifacts) < 1:
                continue
            temp_artifacts = sorted(artifacts, key=self.get_artifact_score, reverse=True)
            best_score = self.get_artifact_score(temp_artifacts[0])
            for a in temp_artifacts[1:]:
                if a.level < 20:
                    next_score = self.get_artifact_score(a)
                    max_diff_artifacts[artifact_type] = a
                    diffs[artifact_type] = best_score - next_score
                    break

        artifact_type = min(diffs, key=diffs.get)
        if max_diff_artifacts[artifact_type] is None:
            print(max_diff_artifacts)

        return max_diff_artifacts[artifact_type]

    def levelup_until_exp(self):
        # 1個目の聖遺物のレベルあげ
        for artifact_type in TYPES:
            artifacts = self.bag[artifact_type]
            if len(artifacts) > 0:
                temp_artifacts = sorted(artifacts, key=self.get_artifact_score, reverse=True)
                artifact = temp_artifacts[0]
                if artifact.level == 4:
                    artifact.level_up(16)
                    self.exp -= COST_LEVEL_20 - COST_LEVEL_4
                elif artifact.level == 0:
                    artifact.level_up(20)
                    self.exp -= COST_LEVEL_20

        # 2個目以降は伸びしろがありそうなやつを選んでレベルを上げる
        while True:
            artifact = self._get_max_diff_artifact()
            if artifact.level == 4:
                self.exp -= COST_LEVEL_20 - COST_LEVEL_4
                if self.exp < 0:
                    break
                artifact.level_up(16)
            elif artifact.level == 0:
                self.exp -= COST_LEVEL_20
                if self.exp < 0:
                    break
                artifact.level_up(20)

    def get_scores(self, free_artifacts):
        scores = {artifact_type: -1 for artifact_type in TYPES}
        for artifact_type in TYPES:
            artifacts = self.bag[artifact_type]
            if len(artifacts) > 0:
                temp_artifacts = sorted(artifacts, key=self.get_artifact_score, reverse=True)
            best_artifact = temp_artifacts[0]
            scores[artifact_type] = self.get_artifact_score(best_artifact)

        miss_type = []
        for artifact_type in TYPES:
            if scores[artifact_type] < 0:
                miss_type.append(artifact_type)
        if len(miss_type) > 1:
            # 2箇所以上足りないので厳選失敗
            return None
        elif len(miss_type) == 1:
            scores[miss_type[0]] = free_artifacts[miss_type[0]]
        else:
            diff = np.array(list(free_artifacts.values())) - np.array(list(scores.values()))
            free_type = np.argmax(diff)
            if diff[free_type] < 0:
                return np.sum(list(scores.values())), scores  # フリー枠よりも厳選したやつのほうがスコアが良い
            else:
                scores[free_type] = free_artifacts[free_type]

        return np.sum(list(scores.values())), scores


if __name__ == "__main__":
    desired_main_statuses = {"Flower": "HP", "Plume": "ATK", "Sands": "ATK%", "Goblet": "PYR_DMG", "Circlet": "CR"}
    desired_sub_status = "ATK%"

    free_artifacts = {artifact_type: 0 for artifact_type in TYPES}

    traveler = Traveler(desired_main_statuses, desired_sub_status)
    traveler.spend_weeks(8)
    traveler.levelup_4(50)
    traveler.levelup_until_exp()
    score, scores = traveler.get_scores(free_artifacts)
    print(score)
