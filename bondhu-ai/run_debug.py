"""
Debug wrapper to catch any startup errors
"""
import sys
import traceback
import faulthandler

# Enable faulthandler to catch segfaults
faulthandler.enable()

print("=" * 80)
print("BONDHU AI DEBUG STARTUP")
print("=" * 80)

try:
    print("\n[1/5] Importing main module...")
    import main
    print("      SUCCESS: main module imported")
    
    print("\n[2/5] Checking if __name__ == '__main__' block exists...")
    if hasattr(main, '__name__'):
        print("      SUCCESS: Module name:", main.__name__)
    
    print("\n[3/5] Importing uvicorn...")
    import uvicorn
    print("      SUCCESS: uvicorn imported")
    
    print("\n[4/5] Getting configuration...")
    from core import get_config
    config = get_config()
    print(f"      SUCCESS: Config loaded - Host: {config.api_host}, Port: {config.api_port}")
    
    print("\n[5/5] Starting FastAPI server...")
    print("=" * 80)
    print(f"Starting server at http://{config.api_host}:{config.api_port}")
    print("Press CTRL+C to stop")
    print("=" * 80)
    print()
    
    # Run uvicorn
    uvicorn.run(
        "main:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.api_debug,
        log_level="info"
    )
    
except KeyboardInterrupt:
    print("\n\nServer stopped by user (CTRL+C)")
    sys.exit(0)
    
except ImportError as e:
    print("\n" + "=" * 80)
    print("IMPORT ERROR DETECTED")
    print("=" * 80)
    print(f"Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    print("\n" + "=" * 80)
    sys.exit(1)
    
except Exception as e:
    print("\n" + "=" * 80)
    print("STARTUP ERROR DETECTED")
    print("=" * 80)
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    print("\n" + "=" * 80)
    sys.exit(1)
