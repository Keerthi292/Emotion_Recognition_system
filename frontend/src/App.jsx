"use client"

import { useState, useEffect } from "react"
import { Container, Row, Col, Card, Button, Form, Alert, Badge, Spinner } from "react-bootstrap"

export default function App() {
  const [textInput, setTextInput] = useState("")
  const [audioFile, setAudioFile] = useState(null)
  const [imageFile, setImageFile] = useState(null)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [useMockAPI, setUseMockAPI] = useState(true)
  const [showSettings, setShowSettings] = useState(false)
  const [backendStatus, setBackendStatus] = useState("checking")

  // Check backend status on component mount
  useEffect(() => {
    checkBackendStatus()
  }, [])

  const checkBackendStatus = async () => {
    try {
      const response = await fetch("http://localhost:5000/health")
      if (response.ok) {
        setBackendStatus("online")
        setUseMockAPI(false)
      } else {
        setBackendStatus("offline")
      }
    } catch (error) {
      setBackendStatus("offline")
    }
  }

  // Mock emotion detection functions
  const mockTextEmotionAnalysis = (text) => {
    const emotions = ["joy", "sadness", "anger", "fear", "surprise", "neutral"]
    const results = []

    const lowerText = text.toLowerCase()

    if (lowerText.includes("happy") || lowerText.includes("excited") || lowerText.includes("great")) {
      results.push({ emotion: "joy", confidence: 75 + Math.random() * 20 })
    }
    if (lowerText.includes("nervous") || lowerText.includes("worried") || lowerText.includes("anxious")) {
      results.push({ emotion: "fear", confidence: 60 + Math.random() * 25 })
    }
    if (lowerText.includes("confident") || lowerText.includes("ready") || lowerText.includes("prepared")) {
      results.push({ emotion: "neutral", confidence: 70 + Math.random() * 20 })
    }
    if (lowerText.includes("sad") || lowerText.includes("disappointed") || lowerText.includes("down")) {
      results.push({ emotion: "sadness", confidence: 65 + Math.random() * 20 })
    }
    if (lowerText.includes("angry") || lowerText.includes("frustrated") || lowerText.includes("mad")) {
      results.push({ emotion: "anger", confidence: 70 + Math.random() * 15 })
    }

    if (results.length === 0) {
      const randomEmotions = emotions.sort(() => 0.5 - Math.random()).slice(0, 3)
      randomEmotions.forEach((emotion) => {
        results.push({ emotion, confidence: 20 + Math.random() * 60 })
      })
    }

    const total = results.reduce((sum, r) => sum + r.confidence, 0)
    return results
      .map((r) => ({ ...r, confidence: (r.confidence / total) * 100 }))
      .sort((a, b) => b.confidence - a.confidence)
  }

  const mockAudioEmotionAnalysis = () => {
    return [
      { emotion: "neutral", confidence: 45 + Math.random() * 20 },
      { emotion: "fear", confidence: 25 + Math.random() * 15 },
      { emotion: "joy", confidence: 15 + Math.random() * 15 },
      { emotion: "surprise", confidence: 10 + Math.random() * 10 },
      { emotion: "sadness", confidence: 5 + Math.random() * 10 },
    ].sort((a, b) => b.confidence - a.confidence)
  }

  const mockVisualEmotionAnalysis = () => {
    return [
      { emotion: "neutral", confidence: 40 + Math.random() * 25 },
      { emotion: "joy", confidence: 30 + Math.random() * 20 },
      { emotion: "surprise", confidence: 15 + Math.random() * 15 },
      { emotion: "fear", confidence: 10 + Math.random() * 10 },
      { emotion: "sadness", confidence: 5 + Math.random() * 10 },
    ].sort((a, b) => b.confidence - a.confidence)
  }

  const combineEmotions = (textEmotions, audioEmotions, visualEmotions) => {
    const emotionMap = new Map()
    const weights = { text: 0.4, audio: 0.3, visual: 0.3 }
    ;[
      { emotions: textEmotions, weight: weights.text },
      { emotions: audioEmotions, weight: weights.audio },
      { emotions: visualEmotions, weight: weights.visual },
    ].forEach(({ emotions, weight }) => {
      emotions.forEach(({ emotion, confidence }) => {
        const current = emotionMap.get(emotion) || 0
        emotionMap.set(emotion, current + confidence * weight)
      })
    })

    return Array.from(emotionMap.entries())
      .map(([emotion, confidence]) => ({ emotion, confidence }))
      .sort((a, b) => b.confidence - a.confidence)
      .slice(0, 5)
  }

  const generateInsights = (combinedEmotions) => {
    if (!combinedEmotions.length) return "No emotions detected."

    const topEmotion = combinedEmotions[0]
    const secondEmotion = combinedEmotions[1]

    let insight = ""

    if (topEmotion.emotion === "joy" && topEmotion.confidence > 50) {
      insight = "Great! You're showing positive emotions. This confidence will serve you well in interviews."
    } else if (topEmotion.emotion === "fear" && topEmotion.confidence > 40) {
      insight = "It's normal to feel nervous during interviews. Try deep breathing exercises to manage anxiety."
    } else if (topEmotion.emotion === "neutral" && topEmotion.confidence > 40) {
      insight = "You're maintaining composure well. Consider adding more enthusiasm to show engagement."
    } else if (secondEmotion && Math.abs(topEmotion.confidence - secondEmotion.confidence) < 20) {
      insight = `You're experiencing mixed emotions (${topEmotion.emotion} and ${secondEmotion.emotion}). This is completely normal in interview settings.`
    } else {
      insight = "Your emotional state shows complexity, which is natural. Focus on highlighting your strengths."
    }

    return insight
  }

  const callRealAPI = async () => {
    const formData = new FormData()
    if (textInput) formData.append("text", textInput)
    if (audioFile) formData.append("audio", audioFile)
    if (imageFile) formData.append("image", imageFile)

    const response = await fetch("http://localhost:5000/analyze", {
      method: "POST",
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  }

  const callMockAPI = async () => {
    await new Promise((resolve) => setTimeout(resolve, 2000))

    const analysisResult = {}

    if (textInput.trim()) {
      analysisResult.text_emotions = mockTextEmotionAnalysis(textInput)
    }

    if (audioFile) {
      analysisResult.audio_emotions = mockAudioEmotionAnalysis()
    }

    if (imageFile) {
      analysisResult.visual_emotions = mockVisualEmotionAnalysis()
    }

    const textEmotions = analysisResult.text_emotions || []
    const audioEmotions = analysisResult.audio_emotions || []
    const visualEmotions = analysisResult.visual_emotions || []

    if (textEmotions.length > 0 || audioEmotions.length > 0 || visualEmotions.length > 0) {
      analysisResult.combined_emotions = combineEmotions(textEmotions, audioEmotions, visualEmotions)
    }

    return analysisResult
  }

  const handleAnalyze = async () => {
    if (!textInput && !audioFile && !imageFile) {
      alert("Please provide at least one input (text, audio, or image)")
      return
    }

    setLoading(true)

    try {
      let data
      if (useMockAPI) {
        data = await callMockAPI()
      } else {
        data = await callRealAPI()
      }

      setResults(data)
    } catch (error) {
      console.error("Error:", error)
      if (useMockAPI) {
        alert("Error in mock analysis. Please try again.")
      } else {
        alert("Error connecting to server. Please ensure the backend is running on http://localhost:5000")
      }
    } finally {
      setLoading(false)
    }
  }

  const loadSampleData = () => {
    setTextInput(
      "I'm feeling quite nervous about this interview, but I'm also excited about the opportunity. I've prepared well and I'm confident in my abilities, though I can't help but feel a bit anxious about the questions they might ask. Overall, I'm happy to be here and ready to showcase my skills.",
    )

    const mockAudioFile = new File(["mock audio data"], "sample-interview-response.wav", { type: "audio/wav" })
    setAudioFile(mockAudioFile)

    const mockImageFile = new File(["mock image data"], "candidate-photo.jpg", { type: "image/jpeg" })
    setImageFile(mockImageFile)
  }

  const clearAll = () => {
    setTextInput("")
    setAudioFile(null)
    setImageFile(null)
    setResults(null)
  }

  const getEmotionIcon = (emotion) => {
    const icons = {
      joy: "bi-emoji-smile",
      happiness: "bi-emoji-smile",
      happy: "bi-emoji-smile",
      neutral: "bi-emoji-neutral",
      fear: "bi-emoji-frown",
      anxiety: "bi-emoji-frown",
      sadness: "bi-emoji-frown",
      sad: "bi-emoji-frown",
      anger: "bi-emoji-angry",
      angry: "bi-emoji-angry",
      surprise: "bi-emoji-surprise",
      disgust: "bi-emoji-dizzy",
    }
    return icons[emotion] || "bi-emoji-neutral"
  }

  const renderEmotionChart = (emotions, title, icon) => {
    return (
      <Card className="results-card">
        <Card.Header className="bg-light">
          <h5 className="mb-0">
            <i className={`bi ${icon} me-2`}></i>
            {title}
          </h5>
        </Card.Header>
        <Card.Body>
          {emotions.slice(0, 5).map((emotion, index) => (
            <div key={index} className="mb-3">
              <div className="d-flex justify-content-between align-items-center mb-1">
                <span className="fw-medium text-capitalize">
                  <i className={`bi ${getEmotionIcon(emotion.emotion)} me-2`}></i>
                  {emotion.emotion}
                </span>
                <Badge bg="secondary">{emotion.confidence.toFixed(1)}%</Badge>
              </div>
              <div className="position-relative">
                <div className="bg-light rounded" style={{ height: "8px" }}>
                  <div
                    className={`emotion-bar emotion-${emotion.emotion}`}
                    style={{ width: `${Math.min(emotion.confidence, 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </Card.Body>
      </Card>
    )
  }

  return (
    <div style={{ minHeight: "100vh", padding: "20px 0" }}>
      <Container>
        <div className="main-container">
          {/* <div className="version-badge">v9.0</div> */}

          {/* Header */}
          <div className="header-section position-relative">
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <h1 className="display-4 fw-bold mb-2">
                  {/* <i className="bi bi-robot me-3"></i> */}
                  AI Emotion Detection System
                </h1>
                <p className="lead mb-0">Advanced emotion analysis for remote job interviews</p>
              </div>
              <Button variant="outline-light" onClick={() => setShowSettings(!showSettings)} className="rounded-pill">
                <i className="bi bi-gear"></i>
              </Button>
            </div>

            {showSettings && (
              <Card className="settings-panel mt-4">
                <Card.Body>
                  <div className="d-flex justify-content-between align-items-center mb-3">
                    <div>
                      <Form.Check
                        type="switch"
                        id="mockAPI"
                        label="Use Mock API (for demo without backend)"
                        checked={useMockAPI}
                        onChange={(e) => setUseMockAPI(e.target.checked)}
                      />
                      <small className="text-muted">
                        {useMockAPI
                          ? "Using simulated AI models for demonstration"
                          : "Connecting to Python backend with real AI models"}
                      </small>
                    </div>
                    <div className="text-end">
                      <div className="d-flex align-items-center">
                        <span
                          className={`status-indicator ${backendStatus === "online" ? "status-online" : "status-offline"}`}
                        ></span>
                        <small className="text-muted">
                          Backend: {backendStatus === "checking" ? "Checking..." : backendStatus}
                        </small>
                      </div>
                      <Button variant="link" size="sm" onClick={checkBackendStatus}>
                        <i className="bi bi-arrow-clockwise"></i> Refresh
                      </Button>
                    </div>
                  </div>
                </Card.Body>
              </Card>
            )}
          </div>

          {/* Main Content */}
          <div className="p-4">
            <Row>
              {/* Input Section */}
              <Col lg={6}>
                <div className="mb-4">
                  <Card>
                    <Card.Header>
                      <h5 className="mb-0">
                        <i className="bi bi-chat-text me-2"></i>
                        Text Input
                      </h5>
                    </Card.Header>
                    <Card.Body>
                      <Form.Control
                        as="textarea"
                        rows={4}
                        value={textInput}
                        onChange={(e) => setTextInput(e.target.value)}
                        placeholder="Enter your interview response or thoughts here... (e.g., 'I'm excited about this opportunity but feeling a bit nervous about the technical questions')"
                        maxLength={500}
                      />
                      <div className="d-flex justify-content-between mt-2">
                        <small className="text-muted">{textInput.length}/500 characters</small>
                        {textInput && (
                          <Button variant="link" size="sm" onClick={() => setTextInput("")}>
                            <i className="bi bi-x-circle"></i> Clear
                          </Button>
                        )}
                      </div>
                    </Card.Body>
                  </Card>
                </div>

                <div className="mb-4">
                  <Card>
                    <Card.Header>
                      <h5 className="mb-0">
                        <i className="bi bi-mic me-2"></i>
                        Audio Input
                      </h5>
                    </Card.Header>
                    <Card.Body>
                      <div className="upload-area">
                        <Form.Control
                          type="file"
                          accept="audio/*"
                          onChange={(e) => setAudioFile(e.target.files?.[0] || null)}
                          className="d-none"
                          id="audio-upload"
                        />
                        <label htmlFor="audio-upload" className="w-100 cursor-pointer">
                          <i className="bi bi-cloud-upload display-4 text-muted"></i>
                          <p className="mt-2 mb-1">
                            {audioFile ? (
                              <>
                                <i className="bi bi-file-earmark-music me-2"></i>
                                {audioFile.name}
                              </>
                            ) : (
                              "Click to upload audio file (WAV, MP3, etc.)"
                            )}
                          </p>
                          <small className="text-muted">Supported formats: WAV, MP3, FLAC, M4A</small>
                        </label>
                      </div>
                      {audioFile && (
                        <div className="mt-2 text-center">
                          <Button variant="outline-danger" size="sm" onClick={() => setAudioFile(null)}>
                            <i className="bi bi-trash"></i> Remove
                          </Button>
                        </div>
                      )}
                    </Card.Body>
                  </Card>
                </div>

                <div className="mb-4">
                  <Card>
                    <Card.Header>
                      <h5 className="mb-0">
                        <i className="bi bi-camera me-2"></i>
                        Visual Input
                      </h5>
                    </Card.Header>
                    <Card.Body>
                      <div className="upload-area">
                        <Form.Control
                          type="file"
                          accept="image/*"
                          onChange={(e) => setImageFile(e.target.files?.[0] || null)}
                          className="d-none"
                          id="image-upload"
                        />
                        <label htmlFor="image-upload" className="w-100 cursor-pointer">
                          <i className="bi bi-image display-4 text-muted"></i>
                          <p className="mt-2 mb-1">
                            {imageFile ? (
                              <>
                                <i className="bi bi-file-earmark-image me-2"></i>
                                {imageFile.name}
                              </>
                            ) : (
                              "Click to upload image file (JPG, PNG, etc.)"
                            )}
                          </p>
                          <small className="text-muted">Supported formats: JPG, PNG, BMP, GIF</small>
                        </label>
                      </div>
                      {imageFile && (
                        <div className="mt-2 text-center">
                          <Button variant="outline-danger" size="sm" onClick={() => setImageFile(null)}>
                            <i className="bi bi-trash"></i> Remove
                          </Button>
                        </div>
                      )}
                    </Card.Body>
                  </Card>
                </div>

                <div className="d-grid gap-2 mb-4">
                  <div className="d-flex gap-2">
                    <Button variant="outline-secondary" onClick={loadSampleData} className="flex-fill">
                      <i className="bi bi-file-earmark-text me-2"></i>
                      Load Sample Data
                    </Button>
                    <Button variant="outline-danger" onClick={clearAll} className="flex-fill">
                      <i className="bi bi-trash me-2"></i>
                      Clear All
                    </Button>
                  </div>
                  <Button className="btn-analyze text-white" onClick={handleAnalyze} disabled={loading} size="lg">
                    {loading ? (
                      <>
                        <Spinner animation="border" size="sm" className="me-2" />
                        Analyzing Emotions...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-search me-2"></i>
                        Analyze Emotions
                      </>
                    )}
                  </Button>
                </div>

                {backendStatus === "offline" && !useMockAPI && (
                  <Alert variant="warning" className="text-center">
                    <i className="bi bi-exclamation-triangle me-2"></i>
                    Backend server is offline. Using Mock API mode.
                    <br />
                    <small>
                      Start the backend server: <code>cd backend && python app.py</code>
                    </small>
                  </Alert>
                )}
              </Col>

              {/* Results Section */}
              <Col lg={6}>
                {results ? (
                  <>
                    <div className="d-flex justify-content-between align-items-center mb-4">
                      <h2 className="fw-bold">Emotion Analysis Results</h2>
                      {/* <Badge bg={useMockAPI ? "warning" : "success"}>
                        {useMockAPI ? "🤖 Mock Analysis" : "🧠 AI Analysis"}
                      </Badge> */}
                    </div>

                    {results.combined_emotions &&
                      renderEmotionChart(results.combined_emotions, "Combined Analysis", "bi-bullseye")}

                    {results.text_emotions &&
                      renderEmotionChart(results.text_emotions, "Text Emotions", "bi-chat-text")}

                    {results.audio_emotions &&
                      renderEmotionChart(results.audio_emotions, "Audio Emotions", "bi-soundwave")}

                    {results.visual_emotions &&
                      renderEmotionChart(results.visual_emotions, "Visual Emotions", "bi-eye")}

                    {results.combined_emotions && (
                      <Card className="insight-card">
                        <Card.Body>
                          {/* <h5 className="fw-bold text-primary">
                            <i className="bi bi-lightbulb me-2"></i>
                            AI Insights for Interview Performance
                          </h5>
                          <p className="mb-2">{generateInsights(results.combined_emotions)}</p>
                          <small className="text-muted">
                            Remember: Multiple emotions are normal in interviews. The key is managing them effectively.
                          </small> */}
                        </Card.Body>
                      </Card>
                    )}

                    {/* <Card className="feature-card mt-3">
                      <Card.Body>
                        <h5 className="fw-bold text-success">
                          <i className="bi bi-check-circle me-2"></i>
                          Key Features Demonstrated
                        </h5>
                        <ul className="list-unstyled mb-0">
                          <li>
                            <i className="bi bi-check text-success me-2"></i>
                            Multi-modal emotion detection (text + audio + visual)
                          </li>
                          <li>
                            <i className="bi bi-check text-success me-2"></i>
                            Ambiguous emotion handling with confidence scores
                          </li>
                          <li>
                            <i className="bi bi-check text-success me-2"></i>
                            Interview-specific insights and recommendations
                          </li>
                          <li>
                            <i className="bi bi-check text-success me-2"></i>
                            Real-time processing with pretrained AI models
                          </li>
                        </ul>
                      </Card.Body>
                    </Card> */}
                  </>
                ) : (
                  <Card className="text-center" style={{ height: "400px" }}>
                    <Card.Body className="d-flex flex-column justify-content-center">
                      <i className="bi bi-camera display-1 text-muted mb-4"></i>
                      <h3 className="fw-bold text-muted mb-2">Ready for Analysis</h3>
                      <p className="text-muted mb-4">Upload your inputs and click "Analyze Emotions" to see results</p>
                      <small className="text-muted">
                        <i className="bi bi-lightbulb me-1"></i>
                        Try the "Load Sample Data" button for a quick demo
                      </small>
                    </Card.Body>
                  </Card>
                )}
              </Col>
            </Row>
          </div>

          {/* Footer */}
          {/* <div className="footer-section">
            <small className="text-muted">
              AI Emotion Detection System v9.0 | Developed by Keerthi N (1RF23MC039) | Project Phase-2: Emotion
              Detection for Remote Job Interviews
            </small>
          </div> */}
        </div>
      </Container>
    </div>
  )
}
