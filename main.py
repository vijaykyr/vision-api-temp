import argparse
import base64
import cv2
import os

from apiclient.discovery import build

# Author: reddyv@
# Last Update: 03-11-2016
# Usage:
#   python main.py --help
# Todo:
#   1) See if you can convert the cv2 image format to base64 directly in memory 
#   without having to write to disk first
#   2) Validate JSON responses. Currently you assume API request will be succesfull
#   3) Evaluate using a lighterweight framegrabber than OpenCV.

def main(video_file, sample_rate, APIKey):
  BATCH_LIMIT = 8 #number of images to send per API request, documented limits
  # are 16 images per quest, and 8 images per second
  
  #obtain service handle for vision API using API Key
  service = build('vision', 'v1', 
  discoveryServiceUrl='https://vision.googleapis.com/$discovery/rest?version=v1',
  developerKey=APIKey)
  
  #initialize vars and grab initial frame
  vidcap = cv2.VideoCapture(video_file)
  position = 0
  frame = 0
  batch_count = 0
  base64_images = [] 
  success,image = vidcap.read()
  
  while success: 
    
    #read in frames one batch at a time
    while success and batch_count < BATCH_LIMIT:
      
      #convert frame to base64
      cv2.imwrite('temp.jpg', image) 
      with open('temp.jpg','rb') as image:
        base64_images.append((position/1000,base64.b64encode(image.read())))
    
      #advance to next image
      if sample_rate > 0: position = position+1000*sample_rate
      else: position = -1 #terminate
      frame += 1
      batch_count += 1
      vidcap.set(0,position)
      success,image = vidcap.read()
  
  
    #send batch to vision API
    json_request = {'requests': []}
    for img in base64_images:
      json_request['requests'].append(
        {
          'image': {
            'content': img[1] #img is a tuple (timestamp, base64image)
           },
          'features': [{
            'type': 'LABEL_DETECTION',
            'maxResults': 3,
           }] 
        })
      
    service_request = service.images().annotate(body=json_request)
    responses = service_request.execute()

    #response format
    #{u'responses': [{u'labelAnnotations': [{u'score': 0.99651724, u'mid':
    # u'/m/01c4rd', u'description': u'beak'}, {u'score': 0.96588981, u'mid':
    # u'/m/015p6', u'description': u'bird'}, {u'score': 0.85704041, u'mid':
    # u'/m/09686', u'description': u'vertebrate'}]}]}

    #process response and print results
    for response, img in zip(responses['responses'],base64_images):
      labels = ''
      if(response):
        for annotation in response['labelAnnotations']:
          labels += annotation['description']+', '
        labels = labels[:-2] #trim trailing comma and space
      
        # ASSUMPTION: this assumes the API returns responses in the order they
        # were received. Otherwise the timestamps may not be paired with the 
        # correct lables
        print('{0:8}{1}'.format(str(img[0])+'sec:',labels))
      else: print('{0:8}n/a'.format(str(img[0])+'sec:'))
    
    #reset for next batch
    batch_count = 0
    base64_images = []

  
  #cleanup
  os.remove("temp.jpg")
  
if __name__ == '__main__':
  
  #configure command line options
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
  
  #read in command line arguments
  args = parser.parse_args()
  
  #start execution
  main(args.video_file,args.samplerate,args.APIKey)
