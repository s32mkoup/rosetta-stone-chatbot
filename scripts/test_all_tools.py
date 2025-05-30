#!/usr/bin/env python3
"""
Test all tools and components of the Rosetta Stone Agent
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_basic_imports():
    """Test basic package imports"""
    print("🧪 Testing basic imports...")
    
    try:
        from core.config import Config, get_config
        print("✅ Core config import successful")
    except ImportError as e:
        print(f"❌ Core config import failed: {e}")
        return False
    
    try:
        from core.agent import RosettaStoneAgent
        print("✅ Core agent import successful")
    except ImportError as e:
        print(f"❌ Core agent import failed: {e}")
        return False
    
    try:
        from persona.rosetta_persona import RosettaPersona
        print("✅ Persona import successful")
    except ImportError as e:
        print(f"❌ Persona import failed: {e}")
        return False
    
    return True

def test_tool_imports():
    """Test tool imports"""
    print("\n🛠️ Testing tool imports...")
    
    tools_to_test = [
        ("tools.wikipedia_tool", "WikipediaTool"),
        ("tools.egyptian_tool", "EgyptianKnowledgeTool"),
        ("tools.historical_tool", "HistoricalTimelineTool"),
        ("tools.translation_tool", "TranslationTool")
    ]
    
    success_count = 0
    
    for module_name, class_name in tools_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            tool_class = getattr(module, class_name)
            print(f"✅ {class_name} import successful")
            success_count += 1
        except ImportError as e:
            print(f"❌ {class_name} import failed: {e}")
        except AttributeError as e:
            print(f"❌ {class_name} class not found: {e}")
    
    return success_count == len(tools_to_test)

def test_tool_registry():
    """Test tool registry functionality"""
    print("\n🗂️ Testing tool registry...")
    
    try:
        from tools.tool_registry import get_tool_registry
        from core.config import get_config
        
        config = get_config()
        registry = get_tool_registry(config)
        
        print(f"✅ Tool registry created with {len(registry.tools)} tools")
        
        # Test tool registration
        available_tools = list(registry.tools.keys())
        print(f"📋 Available tools: {', '.join(available_tools)}")
        
        return len(registry.tools) > 0
        
    except Exception as e:
        print(f"❌ Tool registry test failed: {e}")
        return False

def test_agent_initialization():
    """Test agent initialization"""
    print("\n🤖 Testing agent initialization...")
    
    try:
        from core.agent import RosettaStoneAgent
        from core.config import get_config
        
        config = get_config()
        
        # Mock the HF_TOKEN for testing
        if not config.llm.hf_token or config.llm.hf_token == "hf_your_token_here":
            print("⚠️ No HF_TOKEN set, using mock token for testing")
            config.llm.hf_token = "hf_mock_token_for_testing"
        
        try:
            agent = RosettaStoneAgent(config)
            print("✅ Agent initialized successfully")
            
            # Test agent status
            status = agent.get_agent_status()
            print(f"📊 Agent status: {status['framework']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Agent initialization failed: {e}")
            print("💡 This might be due to missing HF_TOKEN or network issues")
            return False
        
    except ImportError as e:
        print(f"❌ Agent import failed: {e}")
        return False

def test_interface_imports():
    """Test interface imports"""
    print("\n🖥️ Testing interface imports...")
    
    success_count = 0
    
    try:
        from interfaces.cli_chat import CLIInterface
        print("✅ CLI interface import successful")
        success_count += 1
    except ImportError as e:
        print(f"❌ CLI interface import failed: {e}")
    
    try:
        from interfaces.gradio_app import GradioInterface
        print("✅ Gradio interface import successful")
        success_count += 1
    except ImportError as e:
        print(f"❌ Gradio interface import failed: {e}")
    
    return success_count >= 1  # At least one interface should work

def test_framework_imports():
    """Test framework imports (optional)"""
    print("\n🧮 Testing framework imports (optional)...")
    
    frameworks = [
        ("frameworks.smolagents_impl", "SmolAgentsFramework"),
        ("frameworks.llamaindex_impl", "LlamaIndexFramework"), 
        ("frameworks.langgraph_impl", "LangGraphFramework")
    ]
    
    working_frameworks = 0
    
    for module_name, class_name in frameworks:
        try:
            module = __import__(module_name, fromlist=[class_name])
            framework_class = getattr(module, class_name)
            print(f"✅ {class_name} available")
            working_frameworks += 1
        except ImportError as e:
            print(f"⚠️ {class_name} not available: {e}")
        except AttributeError as e:
            print(f"⚠️ {class_name} class not found: {e}")
    
    print(f"📊 {working_frameworks}/3 frameworks available")
    return True  # Frameworks are optional

def test_configuration():
    """Test configuration loading"""
    print("\n⚙️ Testing configuration...")
    
    try:
        from core.config import Config
        
        # Test default config
        config = Config()
        print("✅ Default configuration loaded")
        
        # Test config validation
        config.validate_all()
        print("✅ Configuration validation passed")
        
        # Print some config info
        print(f"📋 Model: {config.llm.model_name}")
        print(f"📋 Provider: {config.llm.provider}")
        print(f"📋 Framework: {config.agent.framework.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def run_all_tests(config_file=None, verbose=False):
    """Run all tests and return success status"""
    
    print("🏺 Rosetta Stone Agent - Diagnostic Tests")
    print("=" * 60)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Configuration", test_configuration),
        ("Tool Imports", test_tool_imports),
        ("Tool Registry", test_tool_registry),
        ("Interface Imports", test_interface_imports),
        ("Framework Imports", test_framework_imports),
        ("Agent Initialization", test_agent_initialization)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        
        try:
            success = test_func()
            if success:
                passed_tests += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"💥 {test_name} CRASHED: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! The Rosetta Stone Agent is ready!")
        return True
    elif passed_tests >= total_tests * 0.7:  # 70% pass rate
        print("⚠️ Most tests passed. Agent should work with some limitations.")
        return True
    else:
        print("❌ Many tests failed. Please check your installation.")
        return False

def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Rosetta Stone Agent components")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    success = run_all_tests(args.config, args.verbose)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()