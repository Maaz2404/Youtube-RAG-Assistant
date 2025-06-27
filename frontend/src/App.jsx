import { useState,useEffect } from "react";
import axios from "axios";


const App = () => {
  const [videoId, setVideoId] = useState("");
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");

  useEffect(() => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0]?.id) {
      chrome.tabs.sendMessage(
        tabs[0].id,
        { type: "GET_VIDEO_ID" },
        (response) => {
          if (chrome.runtime.lastError) {
            console.error("❌ Error:", chrome.runtime.lastError.message);
            return;
          }
          if (response?.videoId) {
            console.log("✅ Got video ID from content script:", response.videoId);
            setVideoId(response.videoId);
          } else {
            console.warn("⚠️ No video ID returned.");
          }
        }
      );
    }
  });
}, []);


  const handleSearch = async () => {
    try{
      console.log("Sending query to llm")
      console.log("Sending video_id:", videoId);
      console.log("Sending query:", query);
      const response = await axios.post("https://localhost:8000/ask", {
        video_id : videoId,
        query : query
      });
      setAnswer(response.data.answer)
    }
    catch (error) {
      console.error("Error fetching data:", error);
    }
  }


  return(
    <div className="flex-col mt-4 w-[300px] p-4">
      <h1 className="text-lg font-bold mb-2">🎥 YouTube RAG Assistant</h1>
      <div className="flex flex-col mb-4">
        <textarea
          placeholder="Ask something.."
          value={query}
          onChange={(e)=> {setQuery(e.target.value)}}
          className="w-full min-h-[80px] p-2 border rounded resize-none overflow-y-auto"
        />
        <div className="flex w-full gap-2 mt-2">
          <button
            className="w-1/2 h-4 text-white bg-red-600 rounded-l py-2"
            onClick={handleSearch}
          >
            Ask
          </button>
          <button
            className="w-1/2 h-4 text-white bg-red-600 rounded-l py-2"
            onClick={() => setQuery("")}
          >
            Clear
          </button>
        </div>
      </div>
      
    {answer && (
    <div className="mt-4 bg-gray-100 p-2 rounded">
      <p className="text-gray-700">{answer}</p>
    </div>
   )}
    </div>  
  )


}



export default App;