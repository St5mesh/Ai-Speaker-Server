#!/bin/bash

# GPU Stack Health Check Script
# Created: December 13, 2025
# Version: 1.0.0-prototype
#
# Quick verification that all services are running and healthy
# Usage: ./health_check.sh

set -e

RESET='\033[0m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'

# Configuration
XIAOZHI_WS_PORT=${XIAOZHI_WS_PORT:-8000}
XIAOZHI_HTTP_PORT=${XIAOZHI_HTTP_PORT:-8003}
LM_STUDIO_PORT=${LM_STUDIO_PORT:-1234}
FISHSPEECH_PORT=${FISHSPEECH_PORT:-8080}
LM_STUDIO_IP=${LM_STUDIO_IP:-127.0.0.1}

check_count=0
pass_count=0
fail_count=0

log_check() {
    echo -e "${BLUE}[Check $((++check_count))]${RESET} $1"
}

pass() {
    echo -e "${GREEN}✓ $1${RESET}"
    ((pass_count++))
}

fail() {
    echo -e "${RED}✗ $1${RESET}"
    ((fail_count++))
}

warn() {
    echo -e "${YELLOW}⚠ $1${RESET}"
}

echo -e "${BLUE}════════════════════════════════════════════════════════${RESET}"
echo -e "${BLUE}GPU Stack Health Check${RESET}"
echo -e "${BLUE}════════════════════════════════════════════════════════${RESET}"
echo ""

# =============================================================================
# 1. GPU & CUDA Check
# =============================================================================

log_check "GPU & CUDA Detection"

if command -v nvidia-smi &> /dev/null; then
    pass "NVIDIA drivers installed"
    
    if nvidia-smi &> /dev/null; then
        pass "GPU detected"
        nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits | while read -r gpu; do
            echo "         GPU: $gpu"
        done
        
        # Check VRAM
        total_vram=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
        if [ "$total_vram" -ge 12000 ]; then
            pass "Sufficient VRAM: ${total_vram}MB (need ≥12GB for comfortable operation)"
        else
            warn "Lower VRAM: ${total_vram}MB (recommended ≥12GB)"
        fi
    else
        fail "GPU not accessible (check driver/permissions)"
    fi
else
    fail "NVIDIA drivers not installed"
fi
echo ""

# =============================================================================
# 2. Python & Dependencies Check
# =============================================================================

log_check "Python Environment"

if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    pass "Python installed: $python_version"
    
    if python3 -c "import torch; print('PyTorch version:', torch.__version__)" 2>/dev/null; then
        pass "PyTorch installed"
        
        if python3 -c "import torch; print('CUDA available:', torch.cuda.is_available())" 2>/dev/null | grep -q "True"; then
            pass "PyTorch CUDA support enabled"
        else
            warn "PyTorch CUDA not enabled (CPU mode)"
        fi
    else
        fail "PyTorch not installed (run: pip install torch torchaudio)"
    fi
    
    # Check other key dependencies
    for pkg in funasr numpy requests websockets; do
        if python3 -c "import $pkg" 2>/dev/null; then
            pass "$pkg installed"
        else
            warn "$pkg not installed"
        fi
    done
else
    fail "Python not installed"
fi
echo ""

# =============================================================================
# 3. Configuration Files Check
# =============================================================================

log_check "Configuration Files"

config_path="main/xiaozhi-server/data/.config.yaml"
if [ -f "$config_path" ]; then
    pass "GPU stack config found: $config_path"
    
    # Check key sections
    if grep -q "selected_module:" "$config_path"; then
        pass "Module selection configured"
    else
        warn "Module selection not configured"
    fi
    
    if grep -q "LMStudioLLM:" "$config_path"; then
        pass "LM Studio configured"
    else
        warn "LM Studio not configured"
    fi
    
    if grep -q "FishSpeech:" "$config_path"; then
        pass "FishSpeech configured"
    else
        warn "FishSpeech not configured"
    fi
else
    fail "GPU stack config not found at: $config_path"
fi

if [ -f "main/xiaozhi-server/config.yaml" ]; then
    pass "Default config found"
else
    warn "Default config not found"
fi
echo ""

# =============================================================================
# 4. Models Check
# =============================================================================

log_check "AI Models"

