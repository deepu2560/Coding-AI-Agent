import os

def get_files_info(working_directory: str, directory: str = ".") -> str:
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))
        valid_target_dir = os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs

        if not valid_target_dir:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'

        files_list = os.listdir(target_dir)
        files_list_path = []

        for file in files_list:
            file_path = os.path.join(target_dir, file)
            file_size = os.path.getsize(file_path)
            file_isDir = os.path.isdir(file_path)

            file_str = f"- {file}: file_size={file_size} bytes, is_dir={file_isDir}"
            files_list_path.append(file_str)

        files_info = "\n".join(files_list_path)
        return f'Result for {"current" if directory == "." else directory} directory:\n{files_info}'
        return f'Success: "{directory}" is within the working directory'
    except Exception as e:
        return f"Error: {e}"


schema_get_files_info = {
    "type": "function",
    "function": {
        "name": "get_files_info",
        "description": "Lists files in a specified directory relative to the working directory, providing file size and directory status",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory to list, relative to the working directory. Defaults to current directory."
                }
            },
            "additionalProperties": False
        },
    },
}