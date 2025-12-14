# Copilot Instructions for xiaozhi-esp32-server

## Project Overview

**xiaozhi-esp32-server** is a comprehensive backend system for ESP32-based AI voice assistants. It integrates Python (AI engine), Java/Spring Boot (management API), Vue.js (web UI), and uni-app (mobile UI) to create a distributed voice interaction platform following "human-machine symbiosis" principles.

**Core Purpose**: Enable users to build self-hosted AI voice assistants compatible with Xiaozhi ESP32 devices with full control over AI services (ASR, LLM, TTS), device management, and IoT integration.

## Architecture & Key Components

### Component Relationships
```
ESP32 Hardware (Client)
        ↕ WebSocket (voice streaming)
xiaozhi-server (Python, Port 8000)
    ├─ VAD, ASR, LLM, TTS modules
    ├─ Plugin system for device control
    └─ MCP (Model Context Protocol) support
        ├─ Device MCP (to ESP32)
        ├─ Server MCP (to external services)
        └─ MCP Endpoint (to remote MCP servers)

manager-api (Java Spring Boot, Port 8002)
    ├─ RESTful APIs for configuration
    ├─ MySQL persistence layer
    └─ Redis caching

manager-web (Vue.js, SPA)
    └─ HTTP calls to manager-api

manager-mobile (uni-app v3 + Vue 3)
    └─ HTTP calls to manager-api
```

### Data Flow Patterns
1. **Voice Interaction Loop**: ESP32 → WebSocket → xiaozhi-server (VAD/ASR/LLM/TTS) → WebSocket → ESP32
2. **Configuration Sync**: manager-web/mobile → manager-api (HTTP) → Database/Redis, then xiaozhi-server periodically pulls config from manager-api
3. **Tool Execution**: xiaozhi-server dispatches plugin/MCP calls based on LLM function selection
4. **Device Commands**: MCP messages between xiaozhi-server and ESP32 for capability advertisement and control

## Critical Development Workflows

### Python Server (xiaozhi-server)
- **Start server**: `cd main/xiaozhi-server && python app.py`
- **Dependencies**: Check `requirements.txt` (Python 3.10 recommended due to torch/torchaudio pinning)
- **Config precedence**: `data/.config.yaml` (local override) > `config.yaml` (defaults)
- **Key modules**: `core/websocket_server.py` (WebSocket listener), `core/connection.py` (per-device handler), `plugins_func/` (plugin system)
- **Logging**: Uses loguru, configured in `config/logger.py`; output format uses custom tags via `logger.bind(tag=TAG)`

### Java API (manager-api)
- **Start**: Maven build, default port 8002
- **Build**: `mvn clean package` (JDK 21, Maven 3.8+)
- **API docs**: POST-startup at `http://localhost:8002/xiaozhi/doc.html` (Knife4j/Swagger)
- **Stack**: Spring Boot 3.4.3, MyBatis Plus, Druid, Liquibase for migrations
- **Key pattern**: RESTful endpoints serve config to both web UI and xiaozhi-server HTTP requests

### Frontend (manager-web & manager-mobile)
- **manager-web**: Standard Vue.js SPA, `npm run dev` (or equivalent)
- **manager-mobile**: uni-app v3 ecosystem
  - Dev: `pnpm install` then `pnpm dev:h5` (H5), `pnpm dev:mp-weixin` (WeChat), or HBuilderX for App
  - Config: Environment files in `env/` directory (`.env.development`, `.env.production`)
  - Critical: Set `VITE_SERVER_BASEURL` to manager-api address

### Docker Deployment
- **Single-service compose**: Use `main/xiaozhi-server/docker-compose.yml`
- **All-in-one compose**: `main/xiaozhi-server/docker-compose_all.yml` (includes MySQL, Redis, manager-api)
- **Base image**: `Dockerfile-server-base` (heavy dependencies), `Dockerfile-server` (application layer)
- **Web Dockerfile**: `Dockerfile-web` (for manager-web frontend)

## Project-Specific Conventions & Patterns

### Plugin/Function System
- **Location**: `main/xiaozhi-server/plugins_func/`
- **Pattern**: Functions must be registered via `DeviceTypeRegistry` in `register.py`
- **Types**: 
  - `ToolType.NONE` (tool call only)
  - `ToolType.WAIT` (wait for function result)
  - `ToolType.CHANGE_SYS_PROMPT` (role change)
  - `ToolType.SYSTEM_CTL` (exit, play music, etc. - needs `conn` param)
  - `ToolType.IOT_CTL` (device control - needs `conn` param)
  - `ToolType.MCP_CLIENT` (external MCP services)
- **Return**: `ActionResponse(action=Action.REQLLM, result=...)` tells LLM to process result further

### MCP (Model Context Protocol) Integration - THREE Models
1. **Device MCP** (`core/providers/tools/device_mcp/`): xiaozhi-server ↔ ESP32 capabilities
2. **Server MCP** (`core/providers/tools/server_mcp/`): xiaozhi-server → External MCP servers (via stdio/SSE)
   - Config: `data/.mcp_server_settings.json` (JSON with `mcpServers` object)
   - Example: `{"mcpServers": {"my_service": {"command": "npx", "args": ["..."]}}}`
3. **MCP Endpoint** (`core/providers/tools/mcp_endpoint/`): xiaozhi-server → Remote MCP WebSocket endpoint
   - Config: `config.yaml` key `mcp_endpoint_url`

**Critical**: Each MCP type has different client classes (`ServerMCPClient`, `MCPClient`, `MCPEndpointClient`) with different initialization flows. Executors are `ServerMCPExecutor`, `MCPExecutor`, `MCPEndpointExecutor`.

