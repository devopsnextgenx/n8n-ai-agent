from typing import Union, Dict, Any, Optional
import traceback
import threading
import time
import os

class ScriptExecutor:
    def __init__(self, logger, safe_modules=None):
        # Define allowed modules for importing
        self.safe_modules = safe_modules or {'math', 'datetime', 'json', 'random', 'types', 'base64', 'cryptography'}
        self.logger = logger

    def validate_imports(self, script: str) -> bool:
        """Check if script only imports allowed modules"""
        import_lines = [line.strip() for line in script.split('\n') 
                       if line.strip().startswith('import') or 
                          line.strip().startswith('from')]
        
        for line in import_lines:
            module = line.split()[1].split('.')[0]
            if module not in self.safe_modules:
                raise ValueError(f"Import of module '{module}' is not allowed")
        return True
    
    def run_in_main_thread(self, script, local_namespace):
        if threading.current_thread() is threading.main_thread():
            exec(script, {'__builtins__': __builtins__}, local_namespace)
        else:
            raise RuntimeError("This function must be called from the main thread")

    def execute_script(self, 
                      script: str, 
                      local_vars: Optional[Dict[str, Any]] = None) -> Union[Any, Exception]:
        """
        Execute the LLM-generated script with safety measures
        
        Args:
            script: The Python script as a string
            local_vars: Dictionary of local variables to be available to the script
            
        Returns:
            The result of script execution or raises an exception
        """
        try:
            # Validate imports first
            self.validate_imports(script)
            
            # Create a new dictionary for local variables if none provided
            local_namespace = local_vars or {}
            
            # Create a global namespace with necessary modules
            global_namespace = {
                '__builtins__': __builtins__,
                'types': __import__('types')
            }
            # Remove None entries
            global_namespace = {k: v for k, v in global_namespace.items() if v is not None}
            
            # Execute the script in the controlled namespace
            # self.run_in_main_thread(script, local_namespace)
            # remove print statements from script
            script = "\n".join([line for line in script.split("\n") if "print(" not in line])
            exec(script, global_namespace, local_namespace)
            self.logger.debug("Script executed successfully. Local namespace: %s", local_namespace)
            # with open("contents/local_namespace.log", 'w', encoding='utf-8') as f:
            #     f.write(str(local_namespace))
            
            # Filter local namespace to only include serializable values
            filtered_namespace = {}
            if "result" in local_namespace:
                # Special handling for the result variable
                result_value = local_namespace["result"]
                if not callable(result_value) and not isinstance(result_value, type):
                    try:
                        # Test if it can be serialized to JSON
                        import json
                        json.dumps(result_value)
                        return {"result": result_value}
                    except (TypeError, OverflowError):
                        return {"result": str(result_value)}
                else:
                    return {"result": str(result_value)}
            else:
                # Filter the entire namespace
                for key, value in local_namespace.items():
                    # Skip functions, classes and other non-serializable types
                    if not key.startswith('__') and not callable(value) and not isinstance(value, type):
                        try:
                            # Test if it can be serialized to JSON
                            import json
                            json.dumps(value)
                            filtered_namespace[key] = value
                        except (TypeError, OverflowError):
                            # Convert non-serializable objects to strings
                            filtered_namespace[key] = str(value)
                return filtered_namespace
            
        except Exception as e:
            error_msg = f"Script execution failed: {str(e)}\n{traceback.format_exc()}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

# Example usage
def run_script(script_text: str, logger) -> Dict[str, Any]:
    """
    Wrapper function to run generated script and verify outputs

    Args:
        script_text: The script text from LLM
        required_vars: List of variable names that should be present after execution
        
    Returns:
        Dictionary containing the script's output variables
    """
    os.makedirs("contents", exist_ok=True)
    with open("contents/script.py", 'w', encoding='utf-8') as f:
        f.write(script_text)

    executor = ScriptExecutor(logger)
    
    try:
        # Execute the script
        start_time = time.time()
        logger.debug(f"Executing script...")
        try:
            result: Any = executor.execute_script(script_text)
        except Exception as e:
            logger.error(f"Failed to execute script: {str(e)}")
            return {"error": str(e)}

        elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        logger.debug(f"Script execution completed in {elapsed_time:.2f}ms.")
        logger.debug(f"Script result: {result}")
        
        # Ensure contents directory exists
        os.makedirs("contents", exist_ok=True)
        with open("contents/result.md", 'w', encoding='utf-8') as f:
            f.write(str(result))
        
        # Make sure we only return JSON serializable data
        if isinstance(result, dict):
            # Filter out any non-serializable values (like functions)
            filtered_result = {}
            for key, value in result.items():
                # Skip functions and other non-serializable types
                if not callable(value) and not isinstance(value, type):
                    try:
                        # Test if it can be converted to JSON
                        import json
                        json.dumps(value)
                        filtered_result[key] = value
                    except (TypeError, OverflowError):
                        # If it can't be serialized, convert to string
                        filtered_result[key] = str(value)
            return filtered_result
        else:
            # If result is not a dict, try to make it serializable
            try:
                import json
                json.dumps(result)
                print("Result is JSON serializable")
                return result
            except (TypeError, OverflowError):
                print("Result is not JSON serializable")
                return {"result": str(result)}
        
    except Exception as e:
        logger.error(f"Error running script: {str(e)}")
        return {"error": str(e)}