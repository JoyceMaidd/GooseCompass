"""Structured output types for the planner's PydanticAI agents."""

from pydantic import BaseModel, Field

from backend.planner.models import PlannerPhase


class HostSchoolFinding(BaseModel):
    """A single grounded fact about a host school, found via retrieval.

    Args:
        school_name: Name of the host institution.
        country: Country the host institution is located in, if known.
        program_url: URL to the host institution's exchange program page, if known.
        summary: Grounded summary of what retrieval returned about this school.
    """

    school_name: str
    country: str | None = None
    program_url: str | None = None
    summary: str


class HostSchoolResearchResult(BaseModel):
    """Grounded findings from the host-school research specialist.

    Args:
        findings: Host schools found via retrieval, grounded in retrieved content.
        insufficient_context: True when retrieval returned nothing relevant.
    """

    findings: list[HostSchoolFinding]
    insufficient_context: bool = Field(default=False)


class PhaseTrackingUpdate(BaseModel):
    """Recommendation from the phase-tracking specialist.

    Args:
        current_phase: The student's current stage in the exchange process.
        recommended_next_steps: Concrete next actions for the student to take.
        rationale: Explanation grounded in the student's recorded plan state.
    """

    current_phase: PlannerPhase
    recommended_next_steps: list[str]
    rationale: str


class PlanSnapshot(BaseModel):
    """Read-only summary of a plan's state, for the phase-tracking tool.

    Args:
        current_phase: The student's current stage in the exchange process.
        host_schools: The student's recorded host schools, as plain dicts.
        course_matches: The student's recorded course matches, as plain dicts.
    """

    current_phase: PlannerPhase
    host_schools: list[dict]
    course_matches: list[dict]


class PlannerAssistantReply(BaseModel):
    """Unified reply from the coordinator agent.

    Args:
        message: The coordinator's synthesized reply to the student.
        host_school_findings: Findings surfaced by the host-school specialist, if delegated to.
        phase_update: Recommendation surfaced by the phase-tracking specialist, if delegated to.
    """

    message: str
    host_school_findings: list[HostSchoolFinding] = Field(default_factory=list)
    phase_update: PhaseTrackingUpdate | None = None
