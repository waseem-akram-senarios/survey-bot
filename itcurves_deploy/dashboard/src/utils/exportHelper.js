import ApiLinks from '../network/apiLinks';

const API_BASE = ApiLinks.API_BASE_URL;

export async function downloadCSV(endpoint, filename) {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: { 'accept': 'text/csv' },
    });
    if (!response.ok) throw new Error(`Export failed: ${response.status}`);
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    return true;
  } catch (error) {
    console.error('Export error:', error);
    throw error;
  }
}

export function exportAllSurveys() {
  return downloadCSV(ApiLinks.EXPORT_SURVEYS, 'survey_responses.csv');
}

export function exportTranscripts() {
  return downloadCSV(ApiLinks.EXPORT_TRANSCRIPTS, 'call_transcripts.csv');
}

export function exportSurveyResponses(surveyId) {
  return downloadCSV(ApiLinks.EXPORT_SURVEY_RESPONSES(surveyId), `survey_${surveyId}_responses.csv`);
}
