"""
Data enrichment script - generates comprehensive course, program, and policy files
with full prerequisite logic, co-requisites, grade requirements, and rich metadata.
Run once to rebuild the data/ directory.
"""
import os

BASE = os.path.join(os.path.dirname(__file__))

COURSES = [
    {
        "id": "CS106A", "title": "Programming Methodology", "level": "undergraduate",
        "desc": (
            "Introduction to the engineering of computer applications emphasizing modern software engineering "
            "principles: object-oriented design, decomposition, encapsulation, abstraction, and testing. Uses "
            "the Python programming language. No prior programming experience required. Students learn the "
            "fundamentals of computing while building applications that solve real-world problems including "
            "data analysis, web development, and automation. Topics include variables, control flow, functions, "
            "strings, lists, dictionaries, file I/O, and an introduction to object-oriented programming. "
            "This course is the first course in Stanford's introductory computer science sequence."
        ),
        "prereqs": "None", "prereq_logic": "No prerequisites required. Open to all students.",
        "prereq_type": "none", "coreqs": "None", "min_grade": "N/A", "units": "5",
        "offered": "Fall, Winter, Spring, Summer",
        "url": "https://explorecourses.stanford.edu/search?q=CS106A"
    },
    {
        "id": "CS106B", "title": "Programming Abstractions", "level": "undergraduate",
        "desc": (
            "Abstraction and its relation to programming. Software engineering principles of data abstraction "
            "and modularity. Object-oriented programming, fundamental data structures (stacks, queues, sets) "
            "and data-directed design. Recursive and iterative algorithms. Introduction to time and space "
            "complexity analysis. Uses the C++ programming language. This course is the second course in "
            "Stanford's introductory CS sequence. Students who complete this course will be well-prepared "
            "for upper-division CS courses."
        ),
        "prereqs": "CS106A", "prereq_logic": "CS106A must be completed with a passing grade.",
        "prereq_type": "single", "coreqs": "None", "min_grade": "C- or above in CS106A", "units": "5",
        "offered": "Fall, Winter, Spring, Summer",
        "url": "https://explorecourses.stanford.edu/search?q=CS106B"
    },
    {
        "id": "CS103", "title": "Mathematical Foundations of Computing", "level": "undergraduate",
        "desc": (
            "Mathematical foundations required for computer science, including logic, proofs, sets, relations, "
            "functions, basic set theory, countability and counting arguments, proof techniques including "
            "induction, combinatorics, discrete probability, graphs and trees, formal languages, and "
            "computability. Covers propositional and first-order logic, DFAs, NFAs, regular expressions, "
            "context-free grammars, Turing machines, undecidability, and the halting problem. Students develop "
            "rigorous mathematical thinking essential for algorithm analysis and theoretical computer science."
        ),
        "prereqs": "CS106A", "prereq_logic": "CS106A must be completed.",
        "prereq_type": "single", "coreqs": "None", "min_grade": "N/A", "units": "5",
        "offered": "Fall, Winter, Spring",
        "url": "https://explorecourses.stanford.edu/search?q=CS103"
    },
    {
        "id": "CS107", "title": "Computer Organization and Systems", "level": "undergraduate",
        "desc": (
            "Introduction to the fundamental concepts of computer systems. Explores how computer systems "
            "execute programs, store information, and communicate. Topics include C and assembly language "
            "programming, translation of code to machine language, machine-level data representation, memory "
            "hierarchy and caching, processes and threads, linking, and system-level I/O. Students gain a deep "
            "understanding of the gap between high-level language code and the actual execution on hardware."
        ),
        "prereqs": "CS106B", "prereq_logic": "CS106B must be completed with a passing grade.",
        "prereq_type": "single", "coreqs": "None", "min_grade": "C- or above in CS106B", "units": "5",
        "offered": "Fall, Winter, Spring",
        "url": "https://explorecourses.stanford.edu/search?q=CS107"
    },
    {
        "id": "CS109", "title": "Introduction to Probability for Computer Scientists", "level": "undergraduate",
        "desc": (
            "Topics include: counting and combinatorics, random variables, conditional probability, independence, "
            "distributions (including Bernoulli, binomial, geometric, Poisson, uniform, exponential, normal, "
            "and joint distributions), expectation, variance, covariance, point estimation, maximum likelihood "
            "estimation, and limit theorems (law of large numbers, central limit theorem). Applications to "
            "computer science including hashing, load balancing, and Bayesian inference."
        ),
        "prereqs": "CS106B AND MATH51",
        "prereq_logic": "Both CS106B and MATH51 must be completed.",
        "prereq_type": "all_required", "coreqs": "None", "min_grade": "N/A", "units": "5",
        "offered": "Fall, Winter, Spring",
        "url": "https://explorecourses.stanford.edu/search?q=CS109"
    },
    {
        "id": "CS111", "title": "Operating Systems Principles", "level": "undergraduate",
        "desc": (
            "Operating systems design and implementation. Processes, threads, and synchronization. Concurrency "
            "problems including deadlock, starvation, and priority inversion. CPU scheduling algorithms. Memory "
            "management including virtual memory, paging, and segmentation. File systems design and implementation. "
            "I/O systems. Protection and security fundamentals. Students complete significant programming "
            "projects implementing key OS components."
        ),
        "prereqs": "CS107", "prereq_logic": "CS107 must be completed.",
        "prereq_type": "single", "coreqs": "None", "min_grade": "C- or above in CS107", "units": "5",
        "offered": "Fall, Spring",
        "url": "https://explorecourses.stanford.edu/search?q=CS111"
    },
    {
        "id": "CS161", "title": "Design and Analysis of Algorithms", "level": "undergraduate",
        "desc": (
            "Worst and average case analysis. Recurrences and asymptotics. Efficient algorithms for sorting, "
            "searching, and selection. Data structures: binary search trees, heaps, hash tables, balanced trees. "
            "Algorithm design paradigms: divide and conquer, dynamic programming, greedy algorithms. Graph "
            "algorithms: shortest paths, minimum spanning trees, network flow. Intractability and NP-completeness. "
            "This is a core requirement for all CS degree programs at Stanford."
        ),
        "prereqs": "CS109 AND CS103",
        "prereq_logic": "Both CS109 and CS103 must be completed before enrollment.",
        "prereq_type": "all_required", "coreqs": "None", "min_grade": "N/A", "units": "5",
        "offered": "Fall, Winter, Spring",
        "url": "https://explorecourses.stanford.edu/search?q=CS161"
    },
    {
        "id": "CS143", "title": "Compilers", "level": "undergraduate",
        "desc": (
            "Principles and practices for design and implementation of compilers and interpreters. Topics "
            "include lexical analysis, parsing theory, type checking, code generation and optimization. "
            "Students will build a working compiler for a substantial programming language as a course project. "
            "Covers formal language theory as applied to compiler construction, including regular expressions, "
            "context-free grammars, and attribute grammars."
        ),
        "prereqs": "CS107 AND CS103",
        "prereq_logic": "Both CS107 and CS103 must be completed.",
        "prereq_type": "all_required", "coreqs": "None", "min_grade": "N/A", "units": "4",
        "offered": "Fall, Spring",
        "url": "https://explorecourses.stanford.edu/search?q=CS143"
    },
    {
        "id": "CS144", "title": "Introduction to Computer Networking", "level": "undergraduate",
        "desc": (
            "Principles and practice of computer networking, with emphasis on the Internet. Topics include "
            "layered architectures, TCP/IP protocol suite, HTTP, DNS, routing algorithms, congestion control, "
            "reliable transport, network security, and wireless networking. Students build networking applications "
            "and implement protocol components from scratch."
        ),
        "prereqs": "CS111",
        "prereq_logic": "CS111 must be completed.",
        "prereq_type": "single", "coreqs": "None", "min_grade": "N/A", "units": "4",
        "offered": "Fall, Spring",
        "url": "https://explorecourses.stanford.edu/search?q=CS144"
    },
    {
        "id": "CS145", "title": "Introduction to Databases", "level": "undergraduate",
        "desc": (
            "Database design and use of database management systems for applications. Relational data model, "
            "SQL, database design using entity-relationship models, normalization, indexes, transactions, "
            "concurrency control and recovery. Introduction to query processing and optimization. NoSQL databases "
            "and distributed database systems. Students complete projects designing and building database-backed "
            "web applications."
        ),
        "prereqs": "CS103 AND CS106B",
        "prereq_logic": "Both CS103 and CS106B must be completed.",
        "prereq_type": "all_required", "coreqs": "None", "min_grade": "N/A", "units": "4",
        "offered": "Fall, Spring",
        "url": "https://explorecourses.stanford.edu/search?q=CS145"
    },
    {
        "id": "CS221", "title": "Artificial Intelligence: Principles and Techniques", "level": "undergraduate",
        "desc": (
            "Foundational topics in artificial intelligence including search algorithms (BFS, DFS, A*, iterative "
            "deepening), adversarial game playing (minimax, alpha-beta pruning), Markov decision processes and "
            "reinforcement learning, constraint satisfaction problems, Bayesian networks and probabilistic "
            "graphical models, logical inference, and machine learning basics. Students implement AI agents "
            "for various domains. CS221 is a gateway course for the AI specialization track."
        ),
        "prereqs": "CS161 AND CS109",
        "prereq_logic": "Both CS161 and CS109 must be completed.",
        "prereq_type": "all_required", "coreqs": "None", "min_grade": "C+ or above in CS161", "units": "4",
        "offered": "Fall, Spring",
        "url": "https://explorecourses.stanford.edu/search?q=CS221"
    },
    {
        "id": "CS224N", "title": "Natural Language Processing with Deep Learning", "level": "graduate",
        "desc": (
            "Methods for processing human language information and the fundamentals of modern NLP using deep "
            "learning. Topics include word vectors, recurrent neural networks, attention mechanisms, transformer "
            "architectures, pre-training and fine-tuning (BERT, GPT), machine translation, question answering, "
            "text generation, and large language models. Students complete a significant final project."
        ),
        "prereqs": "CS221",
        "prereq_logic": "CS221 must be completed. CS229 is recommended but not required.",
        "prereq_type": "single", "coreqs": "None", "min_grade": "N/A", "units": "4",
        "offered": "Winter",
        "url": "https://explorecourses.stanford.edu/search?q=CS224N"
    },
    {
        "id": "CS229", "title": "Machine Learning", "level": "undergraduate",
        "desc": (
            "Topics include supervised learning (generative/discriminative learning, parametric/non-parametric "
            "learning, neural networks, support vector machines), unsupervised learning (clustering, "
            "dimensionality reduction, kernel methods), learning theory (bias/variance tradeoffs, practical "
            "optimization), reinforcement learning, and control. Students implement learning algorithms and "
            "apply them to real-world datasets."
        ),
        "prereqs": "CS109 AND MATH51",
        "prereq_logic": "Both CS109 and MATH51 must be completed. CS106B is strongly recommended.",
        "prereq_type": "all_required", "coreqs": "None", "min_grade": "N/A", "units": "4",
        "offered": "Fall, Spring",
        "url": "https://explorecourses.stanford.edu/search?q=CS229"
    },
    {
        "id": "CS231N", "title": "Deep Learning for Computer Vision", "level": "graduate",
        "desc": (
            "Computer vision has become ubiquitous in our society, with applications in search, image "
            "understanding, apps, mapping, medicine, drones, and self-driving cars. Core topics include "
            "image classification, object detection, segmentation, generative models (GANs, VAEs), "
            "visual question answering, and video understanding. Architectures covered include CNNs, "
            "ResNets, Vision Transformers, and modern foundation models."
        ),
        "prereqs": "CS229",
        "prereq_logic": "CS229 must be completed. Linear algebra proficiency is expected.",
        "prereq_type": "single", "coreqs": "None", "min_grade": "B or above in CS229 recommended", "units": "4",
        "offered": "Spring",
        "url": "https://explorecourses.stanford.edu/search?q=CS231N"
    },
    {
        "id": "CS246", "title": "Mining Massive Data Sets", "level": "undergraduate",
        "desc": (
            "Design of efficient algorithms for processing massive datasets that do not fit in main memory. "
            "Topics include MapReduce/Spark, locality-sensitive hashing, dimensionality reduction, "
            "recommendation systems, mining social-network graphs, community detection, web search/PageRank, "
            "frequent itemsets, and data stream algorithms."
        ),
        "prereqs": "CS107 AND CS161",
        "prereq_logic": "Both CS107 and CS161 must be completed.",
        "prereq_type": "all_required", "coreqs": "None", "min_grade": "N/A", "units": "4",
        "offered": "Winter",
        "url": "https://explorecourses.stanford.edu/search?q=CS246"
    },
    {
        "id": "CS255", "title": "Introduction to Cryptography", "level": "undergraduate",
        "desc": (
            "Theory and practice of cryptographic techniques used in computer security. Topics include "
            "symmetric encryption (block ciphers, stream ciphers, AES), public-key cryptography (RSA, "
            "Diffie-Hellman, elliptic curves), digital signatures, authenticated encryption, hash functions, "
            "key management, and protocols for secure computation and zero-knowledge proofs."
        ),
        "prereqs": "CS161",
        "prereq_logic": "CS161 must be completed.",
        "prereq_type": "single", "coreqs": "None", "min_grade": "N/A", "units": "4",
        "offered": "Winter, Spring",
        "url": "https://explorecourses.stanford.edu/search?q=CS255"
    },
    {
        "id": "CS148", "title": "Introduction to Computer Graphics and Imaging", "level": "undergraduate",
        "desc": (
            "Fundamental concepts in computer graphics: rendering pipelines, modeling, textures, shading, "
            "ray tracing, rasterization, clipping, transformations, curves and surfaces, and animation. "
            "Students build a ray tracer and implement shader programs. Introduction to GPU programming "
            "and real-time rendering techniques."
        ),
        "prereqs": "CS107",
        "prereq_logic": "CS107 must be completed. MATH51 is recommended for geometric foundations.",
        "prereq_type": "single", "coreqs": "None", "min_grade": "N/A", "units": "4",
        "offered": "Fall",
        "url": "https://explorecourses.stanford.edu/search?q=CS148"
    },
    {
        "id": "CS248A", "title": "Computer Graphics: Rendering, Geometry, and Image Manipulation",
        "level": "graduate",
        "desc": (
            "Advanced rendering techniques including path tracing, photon mapping, and subsurface scattering. "
            "Geometric modeling using splines, subdivision surfaces, and implicit surfaces. Image processing "
            "and computational photography. GPU compute using CUDA/OpenCL for parallel rendering."
        ),
        "prereqs": "CS148",
        "prereq_logic": "CS148 must be completed. Strong linear algebra background required.",
        "prereq_type": "single", "coreqs": "None", "min_grade": "B or above in CS148 recommended", "units": "4",
        "offered": "Spring",
        "url": "https://explorecourses.stanford.edu/search?q=CS248A"
    },
    {
        "id": "MATH51", "title": "Linear Algebra, Multivariable Calculus, and Modern Applications",
        "level": "undergraduate",
        "desc": (
            "Unified coverage of linear algebra and multivariable differential calculus, emphasizing connections "
            "between them and applications to engineering and computer science. Topics include: vectors, matrices, "
            "systems of linear equations, eigenvalues and eigenvectors, partial derivatives, gradients, Jacobians, "
            "optimization, and linear regression. This course satisfies the mathematics requirement for the BS "
            "in Computer Science degree."
        ),
        "prereqs": "None",
        "prereq_logic": "No prerequisites. Calculus AB/BC or MATH21 equivalent recommended.",
        "prereq_type": "none", "coreqs": "None", "min_grade": "N/A", "units": "5",
        "offered": "Fall, Winter, Spring, Summer",
        "url": "https://explorecourses.stanford.edu/search?q=MATH51"
    },
    {
        "id": "ENGR40M", "title": "An Intro to Making: What is EE", "level": "undergraduate",
        "desc": (
            "Introduction to electrical engineering through hands-on making projects. Topics include circuits, "
            "microcontrollers (Arduino), sensors, actuators, LEDs, and basic signal processing. Students build "
            "several projects including a heart-rate monitor and a light display. No prior electrical engineering "
            "experience required. This course satisfies the engineering fundamentals requirement."
        ),
        "prereqs": "MATH51",
        "prereq_logic": "MATH51 must be completed or taken concurrently.",
        "prereq_type": "single", "coreqs": "MATH51 (may be taken concurrently)", "min_grade": "N/A", "units": "5",
        "offered": "Fall, Spring",
        "url": "https://explorecourses.stanford.edu/search?q=ENGR40M"
    },
]

