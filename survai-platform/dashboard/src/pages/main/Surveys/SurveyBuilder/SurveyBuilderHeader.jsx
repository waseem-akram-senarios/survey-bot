import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  IconButton,
  Tooltip,
  Divider,
  Badge,
  useTheme,
} from '@mui/material';
import {
  ArrowBack,
  Save,
  Preview,
  Publish,
  Settings,
  CloudUpload,
  CloudDone,
  CloudQueue,
} from '@mui/icons-material';

const SurveyBuilderHeader = ({
  survey,
  updateSurvey,
  onSave,
  onPublish,
  onPreview,
  previewMode,
  isSaving,
  isDirty,
  onBack,
}) => {
  const theme = useTheme();
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [tempTitle, setTempTitle] = useState(survey.title);

  const handleTitleClick = () => {
    setIsEditingTitle(true);
    setTempTitle(survey.title);
  };

  const handleTitleSave = () => {
    if (tempTitle.trim() && tempTitle !== survey.title) {
      updateSurvey({ title: tempTitle.trim() });
    }
    setIsEditingTitle(false);
  };

  const handleTitleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleTitleSave();
    } else if (e.key === 'Escape') {
      setIsEditingTitle(false);
      setTempTitle(survey.title);
    }
  };

  const getSaveIcon = () => {
    if (isSaving) return <CloudQueue sx={{ animation: 'pulse 1s infinite' }} />;
    if (isDirty) return <CloudUpload />;
    return <CloudDone />;
  };

  const getSaveColor = () => {
    if (isSaving) return 'warning';
    if (isDirty) return 'action';
    return 'success';
  };

  return (
    <Box
      sx={{
        bgcolor: 'white',
        borderBottom: '1px solid',
        borderColor: 'divider',
        px: 3,
        py: 2,
        display: 'flex',
        alignItems: 'center',
        gap: 2,
        minHeight: 72,
      }}
    >
      {/* Back Button */}
      <Tooltip title="Back to Surveys">
        <IconButton onClick={onBack} sx={{ color: 'text.secondary' }}>
          <ArrowBack />
        </IconButton>
      </Tooltip>

      <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />

      {/* Survey Title */}
      <Box sx={{ flex: 1, minWidth: 0 }}>
        {isEditingTitle ? (
          <TextField
            value={tempTitle}
            onChange={(e) => setTempTitle(e.target.value)}
            onBlur={handleTitleSave}
            onKeyDown={handleTitleKeyPress}
            variant="outlined"
            size="small"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
                fontSize: '1.25rem',
                fontWeight: 600,
              },
            }}
            autoFocus
          />
        ) : (
          <Typography
            variant="h5"
            sx={{
              fontWeight: 600,
              color: 'text.primary',
              cursor: 'pointer',
              '&:hover': {
                color: 'primary.main',
              },
              display: 'inline-block',
              maxWidth: '100%',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
            onClick={handleTitleClick}
            title="Click to edit title"
          >
            {survey.title}
          </Typography>
        )}
      </Box>

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {/* Save Button */}
        <Tooltip title={isDirty ? "Save changes" : "All changes saved"}>
          <Button
            variant={isDirty ? "contained" : "outlined"}
            startIcon={getSaveIcon()}
            onClick={onSave}
            disabled={isSaving || !isDirty}
            sx={{
              borderRadius: 2,
              px: 2,
              py: 1,
              textTransform: 'none',
              fontWeight: 500,
              borderColor: isDirty ? 'primary.main' : 'divider',
              bgcolor: isDirty ? 'primary.main' : 'transparent',
              color: isDirty ? 'white' : 'text.secondary',
              '&:hover': {
                bgcolor: isDirty ? 'primary.dark' : 'action.hover',
                borderColor: 'primary.main',
              },
              '&:disabled': {
                bgcolor: 'action.disabled',
                color: 'action.disabled',
                borderColor: 'divider',
              },
            }}
          >
            {isSaving ? 'Saving...' : 'Save'}
          </Button>
        </Tooltip>

        {/* Preview Button */}
        <Tooltip title={previewMode ? "Exit Preview" : "Preview Survey"}>
          <Button
            variant={previewMode ? "contained" : "outlined"}
            startIcon={<Preview />}
            onClick={onPreview}
            sx={{
              borderRadius: 2,
              px: 2,
              py: 1,
              textTransform: 'none',
              fontWeight: 500,
              borderColor: previewMode ? 'primary.main' : 'divider',
              bgcolor: previewMode ? 'primary.main' : 'transparent',
              color: previewMode ? 'white' : 'text.secondary',
              '&:hover': {
                bgcolor: previewMode ? 'primary.dark' : 'action.hover',
                borderColor: 'primary.main',
              },
            }}
          >
            {previewMode ? 'Edit' : 'Preview'}
          </Button>
        </Tooltip>

        {/* Publish Button */}
        <Tooltip title="Publish Survey">
          <Button
            variant="contained"
            startIcon={<Publish />}
            onClick={onPublish}
            disabled={isSaving || survey.questions.length === 0}
            sx={{
              borderRadius: 2,
              px: 2,
              py: 1,
              textTransform: 'none',
              fontWeight: 500,
              background: 'linear-gradient(135deg, #4CAF50 0%, #45A049 100%)',
              boxShadow: '0 2px 8px rgba(76, 175, 80, 0.3)',
              '&:hover': {
                background: 'linear-gradient(135deg, #45A049 0%, #3D8B40 100%)',
                boxShadow: '0 4px 12px rgba(76, 175, 80, 0.4)',
              },
              '&:disabled': {
                bgcolor: 'action.disabled',
                color: 'action.disabled',
                boxShadow: 'none',
              },
            }}
          >
            Publish
          </Button>
        </Tooltip>
      </Box>

      {/* Status Indicator */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 2 }}>
        <Badge
          badgeContent={survey.questions.length}
          color="primary"
          sx={{
            '& .MuiBadge-badge': {
              fontSize: '0.7rem',
              height: 16,
              minWidth: 16,
            },
          }}
        >
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              bgcolor: isDirty ? 'warning.main' : 'success.main',
            }}
          />
        </Badge>
        <Typography variant="caption" color="text.secondary">
          {survey.questions.length} {survey.questions.length === 1 ? 'question' : 'questions'}
        </Typography>
      </Box>
    </Box>
  );
};

export default SurveyBuilderHeader;
