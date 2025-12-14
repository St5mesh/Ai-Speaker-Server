# GPU Stack Pre-Flight Checklist

**Created**: December 13, 2025  
**Version**: 1.0.0-prototype  
**Estimated Time**: 10 minutes

## Before You Start: Hardware Verification

- [ ] **RTX 5060 Ti Verified**
  ```bash
  nvidia-smi
  # Should show: NVIDIA RTX 5060 Ti, 16GB VRAM
  ```

- [ ] **CUDA 12 Drivers Installed**
  ```bash
  nvidia-smi --query-gpu=driver_version --format=csv,noheader
  # Should show version 12.x or higher
  ```

- [ ] **50GB+ Free Disk Space**
  ```bash
  df -h main/xiaozhi-server/
  # Should show 50GB+ Available
  ```

- [ ] **16GB+ VRAM Available**
  ```bash
  nvidia-smi --query-gpu=memory.total --format=csv,noheader,mb
  # Should show 16000+ MB (16GB+)
  ```

- [ ] **Internet Connection** (for initial model downloads)

---

## Pre-Installation: Software Setup

- [ ] **Python 3.10+ Installed**
  ```bash
  python --version
  # Output: Python 3.10.x or 3.11.x
  ```

- [ ] **FFmpeg Installed**
  ```bash
  ffmpeg -version
  # Should show ffmpeg version info
  ```

- [ ] **pip Package Manager Updated**
  ```bash
  pip --version
  pip install --upgrade pip
  ```

---

## Before Running: File Verification

### Project Structure
- [ ] **Project Directory Exists**
  ```bash
  ls -d main/xiaozhi-server
  # Should exist without errors
  ```

- [ ] **config.yaml Exists** (Read-only reference)
  ```bash
  ls main/xiaozhi-server/config.yaml
  # Should exist
  ```

- [ ] **data/.config.yaml Created** (Your configuration)
  ```bash
  ls main/xiaozhi-server/data/.config.yaml
  # Should exist after creation
  ```

- [ ] **Models Directory Exists**
  ```bash
  ls -d main/xiaozhi-server/models
  # Should exist
  ```

### Files You Should Have Created
- [ ] `main/xiaozhi-server/data/.config.yaml` - **ESSENTIAL** (provided in GPU_STACK_SETUP.md)
- [ ] Virtual environment activated before install

---

## Setup Phase Checklist

### Step 1: Environment Setup
- [ ] Virtual environment created
  ```bash
  cd main/xiaozhi-server
  python -m venv venv
  ```

- [ ] Virtual environment activated
  ```bash
  source venv/bin/activate  # macOS/Linux
  # OR
  venv\Scripts\activate  # Windows
  ```

- [ ] Pip upgraded in venv
  ```bash
  pip install --upgrade pip
  ```

### Step 2: Install Dependencies
- [ ] PyTorch with CUDA installed
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
  # Verify: python -c "import torch; print(torch.cuda.is_available())"
  ```

- [ ] All requirements.txt installed
  ```bash
  pip install -r requirements.txt
  # Watch for any CUDA-related warnings
  ```

- [ ] FishSpeech installed
  ```bash
  pip install fish-speech
  ```

- [ ] Verify GPU availability
  ```bash
  python -c "import torch; print('CUDA Available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0))"
  # Should output: CUDA Available: True, Device: NVIDIA RTX 5060 Ti
  ```

### Step 3: Configuration
- [ ] `.config.yaml` created in `data/` directory
  ```bash
  ls main/xiaozhi-server/data/.config.yaml
  ```

- [ ] Configuration validated
  ```bash
  python validate_gpu_stack.py
  # Should show mostly green checks
  ```

- [ ] Key endpoints verified in `.config.yaml`:
  - [ ] LM Studio: `http://10.50.10.14:1234/v1`
  - [ ] FishSpeech: `http://127.0.0.1:8080/v1/tts`
  - [ ] ASR model: `models/SenseVoiceSmall`

---

## Pre-Launch: External Services

### LM Studio Setup
- [ ] LM Studio Downloaded
  - [ ] From https://lmstudio.ai/

- [ ] LLaMa 3.1 13B Model Downloaded
  - [ ] Model: `mradermacher/LLaMa-3.1-Instruct-13B-GGUF`
  - [ ] Variant: Q6_K quantization (10.71GB)
  - [ ] Stored in LM Studio models directory

- [ ] LM Studio Launched
  ```bash
  # GUI: Click LM Studio app icon
  # OR Headless: lm-studio serve --host 0.0.0.0 --port 1234
  ```

- [ ] Model Loaded in LM Studio
  - [ ] Navigate to "Local Server" tab
  - [ ] Click "Load" next to your model
  - [ ] Wait for: "Server is listening..."

- [ ] LM Studio Connectivity Verified
  ```bash
  curl http://10.50.10.14:1234/v1/models
  # Should return JSON with model info
  ```

### FishSpeech Setup
- [ ] FishSpeech Installed
  ```bash
  pip install fish-speech
  ```

