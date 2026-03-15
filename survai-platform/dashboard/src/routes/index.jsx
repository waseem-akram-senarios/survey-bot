import { useRoutes, Navigate, useLocation } from 'react-router-dom';

import MainLayout from '../layout/MainLayout';
import ProtectedRoute from '../components/ProtectedRoute';
import Login from '../pages/Login';
import NotFound from '../pages/NotFound';
import FirstTimeLanding from '../pages/FirstTimeLanding';

// Import survey-related components
import Dashboard from '../pages/main/Surveys/Dashboard';
import CreateTemplate from '../pages/main/Templates/CreateTemplate';
import Templates from '../pages/main/Templates/Templates';
import DraftTemplates from '../pages/main/Templates/DraftTemplates';
import ManageSurveys from '../pages/main/Surveys/ManageSurveys';
import CompletedSurveys from '../pages/main/Surveys/CompletedSurveys';
import CreateSurvey from '../pages/main/Surveys/CreateSurveyModern';
import SurveyBuilderAdvanced from '../pages/main/Surveys/SurveyBuilder/SurveyBuilderAdvanced';

// Debug: Check if components are loaded
console.log('CreateSurveyModern component:', CreateSurvey);
console.log('SurveyBuilderAdvanced component:', SurveyBuilderAdvanced);
import GeneratedSurveyView from '../pages/main/Surveys/GeneratedSurveyView';
import SurveyProgressPage from '../pages/main/Surveys/SurveyProgressPage';
import SurveyQuestionAnalytics from '../pages/main/Templates/TemplateAnalytics';
import ImportData from '../pages/main/Surveys/ImportData';
import EditSurvey from '../pages/main/Surveys/EditSurvey';
import Analytics from '../pages/main/Analytics/Analytics';
import RouteDebug from '../pages/main/Surveys/RouteDebug';

const routes = [
    {
      path: '/login',
      element: <Login />
    },
    {
      path: '/',
      element: (
        <ProtectedRoute>
          <MainLayout />
        </ProtectedRoute>
      ),
      children: [
        {
          index: true,
          element: <Navigate to="/dashboard" replace />
        },
        {
          path: 'welcome',
          element: <FirstTimeLanding />
        },
        {
          path: 'dashboard',
          element: <Dashboard />
        },
        {
          path: 'templates/manage',
          element: <Templates />
        },
        {
          path: 'templates/create',
          element: <CreateTemplate />
        },
        {
          path: 'templates/edit',
          element: <CreateTemplate />
        },
        {
          path: 'templates/drafts',
          element: <DraftTemplates />
        },
        {
          path: 'surveys/launch',
          element: <CreateSurvey />
        },
        {
          path: 'surveys/builder',
          element: <SurveyBuilderAdvanced />
        },
        {
          path: 'surveys/generated',
          element: <GeneratedSurveyView />
        },
        {
          path: 'surveys/manage',
          element: <ManageSurveys />
        },
        {
          path: 'surveys/status/:surveyId',
          element: <SurveyProgressPage />
        },
        {
          path: 'surveys/completed',
          element: <CompletedSurveys />
        },
        {
          path: 'templates/create/analytics',
          element: <SurveyQuestionAnalytics />
        },
        {
          path: 'surveys/import',
          element: <ImportData />
        },
        {
          path: 'surveys/edit/:surveyId',
          element: <EditSurvey />
        },
        {
          path: 'analytics',
          element: <Analytics />
        },
        {
          path: 'contacts',
          element: <RouteDebug />
        },
        {
          path: '*',
          element: <RouteDebug />
        }
      ]
    },
    {
      path: '*',
      element: <NotFound />
    }
  ];
  
// Routing Render Function
export default function ThemeRoutes() {
    return useRoutes([...routes]);
}