import React from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  RadioGroup,
  FormControlLabel,
  Radio,
} from '@mui/material';

const MatrixQuestion = ({ question, preview = false, questionNumber, onUpdateQuestion }) => {
  if (preview) {
    return (
      <Box>
        <Typography variant="h6" sx={{ mb: 2 }}>
          {questionNumber && `Q${questionNumber}. `}{question.title}
          {question.required && <span style={{ color: 'red' }}> *</span>}
        </Typography>
        
        {question.description && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {question.description}
          </Typography>
        )}
        
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell></TableCell>
                {question.columns?.map((column) => (
                  <TableCell key={column.id} align="center">
                    {column.text}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {question.rows?.map((row) => (
                <TableRow key={row.id}>
                  <TableCell component="th" scope="row">
                    {row.text}
                  </TableCell>
                  {question.columns?.map((column) => (
                    <TableCell key={column.id} align="center">
                      <RadioGroup name={`${row.id}-${column.id}`}>
                        <FormControlLabel
                          value={`${row.id}-${column.id}`}
                          control={<Radio size="small" />}
                          label=""
                        />
                      </RadioGroup>
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 2 }}>
        {questionNumber && `Q${questionNumber}. `}{question.title}
        {question.required && <span style={{ color: 'red' }}> *</span>}
      </Typography>
      
      {question.description && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {question.description}
        </Typography>
      )}
      
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell></TableCell>
              {question.columns?.map((column) => (
                <TableCell key={column.id} align="center">
                  {column.text}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {question.rows?.map((row) => (
              <TableRow key={row.id}>
                <TableCell component="th" scope="row">
                  {row.text}
                </TableCell>
                {question.columns?.map((column) => (
                  <TableCell key={column.id} align="center">
                    <RadioGroup name={`${row.id}-${column.id}`}>
                      <FormControlLabel
                        value={`${row.id}-${column.id}`}
                        control={<Radio size="small" />}
                        label=""
                      />
                    </RadioGroup>
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default MatrixQuestion;
