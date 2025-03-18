import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../../layout/Navbar/Navbar";

const GetDisabilityInterface = () => {
  const navigate = useNavigate();
  const [timeoutId, setTimeoutId] = useState(null);
  const [step, setStep] = useState(0);

  // Function to handle TTS
  const speakPhrase = async (text) => {
    try {
      const response = await fetch("/api/text-to-speech", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: text }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch TTS from the backend.");
      }
    } catch (err) {
      console.error("Error in speakPhrase:", err);
    }
  };

  // Function to handle STT
  const listenForStart = async () => {
    let retryCount = 0;
    const maxRetries = 2; // Number of times to retry listening

    while (retryCount < maxRetries) {
      try {
        const response = await fetch("/api/speech-to-text", {
          method: "POST",
        });
        const data = await response.json();

        if (data.success) {
          const command = data.command.toLowerCase();
          if (command === "hello.") {
            navigate("/userinterface2"); // Navigate if the command is correct
            return true;
          }
        }
        retryCount++; // Increment retry count if the command is not correct
      } catch (err) {
        console.error("Error in listenForStart:", err);
        retryCount++; // Increment retry count if there's an error
      }
    }

    return false; // Return false if no correct command is received after retries
  };
  // Function to execute multiple phrases sequentially (Step 0)
  const executePhrases = async () => {
    await speakPhrase("Welcome to your AI Coach Assistant");
    await speakPhrase("Let me know a little more about you");
    await speakPhrase(
      "Tell us about your disability so we can customize your coaching experience"
    );
    setStep(1); // Move to Step 1 after all phrases are spoken
  };

  // Handle step transitions
  useEffect(() => {
    if (step === 0) {
      // Step 0: Execute multiple phrases
      executePhrases();
    } else if (step === 1) {
      // Step 1: Speak a phrase and wait for button click or 20 seconds
      speakPhrase(
        "If you're able to see, please click the buttom. Otherwise, wait until the next step."
      ).then(() => {
        const id = setTimeout(() => {
          setStep(2); // Move to Step 2 after 20 seconds
        }, 20000); // 20 seconds
        setTimeoutId(id);
      });
    } else if (step === 2) {
      // Step 2: Speak a phrase, activate STT, and wait for input
      speakPhrase(
        "If you're able to speak, please say Hello. Otherwise, wait until the next step."
      ).then(() => {
        listenForStart().then((success) => {
          const id = setTimeout(() => {
            if (!success) {
              // If no input is received, go back to Step 0
              setStep(0);
            } else {
              // If input is received, handle it (e.g., navigate)
              console.log("STT input received and processed.");
              // Reset for the next cycle
              setStep(0);
            }
          }, 20000); // 20 seconds
          setTimeoutId(id);
        });
      });
    }
  }, [step]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [timeoutId]);

  // Handle button click (for Step 1)
  const handleButtonClick = () => {
    if (step === 1) {
      navigate("/userinterface1"); // Navigate to UserInterface1
      clearTimeout(timeoutId); // Clear the 20-second timeout    }
    }
  };
  return (
    <div>
      <Navbar />
      <h1>Welcome to your AI Coach Assistant</h1>
      <p>Let me know a little more about you :)</p>
      <p>
        Tell us about your disability so we can customize your coaching
        experience
      </p>

      {step === 1 && (
        <div>
          <p>
            1. If you're able to see, please pick one value that associates to
            your disability. Otherwise, wait until the next step.
          </p>
          <button onClick={handleButtonClick}>Click here</button>
        </div>
      )}

      {step === 2 && (
        <div>
          <p>
            2. If you're able to see, please click the buttom. Otherwise, wait
            until the next step.
          </p>
        </div>
      )}

      {step === 3 && (
        <div>
          <p>
            3. If you're not able to do any of above, just move your head down.
          </p>
        </div>
      )}
    </div>
  );
};

export default GetDisabilityInterface;
