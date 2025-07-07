import { useState } from "react";

const Transcripts = ({ loggedIn, transcripts }) => {
    const [hidden, setHidden] = useState(true);

    return (
        <>
            {/* Button fixed to bottom */}
            <div className="fixed left-0 bottom-0 w-full z-50">
                <button
                    onClick={() => {
                        if (loggedIn) setHidden(!hidden);
                        else alert("Please log in to view transcripts.");
                    }}
                    className="w-full bg-red-600 text-white py-2 text-base font-semibold rounded-t-lg shadow transition-colors duration-150 hover:bg-red-700"
                >
                    {hidden ? "View Transcripts" : "Hide Transcripts"}
                </button>
            </div>
            {/* Cards in normal flow, shown only when not hidden */}
            {!hidden && loggedIn && (
                <div className="w-full max-h-40 overflow-y-auto bg-white shadow rounded-b-lg flex flex-col items-center mb-12">
                    {transcripts.length === 0 && (
                        <div className="p-4 text-gray-500">No transcripts found.</div>
                    )}
                    {transcripts.map((transcript, index) => (
                        <div
                            key={index}
                            className="w-[95%] bg-gray-100 rounded-lg p-3 my-2 shadow flex flex-col"
                            style={{ minHeight: "60px" }}
                        >
                            <div className="font-bold text-sm text-gray-800">{transcript.video_title}</div>
                            <div className="text-xs text-gray-600">{transcript.channel_name}</div>
                        </div>
                    ))}
                </div>
            )}
        </>
    );
};

export default Transcripts;