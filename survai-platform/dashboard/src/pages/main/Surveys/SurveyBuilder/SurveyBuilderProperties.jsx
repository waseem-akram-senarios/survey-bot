import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Switch,
  FormControlLabel,
  Button,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  useTheme,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore,
  Settings,
  Info,
  Help,
  Visibility,
  Lock,
  Shuffle,
  Timer,
  Language,
  Email,
  Phone,
  Person,
} from '@mui/icons-material';

// Import property editors for different question types
import MultipleChoiceProperties from './Properties/MultipleChoiceProperties';
import TextProperties from './Properties/TextProperties';
import RatingProperties from './Properties/RatingProperties';
import YesNoProperties from './Properties/YesNoProperties';
import NumberProperties from './Properties/NumberProperties';
import DateProperties from './Properties/DateProperties';
import DropdownProperties from './Properties/DropdownProperties';
import CheckboxProperties from './Properties/CheckboxProperties';
import FileUploadProperties from './Properties/FileUploadProperties';
import MatrixProperties from './Properties/MatrixProperties';

const SurveyBuilderProperties = ({
  survey,
  selectedQuestion,
  onUpdateSurvey,
  onUpdateQuestion,
  previewMode,
  showSettings,
  onToggleSettings,
}) => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState('question');

  const getPropertyComponent = (questionType) => {
    const components = {
      multiple_choice: MultipleChoiceProperties,
      checkbox: CheckboxProperties,
      text: TextProperties,
      rating: RatingProperties,
      yes_no: YesNoProperties,
      number: NumberProperties,
      date: DateProperties,
      dropdown: DropdownProperties,
      file_upload: FileUploadProperties,
      matrix: MatrixProperties,
    };

    const Component = components[questionType];
    return Component ? Component : TextProperties;
  };

  const handleSurveySettingChange = (setting, value) => {
    onUpdateSurvey({
      settings: {
        ...survey.settings,
        [setting]: value,
      },
    });
  };

  if (previewMode) {
    return (
      <Box
        sx={{
          width: 320,
          bgcolor: 'white',
          borderLeft: '1px solid',
          borderColor: 'divider',
          p: 3,
        }}
      >
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
          Preview Mode
        </Typography>
        <Typography variant="body2" color="text.secondary">
          This is how your survey will appear to respondents. Switch to edit mode to make changes.
        </Typography>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        width: 320,
        bgcolor: 'white',
        borderLeft: '1px solid',
        borderColor: 'divider',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
      }}
    >
      {/* Header */}
      <Box sx={{ p: 3, borderBottom: '1px solid', borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Properties
          </Typography>
          <Tooltip title="Survey Settings">
            <IconButton
              size="small"
              onClick={onToggleSettings}
              color={showSettings ? 'primary' : 'default'}
            >
              <Settings />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Content */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {showSettings ? (
          // Survey Settings
          <Box sx={{ p: 3 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 3 }}>
              Survey Settings
            </Typography>

            {/* Basic Settings */}
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Info />
                  <Typography variant="subtitle2">Basic Information</Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <TextField
                  fullWidth
                  label="Survey Title"
                  value={survey.title}
                  onChange={(e) => onUpdateSurvey({ title: e.target.value })}
                  sx={{ mb: 2 }}
                  size="small"
                />
                
                <TextField
                  fullWidth
                  label="Description"
                  value={survey.description || ''}
                  onChange={(e) => onUpdateSurvey({ description: e.target.value })}
                  multiline
                  rows={3}
                  sx={{ mb: 2 }}
                  size="small"
                />
              </AccordionDetails>
            </Accordion>

            {/* Response Settings */}
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Person />
                  <Typography variant="subtitle2">Response Settings</Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <FormControlLabel
                  control={
                    <Switch
                      checked={survey.settings.allowAnonymous}
                      onChange={(e) => handleSurveySettingChange('allowAnonymous', e.target.checked)}
                    />
                  }
                  label="Allow anonymous responses"
                  sx={{ mb: 2, display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={survey.settings.requireAuthentication}
                      onChange={(e) => handleSurveySettingChange('requireAuthentication', e.target.checked)}
                    />
                  }
                  label="Require authentication"
                  sx={{ mb: 2, display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={survey.settings.showProgress}
                      onChange={(e) => handleSurveySettingChange('showProgress', e.target.checked)}
                    />
                  }
                  label="Show progress bar"
                  sx={{ mb: 2, display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
                />
              </AccordionDetails>
            </Accordion>

            {/* Question Settings */}
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Shuffle />
                  <Typography variant="subtitle2">Question Settings</Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <FormControlLabel
                  control={
                    <Switch
                      checked={survey.settings.randomizeQuestions}
                      onChange={(e) => handleSurveySettingChange('randomizeQuestions', e.target.checked)}
                    />
                  }
                  label="Randomize question order"
                  sx={{ mb: 2, display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={survey.settings.showQuestionNumbers}
                      onChange={(e) => handleSurveySettingChange('showQuestionNumbers', e.target.checked)}
                    />
                  }
                  label="Show question numbers"
                  sx={{ mb: 2, display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
                />
              </AccordionDetails>
            </Accordion>

            {/* Language Settings */}
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Language />
                  <Typography variant="subtitle2">Language Settings</Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <TextField
                  fullWidth
                  select
                  label="Default Language"
                  value={survey.settings.defaultLanguage || 'en'}
                  onChange={(e) => handleSurveySettingChange('defaultLanguage', e.target.value)}
                  sx={{ mb: 2 }}
                  size="small"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                </TextField>

                <FormControlLabel
                  control={
                    <Switch
                      checked={survey.settings.allowLanguageSwitch}
                      onChange={(e) => handleSurveySettingChange('allowLanguageSwitch', e.target.checked)}
                    />
                  }
                  label="Allow language switching"
                  sx={{ mb: 2, display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
                />
              </AccordionDetails>
            </Accordion>
          </Box>
        ) : (
          // Question Properties
          selectedQuestion ? (
            <Box sx={{ p: 3 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 3 }}>
                Question Properties
              </Typography>

              {/* Common Properties */}
              <TextField
                fullWidth
                label="Question Title"
                value={selectedQuestion.title}
                onChange={(e) => onUpdateQuestion(selectedQuestion.id, { title: e.target.value })}
                sx={{ mb: 2 }}
                size="small"
                multiline
                rows={2}
              />

              <TextField
                fullWidth
                label="Description (Optional)"
                value={selectedQuestion.description || ''}
                onChange={(e) => onUpdateQuestion(selectedQuestion.id, { description: e.target.value })}
                sx={{ mb: 2 }}
                size="small"
                multiline
                rows={2}
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={selectedQuestion.required}
                    onChange={(e) => onUpdateQuestion(selectedQuestion.id, { required: e.target.checked })}
                  />
                }
                label="Required question"
                sx={{ mb: 3, display: 'flex', flexDirection: 'row-reverse', justifyContent: 'space-between' }}
              />

              <Divider sx={{ mb: 3 }} />

              {/* Type-specific Properties */}
              {(() => {
                const PropertyComponent = getPropertyComponent(selectedQuestion.type);
                return (
                  <PropertyComponent
                    question={selectedQuestion}
                    onUpdateQuestion={onUpdateQuestion}
                  />
                );
              })()}
            </Box>
          ) : (
            // No Question Selected
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  bgcolor: 'action.hover',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: 3,
                }}
              >
                <Help sx={{ fontSize: 40, color: 'text.secondary' }} />
              </Box>
              
              <Typography variant="h6" sx={{ mb: 1, color: 'text.secondary' }}>
                No Question Selected
              </Typography>
              
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Select a question from the canvas to edit its properties, or adjust survey settings.
              </Typography>
              
              <Button
                variant="outlined"
                onClick={onToggleSettings}
                sx={{ borderRadius: 2 }}
              >
                Survey Settings
              </Button>
            </Box>
          )
        )}
      </Box>
    </Box>
  );
};

export default SurveyBuilderProperties;
