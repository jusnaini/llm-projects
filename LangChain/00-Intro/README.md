# 🛠 JSON Syntax for Python Data Processsing

`JSON (JavaScript Object notation)` is fundamental in AI/LLM applications because it's the standard format for API communication, configuration files, and data exchange. 

## Core JSON Syntax
JSON has six data types:

- `Objects`: {"key": "value"} (like Python dictionaries)
- `Arrays`: [1, 2, 3] (like Python lists)
- `Strings`: "text" (must use double quotes)
- `Numbers`: 42 or 3.14
- `Booleans`: true or false (lowercase)
- `Null`: null

## Key rules:

- Keys must be strings in double quotes
- No trailing commas
- No comments allowed
- Case-sensitive (true, not True)

## Essential Python JSON Operations

```python
import json
import requests
from typing import Dict, List, Any
import pandas as pd
```

### 1. BASIC JSON OPERATIONS

```python
# Loading JSON from string
json_string = '''
{
    "model": "gpt-4",
    "messages": [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ],
    "temperature": 0.7,
    "max_tokens": 100
}
'''
```

```python
# Parse JSON string to Python dict
data = json.loads(json_string)
print("Parsed data:", data)
```

```python
# Convert Python dict to JSON string
json_output = json.dumps(data, indent=2)
print("JSON output:", json_output)
```


### 2. FILE OPERATIONS

```python
# Reading from JSON file
def load_json_file(filename: str) -> Dict:
    """Load JSON data from file with error handling."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File {filename} not found")
        return {}
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in {filename}: {e}")
        return {}

# Writing to JSON file
def save_json_file(data: Dict, filename: str) -> None:
    """Save data to JSON file with proper formatting."""
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
```


### 3. NESTED DATA ACCESS & MANIPULATION

```python
# Sample nested JSON (common in AI APIs)
api_response = {
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": "The weather is sunny today."
            },
            "finish_reason": "stop",
            "index": 0
        }
    ],
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 6,
        "total_tokens": 16
    },
    "model": "gpt-3.5-turbo"
}
```

```python
# Safe nested access with get()
def safe_get_nested(data: Dict, *keys, default=None):
    """Safely access nested dictionary values."""
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return default
    return data
```

```python
# Examples of safe access
content = safe_get_nested(api_response, "choices", 0, "message", "content")
tokens = safe_get_nested(api_response, "usage", "total_tokens")
print(f"Content: {content}")
print(f"Tokens used: {tokens}")
```

### 4. PROCESSING ARRAYS/LISTS

```python
# Sample data: list of conversations
conversations = [
    {
        "id": "conv_1",
        "messages": [
            {"role": "user", "content": "What is Python?", "timestamp": "2024-01-01"},
            {"role": "assistant", "content": "Python is a programming language.", "timestamp": "2024-01-01"}
        ],
        "tokens_used": 25
    },
    {
        "id": "conv_2", 
        "messages": [
            {"role": "user", "content": "Explain JSON", "timestamp": "2024-01-02"},
            {"role": "assistant", "content": "JSON is a data format.", "timestamp": "2024-01-02"}
        ],
        "tokens_used": 18
    }
]

```
```python
# Extract specific data from arrays
def extract_user_messages(conversations: List[Dict]) -> List[str]:
    """Extract all user messages from conversations."""
    user_messages = []
    for conv in conversations:
        for msg in conv.get("messages", []):
            if msg.get("role") == "user":
                user_messages.append(msg.get("content", ""))
    return user_messages

```
```python
# Calculate total tokens
total_tokens = sum(conv.get("tokens_used", 0) for conv in conversations)
print(f"Total tokens across conversations: {total_tokens}")
```

### 5. DATA TRANSFORMATION & CLEANING

```python
def clean_and_transform_data(raw_data: Dict) -> Dict:
    """Clean and transform JSON data for processing."""
    cleaned = {}
    
    # Handle missing values
    cleaned['model'] = raw_data.get('model', 'unknown')
    
    # Transform nested structures
    if 'choices' in raw_data and raw_data['choices']:
        cleaned['response'] = raw_data['choices'][0].get('message', {}).get('content', '')
        cleaned['finish_reason'] = raw_data['choices'][0].get('finish_reason', 'unknown')
    
    # Convert data types if needed
    usage = raw_data.get('usage', {})
    cleaned['metrics'] = {
        'prompt_tokens': int(usage.get('prompt_tokens', 0)),
        'completion_tokens': int(usage.get('completion_tokens', 0)),
        'total_tokens': int(usage.get('total_tokens', 0))
    }
    
    return cleaned
```

### 6. HANDLING API RESPONSES

