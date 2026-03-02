import { useEffect, useState } from "react";
import SurveyTableService from "../../services/Surveys/surveyTableService";
import { transformSurveyData, mergeDashboardStats } from "../../utils/Surveys/surveyTableHelpers";
import { useAuth } from "../../context/AuthContext";

const useSurveyPageData = (statsDataFetcher, tableDataFetcher, tenantId) => {
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
  }, [tenantId]);

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
  const { user } = useAuth();
  const tenantId = user?.tenantId ?? null;
  return useSurveyPageData(
    async () => {
      const { surveyStats, templateStats } = await SurveyTableService.getDashboardData(tenantId);
      return mergeDashboardStats(surveyStats, templateStats);
    },
    () => SurveyTableService.getSurveyList(tenantId),
    tenantId
  );
};

// Hook for ManageSurveys page - fetches survey stats and list
export const useManageSurveys = () => {
  const { user } = useAuth();
  const tenantId = user?.tenantId ?? null;
  return useSurveyPageData(
    () => SurveyTableService.getSurveyStats(tenantId),
    () => SurveyTableService.getSurveyList(tenantId),
    tenantId
  );
};

// Hook for CompletedSurveys page - fetches survey stats and completed surveys
export const useCompletedSurveys = () => {
  const { user } = useAuth();
  const tenantId = user?.tenantId ?? null;
  return useSurveyPageData(
    () => SurveyTableService.getSurveyStats(tenantId),
    () => SurveyTableService.getCompletedSurveyList(tenantId),
    tenantId
  );
};
