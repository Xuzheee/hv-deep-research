import type { HistoryReport, ReportData, ProgressStep } from "./types";

// ── GPT-4o Completed Report ────────────────────────────────────────────────
const gpt4oReport: ReportData = {
  report_id: "rpt_20260508_gpt4o_x7a9",
  topic: "GPT-4o",
  subject: "GPT-4o",
  subject_type: "product",
  title: "GPT-4o: Multimodal Flagship Product Analysis",
  subtitle: "OpenAI's omni-architecture model — positioning, evolution, and competitive landscape",
  quality_warning: false,
  quality_issues: [],
  quality_score: 91,
  source_count: 28,
  evidence_count: 47,
  generated_at: "2026-05-08T09:14:23Z",
  limitations: [
    "Pricing data may have changed post-retrieval window",
    "Internal benchmark results not independently verifiable",
  ],
  narrative_report: {
    title: "GPT-4o Deep Narrative",
    one_sentence_definition:
      "GPT-4o is OpenAI's multimodal flagship that combines real-time interaction with broad consumer distribution.",
    opening_judgment:
      "Its competitive position comes less from pure model leadership than from how OpenAI bundled capability, access, and workflow fit.",
    vertical_story: [
      {
        section_id: "narrative_v_01",
        title: "From text scaling to native multimodality",
        content:
          "GPT-4o follows a multi-year path from text-only scaling to a joint audio-image-text model that removed the latency and fragmentation of older pipelines.",
        supporting_evidence_ids: ["ev_001", "ev_002"],
      },
      {
        section_id: "narrative_v_02",
        title: "Distribution became the product moat",
        content:
          "Free-tier access and chat-first packaging turned the model into a consumer surface as much as a technical one.",
        supporting_evidence_ids: ["ev_003", "ev_012"],
      },
    ],
    horizontal_comparison: [
      {
        section_id: "narrative_h_01",
        title: "Balanced general-purpose tier",
        content:
          "GPT-4o sits between premium reasoning systems and cost-optimized variants, where distribution and ecosystem fit matter more than benchmark dominance.",
        supporting_evidence_ids: ["ev_030", "ev_031"],
      },
    ],
    intersection_insights: [
      {
        section_id: "narrative_i_01",
        title: "Architecture shaped positioning",
        content:
          "The same choices that improved access and multimodality also defined the competitive frame around balanced performance and consumer reach.",
        supporting_evidence_ids: ["ev_001", "ev_003", "ev_030"],
      },
    ],
    future_scenarios: {
      most_likely:
        "GPT-4o stays the mainstream default while specialized reasoning and open-source options absorb adjacent workloads.",
      most_dangerous:
        "Competitors match the user experience while offering better economics, reducing the value of GPT-4o's distribution advantage.",
      most_optimistic:
        "GPT-4o becomes the default interaction layer for multimodal knowledge work across consumer and enterprise use cases.",
      supporting_evidence_ids: ["ev_003", "ev_030", "ev_054"],
    },
    source_notes: [
      "OpenAI release notes and launch coverage",
      "Competitive positioning derived from the report's strongest evidence cards",
    ],
  },
  overview: {
    product_overview:
      "GPT-4o (\"omni\") is OpenAI's flagship multimodal large language model, released in May 2024. It unifies text, audio, and image modalities within a single end-to-end trained model—a structural departure from the previous GPT-4 Turbo architecture which processed modalities via separate pipelines. GPT-4o achieves text and code performance on par with GPT-4 Turbo while adding real-time voice interaction with sub-300ms latency and native vision understanding. As of Q1 2026, GPT-4o remains the primary production model powering ChatGPT's free tier, with over 100 million daily active users. It represents OpenAI's strategy of combining frontier capability with accessible distribution.",
    key_findings: [
      {
        finding_id: "kf_01",
        title: "Native omni-architecture enables real-time voice at <300ms latency",
        content:
          "Unlike GPT-4 Turbo which chained Whisper → GPT-4 → TTS, GPT-4o processes audio natively end-to-end. This eliminates the pipeline bottleneck and enables emotional responsiveness, allowing the model to detect and respond to tone, laughter, and pacing. Advanced Voice Mode became generally available in September 2024.",
        confidence: "high",
        supporting_evidence_ids: ["ev_001", "ev_002", "ev_008"],
      },
      {
        finding_id: "kf_02",
        title: "Free-tier access drove 3× user growth but compressed margin",
        content:
          "Making GPT-4o available on ChatGPT's free tier tripled daily active users in Q3 2024 but required significant infrastructure investment. OpenAI reported compute costs outpacing revenue growth in that quarter, though API pricing remained stable at $5/M input tokens.",
        confidence: "high",
        supporting_evidence_ids: ["ev_003", "ev_012"],
      },
      {
        finding_id: "kf_03",
        title: "GPT-4o mini introduced July 2024 as 85% cost reduction variant",
        content:
          "GPT-4o mini was positioned for high-volume, latency-sensitive use cases. At $0.15/M input tokens (vs $5/M for GPT-4o), it immediately displaced GPT-3.5 Turbo in most developer workflows. It achieves 82% of GPT-4o benchmark performance at 3% of the cost.",
        confidence: "high",
        supporting_evidence_ids: ["ev_004", "ev_015"],
      },
      {
        finding_id: "kf_04",
        title: "128K context window with 4K default output creates deployment tradeoffs",
        content:
          "The 128K context window enables long-document processing but the 4K default output limit constrains long-form generation tasks. Developers must explicitly request higher output limits. This creates a friction point compared to Claude 3.5 which defaults to 8K output tokens.",
        confidence: "medium",
        supporting_evidence_ids: ["ev_005", "ev_019"],
      },
      {
        finding_id: "kf_05",
        title: "Structured Outputs (August 2024) became key enterprise adoption driver",
        content:
          "Guaranteed JSON schema compliance via constrained decoding removed the primary integration barrier for enterprise developers. Post-launch surveys showed 62% of enterprise API users cited Structured Outputs as a reason to standardize on GPT-4o.",
        confidence: "medium",
        supporting_evidence_ids: ["ev_006", "ev_021"],
      },
    ],
    release_updates: [
      {
        update_id: "ru_01",
        date: "2024-05-13",
        title: "GPT-4o General Availability",
        content:
          "Initial public release with text, vision, and limited audio capabilities. ChatGPT free tier received GPT-4o access with rate limits. API pricing set at $5/M input, $15/M output tokens.",
        update_type: "product_launch",
        source_url: "https://openai.com/blog/hello-gpt-4o",
        confidence: "high",
      },
      {
        update_id: "ru_02",
        date: "2024-07-18",
        title: "GPT-4o mini Released",
        content:
          "Lightweight variant launched at $0.15/M input tokens. Replaced GPT-3.5 Turbo as the default model for most free-tier interactions.",
        update_type: "product_launch",
        source_url: "https://openai.com/blog/gpt-4o-mini",
        confidence: "high",
      },
      {
        update_id: "ru_03",
        date: "2024-08-06",
        title: "Structured Outputs API Feature",
        content:
          "Guaranteed JSON schema compliance via constrained decoding. Eliminated parsing errors in production pipelines and became a key enterprise adoption accelerator.",
        update_type: "feature_update",
        source_url: "https://openai.com/blog/introducing-structured-outputs",
        confidence: "high",
      },
      {
        update_id: "ru_04",
        date: "2024-09-24",
        title: "Advanced Voice Mode General Availability",
        content:
          "Real-time voice interaction with emotional responsiveness, multi-language support, and custom voice personas rolled out globally to ChatGPT Plus subscribers.",
        update_type: "feature_update",
        source_url: null,
        confidence: "high",
      },
      {
        update_id: "ru_05",
        date: "2024-11-01",
        title: "Canvas Collaborative Editing",
        content:
          "GPT-4o with Canvas introduced as a document co-editing interface, directly competing with Notion AI and Google Docs AI features for productivity workflows.",
        update_type: "feature_update",
        source_url: null,
        confidence: "high",
      },
      {
        update_id: "ru_06",
        date: "2025-02-14",
        title: "GPT-4o Image Generation Upgrade",
        content:
          "Integrated native image generation capabilities (previously DALL-E 3 separately) directly into GPT-4o conversations. Significant improvement in photorealism and instruction following.",
        update_type: "feature_update",
        source_url: null,
        confidence: "high",
      },
    ],
    evidence_groups: [
      {
        group_id: "eg_01",
        label: "Official OpenAI Sources",
        description:
          "Blog posts, API documentation, pricing pages, and release notes from openai.com",
        source_count: 9,
        evidence_count: 18,
        dominant_tier: "tier_1_primary",
        confidence: "high",
        evidence_ids: ["ev_001", "ev_002", "ev_003", "ev_004", "ev_006"],
      },
      {
        group_id: "eg_02",
        label: "Technical Benchmarks & Research",
        description:
          "Arxiv papers, independent benchmark reports, and technical deep-dives from authoritative sources",
        source_count: 7,
        evidence_count: 14,
        dominant_tier: "tier_2_authoritative_secondary",
        confidence: "high",
        evidence_ids: ["ev_008", "ev_009", "ev_012", "ev_015"],
      },
      {
        group_id: "eg_03",
        label: "Developer & Community Signals",
        description:
          "Hacker News discussions, Reddit r/MachineLearning, developer Twitter/X threads on integration patterns",
        source_count: 8,
        evidence_count: 11,
        dominant_tier: "tier_3_community_signal",
        confidence: "medium",
        evidence_ids: ["ev_019", "ev_021", "ev_022"],
      },
      {
        group_id: "eg_04",
        label: "Industry Analysis & Pricing",
        description:
          "Competitive pricing comparisons, market share estimates, and analyst reports from tech media",
        source_count: 4,
        evidence_count: 4,
        dominant_tier: "tier_2_authoritative_secondary",
        confidence: "medium",
        evidence_ids: ["ev_025", "ev_028"],
      },
    ],
    risk_notes: [
      {
        risk_id: "rn_01",
        title: "Internal cannibalization by o3 and o4 reasoning models",
        content:
          "OpenAI's o-series (o1, o3, o4-mini) now captures the premium market for complex reasoning tasks, leaving GPT-4o in a mid-tier position. This risks pricing pressure and unclear product differentiation within OpenAI's own portfolio.",
        severity: "medium",
        supporting_evidence_ids: ["ev_030", "ev_031"],
      },
      {
        risk_id: "rn_02",
        title: "Open-source parity threatens API pricing power",
        content:
          "Meta Llama 3.1 405B and Mistral Large 2 achieve comparable benchmark scores at self-hosted cost structures. As inference infrastructure matures, the cost advantage of open-source may erode GPT-4o's API pricing power for budget-sensitive enterprise segments.",
        severity: "high",
        supporting_evidence_ids: ["ev_032", "ev_033"],
      },
    ],
  },

  vertical: {
    full_text: `GPT-4o's emergence as OpenAI's omni-architecture flagship is best understood not as a sudden innovation but as the culmination of a multi-year architectural migration toward native multimodality. OpenAI's journey began in 2020 with GPT-3—a purely text-based model that established the scaling hypothesis as a viable product paradigm. The implicit bet was that sufficiently large text models would develop emergent reasoning capabilities. This proved correct enough to produce GPT-3.5 and then GPT-4, which demonstrated strong cross-domain reasoning.

The critical pivot came with the realization that modality fragmentation was both a technical bottleneck and a product liability. GPT-4 Turbo's vision capabilities were bolted on via separate processing pipelines—Whisper for audio transcription, CLIP-style encoders for images—which introduced latency, context loss across modality boundaries, and architectural complexity that limited joint reasoning. GPT-4o was OpenAI's answer: a single transformer trained jointly on text, audio spectrograms, and image tokens from inception.

The path dependency established by GPT-3's training corpus—overwhelmingly English-language text—created lasting constraints. Despite efforts to expand multilingual capability, GPT-4o performs measurably better in English than in lower-resource languages, a limitation that stems from the original pretraining distribution rather than model capacity. This is not a fixable bug but a structural artifact of accumulated training choices.`,
    stages: [
      {
        stage_id: "vs_01",
        stage_number: 1,
        title: "GPT-3 Era: Scaling as Product Strategy",
        period: "2020 – 2022",
        summary:
          "GPT-3 established that scaling transformer parameters on text corpora produces commercially useful general intelligence. OpenAI bet on API access as a distribution moat, seeding an ecosystem of fine-tuned applications.",
        key_events: [
          "GPT-3 175B launched June 2020 with API-first distribution",
          "Codex model (2021) demonstrated code generation as first commercial application",
          "InstructGPT (2022) introduced RLHF alignment, critical safety precursor",
          "ChatGPT launched November 2022 using GPT-3.5, achieved 1M users in 5 days",
        ],
        driving_forces: [
          "Scaling law research confirming compute-intelligence relationship",
          "API-first monetization model enabling rapid ecosystem development",
          "Microsoft partnership providing Azure compute and distribution",
        ],
        path_dependencies: [
          "Heavy English-language pretraining bias persists in downstream models",
          "RLHF alignment pipeline became standard practice across industry",
        ],
        supporting_evidence_ids: ["ev_038", "ev_039"],
      },
      {
        stage_id: "vs_02",
        stage_number: 2,
        title: "GPT-4 Transition: Multimodality via Composition",
        period: "2023 – early 2024",
        summary:
          "GPT-4 launched with vision capabilities appended via pipeline composition. High capability but architectural limitations in cross-modal reasoning and audio became apparent, motivating the omni architecture.",
        key_events: [
          "GPT-4 launch March 2023 with text and limited vision (closed beta)",
          "GPT-4V vision API opened September 2023",
          "GPT-4 Turbo launched November 2023 with 128K context, reduced pricing",
          "Whisper-based voice mode added as separate pipeline in ChatGPT",
        ],
        driving_forces: [
          "Enterprise demand for document and image analysis",
          "Competition from Google Gemini's multimodal architecture",
          "User pressure for natural voice interaction",
        ],
        path_dependencies: [
          "Whisper + TTS pipeline established voice interaction pattern before native audio",
          "128K context window set developer expectations for long-context reasoning",
        ],
        supporting_evidence_ids: ["ev_040", "ev_041", "ev_042"],
      },
      {
        stage_id: "vs_03",
        stage_number: 3,
        title: "GPT-4o: Native Omni Architecture",
        period: "May 2024 – Q4 2024",
        summary:
          "GPT-4o unified text, audio, and image in a single jointly-trained model. Real-time voice mode, free-tier access, and structured outputs drove adoption to 100M+ daily users. GPT-4o mini democratized the architecture for cost-sensitive use cases.",
        key_events: [
          "GPT-4o GA May 2024 with ChatGPT free-tier access",
          "Advanced Voice Mode with emotional responsiveness (September 2024)",
          "GPT-4o mini at $0.15/M input tokens (July 2024)",
          "Structured Outputs for enterprise JSON guarantee (August 2024)",
          "Canvas collaborative editing interface (November 2024)",
        ],
        driving_forces: [
          "Consumer product differentiation through real-time voice",
          "Enterprise developer lock-in via Structured Outputs and fine-tuning",
          "Distribution scale via ChatGPT free tier democratization",
        ],
        path_dependencies: [
          "Free-tier access raised infrastructure cost baseline permanently",
          "GPT-4o mini fragmented the product line into cost tiers",
        ],
        supporting_evidence_ids: ["ev_001", "ev_002", "ev_003", "ev_004"],
      },
      {
        stage_id: "vs_04",
        stage_number: 4,
        title: "Portfolio Stratification: o-series vs GPT-4o",
        period: "2025 – present",
        summary:
          "OpenAI's o-series reasoning models (o1, o3, o4-mini) claimed the premium reasoning market, repositioning GPT-4o as the efficient, balanced general-purpose model. GPT-4o now faces pressure from above (o-series) and below (open-source parity).",
        key_events: [
          "o1 preview launch September 2024 for STEM reasoning",
          "o3 and o4-mini released early 2025",
          "GPT-4o image generation natively integrated (February 2025)",
          "Operator API for enterprise customization",
        ],
        driving_forces: [
          "Competitive pressure from DeepSeek R1 reasoning model",
          "Enterprise demand for specialized reasoning over general capability",
          "Cost optimization pressure from open-source inference",
        ],
        path_dependencies: [
          "Two-speed product portfolio creates positioning complexity",
          "GPT-4o locked into 'balanced' positioning between cheap and premium",
        ],
        supporting_evidence_ids: ["ev_030", "ev_031", "ev_043"],
      },
    ],
    key_turning_points: [
      "May 2024: Free ChatGPT access to GPT-4o — redefined baseline expectations for AI model capability across all user segments",
      "September 2024: Advanced Voice Mode GA — first consumer AI product with genuine real-time emotional voice interaction at scale",
      "July 2024: GPT-4o mini pricing at $0.15/M input — triggered industry-wide pricing compression and established new cost floor expectations",
      "August 2024: Structured Outputs — resolved the primary enterprise integration barrier and accelerated production deployments",
      "2025: o-series cannibalization — GPT-4o repositioned from 'flagship' to 'efficient general-purpose,' altering its market narrative",
    ],
    path_dependency_summary:
      "GPT-4o's current positioning is heavily constrained by two compounding path dependencies: (1) The English-language pretraining bias embedded since GPT-3 creates a structural multilingual ceiling that cannot be resolved without full retraining; (2) The free-tier distribution decision locked in a high infrastructure cost structure that pressures margin and limits the ability to restrict access as competition intensifies. These are not temporary competitive disadvantages but structural artifacts of the decisions that built GPT-4o's distribution advantage in the first place. OpenAI's response—portfolio stratification via o-series and GPT-4o mini—creates product complexity but preserves margin at the extremes.",
  },

  horizontal: {
    full_text: `The frontier AI model market has rapidly stratified into at least four distinct competitive layers: (1) closed frontier reasoning models (o3, Claude 3.7 Opus, Gemini 2.0 Ultra), (2) efficient frontier general-purpose models (GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro), (3) cost-optimized inference models (GPT-4o mini, Claude Haiku, Gemini Flash), and (4) open-source alternatives (Llama 3.1 405B, Mistral Large 2, DeepSeek V3). GPT-4o competes most directly in layer 2, where it maintains a distribution advantage via ChatGPT but faces genuine performance parity from Anthropic and Google.

The competitive dynamics in 2025 are characterized by three forces: benchmark convergence (all major providers now achieve similar scores on MMLU, HumanEval, and MATH), differentiation via ecosystem (tooling, APIs, integrations), and pricing pressure from open-source. GPT-4o's primary moat is not model capability per se but the ChatGPT distribution layer and the OpenAI API ecosystem that has accumulated millions of production integrations.

Anthropic's Claude 3.5 Sonnet represents the most credible direct competitor: it exceeds GPT-4o on coding benchmarks (SWE-bench 49% vs 38%) and has a longer default output window. Google's Gemini 1.5 Pro maintains the largest context window (1M tokens) which remains unchallenged. Meta's Llama 3.1 405B provides a self-hosted alternative that achieves near-GPT-4o performance without API costs, representing a structural threat to the API business model rather than a direct consumer substitute.`,
    competitor_scenario: "mature_market",
    positioning_summary:
      "GPT-4o occupies the efficient frontier general-purpose tier with dominant distribution via ChatGPT (100M+ DAU) but faces capability parity from Claude 3.5 Sonnet and Gemini 1.5 Pro. Its primary competitive advantage is ecosystem lock-in and distribution scale rather than model performance differential.",
    competitor_matrix: [
      {
        competitor_id: "comp_01",
        name: "Claude 3.5 Sonnet",
        role: "Primary direct competitor — coding & enterprise analysis",
        strengths: [
          "SWE-bench 49% vs GPT-4o 38% for real-world coding",
          "8K default output window (vs GPT-4o 4K)",
          "Artifacts UI for collaborative document editing",
          "Constitutional AI alignment approach reduces refusals",
        ],
        weaknesses: [
          "No free consumer tier comparable to ChatGPT",
          "Smaller developer ecosystem and fewer integrations",
          "No native image generation capability",
          "claude.ai lags ChatGPT in brand recognition globally",
        ],
        best_for: "Enterprise coding assistants, long-form document analysis, API-first workflows",
        pricing_or_access: "$3/M input, $15/M output (Sonnet). Free tier limited.",
        supporting_evidence_ids: ["ev_050", "ev_051"],
      },
      {
        competitor_id: "comp_02",
        name: "Gemini 1.5 Pro",
        role: "Long-context specialist — Google ecosystem integration",
        strengths: [
          "1M token context window — unchallenged for large document analysis",
          "Native Google Workspace and Search integration",
          "Video understanding capability",
          "Strong multilingual performance",
        ],
        weaknesses: [
          "Variable benchmark consistency across tasks",
          "gemini.google.com UX lags ChatGPT in user satisfaction surveys",
          "Complex pricing tiers (Flash, Pro, Ultra) confuse developers",
          "Enterprise trust deficit post-Bard rebranding confusion",
        ],
        best_for: "Large document analysis, video understanding, Google Workspace power users",
        pricing_or_access: "$1.25/M input, $5/M output (1.5 Pro). Gemini Free tier.",
        supporting_evidence_ids: ["ev_052", "ev_053"],
      },
      {
        competitor_id: "comp_03",
        name: "Llama 3.1 405B (Meta)",
        role: "Open-source alternative — self-hosted production deployment",
        strengths: [
          "Zero API costs at scale with self-hosted inference",
          "Fine-tuneable on proprietary data without vendor data exposure",
          "Apache 2.0 license — commercial use without API dependency",
          "Competitive performance: 86.1% MMLU vs GPT-4o 88.7%",
        ],
        weaknesses: [
          "Infrastructure burden: requires A100/H100 cluster for 405B at scale",
          "No consumer product distribution",
          "Safety alignment lags closed models",
          "Requires MLOps team investment",
        ],
        best_for: "Enterprises with data sovereignty requirements, high-volume inference at scale",
        pricing_or_access: "Self-hosted. Inference cost: ~$3-8/M tokens on cloud A100.",
        supporting_evidence_ids: ["ev_054", "ev_055"],
      },
      {
        competitor_id: "comp_04",
        name: "Mistral Large 2",
        role: "European alternative — multilingual, code, cost efficiency",
        strengths: [
          "Strong European language support (FR, DE, ES, IT)",
          "GDPR-native hosting options (EU region)",
          "Competitive coding: 92% HumanEval",
          "La Plateforme API competitive pricing",
        ],
        weaknesses: [
          "Significantly smaller ecosystem than OpenAI or Google",
          "No consumer product distribution",
          "Context window (128K) matches but doesn't exceed competitors",
          "Limited vision capabilities vs GPT-4o",
        ],
        best_for: "European enterprises requiring GDPR compliance, multilingual applications",
        pricing_or_access: "$3/M input, $9/M output (Large 2 via La Plateforme)",
        supporting_evidence_ids: ["ev_056"],
      },
      {
        competitor_id: "comp_05",
        name: "DeepSeek V3 / R1",
        role: "Cost disruptor — emerging threat from Chinese AI lab",
        strengths: [
          "DeepSeek-R1 achieves o1-level reasoning benchmark at open weights",
          "V3 API at $0.27/M input (vs GPT-4o $5/M) — 18× cheaper",
          "Strong math and coding performance",
          "Rapidly maturing ecosystem in Asian markets",
        ],
        weaknesses: [
          "Data sovereignty concerns for US/EU enterprise",
          "Censorship limitations on political/sensitive topics",
          "API reliability and SLA guarantees less established",
          "US regulatory risk re: Chinese AI model access",
        ],
        best_for: "Cost-sensitive API workloads, Asian market deployments, research applications",
        pricing_or_access: "$0.27/M input tokens for V3. R1 open weights available.",
        supporting_evidence_ids: ["ev_057", "ev_058"],
      },
    ],
    capability_boundaries: [
      {
        boundary_id: "cb_01",
        title: "Real-time voice with emotional responsiveness",
        description:
          "Currently GPT-4o Advanced Voice Mode is the most mature consumer-facing real-time voice AI product. Competitors are shipping voice features but none match the emotional detection and naturalness at scale.",
        boundary_type: "short_term_feature",
        supporting_evidence_ids: ["ev_002", "ev_008"],
      },
      {
        boundary_id: "cb_02",
        title: "ChatGPT distribution network (100M+ DAU)",
        description:
          "The ChatGPT consumer product represents a durable distribution moat that cannot be replicated by API-only competitors. Network effects from plugin/GPT ecosystem, user memory, and behavioral data create compounding advantage.",
        boundary_type: "long_term_moat",
        supporting_evidence_ids: ["ev_003", "ev_012"],
      },
      {
        boundary_id: "cb_03",
        title: "Complex multi-step reasoning vs o-series",
        description:
          "GPT-4o underperforms o1/o3 significantly on AIME, competition math, and complex agentic planning tasks. Users with reasoning-heavy workloads increasingly migrate to o-series, leaving GPT-4o in the efficiency tier.",
        boundary_type: "current_weakness",
        supporting_evidence_ids: ["ev_030", "ev_031"],
      },
      {
        boundary_id: "cb_04",
        title: "Open-source models approaching API cost-performance parity",
        description:
          "DeepSeek V3 and Llama 3.1 405B deliver 85-90% of GPT-4o performance at 3-20× lower cost when self-hosted. As inference infrastructure (vLLM, llama.cpp) matures, the cost barrier to open-source deployment decreases, threatening the API business model.",
        boundary_type: "emerging_threat",
        supporting_evidence_ids: ["ev_054", "ev_057"],
      },
    ],
    recommendations: [
      {
        rec_id: "rec_01",
        title: "Default to GPT-4o for general production API workloads",
        content:
          "For organizations building general-purpose AI features (chat, summarization, classification, moderate complexity generation), GPT-4o's Structured Outputs, function calling, and fine-tuning ecosystem provide the best ROI. Switch to GPT-4o mini for >10K calls/day use cases.",
        priority: "high",
        target_audience: "Product teams, application developers",
        rationale:
          "Best ecosystem maturity, reliable SLA, and comprehensive tooling outweigh the 10-15% premium over alternatives",
        supporting_evidence_ids: ["ev_006", "ev_015", "ev_021"],
      },
      {
        rec_id: "rec_02",
        title: "Evaluate Claude 3.5 Sonnet for code-heavy workflows",
        content:
          "Teams building code review, PR automation, or technical documentation tools should A/B test Claude 3.5 Sonnet. The 11-point SWE-bench advantage and longer output window directly translate to fewer multi-turn loops in code generation pipelines.",
        priority: "high",
        target_audience: "Engineering teams, DevTools builders",
        rationale:
          "Coding benchmark differential is large enough to matter in production, and Anthropic's API is stable",
        supporting_evidence_ids: ["ev_050", "ev_051"],
      },
      {
        rec_id: "rec_03",
        title: "Monitor DeepSeek pricing — hedge with provider-agnostic abstraction",
        content:
          "DeepSeek V3's pricing at $0.27/M input creates significant cost pressure for budget-sensitive workloads. Teams should implement provider-agnostic LLM routing (LiteLLM, Portkey) to enable rapid switching without rearchitecting at the application layer.",
        priority: "medium",
        target_audience: "CTOs, platform teams",
        rationale:
          "The 18× pricing differential cannot be ignored for scale workloads, but regulatory risk requires optionality",
        supporting_evidence_ids: ["ev_057", "ev_058"],
      },
    ],
  },
};

