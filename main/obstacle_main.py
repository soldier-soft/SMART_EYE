from core.hardware.arduino.arduino_comm import ArduinoComm
from core.navigation.obstacle.obstacle_controller import ObstacleController
from core.voice_interface.text_to_speech import TextToSpeech
from core.voice_interface.speech_to_text import SpeechToText
from core.hardware.sensors.sensor_manager import SensorManager
from services.obstacle_service import ObstacleService

def alert_callback(distance):
    tts = TextToSpeech()
    tts.speak(f"Warning! Obstacle ahead at {distance:.1f} centimeters.")

def main():
    arduino = ArduinoComm(port="COM11", baudrate=9600)
    arduino.connect()

    sensor_manager = SensorManager(
        arduino_comm=arduino,
        alert_distance_cm=30,
        alert_callback=alert_callback
    )
    sensor_manager.start_monitoring()

    controller = ObstacleController(sensor_manager=sensor_manager)

    # Example: Respond to move command
    while True:
        cmd = input("Enter move command (forward/left/right/exit): ").strip().lower()
        if cmd == "exit":
            break
        controller.handle_move_command(cmd)

    sensor_manager.stop_monitoring()
    arduino.disconnect()

if __name__ == "__main__":
    main()