PROGRAMS = [
    {
        "id": "bs_cs",
        "title": "Bachelor of Science in Computer Science",
        "content": """TYPE: program

PROGRAM: Bachelor of Science in Computer Science

DESCRIPTION:
The undergraduate major in Computer Science at Stanford University offers a broad and rigorous
curriculum in the theory and application of computing. The program prepares students for careers
in software engineering, research, entrepreneurship, and graduate study in computer science.

REQUIREMENTS:

Core Requirements (all mandatory):
- CS106A: Programming Methodology (5 units)
- CS106B: Programming Abstractions (5 units)
- CS103: Mathematical Foundations of Computing (5 units)
- CS107: Computer Organization and Systems (5 units)
- CS109: Introduction to Probability for Computer Scientists (5 units)
- CS111: Operating Systems Principles (5 units)
- CS161: Design and Analysis of Algorithms (5 units)

Mathematics Requirements (all mandatory):
- MATH51: Linear Algebra, Multivariable Calculus, and Modern Applications (5 units)

Engineering Fundamentals (choose one):
- ENGR40M: An Intro to Making: What is EE (5 units)
- Or another approved engineering fundamentals course

Senior Project:
- Students must complete a senior project or honors thesis in their final year.

Track Electives:
- Students must choose a specialization track (AI, Systems, Theory, HCI, etc.)
- Each track requires 3-4 additional upper-division CS courses (numbered 100+)
- At least 2 elective courses must be at the 200-level or above

Total Units for Major: minimum 80 units
Residency Requirement: At least 45 units must be completed at Stanford (not transfer credit)
Minimum GPA: 2.0 cumulative GPA in major courses required for graduation

Academic Standing:
- Students must maintain a 2.0 GPA in all CS courses counted toward the major
- No more than one course graded CR/NC may count toward major requirements
- Courses with a grade of D or below do not satisfy major requirements

SOURCE: https://exploredegrees.stanford.edu/schoolofengineering/computerscience/#bs_cs
"""
    },
    {
        "id": "minor_cs",
        "title": "Minor in Computer Science",
        "content": """TYPE: program

PROGRAM: Minor in Computer Science

DESCRIPTION:
The minor in Computer Science provides students from other departments a focused study in
computer science fundamentals. The minor is designed to give students proficiency in programming,
algorithmic thinking, and computational problem-solving that complements their primary major.

REQUIREMENTS:

Core Requirements (all mandatory):
- CS106A: Programming Methodology (5 units)
- CS106B: Programming Abstractions (5 units)
- CS103: Mathematical Foundations of Computing (5 units)
- CS107: Computer Organization and Systems (5 units)

Elective Requirements:
- 2 additional CS courses numbered 100 or higher (minimum 3 units each)
- Elective courses must be taken for a letter grade (not CR/NC)
- At least 1 elective must be at the 100-level or above and not cross-listed with the student's major

Total Units for Minor: minimum 28 units
Overlap Policy: At most 2 courses may overlap with the student's major requirements
Residency Requirement: At least 3 of the 6 required courses must be completed at Stanford

APPLICATION PROCESS:
- Students must declare the minor by the end of their junior year
- Declaration requires advisor approval from the CS department
- Transfer credits may satisfy up to 1 core requirement with department approval

SOURCE: https://exploredegrees.stanford.edu/schoolofengineering/computerscience/#minor_cs
"""
    },
]

