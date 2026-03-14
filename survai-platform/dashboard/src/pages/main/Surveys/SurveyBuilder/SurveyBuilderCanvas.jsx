import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  IconButton,
  Tooltip,
  Divider,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Add,
  DragIndicator,
  Delete,
  Edit,
  ContentCopy,
  Visibility,
  VisibilityOff,
  ArrowUpward,
  ArrowDownward,
} from '@mui/icons-material';

// Import question components
import MultipleChoiceQuestion from './Questions/MultipleChoiceQuestion';
import TextQuestion from './Questions/TextQuestion';
import RatingQuestion from './Questions/RatingQuestion';
import YesNoQuestion from './Questions/YesNoQuestion';
import NumberQuestion from './Questions/NumberQuestion';
import DateQuestion from './Questions/DateQuestion';
import DropdownQuestion from './Questions/DropdownQuestion';
import CheckboxQuestion from './Questions/CheckboxQuestion';
import FileUploadQuestion from './Questions/FileUploadQuestion';
import MatrixQuestion from './Questions/MatrixQuestion';

const SurveyBuilderCanvas = ({
  survey,
  selectedQuestion,
  onSelectQuestion,
  onUpdateQuestion,
  onDeleteQuestion,
  onReorderQuestions,
  previewMode,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery('(max-width: 768px)');

  const [draggedQuestion, setDraggedQuestion] = useState(null);
  const [dragOverIndex, setDragOverIndex] = useState(null);

  const getQuestionComponent = (questionType) => {
    const components = {
      multiple_choice: MultipleChoiceQuestion,
      checkbox: CheckboxQuestion,
      text: TextQuestion,
      rating: RatingQuestion,
      yes_no: YesNoQuestion,
      number: NumberQuestion,
      date: DateQuestion,
      dropdown: DropdownQuestion,
      file_upload: FileUploadQuestion,
      matrix: MatrixQuestion,
    };

    const Component = components[questionType];
    return Component ? Component : TextQuestion;
  };

  const handleDragStart = (e, question) => {
    if (previewMode) return;
    
    setDraggedQuestion(question);
    e.dataTransfer.effectAllowed = 'move';
    
    // Create a custom drag image
    const dragImage = e.currentTarget.cloneNode(true);
    dragImage.style.opacity = '0.5';
    dragImage.style.position = 'absolute';
    dragImage.style.top = '-1000px';
    document.body.appendChild(dragImage);
    e.dataTransfer.setDragImage(dragImage, 0, 0);
    setTimeout(() => document.body.removeChild(dragImage), 0);
  };

  const handleDragOver = (e, index) => {
    if (previewMode) return;
    
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverIndex(index);
  };

  const handleDragLeave = () => {
    setDragOverIndex(null);
  };

  const handleDrop = (e, dropIndex) => {
    if (previewMode) return;
    
    e.preventDefault();
    setDragOverIndex(null);
    
    if (!draggedQuestion) return;
    
    const draggedIndex = survey.questions.findIndex(q => q.id === draggedQuestion.id);
    if (draggedIndex === dropIndex) return;
    
    onReorderQuestions(draggedIndex, dropIndex);
    setDraggedQuestion(null);
  };

  const handleDuplicateQuestion = (question) => {
    const duplicatedQuestion = {
      ...question,
      id: `q-${Date.now()}`,
      title: `${question.title} (Copy)`,
      order: question.order + 0.5,
    };
    
    // Insert the duplicated question after the original
    const newQuestions = [...survey.questions];
    const originalIndex = newQuestions.findIndex(q => q.id === question.id);
    newQuestions.splice(originalIndex + 1, 0, duplicatedQuestion);
    
    // Reorder all questions
    newQuestions.forEach((q, index) => {
      q.order = index + 1;
    });
    
    onUpdateQuestion(null, { questions: newQuestions });
  };

  const handleToggleRequired = (question) => {
    onUpdateQuestion(question.id, { required: !question.required });
  };

  const handleMoveQuestion = (questionId, direction) => {
    const currentIndex = survey.questions.findIndex(q => q.id === questionId);
    let newIndex;
    
    if (direction === 'up' && currentIndex > 0) {
      newIndex = currentIndex - 1;
    } else if (direction === 'down' && currentIndex < survey.questions.length - 1) {
      newIndex = currentIndex + 1;
    } else {
      return;
    }
    
    onReorderQuestions(currentIndex, newIndex);
  };

  if (previewMode) {
    return (
      <Box sx={{ flex: 1, p: 3, overflow: 'auto' }}>
        <Paper sx={{ maxWidth: 800, mx: 'auto', p: 4 }}>
          <Typography variant="h4" sx={{ mb: 2, textAlign: 'center' }}>
            {survey.title}
          </Typography>
          
          {survey.description && (
            <Typography variant="body1" sx={{ mb: 4, textAlign: 'center', color: 'text.secondary' }}>
              {survey.description}
            </Typography>
          )}
          
          {survey.questions.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <Typography color="text.secondary">
                No questions added yet. Switch to edit mode to add questions.
              </Typography>
            </Box>
          ) : (
            survey.questions.map((question, index) => {
              const QuestionComponent = getQuestionComponent(question.type);
              return (
                <Box key={question.id} sx={{ mb: 3 }}>
                  <QuestionComponent
                    question={question}
                    preview={true}
                    questionNumber={index + 1}
                  />
                </Box>
              );
            })
          )}
          
          <Box sx={{ mt: 4, textAlign: 'center' }}>
            <Button variant="contained" size="large">
              Submit Survey
            </Button>
          </Box>
        </Paper>
      </Box>
    );
  }

  return (
    <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Canvas Header */}
      <Box sx={{ p: 3, borderBottom: '1px solid', borderColor: 'divider' }}>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
          Survey Questions
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Click on a question to edit its properties
        </Typography>
      </Box>

      {/* Questions Canvas */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
        {survey.questions.length === 0 ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              textAlign: 'center',
              py: 8,
            }}
          >
            <Box
              sx={{
                width: 120,
                height: 120,
                borderRadius: '50%',
                bgcolor: 'action.hover',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 3,
              }}
            >
              <Add sx={{ fontSize: 48, color: 'text.secondary' }} />
            </Box>
            
            <Typography variant="h6" sx={{ mb: 1, color: 'text.secondary' }}>
              Start Building Your Survey
            </Typography>
            
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3, maxWidth: 400 }}>
              Add questions from the sidebar to get started. You can drag and drop to reorder them.
            </Typography>
            
            <Button
              variant="outlined"
              startIcon={<Add />}
              sx={{ borderRadius: 2 }}
            >
              Add Your First Question
            </Button>
          </Box>
        ) : (
          <Box sx={{ maxWidth: 800, mx: 'auto' }}>
            {survey.questions.map((question, index) => {
              const QuestionComponent = getQuestionComponent(question.type);
              const isSelected = selectedQuestion?.id === question.id;
              const isDragOver = dragOverIndex === index;
              
              return (
                <Box key={question.id}>
                  {/* Drop Zone */}
                  <Box
                    onDragOver={(e) => handleDragOver(e, index)}
                    onDragLeave={handleDragLeave}
                    onDrop={(e) => handleDrop(e, index)}
                    sx={{
                      height: isDragOver ? 40 : 0,
                      bgcolor: isDragOver ? 'primary.light' : 'transparent',
                      borderRadius: 1,
                      mb: isDragOver ? 2 : 1,
                      transition: 'all 0.2s ease',
                      border: isDragOver ? `2px dashed ${theme.palette.primary.main}` : 'none',
                    }}
                  />
                  
                  {/* Question Card */}
                  <Paper
                    draggable={!previewMode}
                    onDragStart={(e) => handleDragStart(e, question)}
                    onClick={() => onSelectQuestion(question)}
                    sx={{
                      p: 3,
                      borderRadius: 2,
                      border: isSelected ? `2px solid ${theme.palette.primary.main}` : '1px solid',
                      borderColor: isSelected ? 'primary.main' : 'divider',
                      bgcolor: isSelected ? 'primary.light' : 'white',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        boxShadow: 2,
                        borderColor: 'primary.main',
                      },
                    }}
                  >
                    {/* Question Header */}
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <DragIndicator sx={{ mr: 2, color: 'text.disabled' }} />
                      
                      <Typography variant="body2" color="text.secondary" sx={{ mr: 2 }}>
                        Q{index + 1}
                      </Typography>
                      
                      <Typography
                        variant="subtitle1"
                        sx={{
                          flex: 1,
                          fontWeight: 500,
                          color: isSelected ? 'primary.dark' : 'text.primary',
                        }}
                      >
                        {question.title}
                      </Typography>
                      
                      {question.required && (
                        <Typography
                          variant="caption"
                          sx={{
                            px: 1,
                            py: 0.5,
                            bgcolor: 'error.light',
                            color: 'error.dark',
                            borderRadius: 1,
                            mr: 1,
                          }}
                        >
                          Required
                        </Typography>
                      )}
                      
                      {/* Action Buttons */}
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Tooltip title="Move Up">
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleMoveQuestion(question.id, 'up');
                            }}
                            disabled={index === 0}
                            sx={{ mr: 0.5 }}
                          >
                            <ArrowUpward />
                          </IconButton>
                        </Tooltip>
                        
                        <Tooltip title="Move Down">
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleMoveQuestion(question.id, 'down');
                            }}
                            disabled={index === survey.questions.length - 1}
                            sx={{ mr: 0.5 }}
                          >
                            <ArrowDownward />
                          </IconButton>
                        </Tooltip>
                        
                        <Tooltip title="Duplicate">
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDuplicateQuestion(question);
                            }}
                            sx={{ mr: 0.5 }}
                          >
                            <ContentCopy />
                          </IconButton>
                        </Tooltip>
                        
                        <Tooltip title={question.required ? 'Make Optional' : 'Make Required'}>
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleToggleRequired(question);
                            }}
                            sx={{ mr: 0.5 }}
                          >
                            {question.required ? <Visibility /> : <VisibilityOff />}
                          </IconButton>
                        </Tooltip>
                        
                        <Tooltip title="Delete">
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              onDeleteQuestion(question.id);
                            }}
                            color="error"
                          >
                            <Delete />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </Box>
                    
                    {/* Question Preview */}
                    <Box sx={{ ml: 5 }}>
                      <QuestionComponent
                        question={question}
                        preview={true}
                        questionNumber={index + 1}
                      />
                    </Box>
                  </Paper>
                </Box>
              );
            })}
            
            {/* Final Drop Zone */}
            <Box
              onDragOver={(e) => handleDragOver(e, survey.questions.length)}
              onDragLeave={handleDragLeave}
              onDrop={(e) => handleDrop(e, survey.questions.length)}
              sx={{
                height: dragOverIndex === survey.questions.length ? 40 : 0,
                bgcolor: dragOverIndex === survey.questions.length ? 'primary.light' : 'transparent',
                borderRadius: 1,
                mt: 2,
                transition: 'all 0.2s ease',
                border: dragOverIndex === survey.questions.length ? `2px dashed ${theme.palette.primary.main}` : 'none',
              }}
            />
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default SurveyBuilderCanvas;
