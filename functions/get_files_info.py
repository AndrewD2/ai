import os
from google.genai import types


def get_files_info(working_directory, directory="."):
    full_path = os.path.join(working_directory, directory)

    abs_working_directory = os.path.abspath(working_directory)
    abs_full_path = os.path.abspath(full_path)

    if abs_full_path.startswith(abs_working_directory):
        if not os.path.isdir(abs_full_path):
            return f'Error: "{directory}" is not a directory'
        try:
            entries = os.listdir(abs_full_path)
            output_list = []
       
            for entry in entries:
                entry_path = os.path.join(abs_full_path, entry)
                file_size = os.path.getsize(entry_path)
                is_dir = os.path.isdir(entry_path)
                output_list.append(f"- {entry}: file_size={file_size} bytes, is_dir={is_dir}")
            output = "\n".join(output_list)
            return output
        except Exception as e:
            return f"Error: {str(e)}"
    else:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)