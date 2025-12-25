import uuid
import hashlib


url = "http://www.youtube.com/watch?v=4KdvcQKNfbQ"
hashed = hashlib.sha256(url.encode()).hexdigest()

print(f"{url} -> {hashed}")
print(f"{url} -> {uuid.uuid5(uuid.NAMESPACE_DNS, url)}")