// ── Claude 3.5 Sonnet – Completed with Quality Warning ────────────────────
const claudeReport: ReportData = {
  report_id: "rpt_20260507_claude35_p2q1",
  topic: "Claude 3.5 Sonnet",
  subject: "Claude 3.5 Sonnet",
  subject_type: "product",
  title: "Claude 3.5 Sonnet: Coding-First Frontier Model Analysis",
  subtitle: "Anthropic's production-tier model — positioning, capability boundaries, and differentiation",
  quality_warning: true,
  quality_issues: [
    "Horizontal evidence coverage below threshold: only 6 horizontal evidence cards (target ≥ 8)",
    "Competitor pricing data for Gemini Ultra not found in retrieval window — may be stale",
    "Tier 1 source ratio: 54% (target ≥ 60%) — supplementary search triggered but not fully resolved",
  ],
  quality_score: 74,
  source_count: 19,
  evidence_count: 31,
  generated_at: "2026-05-07T16:42:11Z",
  limitations: [
    "Evidence coverage for horizontal analysis below target threshold",
    "Some competitor pricing data may be outdated",
  ],
  overview: {
    product_overview:
      "Claude 3.5 Sonnet is Anthropic's production-tier large language model, positioned as the primary workhorse for enterprise and developer API usage. It launched in June 2024 and became notable for achieving the highest SWE-bench score (49%) among publicly benchmarked models at the time of release. Claude 3.5 Sonnet is designed around long-horizon reasoning, code generation, and artifact-based collaborative editing via the Artifacts UI in claude.ai.",
    key_findings: [
      {
        finding_id: "kf_c01",
        title: "SWE-bench 49% sets new standard for software engineering tasks",
        content:
          "Claude 3.5 Sonnet achieved 49% on SWE-bench Verified at launch, outperforming GPT-4o (38%) and Gemini 1.5 Pro (31%). This represents a meaningful real-world coding advantage for software engineering automation use cases.",
        confidence: "high",
        supporting_evidence_ids: ["ev_c001", "ev_c002"],
      },
    ],
    release_updates: [
      {
        update_id: "ru_c01",
        date: "2024-06-20",
        title: "Claude 3.5 Sonnet Initial Release",
        content: "Launch with SWE-bench leading performance and Artifacts collaborative editing.",
        update_type: "product_launch",
        source_url: "https://www.anthropic.com/news/claude-3-5-sonnet",
        confidence: "high",
      },
    ],
    evidence_groups: [
      {
        group_id: "eg_c01",
        label: "Official Anthropic Sources",
        description: "Anthropic blog posts, model card, and API documentation",
        source_count: 5,
        evidence_count: 10,
        dominant_tier: "tier_1_primary",
        confidence: "high",
        evidence_ids: ["ev_c001", "ev_c002"],
      },
      {
        group_id: "eg_c02",
        label: "Benchmark & Technical Analysis",
        description: "Independent benchmark reports and developer evaluations",
        source_count: 8,
        evidence_count: 14,
        dominant_tier: "tier_2_authoritative_secondary",
        confidence: "medium",
        evidence_ids: ["ev_c003", "ev_c004"],
      },
      {
        group_id: "eg_c03",
        label: "Community Signals",
        description: "Developer feedback from HN, Reddit, and Twitter/X",
        source_count: 6,
        evidence_count: 7,
        dominant_tier: "tier_3_community_signal",
        confidence: "low",
        evidence_ids: ["ev_c005"],
      },
    ],
    risk_notes: [
      {
        risk_id: "rn_c01",
        title: "Limited free-tier distribution constrains consumer mindshare",
        content:
          "claude.ai's free tier is significantly more restricted than ChatGPT, limiting Claude's brand penetration among non-enterprise users. This distribution gap may compound over time as user habits solidify around ChatGPT.",
        severity: "high",
        supporting_evidence_ids: ["ev_c006"],
      },
    ],
  },
  vertical: {
    full_text: "Partial vertical analysis — see quality warning for coverage limitations.",
    stages: [],
    key_turning_points: [],
    path_dependency_summary: "Insufficient evidence for comprehensive path dependency analysis.",
  },
  horizontal: {
    full_text: "Partial horizontal analysis — evidence coverage below threshold.",
    competitor_scenario: "mature_market",
    positioning_summary:
      "Claude 3.5 Sonnet is positioned as the coding-optimized frontier model for enterprise API use, with leading SWE-bench performance but limited consumer distribution.",
    competitor_matrix: [],
    capability_boundaries: [],
    recommendations: [],
  },
};

