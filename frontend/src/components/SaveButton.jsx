import axios from "axios";

const SaveButton = ({ video_id, onSaved }) => {
  return (
    <button
      className="w-full bg-red-600 hover:bg-red-700 text-white py-2 mt-1 rounded"
      onClick={async () => {
        if (!video_id) {
          alert("No video loaded. Please load a video first.");
          return;
        }
        try {
          await axios.patch(
            `http://127.0.0.1:8000/save/${video_id}`,
            { video_id },
            {
              headers: {
                Authorization: `Bearer ${localStorage.getItem("token")}`,
              },
            }
          );
          console.log("Transcript saved successfully");
          onSaved();
        } catch (error) {
          console.error(error);
        }
      }}
    >
      Save Transcript
    </button>
  );
};

export default SaveButton;