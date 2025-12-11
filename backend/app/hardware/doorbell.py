import asyncio
import logging
from typing import Callable, Optional

from app.config import settings

logger = logging.getLogger(__name__)

# Пытаемся импортировать — если не получается, работаем в симуляции
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

        if not self.sensors_enabled:
            if not GPIO_AVAILABLE:
                logger.info("RPi.GPIO not available - running in simulation mode")
            else:
                logger.info("Sensors disabled in config - running in simulation mode")

    def set_doorbell_callback(self, callback: Callable):
        self._doorbell_callback = callback

    async def start_monitoring(self):
        self._is_monitoring = True
        logger.info("Doorbell monitoring started in simulation mode")

    async def simulate_doorbell_press(self):
        logger.info("Simulating doorbell press")
        if self._doorbell_callback:
            await self._doorbell_callback()

    async def unlock_door(self):
        logger.info("Unlocking door (simulation)")

        logger.info("Simulation: Door lock activated")
        await asyncio.sleep(self.door_lock_open_duration)
        logger.info("Simulation: Door lock deactivated")

        logger.info("Door locked")

    def cleanup(self):
        self._is_monitoring = False
        logger.info("DoorbellManager stopped (simulation)")