# Quick Reference: GPU-Accelerated Stack Operation

**Created**: December 13, 2025  
**Version**: 1.0.0-prototype

## Daily Operation Commands

### 1. Start All Services (3 terminals needed)

**Terminal 1: LM Studio**
```bash
# Launch LM Studio GUI app (one-click, then Load Model)
# OR run headless:
# lm-studio serve --host 0.0.0.0 --port 1234 \
#   --model mradermacher/LLaMa-3.1-Instruct-13B-GGUF
```

**Terminal 2: FishSpeech TTS Server**
```bash
cd /path/to/fish-speech
python -m fish_speech.api.inference_server --device cuda --port 8080
# Expected: "Server started on http://127.0.0.1:8080"
```

**Terminal 3: xiaozhi-server**
```bash
cd main/xiaozhi-server
source venv/bin/activate
python app.py
# Expected: "WebSocket server listening on ws://0.0.0.0:8000/xiaozhi/v1/"
```

### 2. Verify All Services Running
```bash
# Service health check script
echo "=== Checking Services ==="
echo -n "LM Studio: "
curl -s http://10.50.10.14:1234/v1/models > /dev/null && echo "✓ Running" || echo "✗ Down"

echo -n "FishSpeech: "
curl -s http://127.0.0.1:8080/health > /dev/null && echo "✓ Running" || echo "✗ Down"

echo -n "xiaozhi-server: "
curl -s http://127.0.0.1:8003/health > /dev/null && echo "✓ Running" || echo "✗ Down"

echo -n "GPU Status: "
nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader | head -1
```

### 3. Monitor GPU in Real-Time
```bash
# Watch GPU usage continuously
watch -n 1 nvidia-smi

# Or with graph
nvidia-smi -l 1  # Refresh every 1 second

# Check specific process
nvidia-smi pmon  # Shows GPU memory per process
```

### 4. Log Monitoring
```bash
# Monitor xiaozhi-server logs
tail -f main/xiaozhi-server/tmp/server.log

# Search for errors
grep "ERROR\|Exception\|Failed" main/xiaozhi-server/tmp/server.log

# Watch for device connections
tail -f main/xiaozhi-server/tmp/server.log | grep -i "connected\|device\|websocket"
```

### 5. Test Single Component

**Test ASR Only**
```bash
python -c "
from core.providers.asr.funasr_provider import FunASRProvider
asr = FunASRProvider({'model_dir': 'models/SenseVoiceSmall'})
result = asr.recognize('test_audio.wav')
print(f'Recognized: {result}')
"
```

**Test LLM Only**
```bash
curl -X POST http://10.50.10.14:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-instruct-13b",
    "messages": [{"role": "user", "content": "Who are you?"}],
    "temperature": 0.7,
    "max_tokens": 100
  }' | jq '.choices[0].message.content'
```

**Test TTS Only**
```bash
curl -X POST http://127.0.0.1:8080/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello from Tarquin",
    "reference_text": "Hi I am Tarquin your personal assistant"
  }' \
  --output /tmp/test_tts.wav && \
  ffplay /tmp/test_tts.wav  # Play audio
```

---

## Configuration Changes

### Change ASR Model (Advanced)
```yaml
# In data/.config.yaml
ASR:
  FunASR:
    model_dir: models/SenseVoiceSmall  # OR models/Paraformer-large-zh
```

### Change TTS Quality
```yaml
# In data/.config.yaml - Lower latency
TTS:
  FishSpeech:
    max_new_tokens: 512      # Was 1024 (faster)
    chunk_length: 100        # Was 200 (smaller chunks)
    streaming: true          # Keep true for low latency
    temperature: 0.5         # Was 0.7 (more stable)

# Higher quality
TTS:
  FishSpeech:
    max_new_tokens: 2048     # More tokens for better flow
    chunk_length: 300        # Larger chunks
    temperature: 0.8         # More variation
    top_p: 0.8               # More diversity
```

