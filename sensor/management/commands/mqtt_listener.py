from django.core.management.base import BaseCommand
import json
from django.utils import timezone
from sensor.models import SensorData, MonitoringGroup, Notification
from rest_framework.authtoken.models import Token
import paho.mqtt.client as mqtt
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import requests
from django.utils import timezone
from django.utils.timesince import timesince




class Command(BaseCommand):
    help = 'Starts the MQTT listener'
    
    def handle(self, *args, **kwargs):
        mqtt_broker = '192.168.55.100'
        mqtt_port = 1883
        mqtt_user = 'admin'
        mqtt_pass = 'admin'

        tokens = Token.objects.all()
        
        def on_connect(client, userdata, flags, rc):
            print("Connected to MQTT broker with result code " + str(rc))
            for token in tokens:
                data_topic = f"sensor/data/{token.key}"
                menu_topic = f"sensor/menu/{token.key}"
                notification_topic = f"sensor/notification/{token.key}"  
                monitoring_topic = f"sensor/monitoring/{token.key}"  
                
                client.subscribe(data_topic)
                client.subscribe(menu_topic)
                client.subscribe(notification_topic)  # Subscribe to notification topic
                client.subscribe(monitoring_topic)  
                
                print(f"Subscribed to topic: {data_topic}")
                print(f"Subscribed to topic: {menu_topic}")
                print(f"Subscribed to notification topic: {notification_topic}")  # Log the subscription
                print(f"Subscribed to topic: {monitoring_topic}")  # Log the subscription

        def on_message(client, userdata, msg):
            payload = msg.payload.decode()  # Decode the payload to a string
            payload_size = len(msg.payload)  # Get the size in bytes

            print(f"Received message: {payload} on topic {msg.topic}")
            print(f"Payload size (in bytes): {payload_size}")

            try:
                data = json.loads(payload)
                token_key = msg.topic.split('/')[-1]
                token = Token.objects.get(key=token_key)
                user = token.user

                if msg.topic.startswith("sensor/data"):
                    # Extract data
                    food_type = data.get('food_type')
                    spoilage_status_value = data.get('spoilage_status')
                    spoilage_warning_temp = data.get('spoilage_status_warning_temp', "Temperature is safe")
                    spoilage_warning_humidity = data.get('spoilage_status_warning_humidity', "Humidity is safe")
                    start_time = timezone.now()
                    
                    # Map human-readable spoilage status to internal key
                    spoilage_status_mapping = {
                        "Food is Fresh": "food_is_fresh",
                        "Food is at Risk": "food_is_at_risk",
                        "Food is Spoiled": "food_is_spoiled",
                    }
                    
                    spoilage_status = spoilage_status_mapping.get(spoilage_status_value, "food_is_fresh")
                    
                    # Get or create an active monitoring group for the user
                    monitoring_group = MonitoringGroup.objects.filter(user=user, is_done=False).first()

                    if monitoring_group:
                        if monitoring_group.food_type != food_type:
                            print(f"Validation error: User {user.username} is attempting to monitor a different food type '{food_type}' while monitoring group {monitoring_group.id} is active with food type '{monitoring_group.food_type}'.")
                            return

                    if not monitoring_group:
                        monitoring_group = MonitoringGroup.objects.create(
                            user=user,
                            food_type=food_type,
                            start_time=start_time,
                            is_done=False
                        )
                        print(f"Created new monitoring group {monitoring_group.id} for user {user.username} with food type '{food_type}'")

                    # Save the sensor data
                    sensor_data = SensorData(
                        user=user,
                        monitoring_group=monitoring_group,
                        temperature=data.get('temperature'),
                        humidity=data.get('humidity'),
                        methane=data.get('methane'),
                        threshold=data.get('threshold'),
                        ammonia=data.get('ammonia'),
                        food_type=food_type,
                        spoilage_status=spoilage_status,
                        timestamp=timezone.now()
                    )
                    sensor_data.save()
                    print(f"Saved sensor data for user {user.username} under monitoring group {monitoring_group.id}")

                    # Temperature and Humidity Warnings
                    if spoilage_warning_temp != "Temperature is safe" or spoilage_warning_humidity != "Humidity is safe":
                        print('sad')
                        warning_message = ""

                        if spoilage_warning_temp != "Temperature is safe":
                            warning_message += f"Warning: {spoilage_warning_temp}. "
                        
                        if spoilage_warning_humidity != "Humidity is safe":
                            warning_message += f"Warning: {spoilage_warning_humidity}."
                        
                        # Check if a notification with the same user, monitoring group, and message already exists
                        if not Notification.objects.filter(
                            user=user,
                            monitoring_group=monitoring_group,
                            message=warning_message.strip()
                        ).exists():
                            # Create a notification for spoilage warnings
                            notification = Notification.objects.create(
                                user=user,
                                monitoring_group=monitoring_group,
                                message=warning_message.strip(),
                            )

                            topic = f"sensor/notification/{token.key}"
                            payload = json.dumps({
                                "id": notification.id,
                                "message": warning_message.strip(),
                                "spoilage_status": spoilage_status_value
                            })
                            client.publish(topic, payload)
                            print(f"Published warning notification for user {user.username}: {warning_message}")
                        else:
                            print("Notification already exists, skipping publication.")

                    # If food is spoiled, update the monitoring group
                    if spoilage_status == "food_is_spoiled":
                        monitoring_group.is_done = True
                        monitoring_group.end_time = timezone.now()
                        
                        if not monitoring_group.email_notification_sent:
                            # send_spoilage_notification(user, food_type, monitoring_group.id, monitoring_group.start_time, monitoring_group.end_time)
                            monitoring_group.email_notification_sent = True  

                        if not monitoring_group.phone_notification_sent:
                            # send_spoilage_sms(user, food_type)  
                            monitoring_group.phone_notification_sent = True  

                        notification = Notification.objects.create(
                            user=user,
                            monitoring_group=monitoring_group,
                            message=f"{food_type} has spoiled as of {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}.",
                        )    
                        topic = f"sensor/notification/{token.key}"
                        timestamp = timezone.now()  
                        formatted_timestamp = timestamp.strftime('%B %d, %Y at %I:%M %p') 

                        payload = json.dumps({
                            "id": notification.id, 
                            "message": f"{food_type} has spoiled as of {formatted_timestamp}.",
                        })
                        client.publish(topic, payload)  

                        monitoring_group.save()  
                        print(f"Monitoring group {monitoring_group.id} marked as done for user {user.username}")

                elif msg.topic.startswith("sensor/monitoring"):
                    print(f"Monitoring message received for user {user.username}: {data}")

            except Token.DoesNotExist:
                print("Invalid token received.")
            except Exception as e:
                print(f"Error processing message: {e}")

        client = mqtt.Client()
        if mqtt_user and mqtt_pass:
            client.username_pw_set(mqtt_user, mqtt_pass)

        client.on_connect = on_connect
        client.on_message = on_message

        client.connect(mqtt_broker, mqtt_port, 60)
        client.loop_forever()




