import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const StartingInterface = () => {
  const [status, setStatus] = useState('Listening for "Start"...');
  const [recognizedText, setRecognizedText] = useState("");
  const [error, setError] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [intervalId, setIntervalId] = useState(null);

  const navigate = useNavigate(); // React Router hook for navigation

  const phraseToSpeak =
    "Are you ready? Please say START or Click to begin the session.";

  const speakPhrase = async () => {
    try {
      setIsSpeaking(true); // Mark TTS as active
      const response = await fetch("/api/text-to-speech", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: phraseToSpeak }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch TTS from the backend.");
      }

      // Simulate TTS playback duration (e.g., 5 seconds)
      setTimeout(() => {
        setIsSpeaking(false); // Mark TTS as inactive after playback
      }, 4000);
    } catch (err) {
      console.error("Error in speakPhrase:", err);
      setError("Failed to generate speech output.");
      setIsSpeaking(false);
    }
  };

  const listenForStart = async () => {
    if (isSpeaking) return; // Skip STT if TTS is active

    try {
      const response = await fetch("/api/speech-to-text", { method: "POST" });
      const data = await response.json();
      if (data.success && data.message === "Start command recognized") {
        setStatus("Start command recognized! Processing input...");
        setRecognizedText(data.command);
        setError("");
        // Stop speaking and clear the interval when the command is recognized
        clearInterval(intervalId);

        // Navigate to the next page
        navigate("/next");
      } else {
        setStatus(data.message || 'Listening for "Start"...');
        setRecognizedText(data.command || "");
      }
    } catch (err) {
      setError("Failed to connect to the server.");
    }
  };

  useEffect(() => {
    // Start speaking the phrase every 12 seconds
    const id = setInterval(() => {
      speakPhrase();
    }, 12000);
    setIntervalId(id);

    // Continuously listen for the "Start" command
    const listenInterval = setInterval(() => {
      if (!isSpeaking) {
        listenForStart();
      }
    }, 2000);

    // Attach a global click listener to the window
    const handleClick = (event) => {
      if (event.button === 0) {
        // Check if it's a left-click
        navigate("/next");
      }
    };
    window.addEventListener("click", handleClick);

    // Cleanup intervals and event listener on component unmount
    return () => {
      clearInterval(id);
      clearInterval(listenInterval);
      window.removeEventListener("click", handleClick);
    };
  }, [isSpeaking]); // Add isSpeaking as a dependency

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>AI Support Coach</h1>
      <p>Status: {status}</p>
      {recognizedText && <p>Recognized Text: {recognizedText}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
};

export default StartingInterface;
