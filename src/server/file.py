def append_file(file_name,chunk):
    with open(file_name, 'w', encoding="utf8") as file:
        file.write(chunk)
        file.close()


def file_already_exists(file_name):
    try:
        file = open(file_name, encoding="utf8")
    except FileNotFoundError:
        return False
    else:
        file.close()
        return True

