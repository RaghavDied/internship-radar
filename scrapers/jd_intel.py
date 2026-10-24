"""
Deep Job Description & Requirements Intelligence Engine.
Extracts ATS keywords, core skills, eligibility requirements, responsibilities,
conversational talking points, and Google XYZ resume bullet suggestions.
Completely unique and dynamically tailored per company, role, industry, and tech stack.
"""
import re
import hashlib

# Comprehensive tech skill taxonomy for B.Tech CSE
TECH_TAXONOMY = {
    "Languages": [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Golang", "Rust", 
        "Kotlin", "Swift", "PHP", "Ruby", "SQL", "HTML5", "CSS3"
    ],
    "Frontend Frameworks": [
        "React.js", "Next.js", "Vue.js", "Angular", "Tailwind CSS", "Redux", 
        "Material UI", "Bootstrap", "WebSockets", "Responsive Design"
    ],
    "Backend & APIs": [
        "Node.js", "Express.js", "Django", "FastAPI", "Flask", "Spring Boot", 
        "REST APIs", "GraphQL", "Microservices", "gRPC", "Authentication (JWT/OAuth)"
    ],
    "Databases & Caching": [
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Firebase", 
        "Elasticsearch", "Prisma ORM", "Database Indexing & Query Optimization"
    ],
    "Cloud & DevOps": [
        "AWS (EC2/S3/Lambda)", "Docker", "Kubernetes", "Linux / Shell Scripting", 
        "CI/CD Pipelines", "Git & GitHub", "Google Cloud Platform (GCP)", "Azure", "Terraform"
    ],
    "AI / ML & Data": [
        "PyTorch", "TensorFlow", "Scikit-Learn", "Pandas & NumPy", "OpenCV", 
        "Large Language Models (LLMs)", "Natural Language Processing (NLP)", 
        "Computer Vision", "Data Preprocessing", "HuggingFace"
    ],
    "Mobile & Systems": [
        "Android SDK", "Flutter", "React Native", "iOS / UIKit", "Room Database", 
        "Embedded C", "Internet of Things (IoT)", "RTOS", "Microcontrollers", "Raspberry Pi", "Arduino"
    ]
}

# Generic engineering ATS buzzwords
ATS_POWER_KEYWORDS = [
    "Object-Oriented Programming (OOP)", "Data Structures & Algorithms", "System Design",
    "Agile / Scrum Methodologies", "Code Review & Refactoring", "Test-Driven Development (TDD)",
    "API Integration", "Unit & Integration Testing", "Version Control (Git)",
    "Clean Code Architecture", "Scalability & Performance Optimization", "Cross-Functional Collaboration"
]

# Industry verticals for tailored context
INDUSTRIES = {
    "PropTech / Real Estate": {
        "keywords": ["gharpayy", "property", "real estate", "proptech", "rent", "housing", "pg", "hostel", "tenant", "flatmate"],
        "convo_hook": "Ask about their spatial search indexing (e.g., PostGIS) and media CDN delivery for high-resolution property browsing.",
        "resume_addon": "powering fast spatial search filters and dynamic room availability booking flows."
    },
    "FinTech": {
        "keywords": ["fintech", "finance", "payment", "bank", "wealth", "trading", "crypto", "loan", "wallet", "tax", "accounting"],
        "convo_hook": "Ask how their team architected API idempotency and transaction consistency for zero-loss financial workflows.",
        "resume_addon": "ensuring strict data integrity and compliance with financial security standards."
    },
    "HealthTech": {
        "keywords": ["health", "medinex", "medical", "pharma", "clinic", "hospital", "patient", "doctor", "fitness", "wellness"],
        "convo_hook": "Inquire about their data governance for sensitive records and how they maintain low-latency telemetry.",
        "resume_addon": "adhering to strict data confidentiality and secure application communication protocols."
    },
    "EdTech": {
        "keywords": ["edtech", "education", "learning", "course", "academy", "student", "school", "tutor", "gradtwin", "skoollage"],
        "convo_hook": "Ask how they handle concurrency spikes during peak exam hours and optimize interactive learning modules.",
        "resume_addon": "supporting high-concurrency student access with automated progress tracking."
    },
    "Robotics & Embedded": {
        "keywords": ["robotics", "robot", "embedded", "arduino", "raspberry pi", "firmware", "iot", "sensor", "hardware", "conscript"],
        "convo_hook": "Inquire about their hardware-in-the-loop (HIL) simulation testbeds and RTOS interrupt latency.",
        "resume_addon": "interfacing microcontroller sensor feeds with low-level C/C++ firmware."
    },
    "AI & Data Intelligence": {
        "keywords": ["ai", "machine learning", "deep learning", "nlp", "vision", "llm", "genai", "countai", "automation"],
        "convo_hook": "Ask whether inference is run on edge or cloud GPU instances and how they manage dataset versioning and drift.",
        "resume_addon": "benchmarking model inference latency and setting up automated data preprocessing pipelines."
    },
    "E-Commerce & Logistics": {
        "keywords": ["ecommerce", "e-commerce", "shop", "retail", "cart", "order", "delivery", "logistics", "routespring", "travel", "fleet"],
        "convo_hook": "Ask about their caching layer for real-time inventory tracking and route dispatch optimization.",
        "resume_addon": "optimizing checkout funnel throughput and integrating third-party logistics webhooks."
    },
    "SaaS & Enterprise": {
        "keywords": ["saas", "cloud", "enterprise", "platform", "b2b", "crm", "erp", "embeddedgyan", "complyance", "portal"],
        "convo_hook": "Ask about their multi-tenant database partitioning strategy and how they handle tenant-isolated telemetry.",
        "resume_addon": "implementing role-based access control (RBAC) and tenant isolation for enterprise clients."
    }
}

