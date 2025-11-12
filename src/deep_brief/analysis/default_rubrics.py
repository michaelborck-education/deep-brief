"""Default example rubrics for common presentation types."""

from deep_brief.analysis.rubric_system import Rubric, RubricBuilder


def create_academic_presentation_rubric() -> Rubric:
    """Create a rubric for academic presentations (conferences, seminars)."""
    builder = RubricBuilder(
        name="Academic Presentation",
        description="Evaluate academic presentations at conferences, seminars, or classroom settings",
    )

    # Content Category
    content = builder.add_category(
        name="Content Quality",
        description="Evaluation of presentation content",
        weight=2.0,
    )
    content.add_criterion(
        name="Research Depth",
        description="Demonstrates thorough understanding of research methodology and findings",
        weight=1.5,
        scoring_guide="1=Superficial, 3=Adequate, 5=Comprehensive and insightful",
    )
    content.add_criterion(
        name="Clear Thesis/Purpose",
        description="Main research question or contribution is clearly stated",
        weight=1.5,
        scoring_guide="1=Unclear, 3=Moderately clear, 5=Crystal clear",
    )
    content.add_criterion(
        name="Supporting Evidence",
        description="Uses relevant data, citations, and examples to support claims",
        weight=1.0,
        scoring_guide="1=Minimal, 3=Adequate citations, 5=Excellent sourcing",
    )

    # Delivery Category
    delivery = builder.add_category(
        name="Delivery & Presentation",
        description="Evaluation of speaking and visual presentation",
        weight=1.5,
    )
    delivery.add_criterion(
        name="Speaking Clarity",
        description="Speech is clear, at appropriate pace, and easy to understand",
        weight=1.0,
        scoring_guide="1=Hard to follow, 3=Generally clear, 5=Excellent clarity",
    )
    delivery.add_criterion(
        name="Engagement",
        description="Maintains audience attention through tone, eye contact, and enthusiasm",
        weight=1.0,
        scoring_guide="1=Monotone, 3=Adequate, 5=Highly engaging",
    )
    delivery.add_criterion(
        name="Visual Aids",
        description="Slides/visuals are clear, professional, and enhance understanding",
        weight=0.5,
        scoring_guide="1=Distracting, 3=Adequate, 5=Professional and effective",
    )

    # Organization Category
    org = builder.add_category(
        name="Organization & Structure",
        description="Logical flow and coherent presentation structure",
        weight=1.0,
    )
    org.add_criterion(
        name="Logical Flow",
        description="Ideas presented in logical sequence that's easy to follow",
        weight=1.0,
        scoring_guide="1=Disorganized, 3=Generally logical, 5=Excellent flow",
    )
    org.add_criterion(
        name="Time Management",
        description="Appropriately uses allocated time; covers material without rushing or excess",
        weight=0.5,
        scoring_guide="1=Way over/under time, 3=Slightly off, 5=Perfect timing",
    )

    # Set custom scoring scale
    builder.set_scoring_scale(
        min_score=1,
        max_score=5,
        labels={
            1: "Poor - Needs significant improvement",
            2: "Below Average - Notable deficiencies",
            3: "Average - Meets basic expectations",
            4: "Good - Exceeds expectations",
            5: "Excellent - Outstanding work",
        },
    )

    return builder.build(is_template=True, tags=["academic", "conference", "research"])


