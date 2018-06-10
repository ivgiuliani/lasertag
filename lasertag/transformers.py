class BaseTransformer(object):
    def transform(self, tags, value, *args, **kwargs):
        return tags, value