- [ ] FishSpeech Server Started
  ```bash
  python -m fish_speech.api.inference_server --device cuda --port 8080
  # Wait for: "Server started on http://127.0.0.1:8080"
  ```

- [ ] FishSpeech Connectivity Verified
  ```bash
  curl http://127.0.0.1:8080/health
  # Should return: healthy or similar status
  ```

---

## Launch Phase Checklist

### Pre-Launch Verification
- [ ] Validation tool passed
  ```bash
  cd main/xiaozhi-server
  python ../../validate_gpu_stack.py
  # All checks should show green ✓
  ```

- [ ] All 3 external services running:
  - [ ] LM Studio ready (checked above)
  - [ ] FishSpeech ready (checked above)
  - [ ] xiaozhi-server about to start

- [ ] Virtual environment still activated
  ```bash
  which python  # Should show path with /venv/
  ```

### Launch Services

**Terminal 1: Start xiaozhi-server**
- [ ] Navigate to directory
  ```bash
  cd main/xiaozhi-server
  ```

- [ ] Activate venv
  ```bash
  source venv/bin/activate
  ```

- [ ] Start server
  ```bash
  python app.py
  ```

- [ ] Wait for these messages:
  - [ ] `Loading config from data/.config.yaml`
  - [ ] `Selected modules: VAD=SileroVAD, ASR=FunASR, LLM=LMStudioLLM, TTS=FishSpeech`
  - [ ] `WebSocket server listening on ws://0.0.0.0:8000/xiaozhi/v1/`
  - [ ] `HTTP server listening on http://0.0.0.0:8003`

**Terminal 2: Monitor GPU**
- [ ] GPU monitoring started
  ```bash
  watch -n 1 nvidia-smi
  # OR: nvidia-smi -l 1
  # Watch for GPU memory increasing as server starts
  ```

- [ ] Expected VRAM allocation:
  - [ ] Initial: ~0.5GB (baseline)
  - [ ] After load: ~2-3GB (FunASR + SileroVAD)
  - [ ] During inference: up to ~17GB (all models)

**Terminal 3: Monitor Logs**
- [ ] Log monitoring started
  ```bash
  tail -f main/xiaozhi-server/tmp/server.log
  # Watch for any ERROR or WARNING messages
  ```

---

## Post-Launch Verification

### Service Health Check
- [ ] xiaozhi-server responding
  ```bash
  curl http://127.0.0.1:8003/health
  # Should return: OK or 200 status
  ```

- [ ] All services verified
  ```bash
  # Run this command (or copy from GPU_QUICK_REFERENCE.md):
  echo "=== Service Check ===" && \
  echo -n "LM Studio: " && curl -s http://10.50.10.14:1234/v1/models > /dev/null && echo "✓" || echo "✗" && \
  echo -n "FishSpeech: " && curl -s http://127.0.0.1:8080/health > /dev/null && echo "✓" || echo "✗" && \
  echo -n "xiaozhi-server: " && curl -s http://127.0.0.1:8003/health > /dev/null && echo "✓" || echo "✗"
  # Should show 3 checkmarks
  ```

### Component Testing
- [ ] **ASR Test** (requires audio file)
  ```bash
  # See GPU_QUICK_REFERENCE.md for test command
  ```

- [ ] **LLM Test**
  ```bash
  curl -X POST http://10.50.10.14:1234/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"model":"llama-3.1-instruct-13b","messages":[{"role":"user","content":"Hello"}],"max_tokens":50}'
  # Should return JSON response with text
  ```

- [ ] **TTS Test**
  ```bash
  curl -X POST http://127.0.0.1:8080/v1/tts \
    -H "Content-Type: application/json" \
    -d '{"text":"Hello from Tarquin"}' \
    --output test_tts.wav
  # Should create test_tts.wav file
  # Play it: ffplay test_tts.wav
  ```

---

## Troubleshooting During Launch

### If xiaozhi-server won't start:

**Problem: `Config file not found`**
- [ ] Check file exists: `ls main/xiaozhi-server/data/.config.yaml`
- [ ] If missing, create it from template in GPU_STACK_SETUP.md
- [ ] Verify no typos in filename (exactly `.config.yaml`)

**Problem: `CUDA not available`**
- [ ] Verify GPU: `nvidia-smi` (should show your GPU)
- [ ] Check PyTorch: `python -c "import torch; print(torch.cuda.is_available())"`
- [ ] If False, reinstall torch: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`

**Problem: `ModuleNotFoundError`**
- [ ] Ensure venv activated: `which python` (should show `/venv/` in path)
- [ ] Reinstall requirements: `pip install -r requirements.txt`

**Problem: `Connection refused` for LM Studio**
- [ ] Check LM Studio running: Is window open?
- [ ] Verify model loaded: Do you see "Server is listening"?
- [ ] Test endpoint: `curl http://10.50.10.14:1234/v1/models`
- [ ] Check IP address: Replace 10.50.10.14 with your actual LM Studio machine IP

