# AI/ML API

### AI/ML API provides 300+ AI models including Deepseek, Gemini, ChatGPT. The models run at enterprise-grade rate limits and uptimes.

### This section describes how to use the AI/ML API provider with GPT-DB.

1. Sign up at [AI/ML API](https://aimlapi.com/app/?utm_source=gpt_db&utm_medium=github&utm_campaign=integration) and generate an API key.
2. Set the environment variable `AIMLAPI_API_KEY` with your key.
3. Use the `configs/gptdb-proxy-aimlapi.toml` configuration when starting GPT-DB.

### You can look up models at [https://aimlapi.com/models/](https://aimlapi.com/models/?utm_source=gpt_db&utm_medium=github&utm_campaign=integration)

### Or you can use docker/base/Dockerfile to run GPT-DB with AI/ML API:

```dockerfile
# Expose the port for the web server, if you want to run it directly from the Dockerfile
EXPOSE 5670

# Set the environment variable for the AIMLAPI API key
ENV AIMLAPI_API_KEY="***"

# Just uncomment the following line in the `Dockerfile` to use AI/ML API:
CMD ["gptdb", "start", "webserver", "--config", "configs/gptdb-proxy-aimlapi.toml"]
```
