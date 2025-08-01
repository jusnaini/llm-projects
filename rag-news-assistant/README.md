# 📰 News-Based Q&A Assistant (RAG Implementation)

A Retrieval-Augmented Generation (RAG) application that allows users to ask questions about news content and receive AI-generated answers based on relevant document retrieval.

## 🎯 Features

- **Chat-style Interface**: Interactive Q&A using Streamlit's chat components
- **Semantic Search**: Uses sentence transformers for document retrieval
- **AI-Powered Answers**: Generates contextual responses using transformers
- **Real-time Processing**: Dynamic question answering with conversation history
- **Vector-based Retrieval**: FAISS for efficient similarity search

## 🏗️ Project Structure

```
rag-news-assistant/
├── app.py                 # Streamlit web application
├── rag_pipeline.py        # RAG pipeline implementation
├── loader.py             # Document loading utilities
├── requirements.txt      # Python dependencies
├── data/
│   └── news_sample.txt   # Sample news data
├── condaenv/            # Conda environment (created during setup)
└── README.md           # This documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Conda (recommended) or pip
- macOS (tested on Apple Silicon)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd /path/to/rag-news-assistant
   ```

2. **Create and activate conda environment:**
   ```bash
   conda create -y -p ./condaenv python=3.10
   conda activate ./condaenv
   ```

3. **Install dependencies:**
   ```bash
   conda install -y -c conda-forge faiss-cpu
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser:**
   Navigate to `http://localhost:8501`

## 📖 Usage

### Basic Q&A

1. **Start the app** using the commands above
2. **Type your question** in the chat input at the bottom
3. **Press Enter** to submit
4. **View the AI response** in the chat interface

### Example Questions

- "What happened in the last Olympics?"
- "Tell me about Simone Biles' performance"
- "What infrastructure bill was passed?"

### Features

- **Conversation History**: Previous Q&A pairs are preserved during the session
- **Loading Indicators**: Visual feedback during processing
- **Responsive Design**: Works on desktop and mobile browsers

## 🔧 Technical Details

### Core Components

#### `app.py`
- **Streamlit Interface**: Chat-based UI with session state management
- **Pipeline Integration**: Connects user input to RAG pipeline
- **Error Handling**: Graceful handling of processing errors

#### `rag_pipeline.py`
- **RAGPipeline Class**: Main RAG implementation
- **Embedding Model**: Uses `all-MiniLM-L6-v2` for semantic search
- **Generation Model**: Uses `google/flan-t5-base` for answer generation
- **Vector Search**: FAISS index for efficient retrieval

#### `loader.py`
- **Document Loading**: Reads news data from text files
- **Text Processing**: Basic cleaning and formatting
- **File Handling**: UTF-8 encoding support

### Dependencies

#### Core Libraries
- **streamlit**: Web application framework
- **transformers**: Hugging Face transformers for NLP
- **sentence-transformers**: Semantic text embeddings
- **faiss-cpu**: Vector similarity search

#### Supporting Libraries
- **torch**: PyTorch for deep learning
- **scikit-learn**: Machine learning utilities
- **numpy**: Numerical computing
- **pandas**: Data manipulation

## 🛠️ Configuration

### Model Selection

You can modify the models used in `rag_pipeline.py`:

```python
# Change embedding model
embedding_model="all-MiniLM-L6-v2"  # Fast, good quality

# Change generation model  
gen_model="google/flan-t5-base"     # Balanced speed/quality
```

### Data Sources

Add your own news data by:
1. Replacing `data/news_sample.txt` with your content
2. Each line should be a separate news snippet
3. Restart the application

### Performance Tuning

- **Retrieval Count**: Modify `top_k` in `retrieve()` method
- **Generation Length**: Adjust `max_new_tokens` in `generate()` method
- **Cache Settings**: Modify `@st.cache_resource` decorators

## 🔍 Troubleshooting

### Common Issues

#### FAISS Installation Errors
- **Problem**: `ModuleNotFoundError: No module named 'faiss'`
- **Solution**: Use conda instead of pip: `conda install -c conda-forge faiss-cpu`

#### Memory Issues
- **Problem**: Out of memory during model loading
- **Solution**: Reduce batch sizes or use smaller models

#### Slow Performance
- **Problem**: First query takes a long time
- **Solution**: Models are downloaded on first use, subsequent queries are faster

### Environment Issues

#### Python Version Conflicts
- **Problem**: Incompatible Python versions
- **Solution**: Use Python 3.10 as specified in setup

#### Conda Environment
- **Problem**: Environment not activating properly
- **Solution**: Ensure you're using `conda activate ./condaenv`

## 📊 Performance

### Benchmarks
- **Model Loading**: ~30 seconds (first run)
- **Query Processing**: ~2-5 seconds per question
- **Memory Usage**: ~2-3 GB RAM
- **Storage**: ~1-2 GB for models and data

### Optimization Tips
- Use smaller models for faster inference
- Implement model caching for production
- Consider batch processing for multiple queries
- Use GPU acceleration if available

## 🔮 Future Enhancements

### Planned Features
- [ ] Document upload interface
- [ ] Multiple data source support
- [ ] Advanced filtering options
- [ ] Export conversation history
- [ ] User authentication
- [ ] API endpoints

### Technical Improvements
- [ ] Model quantization for faster inference
- [ ] Persistent vector store
- [ ] Real-time data updates
- [ ] Multi-language support
- [ ] Advanced caching strategies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the technical documentation
3. Open an issue on the repository

---

**Happy Questioning! 🚀** 