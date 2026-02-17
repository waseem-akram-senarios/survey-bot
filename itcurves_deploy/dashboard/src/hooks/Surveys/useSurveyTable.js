import { useEffect, useState } from "react";
import SurveyTableService from "../../services/Surveys/surveyTableService";
import { transformSurveyData, mergeDashboardStats } from "../../utils/Surveys/surveyTableHelpers";

const useSurveyPageData = (statsDataFetcher, tableDataFetcher) => {
  const [statsData, setStatsData] = useState({});
  const [tableData, setTableData] = useState([]);
  const [statsLoading, setStatsLoading] = useState(true);
  const [tableLoading, setTableLoading] = useState(true);
  const [statsError, setStatsError] = useState(null);
  const [tableError, setTableError] = useState(null);

  const fetchStatsData = async () => {
    setStatsLoading(true);
    setStatsError(null);
    try {
      const data = await statsDataFetcher();
      setStatsData(data);
    } catch (err) {
      console.error('Error fetching stats data:', err);
      setStatsError(err.message);
    } finally {
      setStatsLoading(false);
    }
  };

  const fetchTableData = async () => {
    setTableLoading(true);
    setTableError(null);
    try {
      const data = await tableDataFetcher();
      setTableData(transformSurveyData(data));
    } catch (err) {
      console.error('Error fetching table data:', err);
      setTableError(err.message);
    } finally {
      setTableLoading(false);
    }
  };

  useEffect(() => {
    fetchStatsData();
    fetchTableData();
  }, []);

  return {
    statsData,
    tableData,
    statsLoading,
    tableLoading,
    statsError,
    tableError,
    globalLoading: statsLoading && tableLoading,
    refetchStats: fetchStatsData,
    refetchTable: fetchTableData,
  };
};

// Hook for Dashboard page - fetches merged stats and survey list
export const useDashboard = () => {
  return useSurveyPageData(
    async () => {
      const { surveyStats, templateStats } = await SurveyTableService.getDashboardData();
      return mergeDashboardStats(surveyStats, templateStats);
    },
    () => SurveyTableService.getSurveyList()
  );
};

// Hook for ManageSurveys page - fetches survey stats and list
export const useManageSurveys = () => {
  return useSurveyPageData(
    () => SurveyTableService.getSurveyStats(),
    () => SurveyTableService.getSurveyList()
  );
};

// Hook for CompletedSurveys page - fetches survey stats and completed surveys
export const useCompletedSurveys = () => {
  return useSurveyPageData(
    () => SurveyTableService.getSurveyStats(),
    () => SurveyTableService.getCompletedSurveyList()
  );
};