**Problem: `Connection refused` for FishSpeech**
- [ ] Check process running: `ps aux | grep fish_speech`
- [ ] Restart: Ctrl+C and run again: `python -m fish_speech.api.inference_server --device cuda --port 8080`
- [ ] Check port: `lsof -i :8080` (should show python process)

### If performance is poor:

**Problem: Slow ASR**
- [ ] Expected: 200-500ms - this is normal
- [ ] Check GPU: `nvidia-smi` (should show 20-40% utilization)
- [ ] Check logs: `grep -i asr tmp/server.log | tail -5`

**Problem: Slow LLM**
- [ ] Expected: 1-3s - this is normal for 13B model
- [ ] Check if first inference: First request always slower (~3s), then ~1-2s
- [ ] Reduce tokens: Set `max_tokens: 256` in `.config.yaml`

**Problem: Slow TTS**
- [ ] Expected: 1-2s - this is normal
- [ ] If much slower: Check GPU load with `nvidia-smi`
- [ ] Reduce quality: Set `streaming: false` (trades speed for quality)

---

## Ongoing Operations Checklist

### Daily Startup
- [ ] [ ] Activate venv
  ```bash
  cd main/xiaozhi-server && source venv/bin/activate
  ```

- [ ] [ ] Start LM Studio (GUI or CLI)
- [ ] [ ] Start FishSpeech
  ```bash
  python -m fish_speech.api.inference_server --device cuda --port 8080
  ```

- [ ] [ ] Start xiaozhi-server
  ```bash
  python app.py
  ```

- [ ] [ ] Monitor GPU in separate terminal
  ```bash
  nvidia-smi -l 1
  ```

### Health Monitoring
- [ ] Check logs for errors
  ```bash
  grep ERROR tmp/server.log
  ```

- [ ] Monitor VRAM usage
  ```bash
  nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader
  ```

- [ ] Verify services every hour
  ```bash
  curl -s http://127.0.0.1:8003/health
  ```

### Weekly Maintenance
- [ ] Clean temp audio files
  ```bash
  rm main/xiaozhi-server/tmp/*.wav
  ```

- [ ] Archive old logs
  ```bash
  mv main/xiaozhi-server/tmp/server.log main/xiaozhi-server/tmp/server.log.$(date +%Y%m%d)
  ```

- [ ] Run validation check
  ```bash
  python validate_gpu_stack.py
  ```

---

## Success Criteria

You'll know everything is working when:

✅ **xiaozhi-server** shows:
- "WebSocket server listening on ws://0.0.0.0:8000/xiaozhi/v1/"
- "HTTP server listening on http://0.0.0.0:8003"
- No ERROR messages in logs

✅ **GPU Monitor** shows:
- FunASR using ~2-3GB VRAM
- LM Studio using ~10GB VRAM  
- FishSpeech using ~4-6GB VRAM during TTS
- Total GPU load: 30-80% during inference

✅ **Service Tests** pass:
- LM Studio: Returns model list
- FishSpeech: Returns health status
- xiaozhi-server: Responds to curl request

✅ **Component Tests** work:
- ASR: Recognizes speech correctly
- LLM: Generates coherent responses
- TTS: Produces clear audio

---

## Files You Need

Before starting, ensure you have:

1. **Configuration**
   ```bash
   main/xiaozhi-server/data/.config.yaml
   ```
   Created from template in GPU_STACK_SETUP.md

2. **Documentation** (for reference)
   - `GPU_STACK_SETUP.md` - Detailed setup
   - `GPU_QUICK_REFERENCE.md` - Daily operations
   - `GPU_STACK_SUMMARY.md` - Overview

3. **Tools**
   - `validate_gpu_stack.py` - Validation tool

4. **Application**
   - `main/xiaozhi-server/app.py` - Start the server
   - `main/xiaozhi-server/requirements.txt` - Install deps

---

## Quick Help Links

- **Setup Issues**: See GPU_STACK_SETUP.md → Troubleshooting section
- **Daily Operations**: See GPU_QUICK_REFERENCE.md
- **Architecture**: See .github/copilot-instructions.md
- **Performance**: See GPU_STACK_SETUP.md → Performance Metrics

---

## Ready to Launch?

✅ **Before you start, please complete all items in this checklist**

When ready:
1. Activate terminal 1: Start LM Studio
2. Activate terminal 2: Start FishSpeech  
3. Activate terminal 3: Start xiaozhi-server
4. Activate terminal 4: Monitor with `nvidia-smi -l 1`
5. Watch logs for "listening" messages
6. Run validation to confirm all services
7. Test a simple query end-to-end
8. Monitor VRAM with `nvidia-smi`

**Congratulations! You now have a fully local, GPU-accelerated AI voice assistant! 🚀**

---

**Questions?** Check GPU_QUICK_REFERENCE.md troubleshooting table first.
**Need details?** Consult GPU_STACK_SETUP.md step-by-step guide.
**Architecture curious?** Read GPU_STACK_SUMMARY.md overview.
