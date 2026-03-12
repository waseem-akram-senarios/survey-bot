// Survey API Utilities
// Working survey creation and management functions

const API_BASE_URL = 'http://localhost:8080/pg/api';

export const surveyAPI = {
  // Get all surveys
  async getSurveys() {
    try {
      const response = await fetch(`${API_BASE_URL}/surveys/list`);
      if (!response.ok) {
        throw new Error('Failed to fetch surveys');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching surveys:', error);
      throw error;
    }
  },

  // Get all templates
  async getTemplates() {
    try {
      const response = await fetch(`${API_BASE_URL}/templates/list`);
      if (!response.ok) {
        throw new Error('Failed to fetch templates');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching templates:', error);
      throw error;
    }
  },

  // Create a new survey
  async createSurvey(surveyData) {
    try {
      // First get available templates
      const templates = await this.getTemplates();
      
      if (!templates || templates.length === 0) {
        throw new Error('No templates available');
      }

      // Use the first available template if not specified
      const templateName = surveyData.templateName || templates[0].TemplateName;
      
      // Create the survey payload with correct structure
      const payload = {
        SurveyId: surveyData.surveyId || `survey_${Date.now()}`,
        Name: templateName, // This must match an existing template name
        Recipient: surveyData.recipient || 'Default User',
        RiderName: surveyData.riderName || 'Default Rider',
        RideId: surveyData.rideId || `RIDE_${Date.now()}`,
        TenantId: surveyData.tenantId || 'itcurves',
        URL: surveyData.url || 'http://localhost:8080',
        Biodata: surveyData.biodata || 'Survey created via dashboard',
        Phone: surveyData.phone || '+15551234567',
        Bilingual: surveyData.bilingual !== undefined ? surveyData.bilingual : true
      };

      console.log('Creating survey with payload:', payload);

      const response = await fetch(`${API_BASE_URL}/surveys/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Survey creation error:', errorText);
        throw new Error(`Failed to create survey: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      console.log('Survey created successfully:', result);
      return result;
    } catch (error) {
      console.error('Error creating survey:', error);
      throw error;
    }
  },

  // Get survey by ID
  async getSurvey(surveyId) {
    try {
      const response = await fetch(`${API_BASE_URL}/surveys/${surveyId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch survey');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching survey:', error);
      throw error;
    }
  },

  // Update survey status
  async updateSurveyStatus(surveyId, status) {
    try {
      const response = await fetch(`${API_BASE_URL}/surveys/${surveyId}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ Status: status }),
      });

      if (!response.ok) {
        throw new Error('Failed to update survey status');
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating survey status:', error);
      throw error;
    }
  },

  // Delete survey
  async deleteSurvey(surveyId) {
    try {
      const response = await fetch(`${API_BASE_URL}/surveys/${surveyId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete survey');
      }

      return { success: true, message: 'Survey deleted successfully' };
    } catch (error) {
      console.error('Error deleting survey:', error);
      throw error;
    }
  },

  // Get survey statistics
  async getSurveyStats() {
    try {
      const response = await fetch(`${API_BASE_URL}/surveys/stats`);
      if (!response.ok) {
        throw new Error('Failed to fetch survey statistics');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching survey stats:', error);
      throw error;
    }
  },

  // Search surveys
  async searchSurveys(query) {
    try {
      const surveys = await this.getSurveys();
      
      if (!query || query.trim() === '') {
        return surveys;
      }

      const searchTerm = query.toLowerCase();
      return surveys.filter(survey => 
        survey.Name?.toLowerCase().includes(searchTerm) ||
        survey.Recipient?.toLowerCase().includes(searchTerm) ||
        survey.RiderName?.toLowerCase().includes(searchTerm) ||
        survey.Biodata?.toLowerCase().includes(searchTerm)
      );
    } catch (error) {
      console.error('Error searching surveys:', error);
      throw error;
    }
  },

  // Filter surveys by status
  async filterSurveys(status) {
    try {
      const surveys = await this.getSurveys();
      
      if (!status || status === 'all') {
        return surveys;
      }

      return surveys.filter(survey => survey.Status === status);
    } catch (error) {
      console.error('Error filtering surveys:', error);
      throw error;
    }
  }
};

// Template API utilities
export const templateAPI = {
  // Get all templates
  async getTemplates() {
    try {
      const response = await fetch(`${API_BASE_URL}/templates/list`);
      if (!response.ok) {
        throw new Error('Failed to fetch templates');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching templates:', error);
      throw error;
    }
  },

  // Create template
  async createTemplate(templateData) {
    try {
      const payload = {
        TemplateName: templateData.templateName || `Template_${Date.now()}`,
        Status: templateData.status || 'Draft',
        Description: templateData.description || 'Template created via dashboard',
        Category: templateData.category || 'General',
        Questions: templateData.questions || []
      };

      const response = await fetch(`${API_BASE_URL}/templates/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Template creation error:', errorText);
        throw new Error(`Failed to create template: ${response.status} - ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating template:', error);
      throw error;
    }
  },

  // Get template questions
  async getTemplateQuestions(templateName) {
    try {
      const response = await fetch(`${API_BASE_URL}/templates/getquestions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ TemplateName: templateName }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch template questions');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching template questions:', error);
      throw error;
    }
  }
};

// Analytics API utilities
export const analyticsAPI = {
  // Get analytics summary
  async getSummary() {
    try {
      const response = await fetch(`${API_BASE_URL}/analytics/summary`);
      if (!response.ok) {
        throw new Error('Failed to fetch analytics summary');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching analytics summary:', error);
      throw error;
    }
  }
};

export default surveyAPI;
