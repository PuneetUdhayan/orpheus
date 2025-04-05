import os
import json
import typing 
import inspect
import importlib.util
from pathlib import Path
from langchain_core.utils.function_calling import convert_to_openai_tool

# os.environ["API_URL"]
# os.environ["API_KEY"]
# os.environ["USER_ID"]

def ensure_init_py():
    folder = Path("tool_folder")
    init_file = folder / '__init__.py'
    if not init_file.exists():
        init_file.touch()  # Create an empty __init__.py file
        print(f"Created: {init_file}")
    else:
        print(f"Already exists: {init_file}")
    
ensure_init_py()
import tool_folder

def get_orpheus_config():
    with open("tool_folder/orpheus.json") as f:
        return json.load(f)



def get_function(tool_config):
    config_path = os.path.join("tool_folder", "orpheus.json")
# Get absolute path to the config file
    config_abs_path = os.path.abspath(config_path)
    config_dir = os.path.dirname(config_abs_path)
    tool_path = tool_config["tool"]
    file_name, func_name = tool_path.split(":")

    # Get full path to the Python file (relative to config file)
    script_path = os.path.join(config_dir, file_name)
    module_name = os.path.splitext(os.path.basename(file_name))[0]

    # Load the module dynamically
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Get the function and signature
    return getattr(tool_folder, func_name)

def get_output_details_for_tool(tool):
    signature = inspect.signature(tool)
    return_annotation = signature.return_annotation

    # Check if the return annotation is a generic type like List[Model]
    origin = typing.get_origin(return_annotation)
    if origin is list or origin is List: # Handles both list and typing.List
        args = typing.get_args(return_annotation)
        if args:
            inner_type = args[0]
            # Check if the inner type is a Pydantic model
            if inspect.isclass(inner_type) and issubclass(inner_type, BaseModel):
                return inner_type.model_json_schema()
    # Optional: Handle case where the function returns a single Pydantic model directly
    elif inspect.isclass(return_annotation) and issubclass(return_annotation, BaseModel):
        return return_annotation.model_json_schema()
    raise Exception("Could not determine output format of tool")

def get_openai_spec(tool):
    open_ai_spec = convert_to_openai_tool(i)
    open_ai_spec['function']['description'] = open_ai_spec['function'].get('description','')+f"""

The output format is:
{json.dumps(get_output_details_for_tool(tool))}

    """
    return open_ai_spec
    
def register_tool(payload):
    pass

def package_tool():
    tool_config = get_orpheus_config()
    ensure_init_py()
    func = get_function(tool_config)
    sig = inspect.signature(func)
    tool_details = {
        "openai_spec": get_openai_spec(sig),
        "output_details": get_output_details_for_tool(sig)
    }



if __name__=="__main__":
    package_tool()