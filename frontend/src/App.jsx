import { useState } from "react";
import axios from "axios";
import FileUpload from "./components/FileUpload";
import JobDescriptionInput from "./components/JobDescriptionInput";
import CandidateList from "./components/CandidateList";
import Button from "./components/Button";
import "./styles.css";

export default function ResumeScreeningApp() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [candidates, setCandidates] = useState([]);

  const handleFileChange = (selectedFile) => {
    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file || !jobDescription) return;
    
    const formData = new FormData();
    formData.append("resume", file);
    formData.append("job_description", jobDescription);

    try {
      await axios.post("http://localhost:5000/upload", formData);
      alert("Resume uploaded successfully!");
    } catch (error) {
      alert("Error uploading resume");
    }
  };

  const fetchCandidates = async () => {
    try {
      const response = await axios.get("http://localhost:5000/candidates");
      setCandidates(response.data);
    } catch (error) {
      alert("Error fetching candidates");
    }
  };

  return (
    <div className="app-container">
      <h1 className="title">Resume Screening System</h1>
      <div className="upload-card">
        <h2 className="upload-title">Upload Resume</h2>
        <FileUpload onFileSelect={handleFileChange} />
        <JobDescriptionInput value={jobDescription} onChange={setJobDescription} />
        <Button onClick={handleUpload} className="upload-button">Upload Resume</Button>
      </div>
      <Button onClick={fetchCandidates} className="view-button">View Candidates</Button>
      <div className="candidates-container">
        <CandidateList candidates={candidates} />
      </div>
    </div>
  );
}
