import { useState, useEffect } from "react";
import axios from "axios";
import Transcripts from "./components/Transcripts";
import SaveButton from "./components/SaveButton";
import TranscribeButton from "./components/TranscribeButton";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
const BASE_URL = import.meta.env.VITE_BASE_URL || "http://127.0.0.1:8000/";

const App = () => {
  const [videoId, setVideoId] = useState("");
  const [query, setQuery] = useState("");
  const [videoTitle, setVideoTitle] = useState("");
  const [channelName, setChannelName] = useState("");
  const [answer, setAnswer] = useState("");
  const [loggedIn, setLoggedIn] = useState(false);
  const [showSignup, setShowSignup] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [loginForm, setLoginForm] = useState({ email: "", password: "" });
  const [signupForm, setSignupForm] = useState({ email: "", password: "" });
  const [authError, setAuthError] = useState("");
  const [transcripts, setTranscripts] = useState([]);
  const [loading, setLoading] = useState(false);
  

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
          setVideoTitle(response.videoTitle);
          setChannelName(response.channelName);
        }
      });
    });
  }, []);

  useEffect(() => {
    if (loggedIn) {
      const token = localStorage.getItem("token");
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      axios.get('http://127.0.0.1:8000/transcripts', { headers })
        .then((response) => {
          setTranscripts(response.data);
        })
        .catch((error) => {
          console.error("Error fetching transcripts:", error);
        });
    } else {
      setTranscripts([]);
    }
  }, [loggedIn]);

  const OnSuccess = () => {
    toast.success("Transcript saved & ready to chat!", {
    position: "bottom-right",
    autoClose: 2000,
    hideProgressBar: true,
    closeOnClick: true,
    pauseOnHover: false,
    draggable: false,
    theme: "dark"
  });
  }

  const handleSearch = async () => {
    try {
      setLoading(true);
      setAnswer("");
      console.log("Sending query to llm");
      console.log("Sending video_id:", videoId);
      console.log("Sending query:", query);
      const token = localStorage.getItem("token");
      const headers = { Authorization: `Bearer ${token || ""}` };
      
      const response = await axios.post(
      `${BASE_URL}ask`,
      {
        video_id: videoId,
        query: query,
        
      },
      { headers }
      );
      setAnswer(response.data.answer);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
    finally{
      setLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthError("");
    try {
      const params = new URLSearchParams();
      params.append("username", loginForm.email);
      params.append("password", loginForm.password);
      const res = await axios.post("http://127.0.0.1:8000/login", params, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });
      localStorage.setItem("token", res.data.access_token);
      setLoggedIn(true);
      setShowLogin(false);
      setLoginForm({ email: "", password: "" });
    } catch (err) {
      setAuthError("Login failed. Please check your credentials.");
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setAuthError("");
    try {
      await axios.post("http://127.0.0.1:8000/signup", {
        email: signupForm.email,
        password: signupForm.password,
      });
      setShowSignup(false);
      setSignupForm({ email: "", password: "" });
      setAuthError("Signup successful! Please log in.");
    } catch (err) {
      setAuthError("Signup failed. Email may already be registered.");
    }
  };

  const handleLogout = () => {
    setLoggedIn(false);
    localStorage.removeItem("token");
  };

  const handleTranscriptSave = () => {
    setTranscripts((prev) => [
      ...prev,
      {
        video_title: videoTitle,
        channel_name: channelName,
      },
    ]);
  };
  const loadTranscript = async (vid) => {
  const token = localStorage.getItem("token");
  try {
    const res = await axios.get(`${BASE_URL}transcripts/${vid}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    setVideoId(res.data.video_id);
    setVideoTitle(res.data.video_title);
    setChannelName(res.data.channel_name);
    toast.success(`Loaded: ${res.data.video_title}`, {
      position: "top-center",
      autoClose: 1500,
      theme: "dark",
    });
  } catch (err) {
    toast.error("Failed to load transcript", {
      position: "top-center",
      autoClose: 2000,
      theme: "dark",
    });
    console.error(err);
  }
};


  return (
    <>
    <div className="w-[350px] min-h-[500px] max-h-[600px] p-3 bg-white overflow-y-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-lg font-bold">🎥 YouTube RAG Assistant</h1>
        <div className="flex gap-2">
          <button
            className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
            onClick={() => {
              if (loggedIn) handleLogout();
              else {
                setShowLogin((v) => !v);
                setShowSignup(false);
                setAuthError("");
              }
            }}
          >
            {loggedIn ? "Log Out" : "Log In"}
          </button>
          <button
            className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
            onClick={() => {
              setShowSignup((v) => !v);
              setShowLogin(false);
              setAuthError("");
            }}
          >
            {showSignup ? "Cancel" : "Sign Up"}
          </button>
        </div>
      </div>

      {showLogin && (
        <form className="mb-4 flex flex-col gap-2" onSubmit={handleLogin}>
          <input
            type="email"
            placeholder="Email"
            value={loginForm.email}
            onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
            className="p-2 border rounded"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={loginForm.password}
            onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
            className="p-2 border rounded"
            required
          />
          <button
            type="submit"
            className="py-2 text-white text-sm bg-red-600 rounded transition-colors duration-150 hover:bg-red-700"
          >
            Log In
          </button>
        </form>
      )}

      {showSignup && (
        <form className="mb-4 flex flex-col gap-2" onSubmit={handleSignup}>
          <input
            type="email"
            placeholder="Email"
            value={signupForm.email}
            onChange={(e) => setSignupForm({ ...signupForm, email: e.target.value })}
            className="p-2 border rounded"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={signupForm.password}
            onChange={(e) => setSignupForm({ ...signupForm, password: e.target.value })}
            className="p-2 border rounded"
            required
          />
          <button
            type="submit"
            className="py-2 text-white text-sm bg-red-600 rounded transition-colors duration-150 hover:bg-red-700"
          >
            Sign Up
          </button>
        </form>
      )}

      {authError && (
        <div className="mb-2 text-red-600 text-sm">{authError}</div>
      )}
      {!videoId ? (
      <div className="text-sm text-red-600 font-medium mb-2">
        ⚠️ Could not detect video ID. Try refreshing the YouTube page and reopening the extension.
      </div>
    ) : (
      <div className="text-sm text-green-600 font-medium mb-2">
        ✅ Video ID loaded
      </div>
    )}

      <div>
        <TranscribeButton video_id={videoId} channel_name={channelName} video_title={videoTitle} onSuccess={OnSuccess} disabled={!videoId} />
      </div>

      <div className="flex flex-col mb-2">
        <textarea
          placeholder="Ask something.."
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
          }}
          className="w-full min-h-[80px] p-2 mb-0 border rounded resize-none overflow-y-auto"
        />
        <div className="flex w-full gap-2 mt-2">
          <button
            className="flex-1 py-2 text-white bg-red-600 rounded-l transition-colors duration-150 hover:bg-red-700 active:bg-red-800 cursor-pointer"
            onClick={handleSearch}
            disabled={!query || !videoId || loading}
          >
            Ask
          </button>
          <button
            className="flex-1 py-2 text-white bg-gray-500 rounded-r transition-colors duration-150 hover:bg-gray-600 active:bg-gray-700 cursor-pointer"
            onClick={() => setQuery("")}
            disabled={!query || loading || !videoId}
          >
            Clear
          </button>
        </div>
      </div>
      
      <SaveButton video_id={videoId} onSaved={handleTranscriptSave} disabled={!videoId} />
      
      {loading ? (
        <div className="mt-4 text-sm text-gray-600">Loading...</div>
      ) : (
        answer && (
          <div className="mt-4 bg-gray-100 p-2 rounded disabled:bg-gray-100 disabled:cursor-not-allowed">
            <p className="text-gray-700 whitespace-pre-wrap">{answer}</p>
          </div>
        )
      )}
      

      <Transcripts loggedIn={loggedIn} transcripts={transcripts} onLoad={loadTranscript} />
    </div>
    
      <ToastContainer/>
    </>
    
  );
};

export default App;
