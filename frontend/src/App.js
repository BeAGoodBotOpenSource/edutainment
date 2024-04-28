import React, { useState, useEffect, useRef } from "react";
import { FileUpload } from 'primereact/fileupload';
import { Button } from 'primereact/button';
import { Accordion, AccordionTab } from 'primereact/accordion';
import { Carousel } from 'primereact/carousel';
import { Checkbox } from 'primereact/checkbox';
import { Dropdown } from 'primereact/dropdown';
import { classNames } from 'primereact/utils';
import { Toast } from 'primereact/toast';
import { v4 as uuidv4 } from 'uuid';
import "primereact/resources/themes/lara-light-indigo/theme.css";
import "primereact/resources/primereact.min.css";
import 'primeicons/primeicons.css';
import './App.css';

function App() {
  const sessionId = uuidv4();
  const [selectedFile, setSelectedFile] = useState(null);
  const [age, setAge] = useState(null);
  const [expertise, setExpertise] = useState(null);
  const [showSuccessToast, setShowSuccessToast] = useState(false);
  const [showErrorToast, setShowErrorToast] = useState(false);
  const [isSubmitDisabled, setIsSubmitDisabled] = useState(true);
  const ageOptions = Array.from({ length: 96 }, (_, i) => ({ label: `${i + 5}`, value: i + 5 }));
  const [videoData, setVideoData] = useState(null);
  const [videoPaths, setVideoPaths] = useState([]);
  const [courseData, setCourseData] = useState([]);
  const [userAnswers, setUserAnswers] = useState({}); 
  const [playingAudio, setPlayingAudio] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const audioRef = useRef(null);

  const lessonTemplate = (lesson) => {
    if (!lesson) {
      return <div>No Lesson Available</div>
    }
    const userAnswer = userAnswers[lesson.lesson_id];
    return (
      <div>
        <h3>Lesson</h3>
        <p>{lesson.lesson_content}</p>
        
        <h4>{lesson.question}</h4>
        
        <div className="answers">
          <p>
            <Checkbox inputId={`${lesson.lesson_id}-right`} value={lesson.right_answer} onChange={() => handleCheck(lesson.lesson_id, lesson.right_answer)} checked={userAnswer === lesson.right_answer}/>
            <label htmlFor={`${lesson.lesson_id}-right`}>{' ' + lesson.right_answer}</label>
          </p>
          <p>
            <Checkbox inputId={`${lesson.lesson_id}-wrong`} value={lesson.wrong_answer} onChange={() => handleCheck(lesson.lesson_id, lesson.wrong_answer)} checked={userAnswer === lesson.wrong_answer}/>
            <label htmlFor={`${lesson.lesson_id}-wrong`}>{' ' + lesson.wrong_answer}</label>
          </p>
        </div>
        
        {userAnswer !== undefined && (
          <div>
            <h4>{userAnswer === lesson.right_answer ? "Correct!" : "Incorrect!"}</h4>
            <p>{lesson.right_answer_explanation}</p>
          </div>
        )}
        <audio ref={audioRef} src={`${process.env.REACT_APP_API_BASE_URL}/${lesson.narration_file}`} />
      </div>
    );
  };
  
  const topicTemplate = (topic) => {
    if (!topic || !topic.lessons) {
      return <div>No topic available</div>;
    }
    return (
      <div>
        <br></br>
        <br></br>
        <br></br>
        <h2>{topic.topicName}</h2>
        <Accordion onTabOpen={handleTabOpen} onTabClose={handleTabClose}>
          {topic.lessons.map((lesson) => (
            <AccordionTab header={`Lesson ${lesson.order_num + 1}`} key={lesson.lesson_id}>
              {lessonTemplate(lesson)}
            </AccordionTab>
          ))}
        </Accordion>
      </div>
    );
  };

  const handleTabOpen = (e) => {
    // Stop the currently playing audio (if any)
    if (audioRef.current) {
      audioRef.current.pause();
    }
    // Get the narration file of the opened lesson and play it
    const lesson = courseData[0]?.lessons[e.index];
    if (lesson) {
      setPlayingAudio(lesson.narration_file);
      setTimeout(() => {
        audioRef.current.src = `${process.env.REACT_APP_API_BASE_URL}/${lesson.narration_file}`;
        audioRef.current.play().catch((error) => console.error("Audio Play Error:", error));
        }, 0);
    }
  };

  const handleTabClose = (e) => {
    // Stop the currently playing audio
    if (audioRef.current) {
      audioRef.current.pause();
      setPlayingAudio(null);
    }
  };

  const handleCheck = (lessonId, selectedAnswer) => {
    setUserAnswers(prev => ({...prev, [lessonId]: selectedAnswer}));
  };

  useEffect(() => {
    if (selectedFile && age && expertise) {
      setIsSubmitDisabled(false);
    } else {
      setIsSubmitDisabled(true);
    }
  }, [selectedFile, age, expertise]);

  function handleFileUpload(event) {
    const file = event.files[0];
    if (file && file.type === "application/pdf") {
      setSelectedFile(file);
      setShowErrorToast(false);
    } else {
      setSelectedFile(null);
      setShowErrorToast(true);
    }
  }

  function handleAgeChange(event) {
    setAge(event.value);
  }

  function handleExpertiseChange(event) {
    setExpertise(event.value);
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (selectedFile && age && expertise) {
      setIsSubmitting(true); // Set isSubmitting to true when form submission starts
      let formData = new FormData();
      formData.append('selectedFile', selectedFile);
      formData.append('age', age);
      formData.append('expertise', expertise);
      formData.append('sessionId', sessionId);
  
      fetch(`${process.env.REACT_APP_API_BASE_URL}/generate-course`, {
        method: "POST",
        mode: "cors",
        body: formData,
      })
      .then((res) => res.json())
      .then((data) => {
        if (data) {
          const formattedData = Object.keys(data).map(topicName => ({
            topicName,
            lessons: data[topicName],
          }));
          setCourseData(formattedData);
          setShowSuccessToast(true);
        }     
        setShowSuccessToast(true);
      })
      .catch(error => {
        console.error(error);
        setShowErrorToast(true);
      })
      .finally(() => {
        setIsSubmitting(false); // Set isSubmitting back to false once submission is complete
      });
      } else {
        setShowErrorToast(true);
      }
  }

  const expertiseOptions = [
    { label: 'Beginner', value: 'beginner' },
    { label: 'Intermediate', value: 'intermediate' },
    { label: 'Advanced', value: 'advanced' }
  ];

  const renderHeader = (title, active) => {
    return (
      <React.Fragment>
        {selectedFile && ( // Display green icon if file is selected
          <i className={classNames('pi', {'pi-check': showSuccessToast})} style={{'fontSize': '1.5em', 'color': 'green', 'marginRight': '10px'}}></i>
        )}
        <span>{title}</span>
      </React.Fragment>
    );
  };

  return (
    <div className="App">
      <header className="App-header">
        <i className="pi pi-book" style={{'fontSize': '2em', 'color': 'black'}}></i>
        <h1 className="App-title" style={{'color': 'black'}}>Learn Anything with BGB EduTainment!</h1>
        <Accordion className="p-accordion">
          <AccordionTab header={renderHeader("Upload PDF")} rightIcon="pi pi-chevron-down">
            <form className="App-form" onSubmit={handleSubmit}>
              <FileUpload
                name="pdf"
                chooseLabel=" Choose PDF"
                uploadLabel="Upload"
                cancelLabel="Cancel"
                customUpload={true}
                accept="application/pdf"
                maxFileSize={2000000}
                onSelect={handleFileUpload}
                className="p-fileupload-content"
              />
              {selectedFile && (
                <div className="p-fileupload-filename">
                  Selected File: {selectedFile.name}
                </div>
              )}
              {showErrorToast && (
                <div className="p-message p-message-error">
                  <span className="p-message-text">Please select a valid PDF file.</span>
                </div>
              )}
            </form>
          </AccordionTab>
          <AccordionTab header={renderHeader("Audience Info")} rightIcon="pi pi-chevron-down">
            <div className="p-field">
              <label htmlFor="age" className="p-d-block">Age </label>
              <Dropdown
                id="age"
                value={age}
                options={ageOptions}
                onChange={handleAgeChange}
                placeholder="Select Age"
                className="w-full md:w-14rem"
              />
            </div>
            <br></br>
            <div className="p-field">
              <label htmlFor="expertise" className="p-d-block">Expertise Level </label>
              <Dropdown
                id="expertise"
                value={expertise}
                options={expertiseOptions}
                onChange={handleExpertiseChange}
                placeholder="Level"
                className="w-full md:w-14rem"
              />
            </div>
          </AccordionTab>
        </Accordion>
        <Button type="submit" label="Submit" className="p-button" onClick={handleSubmit} disabled={isSubmitDisabled || isSubmitting} />
          {isSubmitting && (
            <div className="loading-icon">
              <br></br>
              {/* Replace with your actual loading icon */}
              Loading lessons...
            </div>
          )}
              {courseData && courseData.length > 0 && (
            <div className="course-content">
                <Carousel value={courseData} itemTemplate={topicTemplate} />
            </div>
          )
          }
        <Toast
          visible={showSuccessToast}
          severity="success"
          life={3000}
          onHide={() => setShowSuccessToast(false)}
          position="top-right"
          className="success-toast"
        >
          <div className="p-toast-message">
            <i className="pi pi-check-circle"></i>
            <span>Form submitted successfully!</span>
          </div>
        </Toast>
      </header>
    </div>
  );
}

export default App;
