"""
B.Tech CSE Relevance and Filtering Engine.
Strictly filters out non-CSE roles (Hotel Management, HR, Sales, Telecalling, etc.)
and tags relevant CSE tech stacks and domains.
"""
import re

# Definite non-CSE keywords in Title or Description that auto-reject a listing
EXCLUDED_KEYWORDS = [
    # Hospitality / Hotel
    "hotel", "hospitality", "chef", "cook", "culinary", "restaurant", "steward", "housekeeping", "food & beverage", "f&b",
    # Human Resources & Admin
    "human resources", "talent acquisition", "recruiter", "recruitment", "receptionist", "front office", "office assistant", "personal assistant", "executive assistant", "stenographer", "storyteller",
    # Sales & BPO & Business Dev (Strict non-tech)
    "telecaller", "telecalling", "telesales", "inside sales", "b2b sales", "field sales", "sales executive", "sales intern", "sales",
    "business development", "bda", "bde", "cold calling", "lead generation", "client acquisition", "market research", "business operations",
    # Marketing & Social Media (pure non-engineering)
    "marketing", "social media", "brand marketing", "growth marketing", "digital marketing", "seo intern", "public relations",
    # Accounting & Finance
    "chartered accountant", "accounts executive", "bookkeeping", "audit intern", "taxation", "tally", "finance intern",
    # Content & Media (non-tech)
    "content writer", "content writing", "copywriter", "ghostwriter", "seo writer", "creative writer", "journalist", "news anchor", "voiceover",
    # Creative Design & Video (pure non-engineering)
    "graphic designer", "graphic design", "visual design", "video editor", "video editing", "fashion design", "interior design", "animator", "2d animator", "3d animator", "artist",
    # Healthcare & Others
    "nursing", "dietitian", "nutritionist", "pharmacy", "medical officer", "dentist", "tour guide", "event management", "event coordinator", "legal intern", "law intern", "founders office",
]

# Core CSE domain patterns
DOMAIN_PATTERNS = {
    "AI / ML": [
        r"\b(machine learning|deep learning|data science|ai engineer|ai developer|artificial intelligence|nlp|computer vision|llm|genai|neural network|pytorch|tensorflow|scikit-learn)\b"
    ],
    "Full Stack": [
        r"\b(full\s*stack|fullstack|mern|mean)\b"
    ],
    "Frontend": [
        r"\b(frontend|front\s*end|react|reactjs|vue|vuejs|angular|next\.?js|html5|css3|ui developer)\b"
    ],
    "Backend": [
        r"\b(backend|back\s*end|node\.?js|express\.?js|django|fastapi|flask|spring boot|golang|rails|ruby|php|rest api|microservices)\b"
    ],
    "Mobile": [
        r"\b(mobile app|android|ios|flutter|react native|kotlin|swift)\b"
    ],
    "Cloud & DevOps": [
        r"\b(devops|cloud|aws|azure|gcp|kubernetes|docker|ci[/-]?cd|sre|terraform|linux admin)\b"
    ],
    "Data Engineering": [
        r"\b(data engineer|data engineering|sql|etl|spark|kafka|big data|data analyst|database admin)\b"
    ],
    "Cybersecurity": [
        r"\b(cyber\s*security|information security|infosec|ethical hacking|penetration|soc analyst|network security)\b"
    ],
    "Systems & Embedded": [
        r"\b(embedded|iot|c\+\+|firmware|robotics|fpga|microcontroller|rtos|device driver)\b"
    ],
    "QA & SDET": [
        r"\b(sdet|automation test|qa engineer|test engineer|selenium|cypress|playwright)\b"
    ],
    "Core Software Dev": [
        r"\b(software engineer|software developer|sde|programmer|coding intern|java developer|python developer|c\+\+ developer|golang developer)\b"
    ]
}

TECH_TAGS = [
    "Python", "JavaScript", "TypeScript", "React", "Node.js", "Express",
    "Java", "Spring Boot", "C++", "C#", ".NET", "Golang", "Rust",
    "Flutter", "Android", "iOS", "Kotlin", "Swift",
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Linux",
    "SQL", "PostgreSQL", "MongoDB", "Redis", "GraphQL", "Kafka",
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "OpenCV",
    "Next.js", "Tailwind CSS", "Git"
]

TAG_REGEXES = {
    tag: re.compile(r"\b" + re.escape(tag.lower()) + r"\b", re.IGNORECASE)
    for tag in TECH_TAGS
}
TAG_REGEXES["C++"] = re.compile(r"(?:\bc\+\+|\bcxx\b)", re.IGNORECASE)
TAG_REGEXES["C#"] = re.compile(r"(?:\bc\#|\bc-sharp\b)", re.IGNORECASE)
TAG_REGEXES[".NET"] = re.compile(r"(?:\.net|dotnet)\b", re.IGNORECASE)
TAG_REGEXES["Node.js"] = re.compile(r"(?:node\.?js|nodejs)\b", re.IGNORECASE)
TAG_REGEXES["React"] = re.compile(r"(?:react\.?js|reactjs|\breact\b)", re.IGNORECASE)


def classify_cse_role(title: str, description: str = "") -> dict:
    """
    Evaluates if an internship is relevant to B.Tech Computer Science / Engineering.
    Returns:
        {
            "is_cse": bool,
            "domain": str,
            "score": int,
            "tags": list[str],
            "reason": str
        }
    """
    text = f"{title} {description}".lower()
    title_lower = title.lower()

    # Step 1: Check negative blacklist against title
    for bad in EXCLUDED_KEYWORDS:
        bad_pattern = rf"\b{re.escape(bad)}\b"
        if re.search(bad_pattern, title_lower):
            return {
                "is_cse": False,
                "domain": "Non-Tech",
                "score": 0,
                "tags": [],
                "reason": f"Excluded due to blacklist keyword in title: '{bad}'"
            }

    # Step 2: Check domain matches
    matched_domains = []
    for domain, patterns in DOMAIN_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, title_lower, re.IGNORECASE):
                matched_domains.append((domain, 2))
                break
            elif description and re.search(pat, text, re.IGNORECASE):
                matched_domains.append((domain, 1))
                break

    # Extract tech tags
    extracted_tags = []
    for tag, reg in TAG_REGEXES.items():
        if reg.search(text):
            extracted_tags.append(tag)

    # Step 3: Determine if it qualifies as CSE
    if matched_domains:
        primary_domain = matched_domains[0][0]
        score = 80 + min(len(extracted_tags) * 4, 20)
        return {
            "is_cse": True,
            "domain": primary_domain,
            "score": min(score, 100),
            "tags": extracted_tags,
            "reason": f"Matched CSE domain '{primary_domain}'"
        }

    if extracted_tags and any(k in title_lower for k in ["developer", "engineer", "programmer", "intern", "trainee", "tech"]):
        return {
            "is_cse": True,
            "domain": "Core Software Dev",
            "score": 75,
            "tags": extracted_tags,
            "reason": f"Tech stack tags identified: {', '.join(extracted_tags[:3])}"
        }

    return {
        "is_cse": False,
        "domain": "Unrelated",
        "score": 10,
        "tags": extracted_tags,
        "reason": "No CSE domain or tech stack detected in listing"
    }


def is_cse_internship(title: str, description: str = "") -> bool:
    result = classify_cse_role(title, description)
    return result["is_cse"]
