query = " This is the most important property of exclusive or operation also known as zor. If you apply the same value twice, you get the original value. And to demonstrate that this is actually true, we can bust out Python and take all of the possible combinations of two beats."
# query = "video_id: 4KdvcQKNfbQ title: Programming Party Tricks author: Tsoding"

# from langchain_community.tools import DuckDuckGoSearchRun

# search = DuckDuckGoSearchRun()


# result1 = search.invoke(query, max_results=5)
# print("### result1")
# print(result1)


import json
from ddgs import DDGS

results = DDGS().text(query, max_results=5)
parsed = json.dumps(results, indent=2)

print("### parsed")
print(parsed)
print(f"{len(results) = }")