// ── Cursor AI – Running State ──────────────────────────────────────────────
const cursorProgressSteps: ProgressStep[] = [
  { step_id: "ps_01", label: "Initializing research run", status: "completed", timestamp: "10:31:02" },
  { step_id: "ps_02", label: "Planning research questions", status: "completed", timestamp: "10:31:05" },
  {
    step_id: "ps_03",
    label: "Collecting information (12/12 tool calls)",
    status: "completed",
    timestamp: "10:33:41",
    message: "28 candidate sources found, 7 pages scraped",
  },
  {
    step_id: "ps_04",
    label: "Filtering evidence cards",
    status: "completed",
    timestamp: "10:34:18",
    message: "41 evidence cards extracted",
  },
  {
    step_id: "ps_05",
    label: "Running vertical analysis",
    status: "running",
    message: "Writing historical narrative — Stage 3 of 4...",
  },
  { step_id: "ps_06", label: "Running horizontal analysis", status: "pending" },
  { step_id: "ps_07", label: "Synthesizing report data", status: "pending" },
  { step_id: "ps_08", label: "Quality check", status: "pending" },
  { step_id: "ps_09", label: "Saving report artifacts", status: "pending" },
];

// ── Devin AI – Failed State ────────────────────────────────────────────────

export const mockReports: HistoryReport[] = [
  {
    report_id: "rpt_20260508_gpt4o_x7a9",
    topic: "GPT-4o",
    subject_type: "product",
    status: "completed",
    quality_warning: false,
    quality_score: 91,
    created_at: "2026-05-08T09:14:23Z",
    updated_at: "2026-05-08T09:19:47Z",
    error_message: null,
    report_data: gpt4oReport,
    progress_steps: [],
    progress_message: "Report generated successfully",
  },
  {
    report_id: "rpt_20260507_claude35_p2q1",
    topic: "Claude 3.5 Sonnet",
    subject_type: "product",
    status: "completed",
    quality_warning: true,
    quality_score: 74,
    created_at: "2026-05-07T16:42:11Z",
    updated_at: "2026-05-07T16:49:03Z",
    error_message: null,
    report_data: claudeReport,
    progress_steps: [],
    progress_message: "Report completed with quality warnings",
  },
  {
    report_id: "rpt_20260508_cursor_m3k8",
    topic: "Cursor AI",
    subject_type: "product",
    status: "analyzing_vertical",
    quality_warning: false,
    quality_score: null,
    created_at: "2026-05-08T10:31:02Z",
    updated_at: "2026-05-08T10:34:22Z",
    error_message: null,
    report_data: null,
    progress_steps: cursorProgressSteps,
    progress_message: "Running vertical analysis — Stage 3 of 4...",
  },
  {
    report_id: "rpt_20260506_devin_q9r2",
    topic: "Devin AI (Cognition Labs)",
    subject_type: "product",
    status: "failed",
    quality_warning: false,
    quality_score: null,
    created_at: "2026-05-06T14:22:08Z",
    updated_at: "2026-05-06T14:27:33Z",
    error_message:
      "collect_info reached MAX_TOOL_CALLS limit with insufficient evidence: only 4 horizontal evidence cards found (minimum 8 required). Tavily returned blocked results for devin.ai. Consider Force Refresh to retry.",
    report_data: null,
    progress_steps: [
      { step_id: "d_ps_01", label: "Initializing research run", status: "completed", timestamp: "14:22:09" },
      { step_id: "d_ps_02", label: "Planning research questions", status: "completed", timestamp: "14:22:14" },
      {
        step_id: "d_ps_03",
        label: "Collecting information (12/12 tool calls)",
        status: "completed",
        timestamp: "14:24:51",
        message: "MAX_TOOL_CALLS reached — insufficient evidence",
      },
      {
        step_id: "d_ps_04",
        label: "Filtering evidence cards",
        status: "failed",
        message: "4 horizontal cards found — minimum 8 required. Aborting.",
      },
      { step_id: "d_ps_05", label: "Running vertical analysis", status: "pending" },
      { step_id: "d_ps_06", label: "Running horizontal analysis", status: "pending" },
      { step_id: "d_ps_07", label: "Synthesizing report data", status: "pending" },
      { step_id: "d_ps_08", label: "Quality check", status: "pending" },
      { step_id: "d_ps_09", label: "Saving report artifacts", status: "pending" },
    ],
    progress_message: "Failed: insufficient evidence collected",
  },
  {
    report_id: "rpt_20260505_llangchain_f1t3",
    topic: "LangChain Framework",
    subject_type: "technology",
    status: "completed",
    quality_warning: false,
    quality_score: 88,
    created_at: "2026-05-05T11:08:44Z",
    updated_at: "2026-05-05T11:14:22Z",
    error_message: null,
    report_data: null,
    progress_steps: [],
    progress_message: "Report generated successfully",
  },
  {
    report_id: "rpt_20260504_perplexity_v6b2",
    topic: "Perplexity AI",
    subject_type: "product",
    status: "completed",
    quality_warning: false,
    quality_score: 85,
    created_at: "2026-05-04T09:55:17Z",
    updated_at: "2026-05-04T10:01:49Z",
    error_message: null,
    report_data: null,
    progress_steps: [],
    progress_message: "Report generated successfully",
  },
];