def send_spoilage_notification(user, food_type, monitoring_group_id, start_time, end_time):          
    subject = "Spoilage Alert for Your Monitoring Group"                
                      
    # Render the HTML template with context                
    html_message = render_to_string('spoilage_notification_email.html', {                
        'username': user.username,               
        'food_type': food_type,               
        'monitoring_group_id': monitoring_group_id,               
        'start_time': start_time,             
        'end_time': end_time,              
    })             
             
    email = EmailMessage(
        subject,
        html_message,
        to=[user.email]
    )
    email.content_subtype = 'html'  # Send as HTML
    email.send()

def send_spoilage_sms(user, food_type):
    message = f"Hi {user.username}, unfortunately, your {food_type} has spoiled. Please check it as soon as possible."
    phone_number = user.phone_number  
    print(phone_number)
    print(user)

    url = "https://connect.routee.net/sms"
    headers = {
        "Authorization": "Bearer 06f846fb-465c-4f35-8259-709304ae44c6",
        "Content-Type": "application/json"
    }
    payload = {
        "body": message,
        "to": phone_number,
        "from": "LegionTech"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        # Print the response data for debugging
        print(f"Response data: {response.json()}")  # Print the JSON response data

        if response.status_code == 200:
            print(f"SMS sent successfully to {phone_number} for {user.username}. Response: {response.json()}")
        else:
            print(f"Failed to send SMS: {response.status_code} - {response.text} - Response: {response.json()}")
    except Exception as e:
        print(f"An error occurred while sending SMS: {e}")
