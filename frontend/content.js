(function () {
  const urlParams = new URLSearchParams(window.location.search);
  const videoId = urlParams.get("v");
  console.log("Content script loaded, videoId:", videoId);

  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === "GET_VIDEO_ID") {
      sendResponse({ videoId });
    }
  });
})();
