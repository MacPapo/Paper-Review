def truncate_string(text, length=200):
    if len(text) > length:
        return text[:length] + '...'
    else:
        return text
