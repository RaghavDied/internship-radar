"""
Deep Job Description & Requirements Intelligence Engine.
Extracts ATS keywords, core skills, eligibility requirements, responsibilities,
conversational talking points, and Google XYZ resume bullet suggestions.
"""
import re

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
        "Embedded C", "Internet of Things (IoT)", "RTOS", "Microcontrollers"
    ]
}

# Generic engineering ATS buzzwords
ATS_POWER_KEYWORDS = [
    "Object-Oriented Programming (OOP)", "Data Structures & Algorithms", "System Design",
    "Agile / Scrum Methodologies", "Code Review & Refactoring", "Test-Driven Development (TDD)",
    "API Integration", "Unit & Integration Testing", "Version Control (Git)",
    "Clean Code Architecture", "Scalability & Performance Optimization", "Cross-Functional Collaboration"
]

DOMAIN_RESUME_TEMPLATES = {
    "Full Stack": [
        "Architected and deployed full-stack web features using {skills}, decreasing API response times by 30% through optimized queries.",
        "Engineered end-to-end responsive components and secure RESTful backend endpoints, collaborating in daily agile sprints."
    ],
    "Backend": [
        "Designed and implemented modular backend microservices with {skills}, handling concurrent requests and ensuring 99.9% uptime.",
        "Optimized relational database schema and caching layers with Redis/SQL, reducing database query overhead by 40%."
    ],
    "Frontend": [
        "Developed high-performance interactive user interfaces in {skills}, improving user engagement and PageSpeed metrics by 25%.",
        "Refactored state management architecture and integrated REST APIs, ensuring seamless cross-browser consistency and responsive design."
    ],
    "AI / ML": [
        "Trained and evaluated deep learning / machine learning models using {skills}, achieving over 90% validation accuracy on benchmarks.",
        "Built automated data preprocessing pipelines and fine-tuned predictive algorithms, accelerating model inference pipeline by 35%."
    ],
    "Mobile": [
        "Engineered native mobile application features with {skills}, adhering strictly to Material Design and modern MVVM architecture.",
        "Implemented offline caching, asynchronous network requests, and smooth UI animations, boosting app store user rating."
    ],
    "Cloud & DevOps": [
        "Containerized microservices using Docker and automated CI/CD deployment pipelines on AWS/Linux, slashing release cycles by 50%.",
        "Configured scalable cloud infrastructure monitoring and automated alerts, minimizing mean time to detection (MTTD)."
    ],
    "Data Engineering": [
        "Built resilient ETL data pipelines processing high-volume datasets using {skills}, enabling real-time analytics for stakeholders.",
        "Designed automated SQL reporting workflows and data lake schemas, eliminating manual data reconciliation delays."
    ],
    "Cybersecurity": [
        "Executed vulnerability assessments and security audits, identifying potential exploit vectors and hardening application security.",
        "Implemented robust authentication protocols, input validation, and OWASP Top 10 remediation strategies."
    ],
    "Core Software Dev": [
        "Implemented high-performance algorithms in {skills}, improving memory efficiency and reducing runtime complexity.",
        "Authored comprehensive unit tests and participated in rigorous code reviews, ensuring adherence to clean code standards."
    ]
}


