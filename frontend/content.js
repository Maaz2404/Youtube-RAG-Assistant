(function () {
  // Function to get video data with multiple selector fallbacks
  function getVideoData() {
    const urlParams = new URLSearchParams(window.location.search);
    const videoId = urlParams.get("v");
    
    // Multiple selectors for video title (YouTube changes these frequently)
    const titleSelectors = [
      'h1.ytd-video-primary-info-renderer',
      'h1.title',
      'h1[class*="title"]',
      '.ytd-video-primary-info-renderer h1',
      '#container h1'
    ];
    
    // Multiple selectors for channel name
    const channelSelectors = [
      '#text a.ytd-channel-name',
      '.ytd-channel-name #text',
      '#owner-name a',
      '#channel-name a',
      'a.ytd-channel-name',
      '[class*="channel-name"] a'
    ];
    
    let videoTitle = "";
    let channelName = "";
    
    // Try different selectors for video title
    for (const selector of titleSelectors) {
      const element = document.querySelector(selector);
      if (element && element.innerText.trim()) {
        videoTitle = element.innerText.trim();
        break;
      }
    }
    
    // Try different selectors for channel name
    for (const selector of channelSelectors) {
      const element = document.querySelector(selector);
      if (element && element.innerText.trim()) {
        channelName = element.innerText.trim();
        break;
      }
    }
    
    // Fallback: try to get from meta tags
    if (!videoTitle) {
      const metaTitle = document.querySelector('meta[property="og:title"]')?.content;
      if (metaTitle) videoTitle = metaTitle;
    }
    
    return { videoId, videoTitle, channelName };
  }
  
  // Initial load
  const initialData = getVideoData();
  console.log("Content script loaded, videoId:", initialData.videoId);
  console.log("Video title:", initialData.videoTitle);
  console.log("Channel name:", initialData.channelName);
  
  // Listen for messages from popup
  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === "GET_VIDEO_ID") {
      // Get fresh data when requested (in case page changed)
      const currentData = getVideoData();
      console.log("Sending data to popup:", currentData);
      sendResponse(currentData);
    }
  });
  

})();