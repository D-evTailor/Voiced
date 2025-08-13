flowchart TB
  %% ===== External User =====
  U["Caller / Customer\n(Phone or Web Widget)"]:::ext

  %% ===== Vapi.ai Layer =====
  subgraph VAPI["Vapi.ai Cloud"]
    TEL["Telephony + SIP (inbound/outbound)"]:::svc
    STT["TTS/STT + Call Control"]:::svc
    AGENT["Vapi Agent\n(LLM + Tool Calling,\nHooks, Error Handling,\nFallback & Async Support)"]:::svc
    WEBHK["Vapi Webhooks\n(call.started, transcript, call.ended)"]:::svc
    TEL --> STT --> AGENT
    AGENT --- WEBHK
    noteVAPI["Built‑in: function calling, async support,\nwebhook integration & error handling:contentReference[oaicite:2]{index=2}\nAssistant hooks for call events:contentReference[oaicite:3]{index=3}"]:::note
  end

  %% ===== Edge / Ingress =====
  EDGE["API Gateway / Ingress\n(HTTPS, mTLS, WAF)"]:::infra

  %% ===== Tools Adapter =====
  subgraph TOOLS["FastAPI Tools Adapter\n(thin proxy)"]
    direction TB
    TAPI["Tool Endpoints\ncheck_availability\nhold_slot (TTL)\nconfirm_booking\ncancel_booking\nget_business_info"]:::api
    WH["Webhook Receiver\n(for Vapi events if needed)"]:::api
    OBS1["Tracing / Logs / Metrics"]:::obs
    noteTools["No idempotency/rate limiting here—handled by Vapi.\nJust validate requests and forward to Domain API."]:::note
    WEBHK -- "HTTPS" --> EDGE
    EDGE -- "routes" --> WH
  end
  TAPI -- "forward call" --> DRF

  %% ===== Domain API / Core =====
  subgraph CORE["Django REST Domain API"]
    direction TB
    DRF["CRUD + Domain Endpoints\n(Business, Services, Resources,\nClients, Appointments)"]:::api
    SLOT["Availability Engine\n(buffers, exceptions, TZ, capacity)"]:::svc
    RULES["Booking Rules & Policies\n(cancel windows, overbooking, locks)"]:::svc
    NOTIF["Notification Orchestrator"]:::svc
    OBS2["Tracing / Logs / Metrics"]:::obs
    DRF --> SLOT
    DRF --> RULES
    DRF --> NOTIF
  end

  %% ===== Admin UI =====
  subgraph ADMIN["Management Frontend (React)"]
    UI["Admin UI\n(Business, Resources, Services,\nSchedules, Config)"]:::ui
  end

  %% ===== Shared Infra =====
  subgraph DATA["Platform Services"]
    direction TB
    PG[("PostgreSQL\nRLS / Transactions")]:::db
    REDIS["Redis\n(cache, slot precompute, advisory locks)"]:::cache
    MQ[("Message Broker\n(Redis/Rabbit/Kafka)")]:::mq
    WORK["Background Workers\n(Celery/RQ)"]:::svc
    OTP["OIDC / Auth Provider"]:::infra
    MAIL["Email / SMS Provider"]:::ext
    OBS["Observability Stack\n(OTel Collector, Logs, APM, Dashboards)"]:::obs
  end

  %% ===== Flows =====
  U -- "call/audio" --> TEL
  AGENT -- "tool.call HTTPS" --> EDGE
  EDGE -- "proxy" --> TAPI

  DRF <--> PG
  SLOT <--> PG
  RULES <--> PG
  DRF <--> REDIS
  SLOT <--> REDIS

  TAPI -. "uses (TTL holds, caching)" .-> REDIS
  RULES -. "row/advisory locks" .-> PG

  DRF -- "emits events" --> MQ
  WORK -- "consumes" --> MQ
  WORK --> NOTIF
  NOTIF --> MAIL

  WEBHK -- "events" --> WH
  WH --> MQ
  WH --> OBS

  UI -- "HTTPS + OIDC" --> EDGE
  EDGE -- "routes" --> DRF
  UI -. "realtime (SSE/WebSocket)" .-> DRF

  UI -- "OIDC/OpenID" --> OTP
  DRF --> OBS2
  TAPI --> OBS1
  OBS1 --> OBS
  OBS2 --> OBS

  %% ===== Styles =====
  classDef api fill:#eef,stroke:#446,stroke-width:1.2px;
  classDef svc fill:#f6fff2,stroke:#3a6,stroke-width:1.2px;
  classDef ui fill:#fff7e6,stroke:#a66,stroke-width:1.2px;
  classDef db fill:#fff,stroke:#333,stroke-width:1.4px;
  classDef cache fill:#fff,stroke:#065,stroke-width:1.2px;
  classDef mq fill:#fff,stroke:#650,stroke-width:1.2px;
  classDef obs fill:#f0f5ff,stroke:#335,stroke-width:1.2px,stroke-dasharray: 3 3;
  classDef infra fill:#f9f9f9,stroke:#777,stroke-width:1.2px,stroke-dasharray: 5 3;
  classDef ext fill:#f2f2f2,stroke:#999,stroke-width:1.2px;
  classDef note fill:#fafaf5,stroke:#999,stroke-dasharray:2 2;
