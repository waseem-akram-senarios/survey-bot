// Base URL for API (empty = same origin, e.g. gateway at :8080)
const API_BASE = import.meta.env.VITE_SERVER_URL ?? '';
// Base URL for survey links (empty = same origin, e.g. /survey/id)
export const RECIPIENT_BASE = import.meta.env.VITE_RECIPIENT_URL ?? '';

// When running on server (e.g. http://54.86.65.150:8080), use current origin so API and survey links work
function getEffectiveApiBase() {
  if (typeof window === 'undefined') return API_BASE;
  const origin = window.location.origin;
  if (!API_BASE) return origin;
  if (API_BASE.includes('localhost') && !origin.includes('localhost')) return origin;
  return API_BASE;
}

class ApiLinks {
    static get API_BASE_URL() {
      return getEffectiveApiBase();
    }

    //Templates
    static TEMPLATE_STATS = `/api/templates/stat`;
    static TEMPLATE_LIST = `/api/templates/list`;
    static TEMPLATE_DRAFT_LIST = `/api/templates/list_drafts`;
    static TEMPLATE_QUESTIONS = `/api/templates/getquestions`;
    static TEMPLATE_CLONE = `/api/templates/clone`;
    static TEMPLATE_DELETE = `/api/templates/delete`;
    static TEMPLATE_ADD = `/api/templates/create`;
    static TEMPLATE_STATUS = `/api/templates/status`;
    static TEMPLATE_UPDATE = `/api/templates/update`;
    static TEMPLATE_ADD_QUESTION = `/api/templates/addquestions`;
    static TEMPLATE_DELETE_QUESTION = `/api/templates/deletequestionbyidwithparentchild`;
    static TEMPLATE_TRANSLATE = `/api/templates/translate`;

    // Questions
    static QUESTION_CREATE = `/api/questions`;
    static QUESTION_EDIT = `/api/questions`;
    static QUESTION_DETAILS = (questionId) => `/api/questions/${questionId}`;

    // Survey endpoints
    static SURVEY_STATS = "/api/surveys/stat";
    static SURVEY_LIST = "/api/surveys/list";
    static COMPLETED_SURVEYS_LIST = "/api/surveys/list_completed";
    static DASHBOARD_DATA = "/api/surveys/dashboard";
    static SURVEY_SEND_EMAIL = `/api/surveys/email`;
    static SURVEY_SEND_PHONE = "/api/surveys/make-call";

    // Survey generation and management endpoints
    static SURVEY_GENERATE = '/api/surveys/generate';
    static SURVEY_CREATE = '/api/surveys/create';
    static SURVEY_DELETE = (surveyId) => `/api/surveys/${surveyId}`;
    static SURVEY_UPDATE_DETAILS = (surveyId) => `/api/surveys/${surveyId}/details`;
    static SURVEY_QUESTIONS = (surveyId) => `/api/surveys/${surveyId}/questions`;

    // Import endpoints
    static IMPORT_RIDERS = '/api/import/riders';
    static IMPORT_BULK_SURVEYS = '/api/import/bulk-surveys';

    // Export endpoints
    static EXPORT_SURVEYS = '/api/export/surveys';
    static EXPORT_TRANSCRIPTS = '/api/export/transcripts';
    static EXPORT_CAMPAIGN = (campaignId) => `/api/export/campaign/${campaignId}`;
    static EXPORT_SURVEY_RESPONSES = (surveyId) => `/api/export/survey/${surveyId}/responses`;

    // Analytics endpoints
    static ANALYTICS_SUMMARY = '/api/analytics/summary';
    static ANALYTICS_CAMPAIGN = (campaignId) => `/api/analytics/campaign/${campaignId}`;

    // Callback/Scheduling endpoints
    static SCHEDULE_CALLBACK = '/api/surveys/callback';
    static SCHEDULE_CALL = '/api/scheduler/schedule-call';
    static SCHEDULE_CAMPAIGN = '/api/scheduler/schedule-campaign';

    // Call transcript / recording
    static SURVEY_TRANSCRIPT = (surveyId) => `/api/voice/transcript/${surveyId}`;

    // SMS endpoints
    static SURVEY_SEND_SMS = '/api/surveys/sendsms';
    static SURVEY_SMS = '/api/surveys/sms';

    // Demand Fulfillment endpoints
    static DEMAND_FULFILLMENT = (tenantId) => `/api/analytics/demand-fulfillment/${tenantId}`;
    static RECORD_DEMAND_FULFILLMENT = '/api/analytics/demand-fulfillment';

    // Incentive/Gift Card tracking endpoints
    static INCENTIVES = (tenantId) => `/api/analytics/incentives/${tenantId}`;
    static ISSUE_INCENTIVE = '/api/analytics/incentives/issue';
    static REDEEM_INCENTIVE = '/api/analytics/incentives/redeem';
    static CHECK_INCENTIVE = (riderPhone) => `/api/analytics/incentives/check/${riderPhone}`;
}
  
export default ApiLinks;
