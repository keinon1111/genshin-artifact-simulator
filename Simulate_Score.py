import pylab as plt
from tqdm import tqdm
from ArtifactClass import Artifact


def check_artifact(artifact, policy, desired_main_status, desired_sub_status="ATK%"):
    if artifact.main_status != desired_main_status[artifact.type]:
        return False

    nb_desired_status = 0
    if artifact.main_status in ["CR", "CD"]:
        nb_desired_status += 1
    if "CR" in artifact.sub_status:
        nb_desired_status += 1
    if "CD" in artifact.sub_status:
        nb_desired_status += 1
    if desired_sub_status in artifact.sub_status:
        nb_desired_status += 1

    if nb_desired_status >= policy:
        return True
    else:
        return False


def go_domain(nb_pull):
    temp_artifacts = [Artifact() for _ in range(nb_pull)]
    exp = None  # TODO
    return temp_artifacts, exp


def main(max_days):
    go_domain_per_day = 9  # 180/20
    artifacts = {"Flower": [], "Plume": [], "Sands": [], "Goblet": [], "Circlet": []}
    for day_i in range(max_days):
        todays_artifacts, exp = go_domain(go_domain_per_day)
        for a in todays_artifacts:
            if check_artifact(a, 1, desired_main_status, desired_sub_status):
                a.level_up(20)
                artifacts[a.type].append(a)
    return artifacts


if __name__ == "__main__":
    import matplotlib.font_manager as fm

    font_path = "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"  # 例: Ubuntuのパス
    font_prop = fm.FontProperties(fname=font_path)
    # from matplotlib import rcParams

    # rcParams['font.family'] = 'IPAexGothic'  # 例: IPAexGothicの場合

    desired_main_status = {"Flower": "HP", "Plume": "ATK", "Sands": "ATK%", "Goblet": "PYR_DMG", "Circlet": "CR"}
    desired_sub_status = "ATK%"

    all_scores = []
    for i in tqdm(range(1000)):
        artifacts = main(30)
        max_scores = []
        for type, temp_artifacts in artifacts.items():
            scores = [a.get_score(desired_sub_status) for a in temp_artifacts]
            if len(scores) == 0:
                max_scores.append(0)  # TODO 1個もでなかったときはどうする?
            else:
                max_score = max(scores)
            max_scores.append(max_score)
        all_scores.append(sum(max_scores))
    print(all_scores)
    plt.hist(all_scores)
    plt.xlabel("スコア", fontproperties=font_prop)
    plt.ylabel("人数", fontproperties=font_prop)
    plt.savefig("hist.png")
    plt.show()
