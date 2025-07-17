import { useState } from "react";

const Transcripts = ({ loggedIn, transcripts, onLoad }) => {
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

            {/* Transcript list */}
            {!hidden && loggedIn && (
                <div className="w-full max-h-52 overflow-y-auto bg-white shadow rounded-b-lg px-3 py-2 mb-12">
                    {transcripts.length === 0 ? (
                        <div className="p-4 text-gray-500 text-sm text-center">No transcripts found.</div>
                    ) : (
                        transcripts.map((transcript, index) => (
                            <div
                                key={index}
                                className="bg-gray-100 rounded-md p-3 mb-3 w-full shadow-sm"
                            >
                                <div className="text-sm font-semibold text-gray-800 truncate">
                                    {transcript.video_title}
                                </div>
                                <div className="text-xs text-gray-600 truncate">{transcript.channel_name}</div>

                                <div className="mt-2 flex justify-end">
                                    <button
                                        onClick={() => onLoad(transcript.video_id)}
                                        className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors duration-150"
                                    >
                                        Load
                                    </button>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}
        </>
    );
};

export default Transcripts;
