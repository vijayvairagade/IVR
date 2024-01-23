from signalwire.voice_response import VoiceResponse, Gather
from signalwire.rest import Client as SignalwireClient
from signalwire.rest.resources import voice, message

signalwire_project = 'your_project_id'
signalwire_token = 'your_auth_token'
signalwire_space_url = 'your_space_url'

def send_sms(to, message_body):
    client = SignalwireClient(signalwire_project, signalwire_token, signalwire_space_url)
    messaging = message.Message(client=client)
    
    try:
        messaging.create(
            from_='+1234567890',  # Replace with your SignalWire phone number
            to=to,
            body=message_body
        )
        print(f"SMS sent to {to}")
    except Exception as e:
        print(f"Failed to send SMS: {str(e)}")

def handle_user_input(user_input):
    options = {
        '1': "Redirecting to support.",
        '2': "Redirecting to sales.",
        '3': "Checking your account balance.",
        '4': "Providing general information.",
        '5': "Transferring to customer service.",
        '6': "Transferring to the billing department.",
    }
    return options.get(user_input, "Invalid input. Please try again.")

def ivr_script():
    response = VoiceResponse()

    with response.gather(numDigits=1, action='/ivr', method='POST', timeout=10) as gather:
        gather.say("Welcome to the IVR menu. Press 1 for technical support. Press 2 for sales.")
        gather.say("Press 3 to check your account balance. Press 4 for general information.")
        gather.say("Press 5 to talk to a service executive. Press 6 to transfer to the billing department.")

    user_input = response.gather.input or 'invalid'

    # Handle repeated invalid inputs
    invalid_count = response.session.get('invalid_count', 0)
    if user_input == 'invalid':
        invalid_count += 1
        response.session['invalid_count'] = invalid_count

        if invalid_count >= 3:
            response.say("Too many invalid inputs. Transferring to an operator.")
            response.dial('+9876543210')  # Replace with the other SignalWire phone number
            return response

        response.say("Invalid input. Please try again.")
        return ivr_script()
    else:
        response.session['invalid_count'] = 0

    if user_input == '5':
        # Send SMS to the user
        user_phone_number = '+1234567890'  # Replace with the user's phone number
        sms_body = "Thank you for choosing to talk to our service executive. Please rate your experience after the call."
        send_sms(user_phone_number, sms_body)

        # Add a waiting system with a waiting message and background music
        response.say("Please wait while we connect you to a service executive.")
        response.play("http://your-server.com/your-background-music.mp3")  # Replace with the URL to your background music

    response.say(handle_user_input(user_input))

    return response

if __name__ == "__main__":
    client = SignalwireClient(signalwire_project, signalwire_token, signalwire_space_url)
    call = client.calls.create(to='+1234567890', from_='+0987654321', url='http://your-server.com/your-webhook-endpoint')

    print(call.sid)
