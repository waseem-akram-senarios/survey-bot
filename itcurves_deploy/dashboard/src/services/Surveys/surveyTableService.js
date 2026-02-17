import ApiLinks from '../../network/apiLinks';
import ApiBaseHelper from '../../network/apiBaseHelper';

class SurveyTableService {
  static async getSurveyStats() {
    try {
      return await ApiBaseHelper.get(ApiLinks.SURVEY_STATS);
    } catch (error) {
      console.error('Error fetching survey stats:', error);
      throw error;
    }
  }

  static async getSurveyList() {
    try {
      return await ApiBaseHelper.get(ApiLinks.SURVEY_LIST);
    } catch (error) {
      console.error('Error fetching survey list:', error);
      throw error;
    }
  }

  static async getCompletedSurveyList() {
    try {
      return await ApiBaseHelper.get(ApiLinks.COMPLETED_SURVEYS_LIST);
    } catch (error) {
      console.error('Error fetching completed survey list:', error);
      throw error;
    }
  }

  static async getDashboardData() {
    try {
      const [surveyStats, templateStats] = await Promise.all([
        ApiBaseHelper.get(ApiLinks.SURVEY_STATS),
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
