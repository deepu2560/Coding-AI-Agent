import os

def get_file_content(working_directory: str, file_path: str) -> str:
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_file_path = os.path.normpath(os.path.join(working_dir_abs, file_path))
        valid_file_path = os.path.commonpath([working_dir_abs, target_file_path]) == working_dir_abs

        if not valid_file_path:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(target_file_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        MAX_CHAR_READ_LIMIT = 10000

        with open(target_file_path) as f:
            file_content = f.read(MAX_CHAR_READ_LIMIT)
            if f.read(1):
                file_content += f'[...File "{file_path}" truncated at {MAX_CHAR_READ_LIMIT} characters]'

            return file_content
    except Exception as e:
        return f"Error: {e}"


schema_get_files_content = {
    "type": "function",
    "function": {
        "name": "get_file_content",
        "description": "Reads and returns the contents of a file relative to the working directory",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read, relative to the working directory."
                }
            },
            "required": ["file_path"],
            "additionalProperties": False
        },
    },
}