### Configuration System
- **Primary source**: `config.yaml` (all defaults documented)
- **Local overrides**: Create `data/.config.yaml` for sensitive/local settings (API keys, custom service URLs)
- **Dynamic loading**: If `read_config_from_api: true` in config, xiaozhi-server pulls config from manager-api periodically
- **Key sections**: `server`, `log`, `asr`, `llm`, `tts`, `tts_engine`, `selectedModule`, `wakeup_word_model`, `voiceprint`

### Authentication & Authorization
- **xiaozhi-server**: JWT via `server.auth_key` (config or auto-generated UUID)
- **Device whitelist**: Optional device MAC filtering in `server.auth.allowed_devices`
- **manager-api**: Shiro-based auth (see `pom.xml` for `shiro-spring`)

### Logging Conventions
- **Always use**: `logger.bind(tag=TAG).{info|debug|error}(message)` (TAG = `__name__`)
- **Color-coded console format**: Defined in config.log_format with time, level, tag
- **File logs**: Separate format in config.log_format_file
- **Directory**: Logs in `tmp/` by default, customizable via `log.log_dir`

## Integration Points & External Dependencies

### AI Service Providers
- **ASR** (Automatic Speech Recognition): FunASR, Whisper, PaddleSpeech, Vosk, etc. (configurable)
- **LLM**: OpenAI, Google Gemini, Coze, Local models (configurable in `config.yaml`)
- **TTS**: Edge TTS, Aliyun Cosynthetic, Fish Speech, PaddleSpeech, etc. (configurable)
- **Pattern**: Each service provider wrapped in provider classes under `core/providers/`

### Storage & Caching
- **MySQL** (manager-api): Device registration, user config, OTA metadata
- **Redis** (manager-api): Session caching, config caching to reduce DB hits
- **Local filesystem** (xiaozhi-server): Models in `models/`, audio temp files (deleted per config), logs in `tmp/`

### Cross-Component Communication
- **xiaozhi-server → manager-api**: HTTP GET requests for config (e.g., `/api/config/{device_id}`)
- **ESP32 ↔ xiaozhi-server**: WebSocket with JSON-RPC-like payloads (see `core/handle/` for message handling)
- **manager-web/mobile ↔ manager-api**: RESTful HTTP/JSON with Shiro auth headers

## Code Examples & Patterns

### Adding a Plugin Function
```python
# In plugins_func/register.py or plugin file
from plugins_func.register import ToolType, Action, ActionResponse

async def control_light(conn, state: str):
    """IoT function for light control"""
    # Your device control logic
    return ActionResponse(
        action=Action.RESPONSE,
        response=f"Light turned {state}"
    )

# Register in plugin loader
registry.register_function(
    name="control_light",
    description="Turn smart light on or off",
    func=control_light,
    tool_type=ToolType.IOT_CTL
)
```

### Using MCP Server Tool
```python
# In core/providers/tools/server_mcp/mcp_executor.py
executor = ServerMCPExecutor(conn)
await executor.initialize()
result = await executor.execute(conn, "mcp_weather_get", {"location": "Beijing"})
# Returns ActionResponse with action=Action.REQLLM to process result
```

### Sending WebSocket Messages to Device
```python
# In core/connection.py handler
message = json.dumps({
    "type": "mcp",
    "payload": {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "light_control", "arguments": {"action": "on"}}
    }
})
await conn.websocket.send(message)
```

## Important Files & Directories

| Path | Purpose |
|------|---------|
| `main/xiaozhi-server/app.py` | Server entry point |
| `main/xiaozhi-server/core/websocket_server.py` | WebSocket listener & message dispatcher |
| `main/xiaozhi-server/core/connection.py` | Per-device connection handler (VAD, ASR, LLM, TTS pipeline) |
| `main/xiaozhi-server/plugins_func/` | Plugin registration & execution system |
| `main/xiaozhi-server/config/` | Configuration loading & parsing |
| `main/xiaozhi-server/core/providers/` | AI service implementations (ASR, LLM, TTS) |
| `main/xiaozhi-server/core/providers/tools/` | Plugin & MCP executor implementations |
| `main/manager-api/src/main/` | Java backend (controllers, services, entities) |
| `main/manager-web/src/` | Vue.js SPA code |
| `main/manager-mobile/` | uni-app mobile app |
| `docs/mcp-*.md` | MCP integration detailed guides |
| `docker-compose.yml` / `docker-compose_all.yml` | Deployment orchestration |

## Debugging Tips

1. **WebSocket Issues**: Check `core/websocket_server.py` logging; filter suppresses "invalid handshake" errors (HTTPS→WS port mismatch common)
2. **Config Not Applied**: Verify `data/.config.yaml` syntax (YAML), check precedence (local override > default)
3. **Plugin Not Found**: Ensure registered in `plugins_func/register.py` and device type matches
4. **MCP Connection Failed**: Check `mcp_server_settings.json` path and syntax; server must be startable (stdio/SSE reachable)
5. **Performance**: Monitor VAD, ASR, LLM latency via logs; Redis caching in manager-api helps config distribution

## Known Conventions to Preserve

- **Chinese comments/docstrings**: Project maintained in Chinese; preserve for consistency
- **Async-first design**: WebSocket server, connection handlers, plugin execution all async (asyncio)
- **Config-first approach**: Heavy use of YAML; avoid hardcoding service URLs/credentials
- **Modular AI providers**: Each ASR/LLM/TTS provider is pluggable; avoid monolithic implementations
- **MCP-as-extension-point**: Tools and device capabilities exposed via MCP protocol; prefer MCP for new integrations
