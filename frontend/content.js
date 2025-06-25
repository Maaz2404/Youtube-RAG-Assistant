// content.js
(function () {
  const urlParams = new URLSearchParams(window.location.search);
  const videoId = urlParams.get("v");

  if (videoId) {
    chrome.runtime.sendMessage({ videoId });
    console.log("Sent video ID from content.js:", videoId);
  }
})();
