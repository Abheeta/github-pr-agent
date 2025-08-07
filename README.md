# Github PR Analyzer with LLM

## Project setup instructions
Ensure you have docker installed
- Create an `.env` file
```
REDIS_URL=<url> (use redis://redis:6379/0 by default)
LLM_TO_USE=gemini | ollama
GEMINI_API_KEY=<api_key>
OLLAMA_BASE_URL=<url>
```
### To build the project
```bash
$ docker compose build
```
With Ollama:
```bash
$ docker compose -f docker-compose.ollama.yaml build
```
### To start the project
```bash
$ docker compose start
```
With Ollama:
```bash
$ docker compose -f docker-compose.ollama.yaml start
```
### To stop the project
```bash
$ docker compose down
```
With Ollama:
```bash
$ docker compose -f docker-compose.ollama.yaml down
```
## API Documentation
Find documentation for the apis in the postman collection [here](https://www.postman.com/abheethaa/workspace/potpie-github-pr-agent/collection/13334351-e3145ce6-29c0-4b0a-bcf7-85ec659bd133?action=share&creator=13334351&active-environment=13334351-d1bbf4b1-a3ce-4f64-bebf-83c679d0d309)

## Design decisions
### Redis vs Postgresql

- Celery comes with first class support for Redis allowing to integrate it seamlessly.
- Redis is significantly faster than PostgreSQL for Celery message brokering because it operates entirely in memory, reducing I/O overhead.
- Ideally combination of Redis and Postgres would be used. Redis would be used for short term and ephemeral storage while Postgres would be used for more long term, durable storage and persistance. For example the results of the tasks can be stored in Postgres over Redis to ensure the task results are avaiable for as long as necessary. But for the sake of simplicity I have chosen to use Redis as a broker, backend and cache. 

### Gemini(2.5-flash) and Ollama (codellama:7b)
- I initially used Ollama to perform the PR review.
But since it runs locally, the time it took to generate results was very high, and my laptop was slowing down. 
- So I decided to explore other LLMs and used Gemini 2.5-flash by generating an API key with Google AI Studio.

Gemini performed much better in my runs as its analysis was pretty accurate and consistent.
Whereas codellama:7b made incorrect analysis sometimes and was not consistent.

### Langgraph (for Multi-Step Workflow)

- I chose Langgraph since a multi-step workflow could be orchestrated to do several stages of work such as fetch diff, analyze diff, and it can extend to other usecases such as steps for multiple languages, or even analyze commits as well PRs.

Without it, 
- You're manually orchestrating everything:
- You control Celery task chaining manually
- You build task state machines in your app code or Redis
- You deal with "what to do next" logic yourself
- You pass context manually between steps
- You build retry/failure handling logic from scratch

### Prompt Engineering

There was a lot of trial and error in the prompts I wrote for gemini and ollama (the same prompt did not work for both). Prompts had to be very specific to result in consistently accurate and correctly formatted responses. 

### Webhook Support
I decided to add an extra feature - when calling `POST /analyze-pr` API, the user can optionally provide a webhook url. When the task completes and the results are ready, the webhook url is hit with method POST and the results of the task in the request body. This serves as an alternative to polling the pr-agent server with the `task_id`. 

## Overall Architecture

- FastAPI is being used to run a HTTP server.
- Pydantic models work with FastAPI to validate requests and responses
- Whenever the `POST /analyze-pr` API is hit, a new task is added to the celery queue.
- Celery orchestrates, and runs tasks in a queue.
- Once a analyze task starts running, it invokes the LangGraph agent - which has two steps.
    - The first step involves fetching the code diff for the PR from Github, along with the entire files for all changed files.
    - The second step involves passing the code diff plus files, embedded into a system prompt to an LLM (Gemini/Ollama). The result of this step is formatted to the right response format.

## Future Improvements
- Integrating Postgres for persisting long term data. 
- Langsmith for building observability to ensure LLM reasoning is accurate
- Multi Language support
- More steps to double check the results and retry with alternative LLMs. 
- Better context selection - right now the diff and the file in which the PR occured is being sent to the LLM. Adding an intermediary llm step to determine what is relevant context, and passing it to the analyze step will improve results. Larger token context windows provided by Gemini and other LLMs make it possible to provide entire codebases to determine this. 