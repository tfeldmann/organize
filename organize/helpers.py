def flatten(arr):
    if arr == []:
        return []
    if not isinstance(arr, list):
        return [arr]
    return flatten(arr[0]) + flatten(arr[1:])


def first_key(d):
    return list(d.keys())[0]
