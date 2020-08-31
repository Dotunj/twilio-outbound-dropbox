import os
import dropbox
import requests
from flask import Flask, request, Response, jsonify
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()
app = Flask(__name__)
twilio_client = Client()

@app.route('/voice/call', methods=['GET'])
def make_outbound_call(): 
    twilio_client.calls.create(record=True, to=os.getenv('TWILIO_TO_NUMBER'), from_=os.getenv('TWILIO_FROM_NUMBER'), 
        twiml=f"<Response><Say voice='alice'>Hello, I hope you're having a wonderful day</Say><Pause length='1'/><Say>Goodbye</Say></Response>",
        recording_status_callback=f"{os.getenv('BASE_URL')}/recording/callback",
        recording_status_callback_event='completed')
    return jsonify({ 'message': 'Call has been placed'}), 201

@app.route('/recording/callback', methods=['POST'])
def upload_recording():
    recording_url = request.form['RecordingUrl']
    recording_sid = request.form['RecordingSid']
    dropbox_client = dropbox.Dropbox(os.getenv('DROPBOX_ACCESS_TOKEN'))
    upload_path = f"/twilio-recording/{recording_sid}.mp3"
    with requests.get(recording_url, stream=True) as r:
         dropbox_client.files_upload(r.raw.read(), upload_path)
    return Response(), 200


if __name__ == '__main__':
    app.run()
