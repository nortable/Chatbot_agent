import os
import json
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv  # Import load_dotenv

load_dotenv()
def _get_work_dir_root():
    work_dir_root = os.environ.get("WORKDIR_ROOT", './data/llm_result')
    return work_dir_root

WORKDIR = _get_work_dir_root()

def read_file(filename):
    if not isinstance(filename, str):
        return "filename must be a string"
    filename = os.path.join(WORKDIR, filename)
    if not os.path.exists(filename):
        return f"{filename} does not exist"
    try:
        with open(filename, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def append_to_file(filename, content):
    if not isinstance(filename, str):
        return "filename must be a string"
    if not isinstance(content, str):
        return "content must be a string"
    filename = os.path.join(WORKDIR, filename)
    try:
        if not os.path.exists(filename):
            # 创建文件并写入内容
            with open(filename, 'w') as f:
                f.write(content)
            return "File created and content appended"
        else:
            with open(filename, 'a') as f:
                f.write(content)
            return "Append successful"
    except Exception as e:
        return f"Error appending to file: {e}"

def write_to_file(filename, content):
    if not isinstance(filename, str):
        return "filename must be a string"
    if not isinstance(content, str):
        return "content must be a string"
    filename = os.path.join(WORKDIR, filename)
    if not os.path.exists(WORKDIR):
        os.makedirs(WORKDIR)
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return "Write successful"
    except Exception as e:
        return f"Error writing to file: {e}"

def search(query):
    if not isinstance(query, str):
        return "query must be a string"

    # Debugging: Check if the API key is loaded
    tavily_api_key = os.environ.get("TAVILY_API_KEY")
    if not tavily_api_key:
        return "Error: TAVILY_API_KEY is not set in the environment."

    tavily = TavilySearchResults(max_results=5)
    try:
        ret = tavily.invoke(input=query)
        # If 'ret' is a string, return it directly
        if isinstance(ret, str):
            return ret
        # If 'ret' is a list, process accordingly
        elif isinstance(ret, list):
            content_list = [obj.get('content', '') for obj in ret]
            return "\n".join(content_list)
        else:
            return f"Unexpected return type from tavily.invoke: {type(ret)}"
    except Exception as err:
        return f"Search error: {err}"

def calculator(expression):
    if not isinstance(expression, str):
        return "expression must be a string"
    try:
        # For safety, limit allowed characters
        allowed_chars = "0123456789+-*/(). "
        if not all(c in allowed_chars for c in expression):
            return "Invalid characters in expression"
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"
    
tools_info = [
    {
        "name": "read_file",
        "description": "Reads the content of a specified file. The file should exist before reading.",
        "args": [
            {
                "name": "filename",
                "type": "string",
                "description": "Name of the file to read."
            }
        ]
    },
    {
        "name": "append_to_file",
        "description": "Appends content to a specified file. If the file does not exist, it will be created.",
        "args": [
            {
                "name": "filename",
                "type": "string",
                "description": "Name of the file."
            },
            {
                "name": "content",
                "type": "string",
                "description": "Content to append to the file."
            }
        ]
    },
    {
        "name": "write_to_file",
        "description": "Writes content to a specified file, overwriting any existing content.",
        "args": [
            {
                "name": "filename",
                "type": "string",
                "description": "Name of the file."
            },
            {
                "name": "content",
                "type": "string",
                "description": "Content to write to the file."
            }
        ]
    },
    {
        "name": "search",
        "description": "Performs a search using the provided query and returns relevant content.",
        "args": [
            {
                "name": "query",
                "type": "string",
                "description": "Search query to look up."
            }
        ]
    },
    {
        "name": "calculator",
        "description": "Evaluates a mathematical expression and returns the result.",
        "args": [
            {
                "name": "expression",
                "type": "string",
                "description": "Mathematical expression to evaluate."
            }
        ]
    },
    {
        "name": "finish",
        "description": "use this function when you think you have already complete the target",
        "args": [{
            "name":"answer",
            "type":"string",
            "description":"the goal is final answer"
        }]
    }
]


tools_map = {
    "read_file": read_file,
    "append_to_file": append_to_file,
    "write_to_file": write_to_file,
    "search": search,
    "calculator":calculator
}

def gen_tools_desc():
    tools_desc = []
    for idx, i in enumerate(tools_info):
        args_desc = []
        for info in i['args']:
            args_desc.append({
                "name": info["name"],
                "description": info["description"],
                "type": info["type"]
            })
        args_desc_json = json.dumps(args_desc, ensure_ascii=False)
        tool_desc = f"{idx+1}. {i['name']}: {i['description']}, args: {args_desc_json}"
        tools_desc.append(tool_desc)
    tools_prompt = "\n".join(tools_desc)
    return tools_prompt
