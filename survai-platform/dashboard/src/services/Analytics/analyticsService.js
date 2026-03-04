import ApiBaseHelper from '../../network/apiBaseHelper';
import ApiLinks from '../../network/apiLinks';

class AnalyticsService {
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
}

export default AnalyticsService;
