import math
import random


class Artifact:
    # pre-determined stat probabilities obtained from the wiki
    TYPES = ["Flower", "Plume", "Sands", "Goblet", "Circlet"]

    ARTIFACT_MAIN_STATS = {
        "Flower": {"HP": 100},
        "Plume": {"ATK": 100},
        "Sands": {"HP%": 26.68, "ATK%": 26.66, "DEF%": 26.66, "ER": 10, "EM": 10},
        "Goblet": {
            "HP%": 21.25,
            "ATK%": 21.25,
            "DEF%": 20,
            "PYR_DMG": 5,
            "ELE_DMG": 5,
            "CRY_DMG": 5,
            "HYD_DMG": 5,
            "ANE_DMG": 5,
            "GEO_DMG": 5,
            "PHY_DMG": 5,
            "EM": 2.5,
        },
        "Circlet": {"HP%": 22, "ATK%": 22, "DEF%": 22, "CR": 10, "CD": 10, "HB": 10, "EM": 4},
    }

    ARTIFACT_SUB_STATS_ROLL_RANGE = {
        "HP": [209.13, 239, 268.88, 298.75],
        "ATK": [13.62, 15.56, 17.51, 19.45],
        "DEF": [16.20, 18.52, 20.83, 23.15],
        "HP%": [4.08, 4.66, 5.25, 5.83],
        "ATK%": [4.08, 4.66, 5.25, 5.83],
        "DEF%": [5.10, 5.83, 6.56, 7.29],
        "EM": [16.32, 18.65, 20.98, 23.31],
        "ER": [4.53, 5.18, 5.83, 6.48],
        "CR": [2.72, 3.11, 3.50, 3.89],
        "CD": [5.44, 6.22, 6.99, 7.77],
    }

    SUB_STATS_CHANCE = {
        "HP": {
            "HP": 0,
            "ATK": 15.79,
            "DEF": 15.79,
            "HP%": 10.53,
            "ATK%": 10.53,
            "DEF%": 10.53,
            "ER": 10.53,
            "EM": 10.53,
            "CR": 7.89,
            "CD": 7.89,
        },
        "ATK": {
            "HP": 15.79,
            "ATK": 0,
            "DEF": 15.79,
            "HP%": 10.53,
            "ATK%": 10.53,
            "DEF%": 10.53,
            "ER": 10.53,
            "EM": 10.53,
            "CR": 7.89,
            "CD": 7.89,
        },
        "HP%": {
            "HP": 15,
            "ATK": 15,
            "DEF": 15,
            "HP%": 0,
            "ATK%": 10,
            "DEF%": 10,
            "ER": 10,
            "EM": 10,
            "CR": 7.5,
            "CD": 7.5,
        },
        "ATK%": {
            "HP": 15,
            "ATK": 15,
            "DEF": 15,
            "HP%": 10,
            "ATK%": 0,
            "DEF%": 10,
            "ER": 10,
            "EM": 10,
            "CR": 7.5,
            "CD": 7.5,
        },
        "DEF%": {
            "HP": 15,
            "ATK": 15,
            "DEF": 15,
            "HP%": 10,
            "ATK%": 10,
            "DEF%": 0,
            "ER": 10,
            "EM": 10,
            "CR": 7.5,
            "CD": 7.5,
        },
        "ELEM_DMG": {
            "HP": 13.64,
            "ATK": 13.64,
            "DEF": 13.64,
            "HP%": 9.09,
            "ATK%": 9.09,
            "DEF%": 9.09,
            "ER": 9.09,
            "EM": 9.09,
            "CR": 6.82,
            "CD": 6.82,
        },
        "ER": {
            "HP": 15,
            "ATK": 15,
            "DEF": 15,
            "HP%": 10,
            "ATK%": 10,
            "DEF%": 10,
            "ER": 0,
            "EM": 10,
            "CR": 7.5,
            "CD": 7.5,
        },
        "CR": {
            "HP": 14.63,
            "ATK": 14.63,
            "DEF": 14.63,
            "HP%": 9.76,
            "ATK%": 9.76,
            "DEF%": 9.76,
            "ER": 9.76,
            "EM": 9.76,
            "CR": 0,
            "CD": 7.32,
        },
        "CD": {
            "HP": 14.63,
            "ATK": 14.63,
            "DEF": 14.63,
            "HP%": 9.76,
            "ATK%": 9.76,
            "DEF%": 9.76,
            "ER": 9.76,
            "EM": 9.76,
            "CR": 7.32,
            "CD": 0,
        },
        "EM": {
            "HP": 15,
            "ATK": 15,
            "DEF": 15,
            "HP%": 10,
            "ATK%": 10,
            "DEF%": 10,
            "ER": 10,
            "EM": 0,
            "CR": 7.5,
            "CD": 7.5,
        },
        "HB": {
            "HP": 13.64,
            "ATK": 13.64,
            "DEF": 13.64,
            "HP%": 9.09,
            "ATK%": 9.09,
            "DEF%": 9.09,
            "ER": 9.09,
            "EM": 9.09,
            "CR": 6.82,
            "CD": 6.82,
        },
    }

    # generate random stats when artifact is created
    def __init__(self):

        self.max_level = 20  # max level the artifact can be upgraded to

        self.level = 0
        self.set = random.randint(0, 1)
        self.type = self.TYPES[random.randint(0, len(self.TYPES) - 1)]
        self.main_status = random.choices(
            list(self.ARTIFACT_MAIN_STATS[self.type]), weights=tuple(self.ARTIFACT_MAIN_STATS[self.type].values())
        )[0]

        # generate sub stats
        self.sub_status = {}

        for _ in range(4 if random.randint(1, 5) == 1 else 3):  # generate 4 or 3 substats
            self.generate_subset()

    # when object is printed print the artifact stats
    def __str__(self):
        return (
            f"[level:{self.level}]-[set:{self.set}]-[type:{self.type}]-[main_status:{self.main_status}]-[SS1: ({round(list(self.sub_status.items())[0][1],1)} {list(self.sub_status.items())[0][0]})]-[SS2: ({round(list(self.sub_status.items())[1][1],1)} {list(self.sub_status.items())[1][0]})]-[SS3: ({round(list(self.sub_status.items())[2][1],1)} {list(self.sub_status.items())[2][0]})]"
            + (
                f"-[SS4: ({round(list(self.sub_status.items())[3][1],1)} {list(self.sub_status.items())[3][0]})]"
                if len(self.sub_status) == 4
                else ""
            )
        )

    # function that adds 1 substat to the artifact
    def generate_subset(self):
        stat_generated = False
        while not stat_generated:  # generate until substat is not a repeated one
            generated_stat = random.choices(
                list(self.SUB_STATS_CHANCE["ELEM_DMG" if self.main_status[-3:] == "DMG" else self.main_status]),
                weights=tuple(
                    self.SUB_STATS_CHANCE["ELEM_DMG" if self.main_status[-3:] == "DMG" else self.main_status].values()
                ),
            )[0]

            if generated_stat not in self.sub_status:  # if not duplicate

                self.sub_status[generated_stat] = self.ARTIFACT_SUB_STATS_ROLL_RANGE[generated_stat][
                    random.randint(0, len(self.ARTIFACT_SUB_STATS_ROLL_RANGE[generated_stat]) - 1)
                ]
                stat_generated = True

    # function to level up artifact by n levels
    def level_up(self, levels):
        original_level = self.level  # store current level, before level up
        self.level = min(self.level + levels, self.max_level)  # add levels to arifact but cap at max possible level
        times_to_upgrade = math.floor(self.level / 4) - math.floor(
            original_level / 4
        )  # calculate how many times it will have substat upgrades
        for upgrade in range(times_to_upgrade):  # loop amount of stat level ups
            if len(self.sub_status) == 3:  # if level up and 3 stats add one
                self.generate_subset()
            else:  # else level up stat
                sub_stat_to_upgrade = list(self.sub_status)[random.randint(0, 3)]
                self.sub_status[sub_stat_to_upgrade] += self.ARTIFACT_SUB_STATS_ROLL_RANGE[sub_stat_to_upgrade][
                    random.randint(0, len(self.ARTIFACT_SUB_STATS_ROLL_RANGE[sub_stat_to_upgrade]) - 1)
                ]

    def get_score(self, status_name):
        score = 0
        if "CR" in self.sub_status:
            score += self.sub_status["CR"] * 2
        if "CD" in self.sub_status:
            score += self.sub_status["CD"]

        if status_name in self.sub_status:
            if status_name == "EM":
                score += self.sub_status["EM"] / 4
            else:
                score += self.sub_status[status_name]

        return score
