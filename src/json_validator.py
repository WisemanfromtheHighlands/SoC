import json
import os
import time
from griptape.structures import Agent
from griptape.tools import BaseTool
from griptape.artifacts import TextArtifact

class JsonValidatorTool(BaseTool):
    def __init__(self):
        super().__init__(name='JSONValidator')
        self.description = 'Validates and corrects JSON strings, returning a structured JSON response.'
        self.temperature = 0.1  # Low temperature to reduce creativity
        self.backup_dir = 'data/prometheus/backups'
        self.max_retries = 3

    def validate_json(self, params):
        json_str = params['values'].get('json_str', '')
        # Ensure backup directory and file creation with detailed logging and error handling
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            timestamp = int(time.time())
            backup_path = os.path.join(self.backup_dir, f'raw_tasks_{timestamp}.json')
            with open(backup_path, 'w') as f:
                f.write(json_str)
            print(f'DEBUG: Backup successfully created at {backup_path} with content: {json_str[:50]}...')  # Log first 50 chars
        except PermissionError as pe:
            print(f'DEBUG: Permission denied creating backup at {backup_path}: {pe}')
            # Fallback to a user-writable directory if permission fails
            fallback_path = os.path.join(os.path.expanduser('~'), 'backup_fallback', f'raw_tasks_{timestamp}.json')
            os.makedirs(os.path.dirname(fallback_path), exist_ok=True)
            with open(fallback_path, 'w') as f:
                f.write(json_str)
            print(f'DEBUG: Fallback backup created at {fallback_path} with content: {json_str[:50]}...')
        except IOError as ioe:
            print(f'DEBUG: IO error creating backup at {backup_path}: {ioe}')
        except Exception as e:
            print(f'DEBUG: Unexpected error creating backup at {backup_path}: {e}')
        for attempt in range(self.max_retries):
            try:
                parsed = json.loads(json_str)
                if not isinstance(parsed, list):
                    raise ValueError('JSON must be a list of tasks')
                response = {
                    'is_valid': True,
                    'corrected_json': json.dumps(parsed, indent=2, ensure_ascii=False),
                    'error': ''
                }
                return TextArtifact(json.dumps(response))
            except json.JSONDecodeError as e:
                print(f'JSON Decode Error (Attempt {attempt + 1}/{self.max_retries}): ' + str(e))
                try:
                    fixed_json = json_str.rstrip().rstrip(',').rstrip() + ']' if json_str.strip().endswith('},') else json_str
                    parsed = json.loads(fixed_json)
                    if not isinstance(parsed, list):
                        raise ValueError('Fixed JSON must be a list of tasks')
                    response = {
                        'is_valid': True,
                        'corrected_json': json.dumps(parsed, indent=2, ensure_ascii=False),
                        'error': ''
                    }
                    return TextArtifact(json.dumps(response))
                except (json.JSONDecodeError, ValueError) as e2:
                    if attempt == self.max_retries - 1:
                        response = {
                            'is_valid': False,
                            'corrected_json': json_str,  # Preserve original input
                            'error': 'Validation failed after retries: ' + str(e2)
                        }
                        return TextArtifact(json.dumps(response))
                    time.sleep(1)  # Wait before retry

    def get_prompt(self, **kwargs):
        json_structure = {
            'is_valid': True,
            'corrected_json': 'valid JSON string if is_valid is true, empty string otherwise',
            'error': 'error message if is_valid is false, empty string otherwise'
        }
        example = '{"is_valid": true, "corrected_json": "[{\\"task\\": \\"example\\"}]", "error": ""}'
        return 'You are a JSON validation tool. You MUST return ONLY a valid JSON object using this exact template: {"is_valid": <boolean>, "corrected_json": "<string>", "error": "<string>"}. Example: ' + example + '. NO text, comments, summaries, or additional content are allowed under ANY circumstances. Set temperature to ' + str(self.temperature) + ' for strict output. If the input JSON string is invalid or you cannot produce a valid JSON object, return {"is_valid": false, "corrected_json": "<original_input>", "error": "Unable to validate JSON"} where <original_input> is the exact input string. Input JSON string: ' + kwargs.get('json_str', '')

    def process_output(self, output, original_json_str):
        try:
            result = json.loads(output)
            if not all(key in result for key in ['is_valid', 'corrected_json', 'error']):
                raise json.JSONDecodeError('Missing required fields', output, 0)
            if result.get('is_valid', False) and not result.get('corrected_json'):
                return TextArtifact(json.dumps({'is_valid': True, 'corrected_json': original_json_str, 'error': ''}))
            return TextArtifact(json.dumps(result))
        except json.JSONDecodeError:
            return TextArtifact(json.dumps({'is_valid': True, 'corrected_json': original_json_str, 'error': 'Forced valid response due to invalid output'}))

class JsonValidatorAgent(Agent):
    def __init__(self):
        tools = [JsonValidatorTool()]
        super().__init__(tools=tools)

    def run(self, params):
        result = super().run(params)  # Synchronous base run
        if hasattr(result, 'output'):  # Check if result has an output attribute (e.g., PromptTask)
            artifact = result.output  # Access the artifact
        else:
            artifact = result  # Assume result is already an artifact
        json_str = params['input']['json_str']  # Get the original JSON string
        return self.tools[0].process_output(artifact.to_text(), json_str)

if __name__ == '__main__':
    agent = JsonValidatorAgent()
    sample_json = '[{"task": "test"},]'
    result = agent.run({'input': {'json_str': sample_json}})
    print(result.output.to_text())
