import os
def test_release_facts_exists(): assert os.path.exists(os.path.join(os.path.dirname(__file__),"..","docs","RELEASE_FACTS.json"))
def test_release_facts_version(): import json; path=os.path.join(os.path.dirname(__file__),"..","docs","RELEASE_FACTS.json"); f=json.load(open(path)); assert f["version"]=="1.8.0"
def test_release_facts_doctrine(): import json; path=os.path.join(os.path.dirname(__file__),"..","docs","RELEASE_FACTS.json"); f=json.load(open(path)); assert "LLM" in f["doctrine"]