### Add Voice Cloning Reference
```yaml
TTS:
  FishSpeech:
    reference_audio: ["config/assets/my_voice.wav"]
    reference_text: ["Hi, I'm Tarquin, your personal AI assistant"]
```

### Change LLM Temperature (Creativity)
```yaml
LLM:
  LMStudioLLM:
    temperature: 0.3   # More focused/deterministic
    # OR
    temperature: 1.0   # More creative/random
```

---

## Performance Tuning

### For Speed (Latency)
```yaml
selected_module:
  ASR: FunASR              # Already fast, 200-500ms
  LLM: LMStudioLLM         # 1-3s, hard to optimize further
  TTS: FishSpeech          # Enable streaming: true

LLM:
  LMStudioLLM:
    max_tokens: 256        # Shorter responses = faster
    temperature: 0.3       # Less computation

TTS:
  FishSpeech:
    streaming: true        # 1-2s vs 3-5s
    max_new_tokens: 512
    chunk_length: 100
```

### For Quality (Accuracy)
```yaml
ASR:
  FunASR:
    # Already very accurate, no tuning needed

LLM:
  LMStudioLLM:
    temperature: 0.5       # More focused
    top_p: 0.8             # Quality sampling
    max_tokens: 1000       # Longer, more detailed responses

TTS:
  FishSpeech:
    streaming: false       # Slightly higher quality
    max_new_tokens: 2048
    top_p: 0.9
    temperature: 0.6       # Stable, clear speech
```

### For VRAM (Memory)
```yaml
# Reduce memory usage if getting OOM errors:

LLM:
  LMStudioLLM:
    max_tokens: 256        # Shorter max length

TTS:
  FishSpeech:
    streaming: true        # Uses less memory
    max_new_tokens: 512
    chunk_length: 100
    use_memory_cache: "off" # Disable caching

# OR switch to 8B model in LM Studio (saves 2-3GB)
```

---

## VRAM Usage Reference

**Baseline (nothing running)**
```
GPU Memory: ~0.5 GB
```

**After loading FunASR**
```
GPU Memory: ~2.5 GB
Usage: ASR inference = 200-500ms per request
```

**After loading LM Studio (13B Q6_K)**
```
GPU Memory: ~12 GB total (10GB model + overhead)
Usage: LLM inference = 1-3s per request
```

**After loading FishSpeech**
```
GPU Memory: ~16-17 GB total (peak during TTS)
Usage: TTS inference = 1-2s per request
```

**If VRAM full (>16GB):**
1. Reduce TTS quality (max_new_tokens: 512)
2. Disable streaming (set to false, trades speed for memory)
3. Use 8B LLM model instead of 13B
4. Monitor with `nvidia-smi` - if using >16GB, system RAM fills up

---

## Troubleshooting Quick Fixes

| Problem | Quick Fix | Detailed Fix |
|---------|-----------|-------------|
| ASR gibberish output | Reduce volume, clear noise | Check `min_silence_duration_ms: 200` |
| LLM slow responses | Normal for first inference | Warm up with dummy requests |
| LLM out of memory | Use 8B model instead | Switch model in LM Studio |
| TTS audio choppy | Disable streaming (false) | Increase `chunk_length: 300` |
| TTS out of memory | Set streaming: true | Reduce `max_new_tokens: 512` |
| WebSocket connection fails | Restart xiaozhi-server | Check firewall port 8000 |
| GPU not being used | Verify CUDA installed | Run `nvidia-smi` to check |
| Model download fails | Check internet | Download manually and place in `models/` |

---

## Environment Variables

```bash
# Set CUDA device (if multiple GPUs)
export CUDA_VISIBLE_DEVICES=0

# Reduce CUDA memory allocation overhead
export TF_FORCE_GPU_ALLOW_GROWTH=true

# PyTorch distributed settings
export NCCL_BLOCKING_WAIT=1

# Verify settings
echo $CUDA_VISIBLE_DEVICES
nvidia-smi  # Check which GPU is active
```

