import datetime
from langchain.agents import load_tools, initialize_agent
from langchain.agents import AgentType
from langchain.llms import Ollama

# Get the current date
current_date = datetime.datetime.now().date()
# Define the date after which the model should be set to a different model
target_date = datetime.date(2024, 6, 12)

# Set the model variable based on the current date
if current_date > target_date:
    # Use a more capable model like llama2 or codellama
    llm_model = "llama2"  # or "mistral", "codellama", "phi", etc.
else:
    # Use a lighter model for earlier dates
    llm_model = "llama2:7b"

# Initialize Ollama LLM
# Make sure you have Ollama installed and the model pulled
# Install: curl -fsSL https://ollama.ai/install.sh | sh
# Pull model: ollama pull llama2
llm = Ollama(
    model=llm_model,
    temperature=0,
    # Optional: adjust these parameters based on your needs
    # num_predict=512,  # max tokens to generate
    # top_k=10,
    # top_p=0.3
)

# Load tools (Wikipedia works without API keys, llm-math uses the LLM)
tools = load_tools(["llm-math", "wikipedia"], llm=llm)

# Initialize the agent
agent = initialize_agent(
    tools, 
    llm, 
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,
    verbose=True,
    max_iterations=3,  # Limit iterations to prevent infinite loops
    max_execution_time=60,  # Timeout after 60 seconds
)

# Test question
question = "Tom M. Mitchell is an American computer scientist \
and the Founders University Professor at Carnegie Mellon University (CMU)\
what book did he write?"

try:
    result = agent(question)
    print("Result:", result)
except Exception as e:
    print(f"Error occurred: {e}")
    print("Make sure Ollama is running and the model is available")
