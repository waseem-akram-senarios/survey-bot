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

  const fetchStatsData = async (silent = false) => {
    if (!silent) {
      setStatsLoading(true);
      setStatsError(null);
    }
    try {
      const data = await statsDataFetcher();
      setStatsData(data);
    } catch (err) {
      if (!silent) {
        console.error('Error fetching stats data:', err);
        setStatsError(err.message);
      }
    } finally {
      if (!silent) setStatsLoading(false);
    }
  };

  const fetchTableData = async (silent = false) => {
    if (!silent) {
      setTableLoading(true);
      setTableError(null);
    }
    try {
      const data = await tableDataFetcher();
      setTableData(transformSurveyData(data));
    } catch (err) {
      if (!silent) {
        console.error('Error fetching table data:', err);
        setTableError(err.message);
      }
    } finally {
      if (!silent) setTableLoading(false);
    }
  };

  const refetchAll = (silent = false) => {
    fetchStatsData(silent);
    fetchTableData(silent);
  };

  useEffect(() => {
    fetchStatsData();
    fetchTableData();
  }, [tenantId]);

  // Refetch when user returns to the tab (e.g. after a call completes) so status updates appear
  useEffect(() => {
    const onVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        refetchAll(true);
      }
    };
    document.addEventListener('visibilitychange', onVisibilityChange);
    return () => document.removeEventListener('visibilitychange', onVisibilityChange);
  }, [tenantId]);

  // Periodic refetch every 30s while tab is visible so completed calls show up without leaving the page
  useEffect(() => {
    const interval = setInterval(() => {
      if (document.visibilityState === 'visible') {
        refetchAll(true);
      }
    }, 30000);
    return () => clearInterval(interval);
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
    refetchAll,
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
