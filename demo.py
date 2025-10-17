#!/usr/bin/env python3
"""
Smart Task Planner Demo Script
Demonstrates LLM integration and AI-powered task generation capabilities
"""

from app import LLMTaskPlanner
import json
from datetime import datetime
import time
import sys

def print_banner():
    print("="*60)
    print("     SMART TASK PLANNER - LLM DEMO")
    print("    AI-Powered Task Generation Demo")
    print("="*60)
    print()

def print_llm_status(planner):
    """Display current LLM configuration"""
    print("AI Configuration:")
    print("-" * 40)

    method = planner.llm_method
    if method == "ollama":
        print("[ACTIVE] Using: Ollama (Best Quality)")
        print("   - Natural language AI reasoning")
        print("   - Context-aware task generation")
        print("   - High-quality dependency mapping")
    elif method == "huggingface":
        print("[ACTIVE] Using: HuggingFace Transformers (Good Quality)")
        print("   - Local transformer models")
        print("   - Structured task output")
        print("   - Offline processing")
    else:
        print("[ACTIVE] Using: Enhanced Fallback (Basic Quality)")
        print("   - Rule-based intelligent generation")
        print("   - Pattern recognition algorithms")
        print("   - Reliable task breakdown")

    print()

def print_plan_detailed(plan, plan_num, total_plans):
    """Print a comprehensive plan breakdown"""
    print(f"\n{'='*80}")
    print(f"DEMO {plan_num}/{total_plans}: AI TASK BREAKDOWN")
    print(f"{'='*80}")

    print(f"\nGOAL: {plan['goal']}")
    print(f"DURATION: {plan['estimated_duration']}")
    print(f"TIMELINE: {plan['timeline']['start_date']} to {plan['timeline']['end_date']}")
    print(f"TASKS: {len(plan['tasks'])} total")

    print("\n" + "-"*80)
    print("AI-GENERATED TASK BREAKDOWN:")
    print("-"*80)

    for task in plan['tasks']:
        priority_marker = {"High": "[HIGH]", "Medium": "[MED]", "Low": "[LOW]"}
        priority = priority_marker.get(task['priority'], "[NORMAL]")

        print(f"\n{priority} TASK {task['id']}: {task['title']}")
        print(f"   Description: {task['description']}")
        print(f"   Deadline: {task['deadline']} | Hours: {task['estimated_hours']}h")
        print(f"   Category: {task['category']} | Priority: {task['priority']}")

        if task['dependencies']:
            deps = ', '.join([f"Task {dep}" for dep in task['dependencies']])
            print(f"   Dependencies: {deps}")
        else:
            print(f"   Dependencies: None (can start immediately)")

    print("\n" + "-"*80)
    print("PROJECT MILESTONES:")
    print("-"*80)

    for milestone in plan['timeline']['milestones']:
        print(f"\n[MILESTONE] {milestone['name']}")
        print(f"   Target Date: {milestone['date']}")
        if milestone['tasks_completed']:
            completed = ', '.join([f"Task {task_id}" for task_id in milestone['tasks_completed']])
            print(f"   Tasks to Complete: {completed}")

def main():
    """Main demo orchestration"""
    print_banner()

    try:
        planner = LLMTaskPlanner()
    except Exception as e:
        print(f"[ERROR] Failed to initialize planner: {e}")
        print("Make sure all dependencies are installed.")
        return

    print("Welcome to the Smart Task Planner AI Demo!")
    print("This demonstration will show you the power of AI-driven task planning.\n")

    print_llm_status(planner)

    demo_goals = [
        "Launch a mobile app in 3 weeks",
        "Organize a team building event in 10 days",
        "Learn Python programming in 1 month",
        "Complete a research paper in 2 weeks"
    ]

    print(f"\nPRESET GOAL DEMONSTRATIONS")
    print("="*80)
    print("Watch the AI generate detailed task breakdowns for different goal types\n")

    for i, goal in enumerate(demo_goals, 1):
        print(f"\nDemo {i}/{len(demo_goals)}: Processing '{goal}'")
        print("AI analyzing goal context and requirements...")

        plan = planner.generate_task_plan(goal)
        plan_id = planner.save_plan(goal, plan)
        print(f"[INFO] Saved as Plan ID: {plan_id}")

        print_plan_detailed(plan, i, len(demo_goals))

        if i < len(demo_goals):
            input("\nPress Enter to continue to next demo...")

    print(f"\n{'='*80}")
    print("DEMO COMPLETED SUCCESSFULLY!")
    print(f"{'='*80}")

    print(f"\n[INFO] All demonstrations finished!")
    print(f"\n[INFO] AI Method Used: {planner.llm_method.upper()}")
    print(f"\nKey Takeaways:")
    print("   - AI adapts task generation based on goal context")
    print("   - Different LLM methods provide varying quality levels")
    print("   - Dependencies and timelines are intelligently calculated")
    print("   - Task descriptions are contextually relevant")
    print("   - Milestones help track project progress")

    print(f"\nReady to use the Smart Task Planner:")
    print("   1. Run: python run.py")
    print("   2. Select option 1 (Start Web Application)")
    print("   3. Open: http://localhost:5000")
    print("   4. Enter your own goals and start planning!")

    print(f"\nThank you for trying the Smart Task Planner AI Demo!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n[ERROR] Demo error: {e}")
        print("Make sure the app.py file is in the same directory and dependencies are installed.")