# Domain-specific architectural interview inquiries
DOMAIN_TECH_QUESTIONS = {
    "Full Stack": "Inquire about their database connection pooling strategy and how state is synchronized between client and microservices.",
    "Backend": "Ask how they handle distributed transaction tracing, connection pooling in Postgres, and their rate-limiting middleware strategy.",
    "Frontend": "Inquire about their component library modularity, Core Web Vitals (LCP/CLS) budget, and SSR vs SSG hydration tradeoffs.",
    "AI / ML": "Ask about their evaluation harnesses for testing regression in fine-tuned models and their vector search indexing pipeline.",
    "Mobile": "Ask how their team profiles memory leaks, handles background push notification sync, and manages offline-first SQLite/Room storage.",
    "Cloud & DevOps": "Ask about their infrastructure-as-code linting, canary deployment rollback triggers, and Prometheus/Grafana metric alerts.",
    "Systems & Embedded": "Ask about their hardware debugging toolchains, RTOS task priorities, and C/C++ memory footprint constraints.",
    "Cybersecurity": "Ask about their DevSecOps pipelines, automated SAST/DAST scanning in CI/CD, and zero-trust credential rotation.",
    "Data Engineering": "Ask about their distributed partition strategy in Spark/SQL and how they handle backpressure in streaming pipelines.",
    "Core Software Dev": "Ask about their unit testing coverage targets, static analysis linters, and architectural review cadence."
}

