import argparse
import base64
import cv2
import os

from apiclient.discovery import build

# Author: reddyv@
# Date: 03-04-2016
# Description:
#   1) reads in a video from the command line
#   2) extracts one still frame per second from it
#   3) passes each image still to the vision API and prints the response 
# Usage:
#   from the command line pass positional arguments:
#      video_file  file path of the video you'd like to process.
#      APIKey      The API Key that identifies your Google Cloud Console Project
# Todo:
#   1) See if you convert the cv2 image format to base64 directly in memory 
#   without having to write to disk first
#   2) Can you batch multiple images into a single API request to reduce latency?

def main(video_file, sample_rate, APIKey):
  #obtain service handle for vision API using API Key
  service = build('vision', 'v1', 
  discoveryServiceUrl='https://vision.googleapis.com/$discovery/rest?version=v1',
  developerKey=APIKey)
  
  vidcap = cv2.VideoCapture(video_file)
  position = 0
  frame = 0
  success,image = vidcap.read()

  while success:
    #do stuff with image
    cv2.imwrite("temp.jpg", image)     # save frame as JPEG file
    with open("temp.jpg", 'rb') as image:
      image = base64.b64encode(image.read())  
      service_request = service.images().annotate(
        body={
          'requests': [{
            'image': {
              'content': image
             },
            'features': [{
              'type': 'LABEL_DETECTION',
              'maxResults': 1,
             }]
           }]
        })
      response = service_request.execute()
      print(response)
  
    #advance to next image
    frame = frame + 1
    position = position+1000*sample_rate
    vidcap.set(0,position)
    success,image = vidcap.read()
  
  #cleanup
  os.remove("temp.jpg")
  
if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description='Feed a video to the Google Vision API')
  parser.add_argument(
    'video_file', help='The video you\'d like to process.')
  parser.add_argument(
    'APIKey', help=('The API Key that identifies your Google Cloud Console '
    'Project with Vision API Enabled'))
  parser.add_argument(
    '-s','--sample-rate',dest='samplerate', default=5, choices=range(1,61),
    type=int, help=('The rate at which stills should be sampled from the '
    'video. Default is 5 (one frame per 5 seconds).'))
  args = parser.parse_args()
  main(args.video_file,args.samplerate,args.APIKey)
