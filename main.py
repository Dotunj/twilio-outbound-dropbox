import os
import dropbox
import requests
from flask import Flask, request, Response
from dotenv import load_dotenv
from twilio.twiml.voice_response import Gather, VoiceResponse

load_dotenv()
app = Flask(__name__)

@app.route('/inbound/voice/call', methods=['POST'])
def incoming_voice_call():
    response = VoiceResponse()
    gather = Gather(action='/outbound/voice/call', method='POST')
    gather.say('Please enter the number to dial, followed by the pound sign')
    response.append(gather)
    response.say('We didn\'t receive any input. Goodbye')
    return str(response)

@app.route('/outbound/voice/call', methods=['POST'])
def make_outbound_call():
    phone_number = request.form['Digits']
    response = VoiceResponse()
    response.dial(number=f"+{phone_number}", record=True, recording_status_callback='/recording/callback', recording_status_callback_event='completed')
    response.say('Thanks for calling in')
    return str(response)


@app.route('/recording/callback', methods=['POST'])
def upload_recording():
    dropbox_client = dropbox.Dropbox(os.getenv('DROPBOX_ACCESS_TOKEN'))
    recording_url = request.form['RecordingUrl']
    recording_sid = request.form['RecordingSid']
    upload_path = f"/twilio-recording/{recording_sid}.mp3"
    with requests.get(recording_url, stream=True) as r:
         dropbox_client.files_upload(r.raw.read(), upload_path)
    return Response(), 200


if __name__ == '__main__':
    app.run()