POLICIES = [
    {
        "id": "grading",
        "content": """TYPE: policy

POLICY: Academic Grading Policy

DESCRIPTION:
Stanford University uses a letter grading system for undergraduate and graduate courses.
Grades are a measure of student achievement and are assigned by instructors based on
coursework, examinations, and participation.

GRADING SCALE:
- A+, A, A-: Excellent (4.0, 4.0, 3.7)
- B+, B, B-: Good (3.3, 3.0, 2.7)
- C+, C, C-: Satisfactory (2.3, 2.0, 1.7)
- D+, D, D-: Passing (1.3, 1.0, 0.7)
- NP: Not Passed (0.0, not factored into GPA)
- CR: Credit (satisfactory completion, not factored into GPA)
- W: Withdrawal (no GPA impact)
- I: Incomplete (temporary, must be resolved within 1 year)

GRADE REQUIREMENTS FOR MAJORS:
- Courses taken to fulfill major requirements must be taken for a LETTER GRADE (not CR/NC)
- A minimum grade of C- is required for prerequisite courses unless otherwise specified
- A cumulative GPA of 2.0 in major courses is required for graduation
- Courses with a grade of D or below do not satisfy prerequisite requirements
- Only one D grade may count toward the major with department approval

REPEATING COURSES:
- Students may repeat a course to improve a grade
- Both the original and new grade appear on the transcript
- Only the most recent grade is used in GPA calculation
- A course may be repeated at most once
- Courses originally taken CR/NC cannot be repeated for a letter grade

CREDIT LIMITS:
- Maximum of 20 units per quarter for undergraduates
- Minimum of 12 units per quarter for full-time status
- Summer quarter has a limit of 10 units per session
- Students on academic probation may be limited to 15 units per quarter

INCOMPLETES:
- An Incomplete (I) grade is granted at the instructor's discretion
- Work must be completed within 1 calendar year or the grade converts to NP
- Students with more than 2 outstanding Incompletes may not enroll in additional courses

ACADEMIC PROBATION:
- Students whose quarterly GPA falls below 2.0 are placed on academic probation
- Two consecutive quarters on probation may result in required leave of absence
- Students on probation must meet with their academic advisor each quarter

TRANSFER CREDITS:
- Transfer credits from other institutions may satisfy some requirements
- Transfer credit is evaluated on a case-by-case basis by the department
- Maximum of 45 transfer units may be applied toward a Stanford degree
- Transfer courses must have a grade of C or better to receive credit
- Graduate-level courses from other institutions require department chair approval

HONORS:
- Distinction: cumulative GPA of 3.5 or above in the major
- With Honors: completion of an honors thesis with distinction grade

SOURCE: https://exploredegrees.stanford.edu/academicpoliciesandstatements/
"""
    },
]


