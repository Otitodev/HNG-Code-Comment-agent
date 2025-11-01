# Telex AI Agent 🤖

An intelligent AI-powered agent that integrates with Telex.im to provide contextual assistance through chat interactions. Built with FastAPI and deployed on AWS Lambda with PostgreSQL RDS, the agent processes messages from Telex users and responds with AI-generated content using Mistral AI.

## 🚀 Features

### Core Functionality
- **Telex.im Integration**: Seamless webhook integration with Telex chat platform
- **AI-Powered Responses**: Uses Mistral AI for intelligent conversation and assistance
- **Code Assistance**: Specialized help with programming questions, debugging, and code review
- **Text Summarization**: Summarizes documents and long text content
- **General Chat**: Friendly conversational AI for general inquiries and support
- **Language Detection**: Supports 15+ programming languages with intelligent detection
- **Daily Tips**: Generates personalized coding tips and best practices
- **Health Monitoring**: Built-in health checks, logging, and error handling

### Supported Languages
Python, JavaScript, TypeScript, Java, C#, C++, C, Go, Rust, PHP, Ruby, Swift, Kotlin, SQL, HTML, CSS

## 🏗️ Architecture

```
Telex.im → Webhook → API Gateway → Lambda → Mistral AI
                                     ↓
                            RDS PostgreSQL
```

### AWS Services Used
- **AWS Lambda**: Serverless compute for FastAPI application
- **API Gateway HTTP API**: RESTful API endpoints and webhook handling
- **RDS PostgreSQL**: Managed database for user data and conversation history
- **VPC**: Network isolation and security
- **ECR**: Container registry for Lambda images
- **CloudFormation/SAM**: Infrastructure as Code

## 📋 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome route with API information |
| `/ping` | GET | Health check endpoint |
| `/webhook` | POST | **Main Telex event handler** |
| `/respond` | POST | Internal AI processing route |
| `/test` | GET | Test endpoint for webhook verification |
| `/api/comment` | POST | Legacy code commenting endpoint |
| `/api/daily-tip` | GET | Daily programming tips |

### Webhook Integration

#### Request from Telex.im
```json
{
  "event": "message_received",
  "data": {
    "user": "john_doe",
    "message": "Can you help me debug this Python function?",
    "channel_id": "general",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

#### Response to Telex.im
```json
{
  "response": {
    "message": "I'd be happy to help you debug your Python function! Please share the code and describe what issue you're experiencing. I can help identify common problems and suggest solutions.",
    "action": "reply",
    "metadata": {
      "user": "john_doe",
      "agent": "telex-ai-assistant",
      "response_type": "ai_generated"
    }
  }
}
```

## 🛠️ Local Development

### Prerequisites
- Python 3.11+
- Docker
- AWS CLI configured
- SAM CLI
- Mistral AI API key

### Setup
1. **Clone and setup environment:**
```bash
git clone <repository-url>
cd telex-ai-agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment variables:**
```bash
# Copy and edit .env file
cp .env.example .env
```

Required environment variables:
```env
MISTRAL_API_KEY=your_mistral_api_key_here
TELEX_AGENT_API_KEY=your_telex_api_key_here
TELEX_WEBHOOK_SECRET=your_webhook_secret
DATABASE_URL=sqlite+aiosqlite:///./app.db  # For local development
API_BASE_URL=http://localhost:8080
```

3. **Run locally:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### Testing Locally
```bash
# Test health check
curl -X GET "http://localhost:8080/ping"

# Test webhook endpoint
curl -X POST "http://localhost:8080/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "message_received",
    "data": {
      "user": "test_user",
      "message": "Hello, can you help me with Python?"
    }
  }'

# Test direct AI response
curl -X POST "http://localhost:8080/respond" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain async/await in Python",
    "user": "developer"
  }'
```

## 🚀 AWS Deployment

### Prerequisites
- AWS CLI configured with appropriate permissions
- Docker running
- SAM CLI installed

### Deploy to AWS
1. **Build the application:**
```bash
sam build
```

2. **Deploy with parameters:**
```bash
sam deploy \
  --parameter-overrides \
    MistralApiKey=your_mistral_api_key \
    TelexAgentApiKey=your_telex_api_key \
    DBUsername=codeagent \
    DBPassword=YourSecurePassword123! \
    DBName=codeagentdb \
  --resolve-image-repos \
  --no-confirm-changeset
```

3. **Configure Telex.im:**
   - Set webhook URL to your deployed API endpoint + `/webhook`
   - Configure authentication with your Telex API key
   - Test the integration using the `/test` endpoint

## 🤖 AI Capabilities

### Message Classification
The agent automatically classifies incoming messages:
- **Code Help**: Programming questions, debugging, code review
- **Summarization**: Document summaries, text analysis
- **General Chat**: Greetings, general questions, conversation
- **Default**: Fallback for unclassified messages

