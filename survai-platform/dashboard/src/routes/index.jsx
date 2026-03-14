import { useRoutes, Navigate } from 'react-router-dom';

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
import CreateSurveyBuilder from '../pages/main/Surveys/SurveyBuilder/SurveyBuilderSimple';
import GeneratedSurveyView from '../pages/main/Surveys/GeneratedSurveyView';
import SurveyProgressPage from '../pages/main/Surveys/SurveyProgressPage';
import SurveyQuestionAnalytics from '../pages/main/Templates/TemplateAnalytics';
import ImportData from '../pages/main/Surveys/ImportData';
import EditSurvey from '../pages/main/Surveys/EditSurvey';
import Analytics from '../pages/main/Analytics/Analytics';
import Contacts from '../pages/main/Contacts/Contacts';

const routes = [
    {
      path: '/login',
      element: <Login />
    },
    {
      path: '/',
      element: <Navigate to="/dashboard" replace />
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
          path: '/templates/edit',
          element: <CreateTemplate />
        },
        {
          path: '/templates/drafts',
          element: <DraftTemplates />
        },
        {
          path: '/surveys/launch',
          element: <CreateSurvey />
        },
        {
          path: 'surveys/builder',
          element: <CreateSurveyBuilder />
        },
        {
          path: '/surveys/generated',
          element: <GeneratedSurveyView />
        },
        {
          path: '/surveys/manage',
          element: <ManageSurveys />
        },
        {
          path: '/surveys/status/:surveyId',
          element: <SurveyProgressPage />
        },
        {
          path: '/surveys/completed',
          element: <CompletedSurveys />
        },
        {
          path: '/templates/create/analytics',
          element: <SurveyQuestionAnalytics />
        },
        {
          path: '/surveys/import',
          element: <ImportData />
        },
        {
          path: '/surveys/edit/:surveyId',
          element: <EditSurvey />
        },
        {
          path: '/analytics',
          element: <Analytics />
        },
        {
          path: '/contacts',
          element: <Contacts />
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