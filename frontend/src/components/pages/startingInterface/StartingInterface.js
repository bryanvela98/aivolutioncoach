import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const StartingInterface = () => {
  const [status, setStatus] = useState('Listening for "Start"...');
  const [recognizedText, setRecognizedText] = useState("");
  const [error, setError] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const navigate = useNavigate();

  const phraseToSpeak =
    "Are you ready? Please say START or click to begin the session.";

  // Function to handle TTS
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

      // Simulate TTS playback duration
      setTimeout(() => {
        setIsSpeaking(false);
      }, 4000);
    } catch (err) {
      console.error("Error in speakPhrase:", err);
      setError("Failed to generate speech output.");
      setIsSpeaking(false);
    }
  };

  // Function to handle STT
  const listenForStart = async () => {
    if (isSpeaking) return; // Skip STT if TTS is active

    try {
      const response = await fetch("/api/speech-to-text", {
        method: "POST",
      });
      const data = await response.json();

      if (data.success) {
        const command = data.command.toLowerCase();
        setRecognizedText(command);

        if (command === "start.") {
          setStatus("Start command recognized! Proceeding...");
          setError("");

          // Navigate to the next page
          navigate("/start");
        } else {
          setStatus('Listening for "Start"...');
        }
      } else {
        setError(data.error || "Speech recognition failed.");
      }
    } catch (err) {
      console.error("Error in listenForStart:", err);
      setError("Failed to connect to the server.");
    }
  };

  useEffect(() => {
    // Start speaking the phrase every 12 seconds
    const speakInterval = setInterval(() => {
      speakPhrase();
    }, 10000);

    // Continuously listen for the "Start" command
    const listenInterval = setInterval(() => {
      if (!isSpeaking) {
        listenForStart();
      }
    }, 500);

    // Attach a global click listener to the window
    const handleClick = (event) => {
      if (event.button === 0) {
        // Check if it's a left-click
        navigate("/start");
      }
    };
    window.addEventListener("click", handleClick);

    // Cleanup intervals and event listener on component unmount
    return () => {
      clearInterval(speakInterval);
      clearInterval(listenInterval);
      window.removeEventListener("click", handleClick);
    };
  }, [isSpeaking]);

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
