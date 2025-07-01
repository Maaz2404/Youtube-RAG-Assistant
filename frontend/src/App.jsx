import { useState,useEffect } from "react";
import axios from "axios";


const App = () => {
  const [videoId, setVideoId] = useState("");
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");

  useEffect(() => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const tabId = tabs[0]?.id;
    if (!tabId) return;

    chrome.tabs.sendMessage(tabId, { type: "GET_VIDEO_ID" }, (response) => {
      if (chrome.runtime.lastError) {
        console.error("Msg error:", chrome.runtime.lastError.message);
      } else {
        console.log("Popup received videoId:", response.videoId);
        setVideoId(response.videoId);
      }
    });
  });
}, []);




  const handleSearch = async () => {
    try{
      console.log("Sending query to llm")
      console.log("Sending video_id:", videoId);
      console.log("Sending query:", query);
      const response = await axios.post("http://127.0.0.1:8000/ask", {
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
            className="flex-1 py-2 text-white bg-red-600 rounded-l transition-colors duration-150 hover:bg-red-700 active:bg-red-800 cursor-pointer"
            onClick={handleSearch}
          >
            Ask
          </button>
          <button
            className="flex-1 py-2 text-white bg-gray-500 rounded-r transition-colors duration-150 hover:bg-gray-600 active:bg-gray-700 cursor-pointer"
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