import ApiBaseHelper from '../../network/apiBaseHelper';
import ApiLinks from '../../network/apiLinks';

class AnalyticsService {
  // Core Analytics
  static async getSummary() {
    try {
      return await ApiBaseHelper.get(ApiLinks.ANALYTICS_SUMMARY);
    } catch (error) {
      console.error('Error fetching analytics summary:', error);
      throw error;
    }
  }

  static async getSurveyStats(tenantId) {
    try {
      const params = tenantId ? { params: { tenant_id: tenantId } } : {};
      return await ApiBaseHelper.get(ApiLinks.SURVEY_STATS, params);
    } catch (error) {
      console.error('Error fetching survey stats:', error);
      throw error;
    }
  }

  static async getCompletedSurveys(tenantId) {
    try {
      const params = tenantId ? { params: { tenant_id: tenantId } } : {};
      return await ApiBaseHelper.get(ApiLinks.COMPLETED_SURVEYS_LIST, params);
    } catch (error) {
      console.error('Error fetching completed surveys:', error);
      throw error;
    }
  }

  // Real-time Survey Data
  static async getAllSurveys(tenantId) {
    try {
      const params = tenantId ? { params: { tenant_id: tenantId } } : {};
      return await ApiBaseHelper.get(ApiLinks.SURVEY_LIST, params);
    } catch (error) {
      console.error('Error fetching all surveys:', error);
      throw error;
    }
  }

  static async getInProgressSurveys(tenantId) {
    try {
      const params = tenantId ? { params: { tenant_id: tenantId } } : {};
      return await ApiBaseHelper.get('/api/surveys/list_inprogress', params);
    } catch (error) {
      console.error('Error fetching in-progress surveys:', error);
      throw error;
    }
  }

  // Template Data
  static async getTemplateStats(tenantId) {
    try {
      const params = tenantId ? { params: { tenant_id: tenantId } } : {};
      return await ApiBaseHelper.get(ApiLinks.TEMPLATE_STATS, params);
    } catch (error) {
      console.error('Error fetching template stats:', error);
      throw error;
    }
  }

  static async getAllTemplates() {
    try {
      return await ApiBaseHelper.get(ApiLinks.TEMPLATE_LIST);
    } catch (error) {
      console.error('Error fetching templates:', error);
      throw error;
    }
  }

  // Voice/Call Data
  static async getCallTranscript(surveyId) {
    try {
      return await ApiBaseHelper.get(ApiLinks.SURVEY_TRANSCRIPT(surveyId));
    } catch (error) {
      console.error('Error fetching call transcript:', error);
      throw error;
    }
  }

  // Campaign Data
  static async getCampaignAnalytics(campaignId, tenantId) {
    try {
      const params = tenantId ? { params: { tenant_id: tenantId } } : {};
      return await ApiBaseHelper.get(ApiLinks.ANALYTICS_CAMPAIGN(campaignId), params);
    } catch (error) {
      console.error('Error fetching campaign analytics:', error);
      throw error;
    }
  }

  // Demand Fulfillment
  static async getDemandFulfillment(tenantId) {
    try {
      return await ApiBaseHelper.get(ApiLinks.DEMAND_FULFILLMENT(tenantId));
    } catch (error) {
      console.error('Error fetching demand fulfillment:', error);
      throw error;
    }
  }

  // Incentives/Gift Cards
  static async getIncentives(tenantId) {
    try {
      return await ApiBaseHelper.get(ApiLinks.INCENTIVES(tenantId));
    } catch (error) {
      console.error('Error fetching incentives:', error);
      throw error;
    }
  }

  // Export Data
  static async exportSurveys(tenantId, filters = {}) {
    try {
      const params = tenantId ? { ...filters, params: { tenant_id: tenantId } } : filters;
      return await ApiBaseHelper.get(ApiLinks.EXPORT_SURVEYS, params);
    } catch (error) {
      console.error('Error exporting surveys:', error);
      throw error;
    }
  }

  static async exportTranscripts(tenantId, filters = {}) {
    try {
      const params = tenantId ? { ...filters, params: { tenant_id: tenantId } } : filters;
      return await ApiBaseHelper.get(ApiLinks.EXPORT_TRANSCRIPTS, params);
    } catch (error) {
      console.error('Error exporting transcripts:', error);
      throw error;
    }
  }

  // Real-time Dashboard Data
  static async getDashboardData(tenantId) {
    try {
      const params = tenantId ? { params: { tenant_id: tenantId } } : {};
      return await ApiBaseHelper.get(ApiLinks.DASHBOARD_DATA, params);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw error;
    }
  }

  // Comprehensive Real-time Data Fetch
  static async getAllRealTimeData(tenantId) {
    try {
      const params = tenantId ? { params: { tenant_id: tenantId } } : {};
      
      // Fetch all data in parallel for real-time updates
      const [
        summary,
        surveyStats,
        allSurveys,
        inProgressSurveys,
        completedSurveys,
        templateStats,
        templates,
        dashboardData
      ] = await Promise.all([
        this.getSummary(),
        this.getSurveyStats(tenantId),
        this.getAllSurveys(tenantId),
        this.getInProgressSurveys(tenantId),
        this.getCompletedSurveys(tenantId),
        this.getTemplateStats(tenantId),
        this.getAllTemplates(),
        this.getDashboardData(tenantId)
      ]);

      return {
        summary,
        surveyStats,
        allSurveys,
        inProgressSurveys,
        completedSurveys,
        templateStats,
        templates,
        dashboardData,
        lastUpdated: new Date().toISOString()
      };
    } catch (error) {
      console.error('Error fetching real-time data:', error);
      throw error;
    }
  }

  // WebSocket-like real-time updates (polling fallback)
  static async getRealTimeUpdates(tenantId, lastUpdate) {
    try {
      const params = tenantId ? { 
        params: { 
          tenant_id: tenantId,
          since: lastUpdate
        } 
      } : { params: { since: lastUpdate } };
      
      // This would ideally be a WebSocket, but we'll use polling with timestamp
      const [summary, allSurveys] = await Promise.all([
        this.getSummary(),
        this.getAllSurveys(tenantId)
      ]);

      return {
        summary,
        allSurveys,
        lastUpdated: new Date().toISOString()
      };
    } catch (error) {
      console.error('Error fetching real-time updates:', error);
      throw error;
    }
  }
}

export default AnalyticsService;
