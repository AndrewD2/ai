import os
from google.genai import types


MAX_CHARS = 10000

def get_file_content(working_directory, file_path):
    complete_file_path = os.path.join(working_directory, file_path)
    abs_working_directory = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(complete_file_path)
    if not abs_file_path.startswith(abs_working_directory):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(abs_file_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    try:
        with open(abs_file_path, "r") as f:
            file_content_string = f.read(MAX_CHARS)
            if os.path.getsize(abs_file_path) >= MAX_CHARS:
                return file_content_string + f'\n[...File "{file_path}" truncated at {MAX_CHARS} characters]'
            return file_content_string
    except Exception as e:
        return f"Error: {str(e)}"

schema_get_files_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Read the content of a file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to have contents read.",
            ),
        },
    ),
)