### Response Types
- **Code Assistance**: Detailed programming help with examples
- **Summarization**: Concise summaries of provided content
- **Conversational**: Friendly, helpful responses to general queries
- **Error Handling**: Graceful fallbacks when AI services are unavailable

### Fallback System
1. **Primary**: Mistral AI generated responses
2. **Secondary**: Cached or template responses
3. **Tertiary**: Generic helpful messages
4. **Ultimate**: Error acknowledgment with retry suggestion

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MISTRAL_API_KEY` | Yes | Mistral AI API key for AI responses |
| `TELEX_AGENT_API_KEY` | No | Telex agent API key for authentication |
| `TELEX_WEBHOOK_SECRET` | No | Webhook secret for request validation |
| `DATABASE_URL` | No | PostgreSQL connection string |
| `API_BASE_URL` | No | Base URL for the deployed service |
| `DEBUG` | No | Enable debug mode (default: false) |
| `LOG_LEVEL` | No | Logging level (default: INFO) |

### Database Models
- **DailyTip**: Stores generated tips with language specificity
- **CodeRequest**: Tracks user interactions and detected languages
- **UserLanguagePreference**: Maintains user's programming preferences

## 🔒 Security

### Network Security
- RDS in private subnets (no internet access)
- Lambda in public subnets (cost-optimized)
- Security groups restrict access between services
- API Gateway handles public traffic with rate limiting

### Data Security
- Database encryption at rest
- Environment variables for sensitive data
- Input validation using Pydantic models
- Error message sanitization
- CORS configuration for web security

## 📊 Monitoring & Costs

### Cost Optimization
**Monthly Costs (Estimated):**
- RDS db.t3.micro: ~$13.87/month (free tier eligible)
- Lambda: Usually free (1M requests/month free tier)
- API Gateway: Usually free (1M requests/month free tier)
- Storage & misc: ~$2-5/month

**Total: ~$15-20/month** (with free tier benefits)

### Performance Monitoring
- CloudWatch logs for Lambda function
- Request/response logging with user context
- AI service performance tracking
- Error rate monitoring
- Database performance insights

## 🧪 Testing

### Unit Tests
```bash
pytest tests/
```

### Integration Testing
```bash
# Test webhook with sample Telex payload
curl -X POST "https://your-api-url/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "message_received",
    "data": {
      "user": "test_user",
      "message": "How do I fix a memory leak in Python?",
      "channel_id": "dev-help"
    }
  }'
```

### Telex Integration Testing
1. Configure your Telex.im webhook URL
2. Send test messages through Telex
3. Monitor logs in AWS CloudWatch
4. Verify responses appear in Telex chat

## 🛠️ Development

### Project Structure
```
├── app/
│   ├── main.py                     # FastAPI application with Telex integration
│   ├── config.py                   # Configuration management
│   ├── db.py                       # Database configuration
│   ├── models.py                   # SQLAlchemy models
│   ├── routes/
│   │   ├── telex_webhook.py        # Telex webhook handlers
│   │   ├── comment.py              # Code commenting endpoints
│   │   └── daily_tip.py            # Daily tips endpoints
│   └── services/
│       ├── telex_ai_service.py     # Main AI logic for Telex
│       ├── mistral_service.py      # Mistral AI integration
│       └── language_detector.py    # Language detection logic
├── daily_task.py                   # Automated daily tips
├── template.yaml                   # SAM/CloudFormation template
├── Dockerfile                      # Lambda container image
└── requirements.txt                # Python dependencies
```

### Adding New Features
1. **New Message Types**: Update `_classify_message()` in `TelexAIService`
2. **New AI Capabilities**: Add handlers in `telex_ai_service.py`
3. **New Endpoints**: Create routes in appropriate router files
4. **Database Changes**: Update models and run migrations

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## 📝 Telex.im Integration Guide

### 1. Agent Registration
- Register your agent with Telex.im
- Obtain API keys and webhook secrets
- Configure agent permissions and capabilities

### 2. Webhook Configuration
- Set webhook URL to: `https://your-domain.com/webhook`
- Configure authentication headers
- Set up retry policies and timeout settings

### 3. Testing Integration
- Use the `/test` endpoint to verify connectivity
- Send test messages through Telex interface
- Monitor CloudWatch logs for debugging

### 4. Production Deployment
- Deploy to AWS with production environment variables
- Configure monitoring and alerting
- Set up backup and disaster recovery

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For issues and questions:
1. Check the GitHub Issues
2. Review AWS CloudWatch logs
3. Test the `/ping` endpoint for health status
4. Verify Telex.im webhook configuration
5. Check Mistral AI API key and quotas

## 🔄 Changelog

### v1.0.0 - Telex Integration
- ✅ Telex.im webhook integration
- ✅ Mistral AI conversation engine
- ✅ Code assistance capabilities
- ✅ Text summarization features
- ✅ Health monitoring and logging
- ✅ AWS Lambda deployment
- ✅ Comprehensive error handling
- ✅ Fallback response system

---

**Built with ❤️ using FastAPI, Telex.im, AWS Lambda, and Mistral AI**