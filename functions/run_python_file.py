import os
import subprocess
from google.genai import types


def run_python_file(working_directory, file_path, args=[]):
    complete_file_path = os.path.join(working_directory, file_path)
    abs_working_directory = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(complete_file_path)
    if not abs_file_path.startswith(abs_working_directory):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(abs_file_path):
        return f'Error: File "{file_path}" not found.'
    filename, file_extension = os.path.splitext(file_path)
    if file_extension != ".py":
        return f'Error: "{file_path}" is not a Python file.'
    try:
        completed_process = subprocess.run(["python3", 
        abs_file_path] + args, capture_output=True, 
        timeout=30, cwd=abs_working_directory)
        output = ""
        if completed_process.stdout != b"":
            stdout = completed_process.stdout.decode()
            output += f"STDOUT: {stdout}\n"
        if completed_process.stderr != b"":
            stderr = completed_process.stderr.decode()    
            output += f"STDERR: {stderr}\n"
        if completed_process.stderr == b"" and completed_process.stdout == b"":
            output += "No output produced."
        if completed_process.returncode != 0:
            output += f"Process exited with code {completed_process.returncode}"
        return output
    
    
    except Exception as e:
        return f"Error: executing Python file: {str(e)}"

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Excecutes Python files with optional arguments.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the python file.",
            ),
        },
    ),
)