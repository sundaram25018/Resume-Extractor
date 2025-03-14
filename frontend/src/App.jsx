// frontend/src/App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Container,
  Typography,
  TextField,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  Box,
  styled,
  LinearProgress,
  Alert
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

// Custom theme for background color
const theme = {
  palette: {
    background: {
      default: '#ffffff', // Black background
    },
    text: {
      primary: '#ffffff', // White text
    },
  },
};

const StyledContainer = styled(Container)(() => ({
  backgroundColor: theme.palette.background.default,
  minHeight: '100vh',
  paddingBottom: '32px',
}));

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  marginBottom: theme.spacing(3),
  borderRadius: '10px',
  boxShadow: '0px 3px 5px rgba(0,0,0,0.2)',
  backgroundColor: '#ffffff', // White paper background
}));

const StyledButton = styled(Button)(({ theme }) => ({
  marginTop: theme.spacing(2),
  backgroundColor: '#1976d2',
  color: 'white',
  '&:hover': {
    backgroundColor: '#1565c0',
  },
}));

const StyledTypography = styled(Typography)(({ theme }) => ({
  marginBottom: theme.spacing(2),
  color: '#333',
}));

const App = () => {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [extractedData, setExtractedData] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    setResumeFile(event.target.files[0]);
  };

  const handleDescriptionChange = (event) => {
    setJobDescription(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append('resume', resumeFile);
    formData.append('job_description', jobDescription);

    try {
      const response = await axios.post('http://localhost:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setExtractedData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error uploading resume:', error);
      setError('Failed to upload resume. Please try again.');
      setLoading(false);
    }
  };

  useEffect(() => {
    const fetchCandidates = async () => {
      try {
        const response = await axios.get('http://localhost:5000/candidates');
        setCandidates(response.data);
      } catch (error) {
        console.error('Error fetching candidates:', error);
        setError('Failed to fetch candidates.');
      }
    };

    fetchCandidates();
  }, [extractedData]);

  return (
    <StyledContainer maxWidth="md">
      <StyledTypography variant="h4" component="h1" align="center" gutterBottom>
        AI-Powered Resume Screening System
      </StyledTypography>

      <StyledPaper>
        <form onSubmit={handleSubmit}>
          <Box mb={2}>
            <Button
              variant="contained"
              component="label"
              startIcon={<CloudUploadIcon />}
            >
              Upload Resume
              <input type="file" accept=".pdf,.docx,.txt,.png,.jpg,.jpeg" onChange={handleFileChange} hidden />
            </Button>
            {resumeFile && (
              <Typography variant="body2" style={{ marginLeft: '10px' }}>
                {resumeFile.name}
              </Typography>
            )}
          </Box>
          <TextField
            label="Enter Job Description"
            multiline
            rows={4}
            variant="outlined"
            fullWidth
            value={jobDescription}
            onChange={handleDescriptionChange}
            margin="normal"
          />
          <StyledButton type="submit" variant="contained" color="primary" disabled={loading}>
            {loading ? 'Screening...' : 'Screen Resume'}
          </StyledButton>
        </form>
      </StyledPaper>

      {loading && <LinearProgress />}
      {error && (
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {extractedData && (
        <StyledPaper>
          <Typography variant="h6">Extracted Details</Typography>
          <Typography><strong>Name:</strong> {extractedData.name}</Typography>
          <Typography><strong>Email:</strong> {extractedData.email}</Typography>
          <Typography><strong>Phone:</strong> {extractedData.phone}</Typography>
          <Typography><strong>Skills:</strong> {extractedData.skills}</Typography>
          <Typography><strong>Education:</strong> {extractedData.education}</Typography>
          <Typography><strong>Experience:</strong> {extractedData.experience}</Typography>
          <Typography><strong>Match Score:</strong> {extractedData.match_score?.toFixed(2)}</Typography>
        </StyledPaper>
      )}

      <StyledPaper>
        <Typography variant="h6">Ranked Candidates</Typography>
        <List>
          {candidates.map((candidate, index) => (
            <ListItem key={index}>
              <ListItemText
                primary={`${index + 1}. ${candidate.name} (${candidate.email})`}
                secondary={`Match Score: ${candidate.match_score?.toFixed(2)}`}
              />
            </ListItem>
          ))}
        </List>
      </StyledPaper>
    </StyledContainer>
  );
};

export default App;
