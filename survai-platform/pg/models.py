from datetime import datetime
from typing import List, Literal, Union
from uuid import uuid4

from pydantic import BaseModel, Extra, Field


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


class QuestionP(BaseModel):
    QueId: str = Field(default_factory=lambda: str(uuid4()))
    QueText: str
    QueScale: Union[int, None] = None
    QueCriteria: Literal["scale", "categorical", "open"]
    QueCategories: Union[List[str], None] = None
    ParentId: Union[str, None] = None
    # For child questions: which categories (by text) of the parent should trigger this child
    ParentCategoryTexts: Union[List[str], None] = None
    Autofill: Literal["Yes", "No"] = "No"


class QuestionResponseP(QuestionP):
    pass


class TemplateBaseP(BaseModel):
    TemplateName: str = Field(
        ..., min_length=1, description="Unique name for the template"
    )


class TemplateCreateP(TemplateBaseP):
    pass


class TemplateP(TemplateBaseP):
    """Template model with status and creation date"""

    Status: Literal["Draft", "Published"] = "Draft"
    Date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))


# Request Models
class TemplateNameRequestP(BaseModel):
    """Base model for requests that need a template name"""

    TemplateName: str


class TemplateStatusUpdateP(TemplateNameRequestP):
    """Update template status request"""

    Status: Literal["Draft", "Published"]


class SourceTemplateRequestP(BaseModel):
    """Base model for requests that need a source template name"""

    SourceTemplateName: str


class CloneTemplateRequestP(SourceTemplateRequestP):
    """Request model for cloning a template"""

    NewTemplateName: str = Field(
        ..., min_length=1, description="Name for the new template"
    )


class SpanishTemplateRequestP(SourceTemplateRequestP):
    """Request model for creating a Spanish version of a template"""

    NewTemplateName: str = Field(
        ..., min_length=1, description="Name for the Spanish template"
    )


class TranslateTemplateRequestP(SourceTemplateRequestP):
    """Request model for creating a translated version of a template"""

    NewTemplateName: str = Field(
        ..., min_length=1, description="Name for the translated template"
    )
    NewTemplateLanguage: Literal[
        "Spanish", "German", "French", "Russian", "Chinese"
    ] = Field(..., description="Language for the translated template")


class TemplateQuestionOrderRequestP(BaseModel):
    """Request model for template question operations that need template name and order"""

    TemplateName: str
    Order: int


class GetTemplateQuestionsRequestP(BaseModel):
    """Request model for getting template questions"""

    TemplateName: str


class TemplateStatsP(BaseModel):
    Total_Templates: int
    Total_Draft_Templates: int
    Total_Published_Templates: int
    Total_Templates_ThisMonth: int
    Total_Draft_Templates_ThisMonth: int
    Total_Published_Templates_ThisMonth: int


class TemplateQuestionCreateP(TemplateNameRequestP):
    """Model for adding a question to a template"""

    QueId: str
    Order: int


class TemplateQuestionDeleteRequestP(BaseModel):
    """Request model for deleting a template question by queid"""

    TemplateName: str
    QueId: str


class SurveyBaseP(BaseModel):
    SurveyId: str = Field(default_factory=lambda: str(uuid4()))
    Biodata: str
    Recipient: str
    Name: str  # same as survey name and templatename
    # TemplateName: str  # same as survey name
    RiderName: str
    RideId: str
    TenantId: str


class SurveyCreateP(SurveyBaseP):
    URL: str


class SurveyP(SurveyBaseP):
    URL: str
    Status: Literal["In-Progress", "Completed"] = "In-Progress"
    LaunchDate: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    CompletionDate: str = ""


class SurveyStatusUpdateP(BaseModel):
    Status: Literal["In-Progress", "Completed"]


class SurveyCSATUpdateP(BaseModel):
    CSAT: Union[int, None] = None


class SurveyDurationUpdateP(BaseModel):
    CompletionDuration: Union[int, None] = None


class SurveyQuestion(BaseModel):
    SurveyId: str
    Order: int
    QueId: str


class SurveyQuestionAnswerP(QuestionP):
    Order: int
    Ans: Union[str, None] = None
    RawAns: Union[str, None] = None
    Autofill: Literal["Yes", "No"] = "No"


class SurveyStats(BaseModel):
    Total_Surveys: int
    Total_Active_Surveys: int
    Total_Completed_Surveys: int
    Total_Completed_Surveys_Today: int
    Median_Completion_Duration: int
    Median_Completion_Duration_Today: int
    AverageCSAT: float


class SurveyQuestionUpdateP(QuestionP):
    Order: int
    Ans: str


class SurveyQnAP(BaseModel):
    SurveyId: str
    QuestionswithAns: List[SurveyQuestionAnswerP]


class SurveyQuestionAnswerPhone(BaseModel):
    QueId: str
    RawAns: Union[str, None] = None


class SurveyQnAPhone(BaseModel, extra=Extra.allow):
    SurveyId: str


class SurveyQuestionOrderP(QuestionP):
    Order: int


class SurveyQuestionsP(BaseModel):
    SurveyId: str
    QuestionswithAns: List[SurveyQuestionOrderP]


class SurveyStatusP(BaseModel):
    SurveyId: str
    Status: Literal["In-Progress", "Completed"]
    LaunchDate: str
    CompletionDate: str
    CSAT: Union[int, None] = None


class SurveyFromTemplateP(BaseModel):
    Total: int
    Completed: int
    InProgress: int


class RelevanceP(BaseModel):
    yes_or_no: Literal["Yes", "No"]


class SympathizeP(BaseModel):
    Question: str
    Response: str


class Email(BaseModel):
    SurveyURL: str
    EmailTo: str


##############################


# Request model to fetch a specific question's answer within a survey
class QuestionIdRequestP(BaseModel):
    QueId: str
