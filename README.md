# 🚀 JIRA AI Testcase Generator

An AI-powered service that automatically generates BDD test cases from JIRA tickets using local Ollama models.

---

## ✨ Features

- 🤖 **AI-Powered**: Uses local Ollama (`llama3`) for test case generation  
- 📝 **BDD Format**: Generates Given/When/Then scenarios  
- 🌐 **Web UI**: Simple interface for JIRA integration  
- 🐳 **Docker Ready**: Single container deployment  
- 📥 **Export**: Download test cases as text files  
- ⚡ **Fast**: Optimized for quick generation  

---

## 🚀 Quick Start

### 🔧 Prerequisites

- Docker & Docker Compose  
- Ollama running locally with `llama3` model  

---

### 1️⃣ Start Ollama

```bash
# Install and start Ollama
ollama serve

# Pull llama3 model
ollama pull llama3

2️⃣ Run the Application
# Clone repository
git clone <your-repo-url>
cd jira-ai-testcase-generator

# Start application
docker-compose up --build

👉 Access the UI at:
http://localhost:8000

3️⃣ Configure and Use
Open http://localhost:8000
Enter your JIRA base URL (e.g., https://yourcompany.atlassian.net
)
Enter your email and API token
Enter a JIRA issue ID (e.g., PROJ-123)
Click Generate Test Cases
Download the BDD test cases
🤝 Sharing with Your Team
Option 1: Docker Hub (Recommended)
# Tag image
docker tag jira-ai-testcase-generator:latest yourusername/jira-ai-testcase-generator:latest

# Push to Docker Hub
docker push yourusername/jira-ai-testcase-generator:latest

Team members can run:

docker run -p 8000:8000 yourusername/jira-ai-testcase-generator:latest
Option 2: Docker Compose Bundle

Share the following files:

docker-compose.yml
Dockerfile
requirements.txt
app/

Run:

docker-compose up --build
Option 3: Source Code Bundle

Zip and share the project.

Requirements:

Docker installed
Ollama running locally with llama3
⚙️ Configuration
Environment Variables
Variable	Default	Description
OLLAMA_HOST	http://host.docker.internal:11434
	Ollama server URL
PORT	8000	Application port
🔑 JIRA API Token

Create an API token here:
https://id.atlassian.com/manage-profile/security/api-tokens

🔌 API Endpoints
Method	Endpoint	Description
GET	/	Web UI
GET	/health	Health check
GET	/generate	Generate from JIRA (query params)
POST	/generate-testcases	Generate from text requirement
GET	/download	Download BDD test cases
📌 Example Usage
🔹 Direct API Call
curl "http://localhost:8000/generate?base_url=https://company.atlassian.net&email=user@company.com&token=YOUR_TOKEN&issue=PROJ-123"
🔹 Generate from Text
curl -X POST http://localhost:8000/generate-testcases \
-H "Content-Type: application/json" \
-d '{"requirement": "User login functionality"}'
🏗️ Architecture
jira-ai-testcase-generator/
├── app/
│   └── main.py              # FastAPI application
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Docker image configuration
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
🧠 Tech Stack
Backend: FastAPI (Python)
AI: Ollama (llama3)
Frontend: HTML + JavaScript
Containerization: Docker
Test Format: BDD (Given/When/Then)
🛠️ Troubleshooting
Common Issues

1. Ollama Connection Timeout

Check if running: ollama list
Verify model: ollama show llama3

2. Docker Issues

Rebuild: docker-compose up --build
Logs: docker-compose logs

3. JIRA API Errors

Verify API token permissions
Ensure correct JIRA URL (no /browse)
💻 Development
Local Setup
pip install -r requirements.txt
python app/main.py
🔧 Customization
Modify prompts in app/main.py
Update UI in HTML template
Add new API endpoints
📄 License

MIT License — free to use and modify.
