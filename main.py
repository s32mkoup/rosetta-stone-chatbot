#!/usr/bin/env python3


import sys
import argparse
import asyncio
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main entry point with argument parsing"""
    
    parser = argparse.ArgumentParser(
        description="🏺 Rosetta Stone Agent - Ancient Wisdom Meets Modern AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py cli                     # Start CLI interface
  python main.py web                     # Start web interface  
  python main.py web --port 8080         # Web on custom port
  python main.py test                    # Run diagnostics
  python main.py setup                   # Setup environment
        """
    )
    
    # Mode selection
    parser.add_argument(
        'mode',
        choices=['cli', 'web', 'api', 'test', 'setup'],
        help='Interface mode to start'
    )
    
    # Common arguments
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--user', '-u', 
        type=str,
        default='default_user',
        help='User ID for session'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    # Web interface specific
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=7860,
        help='Port for web interface (default: 7860)'
    )
    
    parser.add_argument(
        '--host',
        type=str, 
        default='127.0.0.1',
        help='Host for web interface (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--share',
        action='store_true',
        help='Create public sharing link for web interface'
    )
    
    # CLI specific
    parser.add_argument(
        '--no-color',
        action='store_true', 
        help='Disable colored output in CLI'
    )
    
    args = parser.parse_args()
    
    # Route to appropriate interface
    try:
        if args.mode == 'cli':
            start_cli_interface(args)
        elif args.mode == 'web':
            start_web_interface(args)
        elif args.mode == 'api':
            start_api_interface(args)
        elif args.mode == 'test':
            run_diagnostics(args)
        elif args.mode == 'setup':
            run_setup(args)
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye, seeker of wisdom!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def start_cli_interface(args):
    """Start the CLI interface"""
    from interfaces.cli_chat import CLIInterface
    
    print("🏺 Starting Rosetta Stone Agent - CLI Mode")
    
    cli = CLIInterface(args.config)
    
    # Apply CLI-specific settings
    if args.no_color:
        cli.colored_output = False
    if args.verbose:
        cli.verbose_mode = True
    
    # Start session
    cli.start_session(args.user)

def start_web_interface(args):
    """Start the web interface"""
    from interfaces.gradio_app import create_gradio_app
    
    print("🏺 Starting Rosetta Stone Agent - Web Mode")
    print(f"🌐 Server: http://{args.host}:{args.port}")
    
    app = create_gradio_app(
        config_file=args.config,
        share=args.share,
        server_port=args.port,
        server_name=args.host
    )
    
    app.launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        show_error=True
    )

def start_api_interface(args):
    """Start the API interface"""
    print("🚧 API interface not yet implemented")
    print("Coming in future version!")
    sys.exit(1)

def run_diagnostics(args):
    """Run system diagnostics"""
    from scripts.test_all_tools import run_all_tests
    
    print("🏺 Rosetta Stone Agent - Diagnostics")
    print("=" * 50)
    
    success = run_all_tests(args.config, args.verbose)
    
    if success:
        print("✅ All diagnostics passed!")
        sys.exit(0)
    else:
        print("❌ Some diagnostics failed!")
        sys.exit(1)

def run_setup(args):
    """Run environment setup"""
    from scripts.setup_environment import main as setup_main
    
    print("🏺 Rosetta Stone Agent - Environment Setup")
    setup_main()

if __name__ == "__main__":
    main()