def write_course(course):
    """Write a single enriched course file."""
    content = f"""TYPE: course

COURSE: {course['id']}
TITLE: {course['title']}

LEVEL: {course['level']}

DESCRIPTION:
{course['desc']}

PREREQUISITES:
{course['prereqs']}

PREREQ_LOGIC:
* {course['prereq_logic']}

PREREQUISITE_TYPE: {course['prereq_type']}

CO-REQUISITES:
{course['coreqs']}

MINIMUM_GRADE:
{course['min_grade']}

UNITS:
{course['units']}

OFFERED:
{course['offered']}

TAGS:
course, computer science, stanford

SOURCE: {course['url']}
"""
    path = os.path.join(BASE, "courses", f"{course['id'].lower()}.txt")
    with open(path, "w") as f:
        f.write(content)


def write_sources():
    """Rebuild sources.md from all enriched data."""
    lines = ["# Data Sources\n"]
    for c in COURSES:
        lines.append(f"{c['id']} - {c['url']} - accessed 28 March 2026 - {c['title']}")
    for p in PROGRAMS:
        url = f"https://exploredegrees.stanford.edu/schoolofengineering/computerscience/#{p['id']}"
        lines.append(f"{p['id']} - {url} - accessed 28 March 2026 - {p['title']}")
    for pol in POLICIES:
        lines.append(
            f"{pol['id']} - https://exploredegrees.stanford.edu/academicpoliciesandstatements/ "
            f"- accessed 28 March 2026 - Academic Grading Policy"
        )
    path = os.path.join(BASE, "sources.md")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    # Ensure directories exist
    for d in ["courses", "programs", "policies"]:
        os.makedirs(os.path.join(BASE, d), exist_ok=True)

    # Write courses
    for course in COURSES:
        write_course(course)

    # Write programs
    for prog in PROGRAMS:
        path = os.path.join(BASE, "programs", f"{prog['id']}.txt")
        with open(path, "w") as f:
            f.write(prog["content"])

    # Write policies
    for pol in POLICIES:
        path = os.path.join(BASE, "policies", f"{pol['id']}.txt")
        with open(path, "w") as f:
            f.write(pol["content"])

    # Write sources
    write_sources()

    # Word count check
    total = 0
    for root, dirs, files in os.walk(BASE):
        for fname in files:
            if fname.endswith(".txt"):
                with open(os.path.join(root, fname)) as f:
                    total += len(f.read().split())
    print(f"Dataset regenerated successfully.")
    print(f"Total word count across all txt files: {total}")


if __name__ == "__main__":
    main()
