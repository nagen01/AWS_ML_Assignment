# -*- coding: utf-8 -*-
"""
AWS_ML_Assignment_01

Nagendra Bahadur Singh

"""
import cv2
import boto3
from contextlib import closing
from pygame import mixer
import time
#from __future__ import print_function

my_text = 'The sun does arise and make happy the skies. The merry bells ring to welcome the spring.'	

if __name__ == "__main__":        
    
    #Polly for listening the voice
    client=boto3.client('polly', region_name='eu-west-1')	    
    response = client.synthesize_speech(Text=my_text, OutputFormat='mp3', VoiceId='Matthew')
    
    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            data = stream.read()
            fo = open("pollytest.mp3", "wb")
            fo.write( data )
            fo.close()     
    mixer.init()
    mixer.music.load("pollytest.mp3")
    mixer.music.play()
    
    #Polly for storing the file on S3
    polly_client = boto3.client('polly',
                    aws_access_key_id='AKIARCLIUCLPHNQQMRHC',                  
        aws_secret_access_key='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',
        region_name='eu-west-1')
    
    response = polly_client.start_speech_synthesis_task(VoiceId='Matthew',
                    OutputS3BucketName='voice-polly-transcribe',
                    OutputS3KeyPrefix='key',
                    OutputFormat='mp3',
                    Text = my_text)
    
    taskId = response['SynthesisTask']['TaskId']    
    print("Task id is {} ".format(taskId))    
    task_status = polly_client.get_speech_synthesis_task(TaskId = taskId)    
    print(task_status)
    
    #Transcribe process starts here
    transcribe = boto3.client('transcribe')
    job_name = "t2"
    job_uri = "s3://voice-polly-transcribe/6e1f3451-7736-4693-87fa-93f1d4b39ca4.mp3"
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat='mp3',
        LanguageCode='en-US'
    )
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("Not ready yet...")
        time.sleep(5)
    print(status)   

cv2.waitKey(0)
cv2.destroyAllWindows()
