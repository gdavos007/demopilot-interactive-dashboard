# DemoPilot Backend

FastAPI backend for the DemoPilot product knowledge agent with VAPI voice integration.

## Features

- FastAPI-based REST API
- VAPI voice integration
- Product knowledge agent with RAG
- Storylane demo integration
- Async-first architecture

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e ".[dev]"
```

3. Create a `.env` file in the backend directory with the following variables:
```env
VAPI_API_KEY=your_vapi_api_key
VAPI_ASSISTANT_ID=your_vapi_assistant_id
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key  # Optional
STORYLANE_SHARE_ID=your_storylane_share_id
```

## Development

1. Start the development server:
```bash
uvicorn app.main:app --reload
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Voice Integration
- POST `/api/v1/voice/webhook` - Handle VAPI voice events
- POST `/api/v1/voice/speak` - Convert text to speech

## Testing

Run tests with pytest:
```bash
pytest
```

## Project Structure

```
/app
  /api
    /v1
      /voice        # Voice integration endpoints
      /knowledge    # Product knowledge endpoints
      /demo         # Storylane demo endpoints
  /core
    /voice         # VAPI client
    /knowledge     # Product knowledge agent
    /demo          # Storylane integration
  /models          # Pydantic models
  /config          # Configuration
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

## License

MIT 