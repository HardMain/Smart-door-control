import asyncio
import logging
from typing import Callable, Optional

from app.config import settings

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    logger.warning("RPi.GPIO not available - running in simulation mode")


class DoorbellManager:
    def __init__(self):
        self.sensors_enabled = settings.sensors_enabled and GPIO_AVAILABLE
        self.doorbell_button_pin = settings.doorbell_button_pin
        self.door_lock_relay_pin = settings.door_lock_relay_pin
        self.door_lock_open_duration = settings.door_lock_open_duration

        self._doorbell_callback: Optional[Callable] = None
        self._is_monitoring = False
        self._last_button_state = True

        if self.sensors_enabled:
            try:
                GPIO.setmode(GPIO.BCM)

                GPIO.setup(self.doorbell_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

                GPIO.setup(self.door_lock_relay_pin, GPIO.OUT, initial=GPIO.LOW)

                logger.info(f"GPIO initialized: button=GPIO{self.doorbell_button_pin}, relay=GPIO{self.door_lock_relay_pin}")
            except Exception as e:
                logger.error(f"GPIO initialization error: {e}")
                self.sensors_enabled = False
        else:
            if not GPIO_AVAILABLE:
                logger.info("RPi.GPIO not available - running in simulation mode")
            else:
                logger.info("Sensors disabled in config - running in simulation mode")

    def set_doorbell_callback(self, callback: Callable):
        self._doorbell_callback = callback

    async def start_monitoring(self):
        self._is_monitoring = True

        if self.sensors_enabled:
            logger.info("Starting doorbell button monitoring (polling mode)")
            asyncio.create_task(self._poll_button())
        else:
            logger.info("Doorbell monitoring in simulation mode")

    async def _poll_button(self):
        while self._is_monitoring:
            try:
                button_state = GPIO.input(self.doorbell_button_pin)

                if self._last_button_state == GPIO.HIGH and button_state == GPIO.LOW:
                    logger.info("Doorbell button pressed (GPIO)")
                    if self._doorbell_callback:
                        await self._doorbell_callback()

                self._last_button_state = button_state

            except Exception as e:
                logger.error(f"Error polling button: {e}")

            await asyncio.sleep(0.1)

    async def simulate_doorbell_press(self):
        logger.info("Simulating doorbell press")
        if self._doorbell_callback:
            await self._doorbell_callback()

    async def unlock_door(self):
        logger.info("Unlocking door")

        if self.sensors_enabled:
            GPIO.output(self.door_lock_relay_pin, GPIO.HIGH)
            logger.info(f"GPIO{self.door_lock_relay_pin} = HIGH (lock opened)")
        else:
            logger.info("Simulation: Door lock activated")

        await asyncio.sleep(self.door_lock_open_duration)

        if self.sensors_enabled:
            GPIO.output(self.door_lock_relay_pin, GPIO.LOW)
            logger.info(f"GPIO{self.door_lock_relay_pin} = LOW (lock closed)")
        else:
            logger.info("Simulation: Door lock deactivated")

        logger.info("Door locked")

    def cleanup(self):
        self._is_monitoring = False

        if self.sensors_enabled:
            try:
                GPIO.output(self.door_lock_relay_pin, GPIO.LOW)
                GPIO.cleanup()
                logger.info("GPIO resources cleaned up")
            except Exception as e:
                logger.error(f"Error during GPIO cleanup: {e}")