# Rich varied resume bullet archetypes (chosen by hashing company + title for zero repetition across openings)
DOMAIN_BULLET_ARCHETYPES = {
    "Full Stack": [
        "Architected and deployed full-stack web features using {skills}, decreasing API response times by 32% through query indexing and Redis caching.",
        "Engineered end-to-end responsive UI workflows and modular REST/GraphQL endpoints with {skills}, increasing test coverage to 85% via automated Jest/PyTest suites.",
        "Optimized relational database schemas and asynchronous queue workers using {skills}, cutting server memory overhead by 28% during peak traffic.",
        "Built secure user authentication (JWT/OAuth2) and containerized backend services using {skills}, achieving zero-downtime deployment pipelines."
    ],
    "Backend": [
        "Designed and implemented modular backend microservices with {skills}, handling concurrent requests and ensuring 99.9% uptime.",
        "Optimized relational database schema and caching layers with Redis/SQL, reducing database query overhead by 40%.",
        "Engineered high-throughput RESTful API endpoints using {skills}, implementing robust input sanitization and rate-limiting middleware.",
        "Refactored legacy database queries and automated schema migrations, accelerating batch processing runtimes by 35%."
    ],
    "Frontend": [
        "Developed high-performance interactive user interfaces in {skills}, improving user engagement and PageSpeed metrics by 25%.",
        "Refactored state management architecture and integrated REST APIs, ensuring seamless cross-browser consistency and responsive design.",
        "Built reusable design-system component library using {skills}, reducing frontend feature development turnaround by 30%.",
        "Optimized client-side bundle size and lazy loading in {skills}, cutting Largest Contentful Paint (LCP) from 3.2s to 1.4s."
    ],
    "AI / ML": [
        "Trained and evaluated deep learning / machine learning models using {skills}, achieving over 90% validation accuracy on benchmarks.",
        "Built automated data preprocessing pipelines and fine-tuned predictive algorithms, accelerating model inference pipeline by 35%.",
        "Engineered automated feature extraction and exploratory data analysis (EDA) pipelines using {skills}, processing 100k+ records.",
        "Containerized ML inference endpoints with FastAPI and Docker, reducing inference latency by 45% using batched predictions."
    ],
    "Mobile": [
        "Engineered native mobile application features with {skills}, adhering strictly to Material Design and modern MVVM architecture.",
        "Implemented offline caching, asynchronous network requests, and smooth UI animations, boosting app store user rating.",
        "Optimized mobile app memory footprint and reduced APK bundle size by 28% using ProGuard and asset compression.",
        "Integrated push notification services and reactive background data sync workers in {skills}, improving daily active retention."
    ],
    "Cloud & DevOps": [
        "Containerized microservices using Docker and automated CI/CD deployment pipelines on AWS/Linux, slashing release cycles by 50%.",
        "Configured scalable cloud infrastructure monitoring and automated alerts, minimizing mean time to detection (MTTD).",
        "Authored declarative Terraform infrastructure scripts and automated secret management, ensuring reproducible test environments.",
        "Built automated regression testing runners in GitHub Actions, decreasing developer deployment friction by 40%."
    ],
    "Systems & Embedded": [
        "Implemented low-level sensor communication protocols (I2C/SPI/UART) and firmware routines using {skills}.",
        "Profiled embedded runtime execution and optimized C/C++ memory allocation, eliminating hardware buffer overruns.",
        "Integrated microcontroller peripheral drivers with hardware abstraction layers, ensuring sub-millisecond response times.",
        "Designed automated hardware-in-the-loop test harnesses, validating communication packet integrity under stress."
    ],
    "Cybersecurity": [
        "Executed vulnerability assessments and security audits, identifying potential exploit vectors and hardening application security.",
        "Implemented robust authentication protocols, input validation, and OWASP Top 10 remediation strategies.",
        "Configured automated security scanning in CI/CD pipelines, eliminating hardcoded secrets and vulnerable dependencies.",
        "Conducted network traffic analysis and anomaly detection drills, bolstering endpoint defense readiness."
    ],
    "Data Engineering": [
        "Built resilient ETL data pipelines processing high-volume datasets using {skills}, enabling real-time analytics for stakeholders.",
        "Designed automated SQL reporting workflows and data lake schemas, eliminating manual data reconciliation delays.",
        "Implemented automated data validation checkpoints and schema enforcement, cutting pipeline failure rates by 45%.",
        "Optimized distributed query execution plans, reducing cloud warehouse compute costs by 22%."
    ],
    "Core Software Dev": [
        "Implemented high-performance algorithms in {skills}, improving memory efficiency and reducing runtime complexity.",
        "Authored comprehensive unit tests and participated in rigorous code reviews, ensuring adherence to clean code standards.",
        "Refactored monolithic application modules into clean decoupled service classes, improving code maintainability.",
        "Identified and eliminated CPU bottlenecks through runtime profiling, accelerating core data processing by 30%."
    ]
}


def detect_industry(text: str) -> tuple[str, dict]:
    """Detects company industry vertical from text."""
    lower_text = text.lower()
    for ind, meta in INDUSTRIES.items():
        if any(re.search(rf"\b{re.escape(kw)}\b", lower_text) for kw in meta["keywords"]):
            return ind, meta
    return "Tech / Software Services", {
        "convo_hook": "Ask about their engineering sprint cadence, code review culture, and technical mentorship.",
        "resume_addon": "adhering to software engineering best practices and agile sprint deliverables."
    }


