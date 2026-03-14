import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Tooltip,
  Divider,
  useTheme,
} from '@mui/material';
import {
  RadioButtonChecked,
  TextFields,
  Star,
  CheckCircle,
  Numbers,
  CalendarToday,
  UploadFile,
  ArrowDropDown,
  CheckBox,
  GridOn,
  DragIndicator,
} from '@mui/icons-material';

const SurveyBuilderSidebar = ({ onAddQuestion, disabled }) => {
  const theme = useTheme();

  const questionTypes = [
    {
      type: 'multiple_choice',
      icon: RadioButtonChecked,
      label: 'Multiple Choice',
      description: 'Choose one option from a list',
      color: '#1976D2',
    },
    {
      type: 'checkbox',
      icon: CheckBox,
      label: 'Checkbox',
      description: 'Select multiple options',
      color: '#388E3C',
    },
    {
      type: 'text',
      icon: TextFields,
      label: 'Text Input',
      description: 'Short text answer',
      color: '#7B1FA2',
    },
    {
      type: 'rating',
      icon: Star,
      label: 'Rating Scale',
      description: 'Rate on a scale',
      color: '#F57C00',
    },
    {
      type: 'yes_no',
      icon: CheckCircle,
      label: 'Yes/No',
      description: 'Binary choice',
      color: '#D32F2F',
    },
    {
      type: 'number',
      icon: Numbers,
      label: 'Number',
      description: 'Numeric input',
      color: '#0288D1',
    },
    {
      type: 'date',
      icon: CalendarToday,
      label: 'Date/Time',
      description: 'Date and time picker',
      color: '#7B1FA2',
    },
    {
      type: 'dropdown',
      icon: ArrowDropDown,
      label: 'Dropdown',
      description: 'Select from dropdown',
      color: '#388E3C',
    },
    {
      type: 'file_upload',
      icon: UploadFile,
      label: 'File Upload',
      description: 'Upload files',
      color: '#F57C00',
    },
    {
      type: 'matrix',
      icon: GridOn,
      label: 'Matrix/Grid',
      description: 'Grid of questions',
      color: '#0288D1',
    },
  ];

  const handleAddQuestion = (questionType) => {
    if (!disabled) {
      onAddQuestion(questionType);
    }
  };

  return (
    <Box
      sx={{
        width: 280,
        bgcolor: 'white',
        borderRight: '1px solid',
        borderColor: 'divider',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
      }}
    >
      {/* Header */}
      <Box sx={{ p: 3, borderBottom: '1px solid', borderColor: 'divider' }}>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
          Question Types
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Drag or click to add questions
        </Typography>
      </Box>

      {/* Question Types List */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {questionTypes.map((questionType, index) => {
          const Icon = questionType.icon;
          
          return (
            <Paper
              key={questionType.type}
              onClick={() => handleAddQuestion(questionType.type)}
              sx={{
                p: 2,
                mb: 2,
                borderRadius: 2,
                cursor: disabled ? 'not-allowed' : 'pointer',
                border: `2px solid ${questionType.color}20`,
                bgcolor: disabled ? 'action.disabled' : 'white',
                transition: 'all 0.2s ease',
                '&:hover': !disabled && {
                  transform: 'translateY(-2px)',
                  boxShadow: `0 4px 12px ${questionType.color}30`,
                  borderColor: questionType.color,
                },
                opacity: disabled ? 0.5 : 1,
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                {/* Icon */}
                <Box
                  sx={{
                    width: 40,
                    height: 40,
                    borderRadius: 2,
                    bgcolor: `${questionType.color}15`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: questionType.color,
                    flexShrink: 0,
                  }}
                >
                  <Icon sx={{ fontSize: 20 }} />
                </Box>

                {/* Content */}
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Typography
                    variant="subtitle2"
                    sx={{
                      fontWeight: 600,
                      color: 'text.primary',
                      mb: 0.5,
                    }}
                  >
                    {questionType.label}
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      color: 'text.secondary',
                      display: 'block',
                      lineHeight: 1.3,
                    }}
                  >
                    {questionType.description}
                  </Typography>
                </Box>

                {/* Drag Indicator */}
                {!disabled && (
                  <DragIndicator
                    sx={{
                      color: 'text.disabled',
                      fontSize: 18,
                      alignSelf: 'center',
                    }}
                  />
                )}
              </Box>
            </Paper>
          );
        })}
      </Box>

      {/* Footer */}
      <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
          💡 Tip: Click to add or drag to position
        </Typography>
        <Button
          variant="outlined"
          size="small"
          fullWidth
          sx={{
            borderRadius: 2,
            textTransform: 'none',
            borderColor: 'divider',
            color: 'text.secondary',
            '&:hover': {
              borderColor: 'primary.main',
              bgcolor: 'action.hover',
            },
          }}
        >
          Import Questions
        </Button>
      </Box>
    </Box>
  );
};

export default SurveyBuilderSidebar;
