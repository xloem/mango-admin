from os.path import join
import json

with open(join(__path__[0], 'MangoRepoABI.json')) as repoABIjson:
    repoABI = json.load(repoABIjson)

with open(join(__path__[0], 'MangoRepo.bin')) as repoABIbin:
    repoCode = repoABIbin.read()
