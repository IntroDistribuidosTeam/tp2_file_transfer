def append_file(file_name,chunk):
    with open(file_name, 'w', encoding="utf8") as file:
        file.write(chunk)
        file.close()




