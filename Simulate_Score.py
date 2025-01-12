from ArtifactClass import Artifact

artifacts = []
for i in range(5):
    my_artifact = Artifact()
    my_artifact.level_up(20)
    artifacts.append(my_artifact)

print(sum([a.get_score("ATK%") for a in artifacts]))
