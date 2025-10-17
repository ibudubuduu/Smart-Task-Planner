# Smart Task Planner

An AI-powered task planning application that breaks down user goals into actionable tasks with timelines, dependencies, and milestones using intelligent reasoning.

## Project Overview

The Smart Task Planner uses advanced language model integration to analyze user goals and automatically generate comprehensive task breakdowns with:
- Detailed task descriptions and time estimates
- Task dependencies and priority levels
- Realistic timelines and deadlines
- Project milestones and checkpoints
- Optional database storage for task persistence

## Features

### Core Functionality
- Goal input processing with natural language understanding
- Intelligent task breakdown generation
- Dependency management and priority assignment
- Timeline generation with realistic deadline estimation
- Milestone tracking for project progress

### Technical Features
- RESTful API with clean endpoint design
- SQLite database for persistent task plan storage
- Responsive web interface for goal submission and plan visualization
- Comprehensive error handling and user feedback
- Health monitoring API endpoint

## System Requirements

### Minimum Requirements
- Python 3.7 or higher
- 2GB available RAM
- 500MB free storage
- Internet connection for initial setup

### Recommended Requirements (for LLM integration)
- Python 3.8 or higher
- 8GB+ RAM (for local LLM models)
- 4GB+ free storage (for model storage)
- Multi-core processor

## Installation

### Quick Setup

1. Download all project files to a folder called `smart-task-planner`

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python run.py
```
Select option 1 to start the web application.

4. Open your browser to:
```
http://localhost:5000
```

### LLM Integration Options

The application supports three AI methods:

**Option 1: Ollama (Recommended - Best Quality)**
```bash
# Install Ollama from https://ollama.ai
# Then pull a model:
ollama pull llama2
```

**Option 2: HuggingFace Transformers (Good Quality)**
```bash
pip install transformers torch
```

**Option 3: Enhanced Fallback (Always Available)**
- No additional setup required
- Uses intelligent rule-based generation
- Works immediately after basic installation

## Usage

### Web Interface
1. Enter a goal with a timeline (e.g., "Launch a mobile app in 3 weeks")
2. Click "Generate AI Task Plan"
3. View the detailed task breakdown with dependencies and milestones

### API Endpoints

**Create Task Plan**
```
POST /api/plan
Content-Type: application/json

{
    "goal": "Launch a mobile app in 3 weeks"
}
```

**Retrieve Task Plan**
```
GET /api/plan/<plan_id>
```

**Check System Health**
```
GET /api/health
```

**Check LLM Status**
```
GET /api/llm-status
```

## Project Structure

```
smart-task-planner/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── run.py                  # Quick start launcher
├── demo.py                 # Interactive demonstration
├── test_api.py            # API testing suite
├── templates/
│   └── index.html         # Web interface
└── README.md              # This file
```

## Development

### Running Tests
```bash
# Terminal 1: Start the application
python app.py

# Terminal 2: Run tests
python test_api.py
```

### Running Demo
```bash
python demo.py
```

## Troubleshooting

**Port 5000 already in use:**
```bash
python -c "from app import app; app.run(port=8080)"
```

**Import errors:**
```bash
pip install Flask==2.3.3
python app.py
```

**Database errors:**
```bash
rm tasks.db
python app.py
```

## Technical Details

### Backend Architecture
- Flask web framework for HTTP server
- SQLite for data persistence
- Multi-tier LLM integration (Ollama/HuggingFace/Fallback)
- RESTful API design

### Frontend Technologies
- Vanilla JavaScript for interactivity
- Responsive CSS design
- Asynchronous API communication

### LLM Integration
- Automatic method detection and selection
- Graceful fallback for unavailable LLM services
- Context-aware task generation
- Pattern recognition for different goal types

## Performance

- Average response time: 2-15 seconds (depending on LLM method)
- Ollama: Best quality, 5-15 seconds
- HuggingFace: Good quality, 3-10 seconds
- Fallback: Basic quality, <2 seconds