def create_business_pitch_rubric() -> Rubric:
    """Create a rubric for business pitches and startup presentations."""
    builder = RubricBuilder(
        name="Business Pitch",
        description="Evaluate business pitches, startup presentations, and investor pitches",
    )

    # Business Model Category
    business = builder.add_category(
        name="Business Model & Value Prop",
        description="Clarity of business model and value proposition",
        weight=2.0,
    )
    business.add_criterion(
        name="Clear Problem Statement",
        description="Identifies and articulates the problem being solved",
        weight=1.0,
        scoring_guide="1=Vague problem, 3=Clear problem, 5=Compelling problem",
    )
    business.add_criterion(
        name="Unique Value Proposition",
        description="Clearly explains what makes the solution unique and valuable",
        weight=1.5,
        scoring_guide="1=Generic, 3=Adequate differentiation, 5=Clear competitive advantage",
    )
    business.add_criterion(
        name="Market Understanding",
        description="Demonstrates knowledge of target market, size, and opportunity",
        weight=1.0,
        scoring_guide="1=No market analysis, 3=Basic market data, 5=In-depth market insights",
    )

    # Financial Category
    financial = builder.add_category(
        name="Financial Viability",
        description="Business financials and sustainability",
        weight=1.5,
    )
    financial.add_criterion(
        name="Revenue Model",
        description="Clear explanation of how the business makes money",
        weight=1.0,
        scoring_guide="1=Unclear, 3=Reasonable model, 5=Compelling monetization",
    )
    financial.add_criterion(
        name="Financial Projections",
        description="Realistic financial projections and path to profitability",
        weight=1.0,
        scoring_guide="1=No projections, 3=Basic numbers, 5=Detailed, realistic forecasts",
    )

    # Presentation Category
    presentation = builder.add_category(
        name="Presentation Quality",
        description="Delivery, visuals, and persuasiveness",
        weight=1.5,
    )
    presentation.add_criterion(
        name="Persuasiveness",
        description="Effectively persuades audience of business potential",
        weight=1.0,
        scoring_guide="1=Unconvincing, 3=Moderately persuasive, 5=Highly compelling",
    )
    presentation.add_criterion(
        name="Confidence & Credibility",
        description="Presenter demonstrates confidence and credibility in the idea",
        weight=0.75,
        scoring_guide="1=Uncertain, 3=Confident, 5=Highly credible and poised",
    )
    presentation.add_criterion(
        name="Visual Design",
        description="Pitch deck is professional, clean, and visually appealing",
        weight=0.75,
        scoring_guide="1=Poor design, 3=Adequate, 5=Professional, polished design",
    )

    builder.set_scoring_scale(
        min_score=1,
        max_score=5,
        labels={
            1: "Poor - Not investment-ready",
            2: "Below Average - Significant concerns",
            3: "Average - Interesting but needs work",
            4: "Good - Strong pitch",
            5: "Excellent - Ready to pitch to investors",
        },
    )

    return builder.build(
        is_template=True, tags=["business", "startup", "pitch", "investor"]
    )


def create_teaching_demo_rubric() -> Rubric:
    """Create a rubric for teaching demonstrations and lesson presentations."""
    builder = RubricBuilder(
        name="Teaching Demonstration",
        description="Evaluate teaching effectiveness, pedagogy, and classroom engagement",
    )

    # Pedagogy Category
    pedagogy = builder.add_category(
        name="Pedagogical Approach",
        description="Teaching methodology and instructional design",
        weight=2.0,
    )
    pedagogy.add_criterion(
        name="Learning Objectives",
        description="Clear learning objectives communicated to students",
        weight=1.0,
        scoring_guide="1=No objectives stated, 3=Objectives mentioned, 5=Clear, measurable objectives",
    )
    pedagogy.add_criterion(
        name="Instructional Design",
        description="Well-structured lesson with clear organization and flow",
        weight=1.5,
        scoring_guide="1=Disorganized, 3=Adequate structure, 5=Excellent instructional design",
    )
    pedagogy.add_criterion(
        name="Active Learning",
        description="Incorporates student engagement and active learning strategies",
        weight=1.0,
        scoring_guide="1=Lecture-only, 3=Some interaction, 5=Highly interactive",
    )

    # Content & Communication Category
    content = builder.add_category(
        name="Content & Communication",
        description="Accuracy, clarity, and depth of content delivery",
        weight=1.5,
    )
    content.add_criterion(
        name="Content Accuracy",
        description="Subject matter is accurate and free of errors",
        weight=0.75,
        scoring_guide="1=Significant errors, 3=Mostly accurate, 5=Fully accurate",
    )
    content.add_criterion(
        name="Explanation Clarity",
        description="Concepts explained clearly and at appropriate level",
        weight=1.0,
        scoring_guide="1=Confusing, 3=Generally clear, 5=Very clear and well-explained",
    )
    content.add_criterion(
        name="Use of Examples",
        description="Effective use of examples to illustrate concepts",
        weight=0.75,
        scoring_guide="1=No examples, 3=Adequate examples, 5=Excellent, relevant examples",
    )

    # Student Engagement Category
    engagement = builder.add_category(
        name="Student Engagement & Classroom Management",
        description="Ability to engage and manage students",
        weight=1.5,
    )
    engagement.add_criterion(
        name="Student Engagement",
        description="Maintains student attention and enthusiasm",
        weight=1.0,
        scoring_guide="1=Students disengaged, 3=Moderate engagement, 5=Highly engaged",
    )
    engagement.add_criterion(
        name="Classroom Dynamics",
        description="Manages classroom effectively; encourages participation",
        weight=1.0,
        scoring_guide="1=Poor management, 3=Adequate management, 5=Excellent dynamics",
    )

    builder.set_scoring_scale(
        min_score=1,
        max_score=5,
        labels={
            1: "Poor - Not effective teaching",
            2: "Below Average - Needs improvement",
            3: "Average - Meets basic standards",
            4: "Good - Effective teaching",
            5: "Excellent - Outstanding educator",
        },
    )

    return builder.build(is_template=True, tags=["teaching", "education", "classroom"])


