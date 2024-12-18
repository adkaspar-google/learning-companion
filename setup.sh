#!/bin/bash

# Function to prompt the user for an environment variable value
function get_env_var {
  local var_name="$1"
  local description="$2"
  local link="$3"

  echo ""
  echo "$description"
  if [[ -n "$link" ]]; then
    echo "You can find more information here: $link"
  fi
  read -p "Enter your $var_name: " value
  echo "$var_name=$value" >> .env
}

# Get the API keys and other environment variables
get_env_var "GOOGLE_API_KEY" "To leverage Google Search and avoid being restricted with reCAPTCHA every few queries, you'll need a Google API key." "https://developers.google.com/custom-search/v1/overview"
get_env_var "GOOGLE_CSE_ID" "You'll also need a Custom Search Engine (CSE) ID." "https://programmablesearchengine.google.com/controlpanel/create"
get_env_var "TAVILY_API_KEY" "To use Tavily search engine as a tool, you'll need a Tavily API key. They have a free tier available." "https://www.tavily.com/"
get_env_var "LANGCHAIN_TRACING_V2" "Enable LangChain tracing to monitor and debug your LangChain applications." "https://docs.langchain.com/docs/guides/langchain_hub/tracing"
get_env_var "LANGCHAIN_ENDPOINT" "If you're using a LangChain Hub endpoint, provide its URL here." "https://docs.langchain.com/docs/guides/langchain_hub/"
get_env_var "LANGCHAIN_API_KEY" "If you're using the LangChain Hub, you'll need a LangChain API key." "https://docs.langchain.com/docs/guides/langchain_hub/"
get_env_var "LANGCHAIN_PROJECT" "If you're using the LangChain Hub, specify your LangChain project name." "https://docs.langchain.com/docs/guides/langchain_hub/"
get_env_var "PROJECT_ID" "Your Google Cloud project ID." "https://console.cloud.google.com/home/dashboard"

echo ""
echo ".env file created successfully!"
