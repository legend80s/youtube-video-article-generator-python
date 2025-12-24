query = "video_id: 4KdvcQKNfbQ title: Programming Party Tricks author: Tsoding"

# from langchain_community.tools import DuckDuckGoSearchRun

# search = DuckDuckGoSearchRun()


# result1 = search.invoke(query, max_results=5)
# print("### result1")
# print(result1)


import json
from ddgs import DDGS

results = DDGS().images(query, max_results=10)
parsed = json.dumps(results, indent=2)

print("### parsed")
print(parsed)
