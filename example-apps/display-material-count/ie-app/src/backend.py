import server
from mqtt_lib import *

# Initial component counts for the machine
component_counts = {
    "transistor": 200,
    "capacitor": 200,
    "resistor": 200
}

def on_message(message):
    """
    Callback function to handle incoming MQTT messages from the 'material_consumption' topic.
    Decrements the corresponding component count based on the message received.
    
    :param message: The MQTT message containing the component name (transistor, capacitor, or resistor).
    """
    global component_counts
    component_type = message.payload.decode("utf-8")
    if component_type in component_counts:
        component_counts[component_type] -= 1
        print(f"Component {component_type} used. Remaining: {component_counts[component_type]}")

def get_current_component_counts() -> dict[str, int]:
    """
    Returns the current counts of transistors, capacitors, and resistors.
    This function is exposed via the '/components' endpoint for the frontend.
    
    :return: A dictionary with the current component counts.
    """
    return component_counts

def main():
    """
    Initializes the MQTT client and subscribes to the 'material_consumption' topic.
    Starts the server to handle RESTful API requests.
    """
    # Initialize the MQTT client
    mqtt_client = MQTTClient(
        broker_address="broker_address", 
        broker_port=1883, 
        username="user", 
        password="password"
    )
    
    # Subscribe to the 'material_consumption' topic
    mqtt_client.subscribe("material_consumption", on_message)
    
    # Start the server to listen for API requests
    server.run_server()

if __name__ == "__main__":
    main()
