import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import sys
from functions.get_files_info import schema_get_files_info
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file
from functions.get_file_content import schema_get_files_content

from functions.get_files_info import get_files_info
from functions.run_python_file import run_python_file
from functions.write_file import write_file
from functions.get_file_content import get_file_content

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question about the codebase, **your very first action should always be to call the `get_files_info` function to understand the project structure.** Then, based on the file information, proceed to call `get_file_content` on relevant files to read their content and gather necessary information.

You can perform the following operations:
- List files and directories
- Read file contents using get_file_content
- Write files using write_files
- Execute Python files using run_python_file

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

functions = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file
}
def main():
    print("Starting main function")

    available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_run_python_file,
        schema_write_file,
        schema_get_files_content
    ]
)
    
    print("Starting main function")

    if len(sys.argv) < 2:
        exit(1)
    user_prompt = sys.argv[1]

    print(f"User prompt: {user_prompt}")

    messages = [
        types.Content(
        role="user", parts=[
        types.Part(text=user_prompt)]),
    ]
    
    verbose = len(sys.argv) > 2 and sys.argv[2] == "--verbose"

    load_dotenv()

    api_key = os.environ.get("GEMINI_API_KEY")

    print(f"API key loaded: {api_key is not None}")
    
    client = genai.Client(api_key=api_key)
    
    print("Client created")
    try:
        i = 20
        while i > 0:
            response = client.models.generate_content(
                model="gemini-2.0-flash-001", 
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions], 
                    system_instruction=system_prompt
                )
            )
            found_final = False
            if not response.function_calls or len(response.function_calls) == 0:
                for c in response.candidates:
                    for p in c.content.parts:
                        if getattr(p, "text", None):
                            print("Final response:")
                            print(p.text)
                            found_final = True
                            break
                    if found_final:
                        break
                if found_final:
                    break

            print("Response received")
            print(f"Response: {response}")

            print(f"DEBUG Response text: {response.text!r}")
            print(f"DEBUG Response candidates: {response.candidates}")
            print(f"DEBUG Response function_calls: {response.function_calls}")
    
            for c in response.candidates:
                messages.append(c.content)
            
    
            if response.function_calls and len(response.function_calls) > 0:
                function_call_part = response.function_calls[0]
                function_call_result = call_function(
                    function_call_part, verbose=verbose)
                print(f"Response: {response}")
                print(f"Function calls: {response.function_calls}")
                print(f"Response text: {response.text}")

                messages.append(function_call_result)
                if not function_call_result.parts[0].function_response.response:
                    raise Exception("Function call failed - no response")

                if verbose:
                   print(f"-> {function_call_result.parts[0].function_response.response}")
            i -= 1
    except Exception as e:
            print(f"Error calling API: {e}")
            return
    if len(sys.argv) > 2 and sys.argv[2] == "--verbose":
        print(f"User prompt: {sys.argv[1]}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

def call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")
    function_name = function_call_part.name

    if function_name not in functions:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],

        )

    function_to_call = functions[function_name]

    args = dict(function_call_part.args)
    args["working_directory"] = "./calculator"

    function_result = function_to_call(**args)

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ]
    )


if __name__ == "__main__":
    main()
