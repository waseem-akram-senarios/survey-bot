import ApiLinks from '../../network/apiLinks';
import ApiBaseHelper from '../../network/apiBaseHelper';

function paramsWithTenant(tenantId) {
  return tenantId ? { params: { tenant_id: tenantId } } : {};
}

class SurveyTableService {
  static async getSurveyStats(tenantId) {
    try {
      return await ApiBaseHelper.get(ApiLinks.SURVEY_STATS, paramsWithTenant(tenantId));
    } catch (error) {
      console.error('Error fetching survey stats:', error);
      throw error;
    }
  }

  static async getSurveyList(tenantId) {
    try {
      return await ApiBaseHelper.get(ApiLinks.SURVEY_LIST, paramsWithTenant(tenantId));
    } catch (error) {
      console.error('Error fetching survey list:', error);
      throw error;
    }
  }

  static async getCompletedSurveyList(tenantId) {
    try {
      return await ApiBaseHelper.get(ApiLinks.COMPLETED_SURVEYS_LIST, paramsWithTenant(tenantId));
    } catch (error) {
      console.error('Error fetching completed survey list:', error);
      throw error;
    }
  }

  static async getDashboardData(tenantId) {
    try {
      const [surveyStats, templateStats] = await Promise.all([
        ApiBaseHelper.get(ApiLinks.SURVEY_STATS, paramsWithTenant(tenantId)),
        ApiBaseHelper.get(ApiLinks.TEMPLATE_STATS)
      ]);
      
      return {
        surveyStats,
        templateStats
      };
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw error;
    }
  }
}

export default SurveyTableService;