models_dir="main/xiaozhi-server/models"
if [ -d "$models_dir" ]; then
    pass "Models directory exists: $models_dir"
    
    if [ -d "$models_dir/SenseVoiceSmall" ]; then
        size=$(du -sh "$models_dir/SenseVoiceSmall" 2>/dev/null | cut -f1)
        pass "FunASR model found (SenseVoiceSmall, ~$size)"
    else
        warn "FunASR model not yet downloaded (will download on first run)"
    fi
else
    warn "Models directory not found (will be created on first run)"
fi
echo ""

# =============================================================================
# 5. Service Port Availability Check
# =============================================================================

log_check "Service Port Availability"

check_port() {
    local port=$1
    local service=$2
    local host=${3:-127.0.0.1}
    
    if timeout 2 bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null; then
        pass "$service is running on $host:$port"
    else
        warn "$service not running on $host:$port (will start when needed)"
    fi
}

check_port $XIAOZHI_WS_PORT "xiaozhi-server (WebSocket)" 127.0.0.1
check_port $XIAOZHI_HTTP_PORT "xiaozhi-server (HTTP)" 127.0.0.1
check_port $LM_STUDIO_PORT "LM Studio" "$LM_STUDIO_IP"
check_port $FISHSPEECH_PORT "FishSpeech" 127.0.0.1
echo ""

# =============================================================================
# 6. Service Health Check (if running)
# =============================================================================

log_check "Service Health Checks"

# Check xiaozhi-server
if curl -s http://127.0.0.1:$XIAOZHI_HTTP_PORT/health &>/dev/null; then
    pass "xiaozhi-server is healthy"
else
    warn "xiaozhi-server not responding (not running yet)"
fi

# Check LM Studio
if curl -s "$LM_STUDIO_IP:$LM_STUDIO_PORT/v1/models" &>/dev/null; then
    pass "LM Studio is responding"
    model=$(curl -s "$LM_STUDIO_IP:$LM_STUDIO_PORT/v1/models" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
    if [ -n "$model" ]; then
        echo "         Model loaded: $model"
    fi
else
    warn "LM Studio not responding (start in another terminal)"
fi

# Check FishSpeech
if curl -s http://127.0.0.1:$FISHSPEECH_PORT/v1/tts -X POST -H "Content-Type: application/json" -d '{"text":"test"}' &>/dev/null; then
    pass "FishSpeech is responding"
else
    warn "FishSpeech not responding (start in another terminal)"
fi
echo ""

# =============================================================================
# 7. Quick Diagnostics
# =============================================================================

log_check "Quick Diagnostics"

# CUDA environment
if echo "$CUDA_VISIBLE_DEVICES" | grep -q "[0-9]"; then
    pass "CUDA_VISIBLE_DEVICES set to: $CUDA_VISIBLE_DEVICES"
else
    if [ -z "$CUDA_VISIBLE_DEVICES" ]; then
        warn "CUDA_VISIBLE_DEVICES not set (using all available GPUs)"
    fi
fi

# Check if running in dev container
if [ -f "/.dockerenv" ]; then
    pass "Running in Docker container"
else
    pass "Running on host machine"
fi
echo ""

# =============================================================================
# Summary
# =============================================================================

echo -e "${BLUE}════════════════════════════════════════════════════════${RESET}"
echo -e "${BLUE}Summary${RESET}"
echo -e "${BLUE}════════════════════════════════════════════════════════${RESET}"

echo ""
echo -e "Checks passed: ${GREEN}$pass_count/$check_count${RESET}"
if [ $fail_count -gt 0 ]; then
    echo -e "Checks failed: ${RED}$fail_count${RESET}"
fi

echo ""

# Exit status
if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${RESET}"
    echo ""
    echo "Next steps:"
    echo "  1. Start FunASR:     cd main/xiaozhi-server && python -m funasr.bin.inference"
    echo "  2. Start LM Studio:  lm-studio  (or use the GUI)"
    echo "  3. Start xiaozhi:    cd main/xiaozhi-server && python app.py"
    echo ""
    echo "Then connect your device via WebSocket to ws://127.0.0.1:8000"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some checks failed. See warnings above.${RESET}"
    echo ""
    echo "Troubleshooting tips:"
    echo "  • Missing dependencies? Run: pip install -r main/xiaozhi-server/requirements.txt"
    echo "  • GPU not detected? Check: nvidia-smi"
    echo "  • Services won't start? Check logs: tail -f main/xiaozhi-server/tmp/xiaozhi.log"
    echo ""
    exit 1
fi
