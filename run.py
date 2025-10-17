#!/usr/bin/env python3
"""
Smart Task Planner - Quick Start Script
Supports LLM integration and provides comprehensive startup options
"""

import subprocess
import sys
import os
import time

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = {
        'flask': 'Flask==2.3.3',
        'flask_cors': 'flask-cors==4.0.0'
    }

    optional_packages = {
        'transformers': 'transformers>=4.30.0',
        'torch': 'torch>=2.0.0',
        'requests': 'requests>=2.31.0'
    }

    missing_required = []
    missing_optional = []

    for package, version in required_packages.items():
        try:
            if package == 'flask_cors':
                import flask_cors
            else:
                __import__(package)
        except ImportError:
            missing_required.append(version)

    for package, version in optional_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_optional.append(version)

    return missing_required, missing_optional

def check_llm_status():
    """Check available LLM methods"""
    llm_status = {
        'ollama': False,
        'transformers': False,
        'fallback': True
    }

    # Check Ollama
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        llm_status['ollama'] = response.status_code == 200
    except:
        pass

    # Check Transformers
    try:
        import transformers
        import torch
        llm_status['transformers'] = True
    except:
        pass

    return llm_status

def print_banner():
    print("="*50)
    print("     SMART TASK PLANNER")
    print("    Enhanced LLM Version")
    print("="*50)
    print()

def print_llm_status():
    print("AI/LLM Status Check:")
    print("-" * 40)

    llm_status = check_llm_status()

    if llm_status['ollama']:
        print("[OK] Ollama: Available (Best Quality)")
        try:
            import requests
            models = requests.get("http://localhost:11434/api/tags").json()
            if models.get('models'):
                print(f"   Models: {len(models['models'])} installed")
            else:
                print("   [WARNING] No models found. Run: ollama pull llama2")
        except:
            print("   [WARNING] Connection issues")
    else:
        print("[INFO] Ollama: Not available")
        print("   To install: https://ollama.ai")

    if llm_status['transformers']:
        print("[OK] HuggingFace: Available (Good Quality)")
        try:
            import torch
            if torch.cuda.is_available():
                print("   GPU acceleration available")
            else:
                print("   Using CPU (slower but works)")
        except:
            print("   [WARNING] Limited functionality")
    else:
        print("[INFO] HuggingFace: Not available")
        print("   To install: pip install transformers torch")

    print("[OK] Fallback: Always available (Basic Quality)")
    print("   Enhanced rule-based task generation")
    print()