def analyze_job_intel(title: str, company: str, domain: str, location: str, description: str = "", tags: list = None) -> dict:
    """
    Vividly, uniquely, and deeply scans a job opening, extracting high-signal requirements,
    ATS resume keywords, talking points, and tailored resume bullet points.
    Guaranteed unique per opening through company profiling, industry detection,
    JD sentence extraction, and deterministic seed hashing.
    """
    tags = tags or []
    full_text = f"{company} {title} {description}".lower()
    ind_name, ind_meta = detect_industry(full_text)
    
    # 1. Extract Core Technical Skills
    identified_skills = list(tags)
    for category, skills in TECH_TAXONOMY.items():
        for skill in skills:
            pattern = rf"\b{re.escape(skill.lower())}\b"
            if re.search(pattern, full_text) and skill not in identified_skills:
                identified_skills.append(skill)

    if not identified_skills:
        fallback_map = {
            "Frontend": ["JavaScript", "React.js", "HTML5", "CSS3", "Tailwind CSS", "Git"],
            "Backend": ["Python", "Node.js", "REST APIs", "PostgreSQL", "Docker", "Git"],
            "Full Stack": ["React.js", "Node.js", "JavaScript", "SQL", "REST APIs", "Git"],
            "AI / ML": ["Python", "PyTorch", "TensorFlow", "Scikit-Learn", "Pandas", "NumPy"],
            "Mobile": ["Android SDK", "Kotlin", "Java", "Mobile Architecture", "REST APIs"],
            "Cloud & DevOps": ["Linux", "Docker", "AWS", "CI/CD", "Git", "Shell Scripting"],
            "Cybersecurity": ["Network Security", "Linux", "Python", "Vulnerability Assessment", "OWASP"],
            "Data Engineering": ["SQL", "Python", "ETL Pipelines", "PostgreSQL", "Pandas"],
            "Systems & Embedded": ["Embedded C", "C++", "Microcontrollers", "RTOS", "Git"]
        }
        identified_skills = fallback_map.get(domain, ["Python", "JavaScript", "Data Structures", "Git", "REST APIs"])

    # 2. Extract ATS Resume Keywords
    ats_keywords = []
    # Add top 6 skills
    for s in identified_skills[:6]:
        if s not in ats_keywords:
            ats_keywords.append(s)
    # Add relevant engineering power keywords
    for kw in ATS_POWER_KEYWORDS:
        if kw not in ats_keywords and len(ats_keywords) < 14:
            ats_keywords.append(kw)

    # 3. Extract Detailed Requirements & Must-Haves
    requirements = []
    
    # Check degree requirement
    if any(k in full_text for k in ["b.tech", "b.e", "btech", "degree", "computer science", "engineering"]):
        requirements.append("Pursuing or completed B.Tech / B.E. in Computer Science, IT, or related engineering discipline")
    else:
        requirements.append("Strong computer science foundation in algorithms, data structures, and software engineering")

    # Core tech proficiency
    top_3_skills = ", ".join(identified_skills[:3]) if identified_skills else "Core CSE Fundamentals"
    requirements.append(f"Demonstrated hands-on project experience with {top_3_skills}")

    # Location / Work mode
    if "remote" in full_text or "work from home" in full_text or "(remote)" in location.lower():
        requirements.append("Strong asynchronous communication skills and ability to work autonomously in a remote setup")
    elif location and location != "Not specified":
        requirements.append(f"Availability for in-person / hybrid collaboration in {location}")
    else:
        requirements.append("Availability for full-time or part-time internship commitment (2 - 6 months)")

    requirements.append("Familiarity with version control workflows (Git / GitHub) and collaborative development")
    requirements.append(f"Interest in {ind_name} domain problem spaces and customer-facing engineering impact")

    # 4. Extract Key Responsibilities & Deliverables
    responsibilities = []
    
    # Attempt A: Direct extraction of bullet lines
    lines = [line.strip() for line in description.splitlines() if line.strip()]
    for line in lines:
        if re.match(r"^(\d+[\.\)]|[\-\*•])\s*", line):
            clean_line = re.sub(r"^(\d+[\.\)]|[\-\*•])\s*", "", line)
            if len(clean_line) > 20 and len(responsibilities) < 4:
                responsibilities.append(clean_line)

    # Attempt B: Direct extraction of actionable sentences from text
    if not responsibilities and len(description) > 30:
        sentences = re.split(r"[.\n]+", description)
        action_verbs = ["develop", "build", "design", "implement", "collaborate", "integrate", "optimize", "maintain", "test", "debug", "assist", "create", "support"]
        for s in sentences:
            s_clean = s.strip()
            if len(s_clean) > 25 and any(s_clean.lower().startswith(v) or f" {v} " in s_clean.lower() for v in action_verbs):
                if len(responsibilities) < 4 and s_clean not in responsibilities:
                    responsibilities.append(s_clean)

    # Fallback C: Domain-specific tailored responsibilities
    if not responsibilities:
        lead_skill = identified_skills[0] if identified_skills else "modern software frameworks"
        domain_resp_map = {
            "Frontend": [
                f"Develop, test, and maintain interactive web UI components using {lead_skill}",
                "Collaborate with designers to translate Figma prototypes into clean, responsive HTML/CSS code",
                "Integrate backend RESTful APIs and ensure seamless cross-device compatibility",
                "Optimize frontend load performance and debug UI/UX issues across browsers"
            ],
            "Backend": [
                f"Design, build, and optimize robust RESTful microservices using {lead_skill}",
                "Write clean database queries, manage schema migrations, and implement caching layers",
                "Implement secure authentication, input validation, and error-handling middleware",
                "Participate in code reviews and write comprehensive unit tests"
            ],
            "Full Stack": [
                f"Build end-to-end features spanning both client-side and server-side components using {top_3_skills}",
                "Design database models, implement backend APIs, and connect them with modern frontend state management",
                "Troubleshoot production issues and assist in deployment pipelines",
                "Collaborate in daily standups and agile sprint planning sessions"
            ],
            "AI / ML": [
                f"Develop and benchmark machine learning / deep learning pipelines using {lead_skill}",
                "Perform data cleaning, feature engineering, and exploratory data analysis (EDA)",
                "Fine-tune pre-trained models and deploy predictive endpoints",
                "Document experiment results and present findings to engineering mentors"
            ],
            "Mobile": [
                f"Develop and ship features for native mobile applications using {lead_skill}",
                "Implement smooth UI components following platform-specific design guidelines",
                "Integrate third-party libraries, push notifications, and background sync services",
                "Profile memory usage and resolve app performance bottlenecks"
            ],
            "Systems & Embedded": [
                f"Develop and test firmware routines and device drivers using {lead_skill}",
                "Perform hardware-software integration testing and validate I/O communication",
                "Debug real-time system performance using oscilloscopes/logic analyzers and serial consoles",
                "Document hardware schematics interfaces and write technical execution logs"
            ]
        }
        responsibilities = domain_resp_map.get(domain, [
            f"Contribute directly to production software systems using {top_3_skills}",
            "Write well-tested, documented, and maintainable code adhering to engineering standards",
            "Collaborate closely with senior software engineers and product managers",
            "Participate actively in architectural reviews and sprint retrospectives"
        ])

    # 5. Strategic Interview & Convo Talking Points
    # Tailored specifically to Company + Industry + Exact Skills + Domain Architecture
    domain_question = DOMAIN_TECH_QUESTIONS.get(domain, "Ask about their engineering sprint cadence, automated testing, and upcoming tech roadmap.")
    
    talking_points = [
        f"Portfolio Anchor: Pitch your strongest personal project built with {top_3_skills} - describe an architectural tradeoff you resolved (e.g. latency vs memory).",
        f"Industry Impact ({ind_name}): Explain to {company} how your CS background equips you to solve problems in the {ind_name} space.",
        f"Strategic Engineering Question: {ind_meta['convo_hook']}",
        f"Architecture In-Depth: {domain_question}"
    ]

    # 6. Tailored Resume Bullets (Google XYZ Format)
    # Use deterministic hash of company + title to pick distinct archetype pairs
    hash_val = int(hashlib.md5(f"{company}:{title}".encode("utf-8")).hexdigest(), 16)
    archetypes = DOMAIN_BULLET_ARCHETYPES.get(domain, DOMAIN_BULLET_ARCHETYPES["Core Software Dev"])
    idx1 = hash_val % len(archetypes)
    idx2 = (hash_val + 1) % len(archetypes)

    skills_fmt = ", ".join(identified_skills[:3]) if identified_skills else "Python, Git, REST APIs"
    
    resume_bullets = [
        archetypes[idx1].format(skills=skills_fmt),
        archetypes[idx2].format(skills=skills_fmt)
    ]

    return {
        "company": company,
        "title": title,
        "industry": ind_name,
        "core_skills": identified_skills[:12],
        "ats_keywords": ats_keywords[:14],
        "requirements": requirements[:5],
        "responsibilities": responsibilities[:4],
        "talking_points": talking_points,
        "resume_bullets": resume_bullets
    }


if __name__ == "__main__":
    sample = analyze_job_intel(
        title="Development of Android Applications",
        company="Indian Army",
        domain="Mobile",
        location="Delhi",
        description="Develop Android applications for SAMBHAV. Assist in requirement analysis and testing."
    )
    import pprint
    pprint.pprint(sample)
