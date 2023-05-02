from langchain.utilities import PythonREPL
python_repl = PythonREPL()
code_string = """
def delete_files_with_extension(file_string, extension):
    file_list = file_string.split()
    delete_list = []
    for file_name in file_list:
        if extension == "":
            if "." not in file_name:
                delete_list.append(file_name)
        elif file_name.endswith(extension):
            delete_list.append(file_name)
    if delete_list:
        return "rm " + " ".join(delete_list)
    else:
        return "No files with extension " + extension + " found."

"""
gpt_output = """
file_string = "delete.html flowers.jpg flowers.tar.gz mario.json"
extension = ""
delete_command = delete_files_with_extension(file_string, extension)
print(delete_command)
"""
print(python_repl.run(code_string + gpt_output))
