import json

# Open Schemas and get keys
def get_schema_keys(schema_fn):
    with open(schema_fn, "r") as f:
        schema = json.load(f)
        # get keys
        key_order = list(schema['properties'].keys())
    return key_order