def create_general_presentation_rubric() -> Rubric:
    """Create a general-purpose rubric for any type of presentation."""
    builder = RubricBuilder(
        name="General Presentation",
        description="Evaluate any type of presentation on core presentation skills",
    )

    # Content Category
    content = builder.add_category(
        name="Content",
        description="Quality and relevance of presentation content",
        weight=1.5,
    )
    content.add_criterion(
        name="Relevance & Focus",
        description="Content is relevant and focused on the topic",
        weight=1.0,
        scoring_guide="1=Off-topic, 3=Generally relevant, 5=Highly relevant and focused",
    )
    content.add_criterion(
        name="Completeness",
        description="Covers the material comprehensively",
        weight=1.0,
        scoring_guide="1=Incomplete, 3=Adequate coverage, 5=Thorough coverage",
    )
    content.add_criterion(
        name="Accuracy",
        description="Information presented is accurate",
        weight=1.0,
        scoring_guide="1=Multiple errors, 3=Mostly accurate, 5=Completely accurate",
    )

    # Delivery Category
    delivery = builder.add_category(
        name="Delivery",
        description="Speaking skills and presence",
        weight=1.5,
    )
    delivery.add_criterion(
        name="Clarity",
        description="Spoken clearly and at appropriate pace",
        weight=1.0,
        scoring_guide="1=Hard to understand, 3=Generally clear, 5=Very clear",
    )
    delivery.add_criterion(
        name="Confidence",
        description="Presents with poise and confidence",
        weight=0.75,
        scoring_guide="1=Very nervous, 3=Reasonably confident, 5=Very confident",
    )
    delivery.add_criterion(
        name="Engagement",
        description="Engages and maintains audience attention",
        weight=0.75,
        scoring_guide="1=Boring, 3=Moderately engaging, 5=Highly engaging",
    )

    # Organization Category
    org = builder.add_category(
        name="Organization",
        description="Structure and logical flow",
        weight=1.0,
    )
    org.add_criterion(
        name="Logical Flow",
        description="Ideas presented in logical sequence",
        weight=1.0,
        scoring_guide="1=Disorganized, 3=Generally logical, 5=Excellent flow",
    )
    org.add_criterion(
        name="Transitions",
        description="Smooth transitions between ideas and sections",
        weight=0.5,
        scoring_guide="1=Abrupt transitions, 3=Adequate transitions, 5=Smooth transitions",
    )

    # Visual Category
    visual = builder.add_category(
        name="Visuals", description="Quality of visual aids", weight=1.0
    )
    visual.add_criterion(
        name="Visual Quality",
        description="Slides/visuals are professional and clear",
        weight=1.0,
        scoring_guide="1=Poor quality, 3=Adequate, 5=Professional",
    )

    builder.set_scoring_scale(
        min_score=1,
        max_score=5,
        labels={
            1: "Poor",
            2: "Below Average",
            3: "Average",
            4: "Good",
            5: "Excellent",
        },
    )

    return builder.build(is_template=True, tags=["general", "presentation"])


def get_default_rubric(rubric_type: str) -> Rubric | None:
    """Get a default rubric by type.

    Args:
        rubric_type: Type of rubric (academic, business, teaching, general)

    Returns:
        Rubric object or None if type not found
    """
    rubrics = {
        "academic": create_academic_presentation_rubric,
        "business": create_business_pitch_rubric,
        "teaching": create_teaching_demo_rubric,
        "general": create_general_presentation_rubric,
    }

    builder = rubrics.get(rubric_type.lower())
    return builder() if builder else None


def list_default_rubrics() -> list[str]:
    """List all available default rubric types."""
    return ["academic", "business", "teaching", "general"]
