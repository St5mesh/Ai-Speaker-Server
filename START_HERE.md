# 🚀 GPU-Accelerated Stack: START HERE

**Created**: December 13, 2025  
**Version**: 1.0.0-prototype

Welcome to your fully local, GPU-accelerated AI voice assistant stack! This page helps you choose the right guide.

## ⏱️ Pick Your Path

### 👀 I Want the 5-Minute Overview
**Read**: [GPU-Accelerated Stack Quick Start](GPU_ACCELERATED_STACK_README.md)
- What you have
- Quick-start commands (3 terminals)
- Performance metrics
- Common issues

**Time**: 5 minutes

---

### ✅ I Want to Verify Everything Works
**Read**: [GPU Stack Pre-Flight Checklist](PRE_FLIGHT_CHECKLIST.md)
- Hardware verification (nvidia-smi, GPU memory)
- Python & CUDA setup check
- Configuration file validation
- Service port verification
- Success criteria

**Time**: 10 minutes  
**Then Run**: `python validate_gpu_stack.py`

---

### 🛠️ I Want Full Setup Instructions
**Read**: [Complete GPU-Accelerated Stack Setup Guide](GPU_STACK_SETUP.md)
- Detailed prerequisites
- FunASR configuration (GPU ASR)
- LM Studio setup (Local LLM)
- FishSpeech setup (GPU TTS)
- xiaozhi-server configuration
- Troubleshooting deep-dive
- Production deployment options

**Time**: 60 minutes

---

### 📚 I Want Technical Details
**Read**: [GPU Stack Implementation Summary](GPU_STACK_SUMMARY.md)
- Architecture overview with diagrams
- Component specifications
- Performance metrics & VRAM usage
- File structure reference
- Service port mappings

**Time**: 15 minutes

---

### 🎯 I Want Daily Operations Reference
**Read**: [GPU Stack Quick Reference](GPU_QUICK_REFERENCE.md)
- Start all services (3-terminal setup)
- Health check commands
- Performance monitoring
- Tuning parameters
- Troubleshooting quick-fix table

**Time**: 10 minutes (reference only)

---

## 🎬 Fastest Path to Running

If you just want to **get it working RIGHT NOW**:

```bash
# 1. Verify your setup
python validate_gpu_stack.py

# 2. Start FunASR (Terminal 1)
cd /path/to/funasr && python -m funasr.bin.inference

# 3. Start LM Studio (Terminal 2)
lm-studio  # or: /path/to/lm-studio-headless

# 4. Start xiaozhi-server (Terminal 3)
cd main/xiaozhi-server && python app.py

# 5. Connect device via WebSocket to ws://127.0.0.1:8000
```

Expected performance:
- **ASR**: 200-500ms (FunASR GPU)
- **LLM**: 1-3s (LM Studio 13B Q6K)
- **TTS**: 1-2s (FishSpeech streaming)
- **E2E Latency**: 2.2-5.7 seconds

Peak VRAM: ~17GB across FunASR (2-3GB) + LM Studio (10GB) + FishSpeech (4-6GB)

---

## 📋 What's Included

| Component | Purpose | File |
|-----------|---------|------|
| **Configuration** | Pre-tuned for RTX 5060 Ti | `main/xiaozhi-server/data/.config.yaml` |
| **Validator Tool** | Setup verification | `validate_gpu_stack.py` |
| **Quick Start** | 5-minute overview | `GPU_ACCELERATED_STACK_README.md` |
| **Checklist** | Pre-flight verification | `PRE_FLIGHT_CHECKLIST.md` |
| **Setup Guide** | Complete 60-min walkthrough | `GPU_STACK_SETUP.md` |
| **Quick Reference** | Daily operations cheat sheet | `GPU_QUICK_REFERENCE.md` |
| **Summary** | Technical architecture | `GPU_STACK_SUMMARY.md` |
| **This Guide** | Navigation & paths | `START_HERE.md` |

---

## ❓ Troubleshooting

**Can't decide which guide?**
- 🏃 In a hurry? → Quick Start (5 min)
- 🤔 Not sure if it works? → Pre-Flight Checklist (10 min)
- 🔧 Want to set up properly? → Full Setup Guide (60 min)

**Something broken?**
- Check [GPU Stack Quick Reference](GPU_QUICK_REFERENCE.md#-troubleshooting) for common fixes
- Run `python validate_gpu_stack.py` to diagnose
- Review [GPU Stack Setup Guide Troubleshooting](GPU_STACK_SETUP.md#troubleshooting-deep-dive) for detailed help

**Need more context?**
- See [IMPLEMENTATION_INDEX.md](IMPLEMENTATION_INDEX.md) for complete file navigation
- See [Copilot Instructions](.github/copilot-instructions.md) for system architecture details

---

## 💡 Key Configuration

Your setup uses:
- **ASR**: FunASR (2-3GB VRAM, 95%+ accuracy)
- **LLM**: LM Studio with LLaMA 3.1 13B Q6K (~10GB VRAM)
- **TTS**: FishSpeech (4-6GB VRAM, voice cloning capable)
- **Memory**: Local private memory (no cloud)
- **Intent**: LLM function calling

⚠️ **Important**: Update the LM Studio URL in `.config.yaml` if running on a different machine:
```yaml
LLM:
  LMStudioLLM:
    url: http://YOUR_LM_STUDIO_IP:1234/v1  # Change to your machine
```

---

## ✨ Next Steps

1. **Run the validator**: `python validate_gpu_stack.py`
2. **Pick a guide** based on time available (see above)
3. **Start the 3 services** following your chosen guide
4. **Test with your device** via WebSocket

**Questions?** Check [GPU_QUICK_REFERENCE.md](GPU_QUICK_REFERENCE.md) first—most issues are covered there.

Good luck! 🚀
