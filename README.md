
## Steps

- Get several top coding LLM (Deepseek Coder, code llama) with support tools (ollama, gradio, langchain, llamaindex, etc.) inside telco (VT first because we have GPU there)
- Setup LLM to work with GPU
- Step web portal to use chatbot
- Code documentation every code inside etl and other critical packages
- Revise code to insert comment into every code chunks
- Use LLM to revise, summarize and control every commit



install mongodb 
brew tap mongodb/brew
brew install mongodb-community@6.0
brew services start mongodb/brew/mongodb-community@6.0

brew --prefix mongodb-community

export PATH="/opt/homebrew/opt/mongodb-community@6.0/bin:$PATH"
mongod

/opt/homebrew/etc/mongod.conf