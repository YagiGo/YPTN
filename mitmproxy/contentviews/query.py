from . import base


class ViewQuery(base.View):
    name = "Query"
    prompt = ("query", "q")

    def __call__(self, data, **metadata):
        query = metadata.get("query")
        if query:
            return "Query", base.format_dict(query)
        else:
            return "Query", base.format_text("")
