import { useState } from "react";
import axios from "axios";

const BASE_URL = import.meta.env.VITE_BASE_URL || "http://127.0.0.1:8000/";

const TranscribeButton = ({ video_id, video_title, channel_name, onSuccess, disabled }) => {
  const [loading, setLoading] = useState(false);

  const handleTranscribe = async () => {
    const sessionId = crypto.randomUUID();
    setLoading(true);
    try {
      const response = await axios.post(
        `${BASE_URL}transcribe?session_id=${sessionId}`,
        {
          video_id,
          video_title,
          channel_name,
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      console.log("Transcription success:", response.data);
      if (onSuccess) onSuccess();
    } catch (error) {
      console.error("Error during transcription:", error);
      alert("An error occurred while transcribing the video. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleTranscribe}
      disabled={loading || disabled}
      className={`w-full py-2 px-4 rounded text-white text-sm font-semibold transition duration-150 ${
        loading || disabled
          ? "bg-gray-400 cursor-not-allowed"
          : "bg-red-600 hover:bg-red-700 active:bg-red-800"
      }`}
    >
      {loading
        ? "Transcribing... (this may take a while)"
        : "Transcribe"}
    </button>
  );
};

export default TranscribeButton;
