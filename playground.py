import json

from fastapi.encoders import jsonable_encoder

b: bytes = b"hello bytes"

print(jsonable_encoder({"input": b}))
print(json.dumps({"input": "hello str"}))
print(json.dumps({"input": f"hello {b}"}))
print(json.dumps({"input": f"hello {str(b)}"}))
print(json.dumps({"input": b}))
