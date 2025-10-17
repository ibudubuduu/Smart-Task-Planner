from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
import json
import sqlite3
from typing import List, Dict, Any
import re
import os

# LLM Integration Options
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

try:
    import requests as ollama_requests
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

app = Flask(__name__)

class LLMTaskPlanner:
    def __init__(self):
        self.init_database()
        self.llm_method = self.initialize_llm()

    def initialize_llm(self):
        '''Initialize the best available LLM method'''

        # Check for Ollama server first (recommended for local development)
        if self.check_ollama_server():
            print("[INFO] Using Ollama local LLM server")
            return "ollama"

        # For HuggingFace, we'll skip it and go straight to fallback
        # because the model quality for task planning is not good enough
        # with the lightweight models we can run locally

        # Check for Hugging Face Transformers
        # Commenting this out to use enhanced fallback instead
        # elif HF_AVAILABLE:
        #     try:
        #         model_name = "microsoft/DialoGPT-medium"
        #         print(f"[INFO] Loading Hugging Face model: {model_name}")
        #         self.hf_generator = pipeline(
        #             "text-generation", 
        #             model=model_name,
        #             tokenizer=model_name,
        #             max_length=1000,
        #             do_sample=True,
        #             temperature=0.7
        #         )
        #         return "huggingface"
        #     except Exception as e:
        #         print(f"[ERROR] Failed to load HF model: {e}")

        # Use enhanced fallback which produces better results than HuggingFace
        print("[INFO] Using enhanced rule-based system (recommended for reliability)")
        return "fallback"

    def check_ollama_server(self):
        '''Check if Ollama server is running'''
        try:
            response = ollama_requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def init_database(self):
        '''Initialize SQLite database for task storage'''
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT NOT NULL,
                plan TEXT NOT NULL,
                llm_method TEXT DEFAULT 'unknown',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def save_plan(self, goal: str, plan: Dict[str, Any]) -> int:
        '''Save the generated plan to database'''
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO task_plans (goal, plan, llm_method) VALUES (?, ?, ?)',
            (goal, json.dumps(plan), self.llm_method)
        )
        plan_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return plan_id

    def get_plan(self, plan_id: int) -> Dict[str, Any]:
        '''Retrieve a plan from database'''
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM task_plans WHERE id = ?', (plan_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'id': result[0],
                'goal': result[1],
                'plan': json.loads(result[2]),
                'llm_method': result[3],
                'created_at': result[4]
            }
        return None

    def generate_with_ollama(self, goal: str) -> Dict[str, Any]:
        '''Generate task plan using Ollama local LLM'''

        prompt = f'''You are a professional project manager. Break down this goal into actionable tasks with realistic timelines and dependencies.

Goal: "{goal}"

Please respond with a JSON object in this exact format:
{{
    "goal": "{goal}",
    "estimated_duration": "X days/weeks",
    "tasks": [
        {{
            "id": 1,
            "title": "Task name",
            "description": "Detailed description",
            "estimated_hours": X,
            "dependencies": [],
            "deadline": "YYYY-MM-DD",
            "priority": "High/Medium/Low",
            "category": "Planning/Development/Testing/Marketing/etc"
        }}
    ],
    "timeline": {{
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD",
        "milestones": [
            {{
                "name": "Milestone name",
                "date": "YYYY-MM-DD",
                "tasks_completed": [1, 2, 3]
            }}
        ]
    }}
}}

Make tasks specific, actionable, and properly sequenced. Use today's date as reference: {datetime.now().strftime("%Y-%m-%d")}'''

        try:
            response = ollama_requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama2",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                llm_response = result.get('response', '')

                try:
                    json_start = llm_response.find('{')
                    json_end = llm_response.rfind('}') + 1

                    if json_start >= 0 and json_end > json_start:
                        json_str = llm_response[json_start:json_end]
                        plan = json.loads(json_str)
                        return plan
                    else:
                        print("[WARNING] No valid JSON found in LLM response, using fallback")
                        return self.fallback_plan_generation(goal)

                except json.JSONDecodeError as e:
                    print(f"[WARNING] JSON parsing error: {e}, using fallback")
                    return self.fallback_plan_generation(goal)
            else:
                print(f"[WARNING] Ollama API error: {response.status_code}")
                return self.fallback_plan_generation(goal)

        except Exception as e:
            print(f"[WARNING] Ollama connection error: {e}")
            return self.fallback_plan_generation(goal)

    def extract_timeframe(self, goal: str) -> int:
        '''Extract time frame from goal text'''
        time_patterns = [
            (r'(\d+)\s*weeks?', lambda x: int(x) * 7),
            (r'(\d+)\s*days?', lambda x: int(x)),
            (r'(\d+)\s*months?', lambda x: int(x) * 30)
        ]

        for pattern, converter in time_patterns:
            match = re.search(pattern, goal.lower())
            if match:
                return converter(match.group(1))

        return 14  # default 2 weeks

    def generate_task_plan(self, goal: str) -> Dict[str, Any]:
        '''Generate a comprehensive task plan using the best available LLM method'''

        print(f"[INFO] Generating plan using: {self.llm_method}")

        if self.llm_method == "ollama":
            return self.generate_with_ollama(goal)
        else:
            # Use enhanced fallback for best results
            return self.fallback_plan_generation(goal)

    def fallback_plan_generation(self, goal: str) -> Dict[str, Any]:
        '''Enhanced rule-based plan generation with intelligent task breakdown'''

        total_days = self.extract_timeframe(goal)
        start_date = datetime.now()
        end_date = start_date + timedelta(days=total_days)

        goal_lower = goal.lower()
        tasks = []

        # Product/App Launch Pattern
        if any(word in goal_lower for word in ['product', 'launch', 'app', 'software', 'platform', 'mobile']):
            tasks = [
                {
                    "id": 1,
                    "title": "Market Research & User Analysis",
                    "description": "Conduct comprehensive market research to identify target audience, analyze competitors, and validate product-market fit. Gather user requirements and pain points.",
                    "estimated_hours": 16,
                    "dependencies": [],
                    "deadline": (start_date + timedelta(days=max(1, total_days//7))).strftime("%Y-%m-%d"),
                    "priority": "High",
                    "category": "Research"
                },
                {
                    "id": 2,
                    "title": "Product Requirements Documentation",
                    "description": "Create detailed product requirements document (PRD) including features, user stories, acceptance criteria, and technical specifications. Define MVP scope.",
                    "estimated_hours": 20,
                    "dependencies": [1],
                    "deadline": (start_date + timedelta(days=max(2, total_days//5))).strftime("%Y-%m-%d"),
                    "priority": "High",
                    "category": "Planning"
                },
                {
                    "id": 3,
                    "title": "UI/UX Design & Prototyping",
                    "description": "Design user interface mockups, create wireframes, develop interactive prototypes, and establish design system. Include user flow diagrams and navigation structure.",
                    "estimated_hours": 32,
                    "dependencies": [2],
                    "deadline": (start_date + timedelta(days=max(4, total_days//3))).strftime("%Y-%m-%d"),
                    "priority": "High",
                    "category": "Design"
                },
                {
                    "id": 4,
                    "title": "Backend Development & API Implementation",
                    "description": "Develop server-side logic, create RESTful APIs, implement database schema, set up authentication, and configure cloud infrastructure. Include error handling and logging.",
                    "estimated_hours": 40,
                    "dependencies": [2],
                    "deadline": (start_date + timedelta(days=max(7, int(total_days*0.6)))).strftime("%Y-%m-%d"),
                    "priority": "High",
                    "category": "Development"
                },
                {
                    "id": 5,
                    "title": "Frontend Development & Integration",
                    "description": "Build mobile app interface, implement screens from designs, integrate with backend APIs, handle state management, and optimize performance.",
                    "estimated_hours": 48,
                    "dependencies": [3, 4],
                    "deadline": (start_date + timedelta(days=max(10, int(total_days*0.7)))).strftime("%Y-%m-%d"),
                    "priority": "High",
                    "category": "Development"
                },
                {
                    "id": 6,
                    "title": "Testing & Quality Assurance",
                    "description": "Execute comprehensive testing including unit tests, integration tests, UI tests, performance testing, and security audits. Fix identified bugs and optimize code.",
                    "estimated_hours": 24,
                    "dependencies": [5],
                    "deadline": (start_date + timedelta(days=max(13, int(total_days*0.85)))).strftime("%Y-%m-%d"),
                    "priority": "High",
                    "category": "Testing"
                },
                {
                    "id": 7,
                    "title": "App Store Preparation & Submission",
                    "description": "Prepare app store listings, create screenshots and promotional materials, write descriptions, configure store settings, and submit for review.",
                    "estimated_hours": 12,
                    "dependencies": [6],
                    "deadline": (start_date + timedelta(days=max(15, int(total_days*0.9)))).strftime("%Y-%m-%d"),
                    "priority": "Medium",
                    "category": "Publishing"
                },
                {
                    "id": 8,
                    "title": "Marketing Campaign & Launch",
                    "description": "Execute marketing strategy, coordinate social media campaigns, send press releases, engage with early users, and monitor initial user feedback and analytics.",
                    "estimated_hours": 16,
                    "dependencies": [7],
                    "deadline": end_date.strftime("%Y-%m-%d"),
                    "priority": "High",
                    "category": "Marketing"
                }
            ]

        # Event Organization Pattern
        elif any(word in goal_lower for word in ['event', 'meeting', 'conference', 'workshop', 'party', 'gathering']):
            tasks = [
                {
                    "id": 1,
                    "title": "Event Concept & Planning",
                    "description": "Define event objectives, determine target audience, establish theme and format, create preliminary budget, and develop overall event strategy.",
                    "estimated_hours": 8,
                    "dependencies": [],
                    "deadline": (start_date + timedelta(days=max(1, total_days//6))).strftime("%Y-%m-%d"),
                    "priority": "High",
                    "category": "Planning"
                },
                {
                    "id": 2,
                    "title": "Venue Selection & Booking",
                    "description": "Research suitable venues, conduct site visits, evaluate capacity and amenities, negotiate contracts, and secure venue booking with required deposits.",
                    "estimated_hours": 12,
                    "dependencies": [1],
                    "deadline": (start_date + timedelta(days=max(2, total_days//4))).strftime("%Y-%m-%d"),
                    "priority": "High",
                    "category": "Logistics"
                },
                {
                    "id": 3,
                    "title": "Vendor Coordination & Services",
                    "description": "Source and book catering services, arrange AV equipment, hire photographers, coordinate with decorators, and confirm all service provider contracts.",
                    "estimated_hours": 16,
                    "dependencies": [2],
                    "deadline": (start_date + timedelta(days=max(4, total_days//2))).strftime("%Y-%m-%d"),
                    "priority": "High",
                    "category": "Logistics"
                },
                {
                    "id": 4,
                    "title": "Guest Management & Invitations",
                    "description": "Compile guest list, design and send invitations (digital/physical), track RSVPs, manage dietary requirements, and arrange seating plan.",
                    "estimated_hours": 10,
                    "dependencies": [1],
                    "deadline": (start_date + timedelta(days=max(3, int(total_days*0.4)))).strftime("%Y-%m-%d"),
                    "priority": "Medium",
                    "category": "Communications"
                },
                {
                    "id": 5,
                    "title": "Event Program & Schedule",
                    "description": "Create detailed event timeline, coordinate speakers or performers, prepare scripts or run sheets, and conduct final walkthroughs with all stakeholders.",
                    "estimated_hours": 8,
                    "dependencies": [2, 3],
                    "deadline": (start_date + timedelta(days=max(6, int(total_days*0.75)))).strftime("%Y-%m-%d"),
                    "priority": "High",
                    "category": "Planning"
                },
                {
                    "id": 6,
                    "title": "Event Execution & Management",
                    "description": "Oversee event setup, coordinate all vendors and staff, manage timeline execution, handle real-time issues, and ensure smooth event flow from start to finish.",
                    "estimated_hours": 12,
                    "dependencies": [3, 4, 5],
                    "deadline": end_date.strftime("%Y-%m-%d"),
                    "priority": "High",
                    "category": "Execution"
                }
            ]

        # Learning/Education Pattern
        elif any(word in goal_lower for word in ['learn', 'study', 'course', 'training', 'skill', 'master']):
            subject = "the subject"
            for word in goal.split():
                if word.lower() in ['python', 'java', 'javascript', 'programming', 'coding', 'data', 'science', 'machine', 'learning']:
                    subject = word.capitalize()
                    break

            tasks = [
                {
                    "id": 1,
                    "title": f"Foundation & Environment Setup for {subject}",
                    "description": f"Install necessary software and tools, set up development environment, learn basic syntax and core concepts of {subject}, and complete beginner tutorials.",
                    "estimated_hours": 12,
                    "dependencies": [],
                    "deadline": (start_date + timedelta(days=max(2, total_days//5))).strftime("%Y-%m-%d"),
                    "priority": "High",
                    "category": "Learning"
                },
                {
                    "id": 2,
                    "title": f"Intermediate Concepts & Hands-on Practice",
                    "description": f"Study intermediate {subject} concepts through structured courses, complete coding exercises and challenges, build small practice projects, and participate in coding communities.",
                    "estimated_hours": 24,
                    "dependencies": [1],
                    "deadline": (start_date + timedelta(days=max(6, int(total_days*0.6)))).strftime("%Y-%m-%d"),
                    "priority": "High",
                    "category": "Learning"
                },
                {
                    "id": 3,
                    "title": f"Advanced Topics & Real-world Applications",
                    "description": f"Explore advanced {subject} topics including best practices, design patterns, optimization techniques. Work on complex problems and study real-world code examples.",
                    "estimated_hours": 20,
                    "dependencies": [2],
                    "deadline": (start_date + timedelta(days=max(10, int(total_days*0.8)))).strftime("%Y-%m-%d"),
                    "priority": "Medium",
                    "category": "Practice"
                },
                {
                    "id": 4,
                    "title": f"Capstone Project & Portfolio Development",
                    "description": f"Design and build a comprehensive {subject} project demonstrating learned skills. Document code, create README, deploy project, and add to professional portfolio.",
                    "estimated_hours": 16,
                    "dependencies": [3],
                    "deadline": end_date.strftime("%Y-%m-%d"),
                    "priority": "High",
                    "category": "Portfolio"
                }
            ]

        # Research/Academic Pattern
        elif any(word in goal_lower for word in ['research', 'paper', 'thesis', 'study', 'analysis', 'report']):
            tasks = [
                {
                    "id": 1,
                    "title": "Topic Selection & Literature Review",
                    "description": "Define research question, conduct comprehensive literature review, identify gaps in existing research, and develop theoretical framework. Compile annotated bibliography.",
                    "estimated_hours": 20,
                    "dependencies": [],
                    "deadline": (start_date + timedelta(days=max(2, total_days//4))).strftime("%Y-%m-%d"),
                    "priority": "High",
                    "category": "Research"
                },
                {
                    "id": 2,
                    "title": "Research Methodology Design",
                    "description": "Develop research methodology, design data collection instruments, establish sampling strategy, and prepare ethics approval documentation if required.",
                    "estimated_hours": 12,
                    "dependencies": [1],
                    "deadline": (start_date + timedelta(days=max(4, total_days//3))).strftime("%Y-%m-%d"),
                    "priority": "High",
                    "category": "Planning"
                },
                {
                    "id": 3,
                    "title": "Data Collection & Analysis",
                    "description": "Execute data collection according to methodology, organize and clean data, perform statistical analysis, generate visualizations, and interpret results.",
                    "estimated_hours": 24,
                    "dependencies": [2],
                    "deadline": (start_date + timedelta(days=max(8, int(total_days*0.65)))).strftime("%Y-%m-%d"),
                    "priority": "High",
                    "category": "Research"
                },
                {
                    "id": 4,
                    "title": "Writing & Documentation",
                    "description": "Write research paper sections (introduction, methodology, results, discussion, conclusion), create tables and figures, ensure proper citations, and format according to requirements.",
                    "estimated_hours": 20,
                    "dependencies": [3],
                    "deadline": (start_date + timedelta(days=max(11, int(total_days*0.85)))).strftime("%Y-%m-%d"),
                    "priority": "High",
                    "category": "Writing"
                },
                {
                    "id": 5,
                    "title": "Review, Revision & Submission",
                    "description": "Proofread paper, incorporate peer feedback, verify citations and references, check formatting compliance, and submit final version before deadline.",
                    "estimated_hours": 12,
                    "dependencies": [4],
                    "deadline": end_date.strftime("%Y-%m-%d"),
                    "priority": "High",
                    "category": "Finalization"
                }
            ]

        # Generic Pattern for other goals
        else:
            num_tasks = max(4, min(7, total_days // 3))
            task_duration = total_days / num_tasks

            phase_templates = [
                {
                    "name": "Planning & Requirements",
                    "description": "Define objectives, gather requirements, identify stakeholders, create project plan, and establish success criteria for: {goal}",
                    "category": "Planning"
                },
                {
                    "name": "Research & Preparation",
                    "description": "Conduct necessary research, gather resources, identify potential challenges, and prepare detailed approach for executing: {goal}",
                    "category": "Research"
                },
                {
                    "name": "Implementation Phase 1",
                    "description": "Begin core execution activities, establish foundations, implement initial components, and validate approach for: {goal}",
                    "category": "Development"
                },
                {
                    "name": "Implementation Phase 2",
                    "description": "Continue development work, integrate components, address identified issues, and complete majority of work for: {goal}",
                    "category": "Development"
                },
                {
                    "name": "Testing & Quality Assurance",
                    "description": "Conduct thorough testing, verify all requirements are met, identify and fix issues, and ensure quality standards for: {goal}",
                    "category": "Testing"
                },
                {
                    "name": "Finalization & Documentation",
                    "description": "Complete remaining tasks, create necessary documentation, prepare deliverables, and finalize all aspects of: {goal}",
                    "category": "Finalization"
                },
                {
                    "name": "Delivery & Completion",
                    "description": "Deliver final output, gather feedback, ensure stakeholder satisfaction, and officially close project for: {goal}",
                    "category": "Completion"
                }
            ]

            for i in range(num_tasks):
                template = phase_templates[min(i, len(phase_templates)-1)]
                task_date = start_date + timedelta(days=int(i * task_duration))

                tasks.append({
                    "id": i + 1,
                    "title": template["name"],
                    "description": template["description"].format(goal=goal),
                    "estimated_hours": 10 + (i % 3) * 6,
                    "dependencies": [i] if i > 0 else [],
                    "deadline": task_date.strftime("%Y-%m-%d"),
                    "priority": ["High", "High", "Medium", "High", "High", "Medium", "High"][min(i, 6)],
                    "category": template["category"]
                })

        # Create meaningful milestones
        milestones = [
            {
                "name": "Project Kickoff & Planning Complete",
                "date": start_date.strftime("%Y-%m-%d"),
                "tasks_completed": []
            }
        ]

        if len(tasks) > 3:
            third_point = len(tasks) // 3
            two_third_point = (len(tasks) * 2) // 3

            milestones.append({
                "name": "Initial Phase Complete",
                "date": (start_date + timedelta(days=total_days//3)).strftime("%Y-%m-%d"),
                "tasks_completed": [task["id"] for task in tasks[:third_point]]
            })

            milestones.append({
                "name": "Development Phase Complete",
                "date": (start_date + timedelta(days=(total_days*2)//3)).strftime("%Y-%m-%d"),
                "tasks_completed": [task["id"] for task in tasks[:two_third_point]]
            })

        milestones.append({
            "name": "Project Completion & Delivery",
            "date": end_date.strftime("%Y-%m-%d"),
            "tasks_completed": [task["id"] for task in tasks]
        })

        return {
            "goal": goal,
            "estimated_duration": f"{total_days} days",
            "tasks": tasks,
            "timeline": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "milestones": milestones
            }
        }

# Initialize the LLM task planner
planner = LLMTaskPlanner()

@app.route('/')
def home():
    '''Serve the main page'''
    return render_template('index.html')

@app.route('/api/plan', methods=['POST'])
def create_plan():
    '''API endpoint to create a task plan using LLM'''
    try:
        data = request.get_json()
        goal = data.get('goal', '').strip()

        if not goal:
            return jsonify({'error': 'Goal is required'}), 400

        # Generate the task plan using LLM
        plan = planner.generate_task_plan(goal)

        # Save to database
        plan_id = planner.save_plan(goal, plan)
        plan['id'] = plan_id
        plan['llm_method'] = planner.llm_method

        return jsonify({
            'success': True,
            'plan': plan,
            'llm_method': planner.llm_method
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/plan/<int:plan_id>', methods=['GET'])
def get_plan(plan_id):
    '''API endpoint to retrieve a saved plan'''
    try:
        plan = planner.get_plan(plan_id)

        if not plan:
            return jsonify({'error': 'Plan not found'}), 404

        return jsonify({
            'success': True,
            'plan': plan
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    '''Health check endpoint with LLM status'''
    return jsonify({
        'status': 'healthy',
        'llm_method': planner.llm_method,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/llm-status', methods=['GET'])
def llm_status():
    '''Get current LLM configuration and status'''
    return jsonify({
        'current_method': planner.llm_method,
        'available_methods': {
            'ollama': planner.check_ollama_server(),
            'huggingface': HF_AVAILABLE,
            'fallback': True
        },
        'recommendations': {
            'ollama': 'Install Ollama and run: ollama pull llama2',
            'huggingface': 'Enhanced fallback provides better results for most use cases'
        }
    })

if __name__ == '__main__':
    print("Smart Task Planner with LLM Integration")
    print(f"Using method: {planner.llm_method}")

    if planner.llm_method == "fallback":
        print("\n[INFO] Using enhanced rule-based system")
        print("This provides reliable, high-quality task breakdowns")
        print("\nFor even better results, install Ollama:")
        print("   - Download from: https://ollama.ai")
        print("   - Run: ollama pull llama2")

    print(f"\nStarting server on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