def main():
    print_banner()

    missing_required, missing_optional = check_dependencies()

    if missing_required:
        print("[ERROR] Missing required packages:")
        for package in missing_required:
            print(f"   - {package}")
        print("\nInstall with: pip install -r requirements.txt")
        print("Or minimal install: pip install Flask==2.3.3")
        return

    print("[OK] Core dependencies satisfied!")

    if missing_optional:
        print("\n[WARNING] Optional LLM packages missing:")
        for package in missing_optional:
            print(f"   - {package}")
        print("   To install: pip install -r requirements.txt")

    print()
    print_llm_status()

    print("Available options:")
    print("1. Start Web Application (recommended)")
    print("2. Run API Tests") 
    print("3. Run Interactive Demo")
    print("4. Check System Status")
    print("5. LLM Setup Assistant")
    print("6. Show Help")
    print("7. Quick Launch (minimal)")

    while True:
        choice = input("\nEnter your choice (1-7): ").strip()

        if choice == '1':
            print("\nStarting web application...")
            print("Application will be available at: http://localhost:5000")
            print("LLM method will be auto-detected and displayed")
            print("Press Ctrl+C to stop the server")
            print("-" * 50)
            try:
                from app import app
                app.run(debug=True, host='0.0.0.0', port=5000)
            except KeyboardInterrupt:
                print("\n\nServer stopped. Goodbye!")
            except ImportError as e:
                print(f"\n[ERROR] Cannot import app: {e}")
                print("Make sure app.py is in the current directory")
            break

        elif choice == '2':
            print("\nRunning API tests...")
            print("[WARNING] Make sure the web app is running in another terminal!")
            input("Press Enter when ready, or Ctrl+C to cancel...")
            try:
                subprocess.run([sys.executable, 'test_api.py'])
            except FileNotFoundError:
                print("[ERROR] test_api.py not found")
            except KeyboardInterrupt:
                print("\n[ERROR] Test cancelled")
            break

        elif choice == '3':
            print("\nStarting interactive demo...")
            try:
                subprocess.run([sys.executable, 'demo.py'])
            except FileNotFoundError:
                print("[ERROR] demo.py not found")
            break

        elif choice == '4':
            print("\nSystem Status Check:")
            print("=" * 50)

            # Check file existence
            required_files = ['app.py', 'requirements.txt', 'templates/index.html']
            for file in required_files:
                if os.path.exists(file):
                    print(f"[OK] {file}")
                else:
                    print(f"[ERROR] {file} - Missing!")

            # Check dependencies again
            missing_req, missing_opt = check_dependencies()
            if not missing_req:
                print("[OK] Required dependencies installed")
            else:
                print(f"[ERROR] Missing: {', '.join(missing_req)}")

            # LLM status
            print_llm_status()

            # Test app import
            try:
                from app import LLMTaskPlanner
                planner = LLMTaskPlanner()
                print(f"[OK] App loads successfully (LLM method: {planner.llm_method})")
            except Exception as e:
                print(f"[ERROR] App import failed: {e}")

            input("\nPress Enter to return to menu...")
            continue

        elif choice == '5':
            print("\nLLM Setup Assistant:")
            print("=" * 50)

            llm_status = check_llm_status()

            print("\nCurrent Status:")
            print(f"   Ollama: {'[OK]' if llm_status['ollama'] else '[NOT AVAILABLE]'}")
            print(f"   HuggingFace: {'[OK]' if llm_status['transformers'] else '[NOT AVAILABLE]'}")
            print(f"   Fallback: [OK]")

            print("\nSetup Options:")
            print("\n1. Ollama (Recommended - Best Quality):")
            print("   - Download from: https://ollama.ai")
            print("   - Install, then run: ollama pull llama2")
            print("   - Automatic startup on most systems")

            print("\n2. HuggingFace Transformers (Good Quality):")
            print("   - Run: pip install transformers torch")
            print("   - Models download automatically on first use")
            print("   - Works offline after initial setup")

            print("\n3. Enhanced Fallback (Always Available):")
            print("   - No additional setup required")
            print("   - Uses intelligent rule-based generation")
            print("   - Provides good quality task breakdowns")

            print("\nRecommendation:")
            if not llm_status['ollama'] and not llm_status['transformers']:
                print("   Install Ollama for best results, or HuggingFace for good local AI")
            elif not llm_status['ollama']:
                print("   Consider installing Ollama for even better task generation")
            else:
                print("   Your setup is optimal! Ollama provides the best quality.")

            input("\nPress Enter to return to menu...")
            continue

        elif choice == '6':
            show_help()
            continue

        elif choice == '7':
            print("\nQuick Launch (minimal dependencies)...")
            try:
                import flask
                from app import app
                print("[OK] Starting with basic features...")
                app.run(debug=False, host='127.0.0.1', port=5000)
            except ImportError:
                print("[ERROR] Flask not installed. Run: pip install Flask==2.3.3")
            except Exception as e:
                print(f"[ERROR]: {e}")
            break

        else:
            print("[ERROR] Invalid choice. Please select 1-7.")

def show_help():
    print("\nSmart Task Planner Help")
    print("=" * 40)
    print("\nWhat is Smart Task Planner?")
    print("An AI-powered application that breaks down your goals into actionable")
    print("tasks with timelines, dependencies, and milestones using LLM reasoning.")

    print("\nQuick Start:")
    print("1. Make sure you have Python 3.7+ installed")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run this script: python run.py")
    print("4. Choose option 1 to start the web app")
    print("5. Open http://localhost:5000 in your browser")

    print("\nProject Files:")
    print("- app.py: Main Flask application with LLM integration")
    print("- templates/index.html: Advanced web interface")
    print("- requirements.txt: Python dependencies")
    print("- demo.py: Interactive command-line demo")
    print("- test_api.py: API testing script")
    print("- README.md: Comprehensive documentation")

    print("\nLLM Integration:")
    print("- Ollama (Best): Natural AI reasoning with local models")
    print("- HuggingFace (Good): Transformer models with local processing")
    print("- Fallback (Basic): Enhanced rule-based intelligent generation")

    print("\nExample Goals to Try:")
    print("- 'Launch a mobile app in 3 weeks'")
    print("- 'Learn Python programming in 1 month'")
    print("- 'Organize a team building event in 10 days'")
    print("- 'Complete a research paper in 2 weeks'")
    print("- 'Plan a wedding in 6 months'")

    print("\nTroubleshooting:")
    print("- Check system status (option 4)")
    print("- Try quick launch (option 7)")
    print("- Install minimal: pip install Flask==2.3.3")
    print("- Check SETUP_GUIDE.md for detailed help")

    input("\nPress Enter to return to menu...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        print("Try running with: python app.py")
