from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


class ParticipantTeamLink(SQLModel, table=True):
    participant_id: Optional[int] = Field(
        default=None, foreign_key="participant.id", primary_key=True
    )
    team_id: Optional[int] = Field(
        default=None, foreign_key="team.id", primary_key=True
    )
    joined_at: datetime = Field(default_factory=datetime.utcnow)


class ParticipantDefault(SQLModel):
    name: str
    email: str
    phone: Optional[str] = None


class Participant(ParticipantDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    teams: List["Team"] = Relationship(
        back_populates="participants",
        link_model=ParticipantTeamLink
    )
    evaluations: List["Evaluation"] = Relationship(
        back_populates="judge"
    )


class ParticipantRead(ParticipantDefault):
    id: int
    evaluations: Optional[List["EvaluationRead"]] = None


class ParticipantCreateOrUpdate(ParticipantDefault):
    team_ids: Optional[List[int]] = None


class TeamDefault(SQLModel):
    name: str


class Team(TeamDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    participants: List[Participant] = Relationship(
        back_populates="teams",
        link_model=ParticipantTeamLink
    )
    submissions: List["Submission"] = Relationship(
        back_populates="team"
    )


class TeamRead(TeamDefault):
    id: int
    participants: Optional[List[ParticipantRead]] = None


class TeamCreateOrUpdate(TeamDefault):
    participant_ids: Optional[List[int]] = None


class ChallengeDefault(SQLModel):
    title: str
    description: Optional[str] = None
    criteria: Optional[str] = None


class Challenge(ChallengeDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    submissions: List["Submission"] = Relationship(
        back_populates="challenge"
    )


class ChallengeRead(ChallengeDefault):
    id: int
    submissions: Optional[List["SubmissionRead"]] = None


class ChallengeCreateOrUpdate(ChallengeDefault):
    pass


class SubmissionDefault(SQLModel):
    team_id: int = Field(foreign_key="team.id")
    challenge_id: int = Field(foreign_key="challenge.id")
    file_url: str


class Submission(SubmissionDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    team: "Team" = Relationship(back_populates="submissions")
    challenge: "Challenge" = Relationship(back_populates="submissions")
    evaluations: List["Evaluation"] = Relationship(
        back_populates="submission"
    )


class SubmissionRead(SubmissionDefault):
    id: int
    submitted_at: datetime
    team: Optional[TeamRead] = None
    challenge: Optional[ChallengeRead] = None
    evaluations: Optional[List["EvaluationRead"]] = None


class SubmissionCreateOrUpdate(SubmissionDefault):
    pass


class EvaluationDefault(SQLModel):
    submission_id: int = Field(foreign_key="submission.id")
    judge_id: int = Field(foreign_key="participant.id")
    score: float
    comments: Optional[str] = None


class Evaluation(EvaluationDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
    submission: "Submission" = Relationship(back_populates="evaluations")
    judge: "Participant" = Relationship(back_populates="evaluations")


class EvaluationRead(EvaluationDefault):
    id: int
    evaluated_at: datetime
    submission: Optional[SubmissionRead] = None
    judge: Optional[ParticipantRead] = None


class EvaluationCreateOrUpdate(EvaluationDefault):
    pass
