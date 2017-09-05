def append(field, n):
    def transform(element):
        element[field].append(n)

    return transform


def append_unique(field, n):
    def transform(element):

        if n not in element[field]:
            element[field].append(n)

    return transform