```python
def process_api_response(response_text: str) -> Dict:
    """Process API response with error handling."""
    try:
        data = json.loads(response_text)
        
        # Check for API errors
        if 'error' in data:
            error_info = data['error']
            raise Exception(f"API Error: {error_info.get('message', 'Unknown error')}")
        
        return clean_and_transform_data(data)
    
    except json.JSONDecodeError:
        raise Exception("Invalid JSON response from API")
```

### 7. BATCH PROCESSING

```python
def process_multiple_responses(json_files: List[str]) -> pd.DataFrame:
    """Process multiple JSON files into a DataFrame."""
    processed_data = []
    
    for file_path in json_files:
        try:
            data = load_json_file(file_path)
            cleaned = clean_and_transform_data(data)
            cleaned['source_file'] = file_path
            processed_data.append(cleaned)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    return pd.DataFrame(processed_data)
```

### 8. VALIDATION & SCHEMA CHECKING

```python
def validate_message_format(message: Dict) -> bool:
    """Validate if message follows expected schema."""
    required_fields = ['role', 'content']
    valid_roles = ['user', 'assistant', 'system']
    
    # Check required fields
    for field in required_fields:
        if field not in message:
            return False
    
    # Check role validity
    if message['role'] not in valid_roles:
        return False
    
    # Check content is string
    if not isinstance(message['content'], str):
        return False
    
    return True
```

### 9. COMMON PATTERNS FOR AI/LLM APPLICATIONS

```python
class JSONProcessor:
    """Utility class for common JSON processing tasks in AI applications."""
    
    @staticmethod
    def extract_text_content(data: Dict) -> str:
        """Extract text content from various API response formats."""
        # OpenAI format
        if 'choices' in data:
            return data['choices'][0]['message']['content']
        
        # Anthropic format
        if 'content' in data:
            if isinstance(data['content'], list):
                return data['content'][0].get('text', '')
            return data['content']
        
        # Generic text field
        if 'text' in data:
            return data['text']
        
        return ""
    
    @staticmethod
    def create_message_payload(role: str, content: str, **kwargs) -> Dict:
        """Create a standardized message payload."""
        message = {
            "role": role,
            "content": content,
            "timestamp": kwargs.get('timestamp'),
            **kwargs
        }
        # Remove None values
        return {k: v for k, v in message.items() if v is not None}
    
    @staticmethod
    def batch_process_conversations(conversations: List[Dict]) -> Dict:
        """Process multiple conversations and return summary statistics."""
        stats = {
            "total_conversations": len(conversations),
            "total_messages": 0,
            "total_tokens": 0,
            "avg_messages_per_conversation": 0,
            "user_message_count": 0,
            "assistant_message_count": 0
        }
        
        for conv in conversations:
            messages = conv.get('messages', [])
            stats['total_messages'] += len(messages)
            stats['total_tokens'] += conv.get('tokens_used', 0)
            
            for msg in messages:
                if msg.get('role') == 'user':
                    stats['user_message_count'] += 1
                elif msg.get('role') == 'assistant':
                    stats['assistant_message_count'] += 1
        
        if stats['total_conversations'] > 0:
            stats['avg_messages_per_conversation'] = stats['total_messages'] / stats['total_conversations']
        
        return stats
```

### EXAMPLE USAGE

```python
if __name__ == "__main__":
    # Example: Process the sample conversations
    processor = JSONProcessor()
    
    # Create some sample messages
    messages = [
        processor.create_message_payload("user", "Hello, how are you?"),
        processor.create_message_payload("assistant", "I'm doing well, thank you!")
    ]
    
    print("Sample messages:", json.dumps(messages, indent=2))
    
    # Process conversation statistics
    stats = processor.batch_process_conversations(conversations)
    print("Conversation stats:", json.dumps(stats, indent=2))
```
## Key Patterns for AI/LLM Applications
- **API Response Handling**: Most AI APIs return nested JSON with specific structures. Always use safe access methods and handle errors gracefully.
- **Message Format Standardization**: Different APIs use different message formats. Create utility functions to normalize them.
- **Batch Processing**: When processing multiple responses or conversations, use generators or pandas for efficiency with large datasets.
- **Schema Validation**: Always validate JSON structure before processing, especially when dealing with user inputs or external APIs.
- **Error Handling**: JSON parsing can fail, so wrap operations in try-catch blocks and provide meaningful error messages.


## Common AI/LLM JSON Patterns

* `OpenAI format`: {"choices": [{"message": {"role": "assistant", "content": "..."}}]}
* `Anthropic format`: {"content": [{"text": "..."}]}
* `Configuration files`: Model parameters, prompt templates
* `Training data`: Conversation logs, fine-tuning datasets

The key is to write defensive code that handles missing fields, unexpected data types, and malformed JSON gracefully.