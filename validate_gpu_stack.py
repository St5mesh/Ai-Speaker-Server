#!/usr/bin/env python3
"""
GPU Stack Configuration Validator
Checks if all components are properly configured and ready to run

Usage:
    python validate_gpu_stack.py           # Normal mode
    python validate_gpu_stack.py --verbose # Detailed error messages
"""

import os
import sys
import subprocess
import json
import argparse
from pathlib import Path
from typing import Tuple, List

class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Global configuration
verbose = False

def print_header(text):
    print(f"\n{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}")
    print(f"{Color.BOLD}{Color.BLUE}{text:^60}{Color.RESET}")
    print(f"{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}\n")

def print_success(text):
    print(f"{Color.GREEN}✓{Color.RESET} {text}")

def print_error(text):
    print(f"{Color.RED}✗{Color.RESET} {text}")

def print_warning(text):
    print(f"{Color.YELLOW}⚠{Color.RESET} {text}")

def print_info(text):
    print(f"{Color.BLUE}ℹ{Color.RESET} {text}")

def print_verbose(text):
    """Only print if verbose mode is enabled"""
    if verbose:
        print(f"{Color.BLUE}  → {text}{Color.RESET}")

def run_command(cmd: str, silent=False) -> Tuple[bool, str]:
    """Run a shell command and return success status and output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
            print_verbose(f"Command failed: {cmd}")
            print_verbose(f"Error: {error_msg}")
            return False, error_msg
    except subprocess.TimeoutExpired:
        print_verbose(f"Command timed out: {cmd}")
        return False, "Command timed out"
    except Exception as e:
        print_verbose(f"Exception running command: {cmd}")
        print_verbose(f"Exception: {str(e)}")esult.stdout.strip()
        else:
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)

def check_python() -> bool:
    """Check Python version"""
    success, output = run_command("python --version")
    if success:
        print_success(f"Python: {output}")
        return True
    else:
        print_error(f"Python check failed: {output}")
        return False

def check_cuda() -> bool:
    """Check CUDA availability"""
    success, output = run_command("nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1")
    if success:
        print_success(f"NVIDIA Driver: {output}")
        
        # Check PyTorch CUDA
        torch_success, torch_output = run_command(
            'python -c "import torch; print(f\'CUDA Available: {torch.cuda.is_available()}\'); print(f\'CUDA Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \\\"N/A\\\"}\');"'
        )
        if torch_success:
            print_success(f"PyTorch: {torch_output.replace(chr(10), ' | ')}")
            return True
        else:
            print_warning("PyTorch CUDA might not be properly configured")
            return False
    else:
        print_error("NVIDIA GPU not detected or nvidia-smi not found")
        return False

def check_gpu_memory() -> bool:
    """Check available GPU memory"""
    success, output = run_command(
        "nvidia-smi --query-gpu=memory.total --format=csv,noheader,mb | head -1"
    )
    if success:
        try:
            mem_mb = int(output)
            mem_gb = mem_mb / 1024
            if mem_gb >= 16:
                print_success(f"GPU Memory: {mem_gb:.1f}GB (Excellent for RTX 5060 Ti)")
                return True
            else:
                print_error(f"GPU Memory: {mem_gb:.1f}GB (Insufficient, need 16GB+)")
                return False
        except:
            print_error(f"Could not parse GPU memory: {output}")
            return False
    else:
        print_error(f"GPU memory check failed: {output}")
        return False

def check_ffmpeg() -> bool:
    """Check FFmpeg installation"""
    success, output = run_command("ffmpeg -version | head -1")
    if success:
        print_success(f"FFmpeg: {output}")
        return True
    else:
        print_warning("FFmpeg not found - audio processing may fail")
        return False

def check_project_structure() -> bool:
    """Check if required project directories exist"""
    base_path = Path("main/xiaozhi-server")
    required_dirs = [
        "core",
        "plugins_func",
        "config",
        "models",
        "data"
    ]
    
    all_exist = True
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists():
            print_success(f"Directory: {dir_name}/")
        else:
            print_error(f"Directory: {dir_name}/ (MISSING)")
            all_exist = False
    
    return all_exist

def check_config_file() -> bool:
    """Check if .config.yaml exists"""
    config_path = Path("main/xiaozhi-server/data/.config.yaml")
    if config_path.exists():
        print_success(f"Config file: .config.yaml (found)")
        
        # Check for key configurations
        with open(config_path, 'r') as f:
            content = f.read()
             configured", "LMStudioLLM:" in content and "url:" in content),
            ("FishSpeech endpoint configured", "FishSpeech:" in content and "api_url:
            ("FunASR", "ASR: FunASR" in content),
            ("LMStudioLLM", "LMStudioLLM:" in content),
            ("FishSpeech", "FishSpeech:" in content),
            ("mem_local_short", "mem_local_short:" in content),
            ("LM Studio endpoint", "http://10.50.10.14:1234" in content),
            ("FishSpeech endpoint", "http://127.0.0.1:8080" in content),
        ]
        
        all_configured = True
        for check_name, result in checks:
            if result:
                print_success(f"  - {check_name} configured")
            else:
                print_warning(f"  - {check_name} not configured")
                all_configured = False
        
        return all_configured
    else:
        print_error("Config file: .config.yaml (NOT FOUND)")
        print_info("Please create main/xiaozhi-server/data/.config.yaml")
        return False

def check_model_files() -> bool:
    """Check if required model files exist"""
    models_to_check = [
        ("FunASR", "main/xiaozhi-server/models/SenseVoiceSmall/model.pt"),
        ("SileroVAD", "main/xiaozhi-server/models/snakers4_silero-vad"),
    ]
    
    all_exist = True
    for model_name, model_path in models_to_check:
        path = Path(model_path)
        if path.exists():
            if path.is_file():
                size_mb = path.stat().st_size / (1024*1024)
                print_success(f"Model: {model_name} ({size_mb:.1f}MB)")
            else:
                print_success(f"Model: {model_name} (directory)")
        else:
            print_warning(f"Model: {model_name} (will be auto-downloaded)")
    
    # Try common LM Studio endpoints
    endpoints = [
        "http://127.0.0.1:1234/v1/models",
        "http://localhost:1234/v1/models",
    ]
    
    for endpoint in endpoints:
        success, output = run_command(f'curl -s --connect-timeout 2 {endpoint}')
        if success and ("data" in output or "error" not in output.lower()):
            print_success(f"LM Studio: Connected ({endpoint.rsplit('/', 1)[0]})")
            if success and "data" in output:
                try:
                    models = json.loads(output)
                    if models.get("data"):
                        print_verbose(f"  Loaded models: {[m.get('id', 'unknown') for m in models['data'][:3]]}")
                except:
                    pass
            return True
        else:
    
    success, output = run_command(
        'curl -s --connect-timeout 2 http://127.0.0.1:8080/v1/tts'
    )
    if success or "error" in output.lower() and "Connection refused" not in output:
        print_success("FishSpeech: Connected (http://127.0.0.1:8080)")
        return True
    else:
        print_warning("FishSpeech: Not responding on http://127.0.0.1:8080")
        print_info("  • Ensure FishSpeech is installed: pip install fish-speech")
        print_info("  • Start TTS server: python -m fish_speech.api.inference_server --device cuda --port 8080")
        print_info("  • Or from fish-speech repo: python -m fish_speech.api.inference
    else:
        print_warning("LM Studio: Not responding (ensure it's running)")
        print_info("Start LM Studio and load model, then try again")
        return False

def check_fishspeech_connection() -> bool:
    """Check if FishSpeech is reachable"""
    print_info("Checking FishSpeech TTS server...")
    success, output = run_command(
        'curl -s http://127.0.0.1:8080/health'
    )
    if success:
        print_success("FishSpeech: Connected (http://127.0.0.1:8080)")
        return True
    else:
        print_warning("FishSpeech: Not responding (ensure it's running)")
        print_info("Start FishSpeech server: python -m fish_speech.api.inference_server --device cuda --port 8080")
        return False

def check_dependencies() -> bool:
    """Check if required Python packages are installed"""
    required_packages = [
        ("torch", "PyTorch"),
        ("torchaudio", "torchaudio"),
        ("funasr", "FunASR"),
        ("mcp", "MCP Protocol"),
    ]
    
    all_installed = True
    for package_name, display_name in required_packages:
        success, _ = run_command(f'python -c "import {package_name}"')
        if success:
            print_success(f"Package: {display_name}")
        else:
            print_error(f"Package: {display_name} (NOT INSTALLED)")
            all_installed = False
    
    return all_installed

def check_disk_space() -> bool:
    """Check available disk space"""
    success, output = run_command("df -BG main/xiaozhi-server | tail -1 | awk '{print $4}'")
    if success:
        try:
            space_gb = int(output.rstrip('G'))
            if space_gb >= 50:
                print_success(f"Disk space: {space_gb}GB available (sufficient)")
                return True
            else:
                print_warning(f"Disk space: {space_gb}GB available (recommend 50GB+)")
                return False
        except:
            print_warning(f"Could not parse disk space: {output}")
            return False
    else:
        print_warning("Could not check disk space")
        return False

def check_ports() -> bool:
    """Check if required ports are available"""
    ports = [
        (8000, "xiaozhi-server WebSocket"),
        (8003, "xiaozhi-server HTTP"),
        (1234, "LM Studio"),
        (8080, "FishSpeech"),
    ]
    
    all_available = True
    for port, service in ports:
        success, _ = run_command(f"nc -zv 127.0.0.1 {port} 2>/dev/null || timeout 1 bash -c 'echo >/dev/tcp/127.0.0.1/{port}' 2>/dev/null")
        if success:
            print_info(f" (in 3 separate terminals):")
        print("  Terminal 1 - LM Studio:")
        print("    lm-studio  # GUI, or headless variant")
        print("    # Then load model: llama-3.1-instruct-13b or similar")
        print()
        print("  Terminal 2 - FishSpeech TTS:")
        print("    python -m fish_speech.api.inference_server --device cuda --port 8080")
        print()
        print("  Terminal 3 - xiaozhi-server:")
        print("    cd main/xiaozhi-server && python app.py")
        print()
        print("  Then connect your ESP32 device via WebSocket to: ws://127.0.0.1:8000")
        print()
        print("Monitor performance:")
        print("  nvidia-smi  # Check GPU usage in real-time")
    else:
        print(f"{Color.YELLOW}{Color.BOLD}⚠ Some checks failed. Please review above.{Color.RESET}\n")
        print("Troubleshooting:")
        print("  1. Missing packages?")
        print("     pip install -r main/xiaozhi-server/requirements.txt")
        print()
        print("  2. Services won't start?")
        print("     cd main/xiaozhi-server && tail -f tmp/xiaozhi.log")
        print()
        print("  3. Still stuck?")
        print("     python validate_gpu_stack.py --verbose")
        print("     # Then check the detailed error messages above v)
    failed = total - passed
    
    global verbose
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="GPU Stack Configuration Validator")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose error output")
    args = parser.parse_args()
    verbose = args.verbose
    
    print_header("GPU Stack Configuration Validator")
    print("RTX 5060 Ti 16GB - FunASR + LM Studio + FishSpeech")
    if verbose:
        print(f"{Color.YELLOW}Verbose mode enabled{Color.RESET}")
    print(
    print(f"{Color.RED}Failed: {failed}{Color.RESET}\n")
    
    if failed == 0:
        print(f"{Color.GREEN}{Color.BOLD}✓ All checks passed! System is ready.{Color.RESET}\n")
        print("Next steps:")
        print("1. Start LM Studio (load your 13B model)")
        print("2. Start FishSpeech: python -m fish_speech.api.inference_server --device cuda --port 8080")
        print("3. Start xiaozhi-server: cd main/xiaozhi-server && python app.py")
        print("4. Monitor GPU: nvidia-smi")
    else:
        print(f"{Color.YELLOW}{Color.BOLD}⚠ Some checks failed. Please review above.{Color.RESET}\n")
        print("Recommended fixes:")
        print("1. Install missing packages: pip install -r main/xiaozhi-server/requirements.txt")
        print("2. Start required services (LM Studio, FishSpeech)")
        print("3. Verify configuration in main/xiaozhi-server/data/.config.yaml")
        print("4. Check GPU drivers: nvidia-smi")

def main():
    print_header("GPU Stack Configuration Validator")
    print("RTX 5060 Ti 16GB - FunASR + LM Studio + FishSpeech\n")
    
    results = {}
    
    # System checks
    print(f"{Color.BOLD}System Requirements{Color.RESET}")
    results["Python"] = check_python()
    results["CUDA/GPU"] = check_cuda()
    results["GPU Memory"] = check_gpu_memory()
    results["FFmpeg"] = check_ffmpeg()
    results["Disk Space"] = check_disk_space()
    
    # Project structure
    print(f"\n{Color.BOLD}Project Structure{Color.RESET}")
    results["Project Structure"] = check_project_structure()
    results["Configuration"] = check_config_file()
    results["Models"] = check_model_files()
    
    # Python dependencies
    print(f"\n{Color.BOLD}Python Dependencies{Color.RESET}")
    results["Dependencies"] = check_dependencies()
    
    # Service checks
    print(f"\n{Color.BOLD}Service Connectivity{Color.RESET}")
    results["LM Studio"] = check_lm_studio_connection()
    results["FishSpeech"] = check_fishspeech_connection()
    results["Ports"] = check_ports()
    
    # Generate report
    generate_report(results)
    
    # Exit code
    failed = sum(1 for v in results.values() if not v)
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()
