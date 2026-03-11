import ApiBaseHelper from '../../network/apiBaseHelper';
import ApiLinks from '../../network/apiLinks';
import { transformApiQuestionsToComponentFormat, transformComponentQuestionsToApiFormat } from '../../utils/Surveys/surveyHelpers';

function getApiErrorMessage(error, fallback) {
  if (error.response?.data?.detail) {
    const d = error.response.data.detail;
    if (typeof d === 'string') return d;
    if (Array.isArray(d)) return d.map((x) => x?.msg ?? x?.loc?.join('.') ?? JSON.stringify(x)).filter(Boolean).join('; ') || fallback;
  }
  if (error.response?.data?.message) return error.response.data.message;
  if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') return 'Network error. Check that the server is running and the dashboard URL is correct.';
  if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) return 'Request timed out. Try again.';
  if (error.response?.status === 404) return 'Not found. Check template name and try again.';
  if (error.response?.status === 400) return error.response?.data?.detail || 'Invalid request.';
  return error.message || fallback;
}

class SurveyService {
  static async generateSurvey(surveyData) {
    try {
      const response = await ApiBaseHelper.post(ApiLinks.SURVEY_GENERATE, {
        SurveyId: surveyData.surveyId,
        Biodata: surveyData.biodata,
        Recipient: surveyData.recipient,
        Name: surveyData.template,
        RiderName: surveyData.riderName,
        RideId: surveyData.rideId,
        TenantId: surveyData.tenantId,
        Phone: (surveyData.phone || "").replace(/\s+/g, ""),
        URL: `${import.meta.env.VITE_RECIPIENT_URL}/survey/${surveyData.surveyId}`,
        Bilingual: surveyData.bilingual ?? false,
      });

      console.log("Generated survey response:", response);

      const transformedQuestions = transformApiQuestionsToComponentFormat(response.QuestionswithAns || []);

      
      return {
        ...surveyData,
        questions: transformedQuestions,
        apiResponse: response
      };
    } catch (error) {
      console.error('Error generating survey:', error);
      const msg = getApiErrorMessage(error, 'Failed to generate survey. Please try again.');
      throw new Error(msg);
    }
  }

  static async launchSurvey(surveyData, questions, aiAugmented = true) {
    try {
      const apiPayload = transformComponentQuestionsToApiFormat(questions, surveyData.surveyId);
      apiPayload.AiAugmented = aiAugmented;
      console.log("Launching survey with payload:", apiPayload);
      
      const response = await ApiBaseHelper.post(ApiLinks.SURVEY_CREATE, apiPayload);
      
      const surveyLink = `${import.meta.env.VITE_RECIPIENT_URL}/survey/${surveyData.surveyId}`;
      
      return {
        success: true,
        message: response.message,
        surveyLink: surveyLink,
        surveyId: surveyData.surveyId
      };
    } catch (error) {
      console.error('Error launching survey:', error);
      const msg = getApiErrorMessage(error, 'Failed to launch survey. Please try again.');
      throw new Error(msg);
    }
  }

  static async fetchSurveyQuestions(surveyId) {
    try {
      const response = await ApiBaseHelper.get(ApiLinks.SURVEY_QUESTIONS(surveyId));
      
      if (response.Questions && Array.isArray(response.Questions)) {
        return transformApiQuestionsToComponentFormat(response.Questions);
      } else {
        throw new Error("Invalid response format");
      }
    } catch (error) {
      console.error('Error fetching survey questions:', error);
      throw new Error('Failed to load survey questions. Please try again.');
    }
  }

  static async fetchSurveyQuestionsRaw(surveyId) {
    try {
      const response = await ApiBaseHelper.get(ApiLinks.SURVEY_QUESTIONS(surveyId));
      
      if (response.Questions && Array.isArray(response.Questions)) {
        return response.Questions; 
      } else {
        throw new Error("Invalid response format");
      }
    } catch (error) {
      console.error('Error fetching raw survey questions:', error);
      throw new Error('Failed to load survey questions. Please try again.');
    }
  }

  static async deleteSurvey(surveyId) {
    try {
      await ApiBaseHelper.delete(ApiLinks.SURVEY_DELETE(surveyId));

      return {
        success: true,
        message: 'Survey deleted successfully'
      };
    } catch (error) {
      console.error('Error deleting survey:', error);
      throw new Error('Failed to delete survey. Please try again.');
    }
  }

  static async sendSurveyByEmail(surveyId, email, language = "en") {
    try {
      const response = await ApiBaseHelper.post(ApiLinks.SURVEY_SEND_EMAIL, {
        SurveyURL: `${import.meta.env.VITE_RECIPIENT_URL}/survey/${surveyId}`,
        EmailTo: email,
        Language: language,
      });

      return {
        success: true,
        message: response.message || 'Survey sent successfully via email',
      };
    } catch (error) {
      console.error('Error sending survey via email:', error);
      throw new Error('Failed to send survey via email. Please try again.');
    }
  }

  static async updateSurveyDetails(surveyId, { recipient, riderName, phone }) {
    try {
      const params = new URLSearchParams();
      if (recipient) params.append("recipient", recipient);
      if (riderName) params.append("rider_name", riderName);
      if (phone) params.append("phone", phone);
      await ApiBaseHelper.patch(`${ApiLinks.SURVEY_UPDATE_DETAILS(surveyId)}?${params.toString()}`);
      return { success: true, message: "Survey updated successfully" };
    } catch (error) {
      console.error("Error updating survey:", error);
      throw new Error("Failed to update survey. Please try again.");
    }
  }

  static async cloneSurvey(originalSurvey) {
    try {
      const newSurveyId = crypto.randomUUID();
      const response = await ApiBaseHelper.post(ApiLinks.SURVEY_GENERATE, {
        SurveyId: newSurveyId,
        Biodata: originalSurvey.Biodata || "",
        Recipient: `${originalSurvey.Recipient || originalSurvey.Name} (Copy)`,
        Name: originalSurvey.Name || originalSurvey.TemplateName || "",
        RiderName: originalSurvey.RiderName || "",
        RideId: originalSurvey.RideId || "",
        TenantId: originalSurvey.TenantId || "",
        Phone: originalSurvey.Phone || "",
        URL: `${import.meta.env.VITE_RECIPIENT_URL}/survey/${newSurveyId}`,
      });

      return {
        success: true,
        surveyId: newSurveyId,
        message: "Survey cloned successfully",
        apiResponse: response,
      };
    } catch (error) {
      console.error("Error cloning survey:", error);
      throw new Error("Failed to clone survey. Please try again.");
    }
  }

  static async fetchTranscript(surveyId) {
    try {
      const response = await ApiBaseHelper.get(ApiLinks.SURVEY_TRANSCRIPT(surveyId));
      return response;
    } catch (error) {
      if (error.response?.status === 404) return null;
      console.error('Error fetching transcript:', error);
      return null;
    }
  }

  static async sendSurveyBySMS(surveyId, phone, provider = "livekit", language = "en") {
    try {
      const queryParams = new URLSearchParams({
        to: phone,
        survey_id: surveyId,
        provider: provider,
        language: language,
      });
      
      const response = await ApiBaseHelper.post(`${ApiLinks.SURVEY_SEND_PHONE}?${queryParams.toString()}`);

      return {
        success: true,
        message: response.message || 'Call initiated successfully',
      };
    } catch (error) {
      console.error('Error sending survey via phone:', error);
      const msg = getApiErrorMessage(error, 'Failed to send survey via phone. Please try again.');
      throw new Error(msg);
    }
  }
}

export default SurveyService;