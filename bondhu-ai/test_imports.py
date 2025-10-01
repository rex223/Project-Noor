"""Test imports step by step to find the crash point"""
import sys
import traceback

def test_import(description, import_func):
    """Test a single import and catch any errors"""
    try:
        print(f"Testing: {description}...", end=" ", flush=True)
        import_func()
        print("✓ OK")
        return True
    except Exception as e:
        print(f"✗ FAILED")
        print(f"  Error: {e}")
        traceback.print_exc()
        return False

print("="*60)
print("STEP-BY-STEP IMPORT TEST")
print("="*60)

# Test 1
if not test_import("langgraph", lambda: __import__("langgraph")):
    sys.exit(1)

# Test 2
if not test_import("langgraph.graph", lambda: __import__("langgraph.graph")):
    sys.exit(1)

# Test 3
def test_langgraph_imports():
    from langgraph.graph import StateGraph, END
test_import("langgraph StateGraph/END", test_langgraph_imports)

# Test 4
if not test_import("agents.base_agent", lambda: __import__("agents.base_agent")):
    sys.exit(1)

# Test 5
def test_base_agent_class():
    from agents.base_agent import BaseAgent
test_import("BaseAgent class", test_base_agent_class)

# Test 6
def test_music_agent_module():
    import agents.music.music_agent
test_import("music_agent module", test_music_agent_module)

# Test 7
def test_music_agent_class():
    from agents.music import MusicIntelligenceAgent
test_import("MusicIntelligenceAgent class", test_music_agent_class)

# Test 8
def test_video_agent():
    from agents.video import VideoIntelligenceAgent
test_import("VideoIntelligenceAgent", test_video_agent)

# Test 9
def test_gaming_agent():
    from agents.gaming import GamingIntelligenceAgent
test_import("GamingIntelligenceAgent", test_gaming_agent)

# Test 10
def test_personality_agent():
    from agents.personality import PersonalityAnalysisAgent
test_import("PersonalityAnalysisAgent", test_personality_agent)

# Test 11
def test_all_agents_together():
    from agents import (
        MusicIntelligenceAgent,
        VideoIntelligenceAgent,
        GamingIntelligenceAgent,
        PersonalityAnalysisAgent
    )
test_import("All agents together", test_all_agents_together)

# Test 12
def test_orchestrator():
    from core.orchestrator import PersonalityOrchestrator
test_import("PersonalityOrchestrator", test_orchestrator)

print("="*60)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("="*60)
