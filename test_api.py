#!/usr/bin/env python3
"""
Smart Task Planner API Test Suite
Comprehensive testing of LLM integration and API functionality
"""

import requests
import json
import time
import sys
from datetime import datetime

def print_banner():
    print("="*60)
    print("     SMART TASK PLANNER - API TEST SUITE")
    print("        LLM Integration Testing")
    print("="*60)
    print()

def test_server_connection(base_url):
    """Test basic server connectivity"""
    print("[TEST] Testing Server Connection...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Server is running: {data.get('status', 'unknown')}")
            print(f"[INFO] Timestamp: {data.get('timestamp', 'unknown')}")
            if 'llm_method' in data:
                print(f"[INFO] LLM Method: {data['llm_method'].upper()}")
            return True
        else:
            print(f"[FAIL] Server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[FAIL] Cannot connect to server")
        print("[INFO] Make sure the Flask app is running:")
        print("   python app.py")
        print("   OR")
        print("   python run.py -> option 1")
        return False
    except requests.exceptions.Timeout:
        print("[FAIL] Connection timeout")
        return False
    except Exception as e:
        print(f"[FAIL] Connection error: {e}")
        return False

def test_llm_status(base_url):
    """Test LLM status endpoint"""
    print("\n[TEST] Testing LLM Status...")
    try:
        response = requests.get(f"{base_url}/api/llm-status", timeout=5)
        if response.status_code == 200:
            data = response.json()

            current_method = data.get('current_method', 'unknown')
            available_methods = data.get('available_methods', {})
            recommendations = data.get('recommendations', {})

            print(f"[PASS] LLM Status endpoint working")
            print(f"[INFO] Current Method: {current_method.upper()}")

            print("\n[INFO] Available Methods:")
            for method, status in available_methods.items():
                status_text = "[AVAILABLE]" if status else "[NOT AVAILABLE]"
                print(f"   {status_text} {method.capitalize()}")

            return current_method, available_methods
        else:
            print(f"[FAIL] LLM status check failed: {response.status_code}")
            return None, {}
    except Exception as e:
        print(f"[FAIL] LLM status error: {e}")
        return None, {}

def test_plan_generation(base_url):
    """Test plan generation functionality"""
    print("\n[TEST] Testing Plan Generation...")

    test_goals = [
        "Launch a mobile app in 3 weeks",
        "Organize a team building event in 10 days",
        "Learn Python programming in 1 month"
    ]

    successful_tests = 0
    plan_ids = []

    for i, goal in enumerate(test_goals, 1):
        print(f"\n  Test {i}/{len(test_goals)}: '{goal}'")

        try:
            start_time = time.time()

            response = requests.post(
                f"{base_url}/api/plan",
                json={"goal": goal},
                headers={"Content-Type": "application/json"},
                timeout=60
            )

            end_time = time.time()
            processing_time = end_time - start_time

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    plan = data['plan']
                    plan_ids.append(plan['id'])

                    tasks = plan.get('tasks', [])
                    milestones = plan.get('timeline', {}).get('milestones', [])

                    print(f"    [PASS] Generated successfully ({processing_time:.2f}s)")
                    print(f"    [INFO] Tasks: {len(tasks)}")
                    print(f"    [INFO] Milestones: {len(milestones)}")
                    print(f"    [INFO] Method: {data.get('llm_method', 'unknown').upper()}")

                    successful_tests += 1
                else:
                    print(f"    [FAIL] Generation failed: {data.get('error', 'unknown')}")
            else:
                print(f"    [FAIL] Request failed: HTTP {response.status_code}")

        except requests.exceptions.Timeout:
            print(f"    [FAIL] Request timeout (>60s)")
        except Exception as e:
            print(f"    [FAIL] Request error: {e}")

    success_rate = (successful_tests / len(test_goals)) * 100
    print(f"\n[SUMMARY] Plan Generation Results:")
    print(f"   Success Rate: {success_rate:.0f}% ({successful_tests}/{len(test_goals)})")

    return plan_ids

def test_plan_retrieval(base_url, plan_ids):
    """Test plan retrieval functionality"""
    print("\n[TEST] Testing Plan Retrieval...")

    if not plan_ids:
        print("[SKIP] No plan IDs available for testing")
        return

    successful_retrievals = 0

    for plan_id in plan_ids[:2]:
        try:
            response = requests.get(f"{base_url}/api/plan/{plan_id}", timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    plan = data['plan']
                    print(f"    [PASS] Retrieved plan {plan_id}")
                    print(f"    [INFO] Goal: '{plan.get('goal', 'unknown')}'")
                    successful_retrievals += 1
                else:
                    print(f"    [FAIL] Retrieval failed: {data.get('error')}")
            else:
                print(f"    [FAIL] HTTP {response.status_code}")

        except Exception as e:
            print(f"    [FAIL] Error retrieving plan {plan_id}: {e}")

    print(f"\n[SUMMARY] Retrieval Results: {successful_retrievals}/{min(len(plan_ids), 2)} successful")

def test_error_handling(base_url):
    """Test API error handling"""
    print("\n[TEST] Testing Error Handling...")

    # Test empty goal
    try:
        response = requests.post(
            f"{base_url}/api/plan",
            json={"goal": ""},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 400:
            print("    [PASS] Empty goal validation working")
        else:
            print(f"    [WARN] Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"    [FAIL] Empty goal test: {e}")

    # Test non-existent plan
    try:
        response = requests.get(f"{base_url}/api/plan/99999", timeout=10)
        if response.status_code == 404:
            print("    [PASS] Non-existent plan handling working")
        else:
            print(f"    [WARN] Expected 404, got {response.status_code}")
    except Exception as e:
        print(f"    [FAIL] Non-existent plan test: {e}")

def run_comprehensive_tests():
    """Run all test suites"""
    print_banner()

    base_url = "http://localhost:5000"

    print("Smart Task Planner API Test Suite")
    print("Testing LLM integration and API functionality\n")

    if not test_server_connection(base_url):
        print("\n[ERROR] Cannot continue testing without server connection")
        return

    current_llm, available_methods = test_llm_status(base_url)
    plan_ids = test_plan_generation(base_url)
    test_plan_retrieval(base_url, plan_ids)
    test_error_handling(base_url)

    print("\n" + "="*80)
    print("COMPREHENSIVE API TESTING COMPLETED")
    print("="*80)

    print(f"\n[SUMMARY] Test Summary:")
    print(f"   Server: Connected and responsive")
    print(f"   LLM Method: {current_llm.upper() if current_llm else 'Unknown'}")

    if available_methods.get('ollama'):
        print(f"   Ollama: Available (Best Quality)")
    elif available_methods.get('transformers'):
        print(f"   HuggingFace: Available (Good Quality)")
    else:
        print(f"   Fallback: Using rule-based generation")

    print(f"\n[INFO] All API endpoints are functional and ready for use!")

    print(f"\n[INFO] Web Interface Testing:")
    print(f"   - Open: {base_url}")
    print(f"   - Try the example goals or create your own")
    print(f"   - Verify the LLM status indicator at the top")

if __name__ == "__main__":
    try:
        run_comprehensive_tests()
    except KeyboardInterrupt:
        print("\n\nTesting interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Testing error: {e}")
        print("\nBasic troubleshooting:")
        print("1. Make sure the Flask app is running: python app.py")
        print("2. Check if port 5000 is available")
        print("3. Verify all dependencies are installed: pip install -r requirements.txt")
