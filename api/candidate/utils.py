def convert_objectid_to_str(document):
    document["_id"] = str(document["_id"])
    return document