---

## Port Reference

| Service | Port | URL | Status Endpoint |
|---------|------|-----|-----------------|
| xiaozhi-server | 8000 | ws://127.0.0.1:8000/xiaozhi/v1/ | HTTP /health |
| HTTP OTA | 8003 | http://127.0.0.1:8003 | HTTP /health |
| LM Studio | 1234 | http://10.50.10.14:1234/v1 | /v1/models |
| FishSpeech | 8080 | http://127.0.0.1:8080/v1 | /health |

---

## Backup & Recovery

### Backup Configuration
```bash
# Backup your .config.yaml
cp main/xiaozhi-server/data/.config.yaml main/xiaozhi-server/data/.config.yaml.backup

# Backup logs
cp main/xiaozhi-server/tmp/server.log main/xiaozhi-server/tmp/server.log.$(date +%s)
```

### Restore Defaults
```bash
# If .config.yaml is corrupted, just delete it
rm main/xiaozhi-server/data/.config.yaml
# The system will use config.yaml defaults
```

### Clear Cache/Temp Files
```bash
# Safe to delete temp files
rm -rf main/xiaozhi-server/tmp/*.wav
rm -rf main/xiaozhi-server/tmp/*.mp3

# Keep logs for debugging
# rm -rf main/xiaozhi-server/tmp/*.log  # Usually want to keep
```

---

## Performance Benchmarking

### Run Full Stack Test
```bash
cd main/xiaozhi-server
python performance_tester.py
```

### Manual E2E Test
```bash
# 1. Record 5 second audio
ffmpeg -f pulse -i default -t 5 -acodec pcm_s16le -ar 16000 test.wav

# 2. Measure ASR latency
time python -c "
from core.providers.asr.funasr_provider import FunASRProvider
asr = FunASRProvider({'model_dir': 'models/SenseVoiceSmall'})
result = asr.recognize('test.wav')
print(result)
"

# 3. Measure LLM latency
time curl -s -X POST http://10.50.10.14:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"llama-3.1-instruct-13b","messages":[{"role":"user","content":"Say hello"}]}' \
  | jq '.choices[0].message.content'

# 4. Measure TTS latency
time curl -s -X POST http://127.0.0.1:8080/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello world"}' --output test_out.wav
```

---

## Getting Help

### Check Logs
```bash
# Error logs
grep ERROR main/xiaozhi-server/tmp/server.log | tail -20

# CUDA/GPU errors
grep -i "cuda\|gpu" main/xiaozhi-server/tmp/server.log

# Service startup
grep "listening\|started\|initialized" main/xiaozhi-server/tmp/server.log | head -20
```

### Reset Everything
```bash
# Stop all services first (Ctrl+C in each terminal)

# Clear caches
rm -rf main/xiaozhi-server/tmp/*.wav
rm -rf main/xiaozhi-server/tmp/*.mp3

# Restart from fresh
python app.py
```

---

## System Requirements Checklist

- [ ] RTX 5060 Ti detected: `nvidia-smi`
- [ ] CUDA 12 installed: `nvcc --version`
- [ ] Python 3.10: `python --version`
- [ ] PyTorch GPU: `python -c "import torch; print(torch.cuda.is_available())"`
- [ ] FFmpeg installed: `ffmpeg -version`
- [ ] 50GB free disk: `df -h`
- [ ] Ports 8000, 8003, 1234, 8080 available
- [ ] Internet for initial model download

---

## Contact & Support

For issues specific to this GPU stack configuration:
1. Check `GPU_STACK_SETUP.md` detailed guide
2. Review logs: `tail -f main/xiaozhi-server/tmp/server.log`
3. Monitor GPU: `watch -n 1 nvidia-smi`
4. Check services: Run verification script above