def analyze_job_intel(title: str, company: str, domain: str, location: str, description: str = "", tags: list = None) -> dict:
    """
    Vividly and deeply scans a job opening, extracting high-signal requirements,
    ATS resume keywords, talking points, and tailored resume bullet points.
    """
    tags = tags or []
    full_text = f"{title} {description}".lower()
    
    # 1. Extract Core Technical Skills
    identified_skills = list(tags)
    for category, skills in TECH_TAXONOMY.items():
        for skill in skills:
            pattern = rf"\b{re.escape(skill.lower())}\b"
            if re.search(pattern, full_text) and skill not in identified_skills:
                identified_skills.append(skill)

    if not identified_skills:
        # Fallback to domain standards
        fallback_map = {
            "Frontend": ["JavaScript", "React.js", "HTML5", "CSS3", "Tailwind CSS", "Git"],
            "Backend": ["Python", "Node.js", "REST APIs", "PostgreSQL", "Docker", "Git"],
            "Full Stack": ["React.js", "Node.js", "JavaScript", "SQL", "REST APIs", "Git"],
            "AI / ML": ["Python", "PyTorch", "TensorFlow", "Scikit-Learn", "Pandas", "NumPy"],
            "Mobile": ["Android SDK", "Kotlin", "Java", "Mobile Architecture", "REST APIs"],
            "Cloud & DevOps": ["Linux", "Docker", "AWS", "CI/CD", "Git", "Shell Scripting"],
            "Cybersecurity": ["Network Security", "Linux", "Python", "Vulnerability Assessment", "OWASP"],
            "Data Engineering": ["SQL", "Python", "ETL Pipelines", "PostgreSQL", "Pandas"],
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
    top_3_skills = ", ".join(identified_skills[:3]) if identified_skills else "Python, Java, or JavaScript"
    requirements.append(f"Demonstrated hands-on project experience with {top_3_skills}")

    # Location / Work mode
    if "remote" in full_text or "work from home" in full_text or "(remote)" in location.lower():
        requirements.append("Strong asynchronous communication skills and ability to work autonomously in a remote setup")
    elif location and location != "Not specified":
        requirements.append(f"Availability for in-person / hybrid collaboration in {location}")
    else:
        requirements.append("Availability for full-time or part-time internship commitment (2 - 6 months)")

    requirements.append("Familiarity with version control workflows (Git / GitHub) and collaborative development")
    requirements.append("Proactive problem-solving attitude with ability to pick up new tools and frameworks quickly")

    # 4. Extract Key Responsibilities & Deliverables
    responsibilities = []
    if "responsibilities" in full_text or "day-to-day" in full_text:
        # Extract lines from description
        lines = [line.strip() for line in description.splitlines() if line.strip()]
        for line in lines:
            if re.match(r"^(\d+[\.\)]|[\-\*•])\s*", line):
                clean_line = re.sub(r"^(\d+[\.\)]|[\-\*•])\s*", "", line)
                if len(clean_line) > 20 and len(responsibilities) < 4:
                    responsibilities.append(clean_line)

    if not responsibilities:
        # Generate rich domain-specific responsibilities
        domain_resp_map = {
            "Frontend": [
                f"Develop, test, and maintain interactive web UI components using {identified_skills[0] if identified_skills else 'React'}",
                "Collaborate with designers to translate Figma prototypes into clean, responsive HTML/CSS code",
                "Integrate backend RESTful APIs and ensure seamless cross-device compatibility",
                "Optimize frontend load performance and debug UI/UX issues across browsers"
            ],
            "Backend": [
                f"Design, build, and optimize robust RESTful microservices using {identified_skills[0] if identified_skills else 'Node.js/Python'}",
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
                f"Develop and benchmark machine learning / deep learning pipelines using {identified_skills[0] if identified_skills else 'Python/PyTorch'}",
                "Perform data cleaning, feature engineering, and exploratory data analysis (EDA)",
                "Fine-tune pre-trained models and deploy predictive endpoints",
                "Document experiment results and present findings to engineering mentors"
            ],
            "Mobile": [
                f"Develop and ship features for native mobile applications using {identified_skills[0] if identified_skills else 'Android/Flutter'}",
                "Implement smooth UI components following platform-specific design guidelines",
                "Integrate third-party libraries, push notifications, and background sync services",
                "Profile memory usage and resolve app performance bottlenecks"
            ]
        }
        responsibilities = domain_resp_map.get(domain, [
            f"Contribute directly to production software systems using {top_3_skills}",
            "Write well-tested, documented, and maintainable code adhering to engineering standards",
            "Collaborate closely with senior software engineers and product managers",
            "Participate actively in architectural reviews and sprint retrospectives"
        ])

    # 5. Strategic Interview & Convo Talking Points
    talking_points = [
        f"Portfolio Anchor: Highlight your strongest personal project built with {top_3_skills} and explain an architectural tradeoff you made.",
        f"Problem Solving: Discuss how your background as a B.Tech CSE student equips you to contribute to {company}'s current technical initiatives.",
        f"Smart Question to Ask: Ask about {company}'s deployment cadence, test automation practices, or upcoming tech roadmap."
    ]

    # 6. Tailored Resume Bullets (Google XYZ Format)
    template_pair = DOMAIN_RESUME_TEMPLATES.get(domain, DOMAIN_RESUME_TEMPLATES["Core Software Dev"])
    skills_fmt = ", ".join(identified_skills[:3])
    resume_bullets = [
        template_pair[0].format(skills=skills_fmt),
        template_pair[1].format(skills=skills_fmt)
    ]

    return {
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
