# vision-api-video
A containerized python app that:

  1. reads in a video file and Google API Key from the command line
  2. samples still frames from the video (default 1 frame per 5 seconds)
  3. passes each image still to the Google Vision API and prints the response 
