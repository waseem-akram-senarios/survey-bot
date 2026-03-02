import ApiLinks from '../network/apiLinks';

const API_BASE = ApiLinks.API_BASE_URL;

export async function downloadCSV(endpoint, filename, queryParams = {}) {
  try {
    const url = new URL(endpoint, API_BASE);
    Object.entries(queryParams).forEach(([key, value]) => {
      if (value != null && value !== '') {
        url.searchParams.set(key, value);
      }
    });
    const response = await fetch(url.toString(), {
      headers: { 'accept': 'text/csv' },
    });
    if (!response.ok) throw new Error(`Export failed: ${response.status}`);
    const blob = await response.blob();
    const blobUrl = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(blobUrl);
    return true;
  } catch (error) {
    console.error('Export error:', error);
    throw error;
  }
}

export function exportAllSurveys(tenantId) {
  return downloadCSV(ApiLinks.EXPORT_SURVEYS, 'survey_responses.csv', tenantId ? { tenant_id: tenantId } : {});
}

export function exportTranscripts(tenantId) {
  return downloadCSV(ApiLinks.EXPORT_TRANSCRIPTS, 'call_transcripts.csv', tenantId ? { tenant_id: tenantId } : {});
}

export function exportSurveyResponses(surveyId, tenantId) {
  return downloadCSV(
    ApiLinks.EXPORT_SURVEY_RESPONSES(surveyId),
    `survey_${surveyId}_responses.csv`,
    tenantId ? { tenant_id: tenantId } : {}
  );
}
