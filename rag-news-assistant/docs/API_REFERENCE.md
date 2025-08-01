# API Reference

## RAGPipeline Class

The main class that implements the Retrieval-Augmented Generation pipeline.

### Constructor

```python
RAGPipeline(docs, embedding_model="all-MiniLM-L6-v2", gen_model="google/flan-t5-base")
```

**Parameters:**
- `docs` (list): List of document strings to index
- `embedding_model` (str): Hugging Face model name for embeddings (default: "all-MiniLM-L6-v2")
- `gen_model` (str): Hugging Face model name for text generation (default: "google/flan-t5-base")

**Example:**
```python
from rag_pipeline import RAGPipeline
from loader import load_news

docs = load_news()
pipeline = RAGPipeline(docs)
```

### Methods

#### `retrieve(query, top_k=3)`

Retrieves the most relevant documents for a given query.

**Parameters:**
- `query` (str): The search query
- `top_k` (int): Number of documents to retrieve (default: 3)

**Returns:**
- `list`: List of relevant document strings

**Example:**
```python
relevant_docs = pipeline.retrieve("What happened in the Olympics?", top_k=5)
```

#### `generate(query, context)`

Generates an answer based on the query and retrieved context.

**Parameters:**
- `query` (str): The user's question
- `context` (list): List of relevant document strings

**Returns:**
- `str`: Generated answer text

**Example:**
```python
context = pipeline.retrieve("Olympics question")
answer = pipeline.generate("What happened in the Olympics?", context)
```

#### `answer(query)`

Complete RAG pipeline: retrieves relevant documents and generates an answer.

**Parameters:**
- `query` (str): The user's question

**Returns:**
- `str`: Generated answer based on retrieved context

**Example:**
```python
answer = pipeline.answer("What happened in the Olympics?")
```

## Loader Module

### Functions

#### `load_news(file_path="data/news_sample.txt")`

Loads news documents from a text file.

**Parameters:**
- `file_path` (str): Path to the text file containing news data

**Returns:**
- `list`: List of document strings

**Example:**
```python
from loader import load_news

docs = load_news("data/my_news.txt")
```

## Streamlit App Interface

### Session State Variables

The app uses Streamlit's session state to maintain conversation history:

```python
st.session_state.messages = [
    {"role": "user", "content": "What happened in the Olympics?"},
    {"role": "assistant", "content": "The 2020 Summer Olympics were held in Tokyo..."}
]
```

### Chat Components

#### `st.chat_input(placeholder)`

Creates a chat input widget at the bottom of the app.

**Parameters:**
- `placeholder` (str): Placeholder text for the input field

#### `st.chat_message(role)`

Creates a chat message container.

**Parameters:**
- `role` (str): Either "user" or "assistant"

### Caching

#### `@st.cache_resource`

Decorator used to cache the RAG pipeline to avoid reloading models on each interaction.

**Example:**
```python
@st.cache_resource
def get_pipeline():
    docs = load_news()
    return RAGPipeline(docs)
```

## Configuration Options

### Model Parameters

You can customize the models used in the pipeline:

```python
# For faster inference (smaller models)
pipeline = RAGPipeline(
    docs,
    embedding_model="all-MiniLM-L6-v2",  # Fast embedding model
    gen_model="google/flan-t5-small"     # Smaller generation model
)

# For better quality (larger models)
pipeline = RAGPipeline(
    docs,
    embedding_model="all-mpnet-base-v2",  # Higher quality embeddings
    gen_model="google/flan-t5-large"      # Larger generation model
)
```

### Generation Parameters

Modify generation behavior in the `generate` method:

```python
def generate(self, query, context):
    prompt = f"Context: {' '.join(context)}\n\nQuestion: {query}\nAnswer:"
    result = self.generator(
        prompt, 
        max_new_tokens=128,    # Increase for longer answers
        temperature=0.7,       # Control randomness (0.0-1.0)
        do_sample=True         # Enable sampling
    )
    return result[0]['generated_text']
```

### Retrieval Parameters

Adjust retrieval behavior:

```python
def retrieve(self, query, top_k=5):  # Increase for more context
    query_emb = self.embedder.encode([query], convert_to_numpy=True)
    D, I = self.index.search(query_emb, top_k)
    return [self.docs[i] for i in I[0]]
```

## Error Handling

### Common Exceptions

#### `ModuleNotFoundError`
- **Cause**: Missing dependencies
- **Solution**: Install required packages

#### `FileNotFoundError`
- **Cause**: Missing data file
- **Solution**: Ensure `data/news_sample.txt` exists

#### `RuntimeError`
- **Cause**: Model loading issues
- **Solution**: Check internet connection for model downloads

### Error Handling Example

```python
try:
    answer = pipeline.answer(query)
except Exception as e:
    st.error(f"Error processing query: {str(e)}")
    st.info("Please try again or check your internet connection.")
```

## Performance Considerations

### Memory Usage

- **Embedding Model**: ~100-200 MB
- **Generation Model**: ~1-3 GB
- **FAISS Index**: ~10-50 MB (depends on document count)

### Processing Time

- **First Run**: 30-60 seconds (model downloads)
- **Subsequent Queries**: 2-5 seconds
- **Retrieval**: <1 second
- **Generation**: 1-4 seconds

### Optimization Tips

1. **Use smaller models** for faster inference
2. **Implement caching** for frequently asked questions
3. **Batch process** multiple queries
4. **Use GPU acceleration** if available
5. **Limit document count** for faster retrieval 