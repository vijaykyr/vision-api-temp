import argparse
import base64
import cv2
import os

from apiclient.discovery import build

# Author: reddyv@
# Date: 03-06-2016
# Usage:
#   python main.py --help
# Todo:
#   1) Batch multiple images into a single API request to reduce latency. Docs 
#   say you can batch up to 16 images per request, but it will only respond to
#   8 images per second
#   2) See if you convert the cv2 image format to base64 directly in memory 
#   without having to write to disk first

def main(video_file, sample_rate, APIKey):
  #obtain service handle for vision API using API Key
  service = build('vision', 'v1', 
  discoveryServiceUrl='https://vision.googleapis.com/$discovery/rest?version=v1',
  developerKey=APIKey)
  
  vidcap = cv2.VideoCapture(video_file)
  position = 0
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
              'maxResults': 3,
             }]
           }]
        })
      response = service_request.execute()
      
      #response format
      #{u'responses': [{u'labelAnnotations': [{u'score': 0.99651724, u'mid':
      # u'/m/01c4rd', u'description': u'beak'}, {u'score': 0.96588981, u'mid':
      # u'/m/015p6', u'description': u'bird'}, {u'score': 0.85704041, u'mid':
      # u'/m/09686', u'description': u'vertebrate'}]}]}
      
      #extract labels from response and print
      labelAnnotations = response['responses'][0]['labelAnnotations']
      labels = ''
      for annotation in labelAnnotations:
        labels += annotation['description']+', '
      labels = labels[:-2] #trim trailing comma and space
      
      print('{} sec:\t{}'.format(position/1000,labels))
  
    #advance to next image
    if sample_rate > 0: position = position+1000*sample_rate
    else: position = -1 #terminate
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
    '-s','--sample-rate',dest='samplerate', default=5, type=int, 
    help=('The rate at which stills should be sampled from the '
    'video. Default is 5 (one frame per 5 seconds).'))
  args = parser.parse_args()
  main(args.video_file,args.samplerate,args.APIKey)
