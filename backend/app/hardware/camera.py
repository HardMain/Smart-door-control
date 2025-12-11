import io
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

from app.config import settings

logger = logging.getLogger(__name__)

try:
    from picamera2 import Picamera2
    CAMERA_AVAILABLE = True
except ImportError:
    CAMERA_AVAILABLE = False
    logger.warning("picamera2 not available - running in simulation mode")


class CameraService:
    def __init__(self):
        self.camera_enabled = settings.camera_enabled and CAMERA_AVAILABLE
        self.camera = None

        if self.camera_enabled:
            try:
                self.camera = Picamera2()
                config = self.camera.create_still_configuration(
                    main={"size": (1920, 1080)},
                    buffer_count=2
                )
                self.camera.configure(config)
                self.camera.start()
                logger.info("Picamera2 initialized successfully (1920x1080)")
            except Exception as e:
                logger.error(f"Camera initialization error: {e}")
                self.camera_enabled = False
                self.camera = None
        else:
            if not CAMERA_AVAILABLE:
                logger.info("picamera2 not available - running in simulation mode")
            else:
                logger.info("Camera disabled in config - running in simulation mode")

    async def capture_photo(self) -> bytes:
        if self.camera_enabled:
            return self._capture_real_photo()
        else:
            return self._generate_simulation_photo()

    def _capture_real_photo(self) -> bytes:
        logger.info("Capturing photo from camera")

        image_array = self.camera.capture_array()

        image = Image.fromarray(image_array)

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)

        logger.info("Photo captured successfully")
        return img_byte_arr.getvalue()

    def _generate_simulation_photo(self) -> bytes:
        logger.info("Generating simulation photo")

        width, height = 640, 480
        image = Image.new('RGB', (width, height), color=(73, 109, 137))

        draw = ImageDraw.Draw(image)

        text = f"Simulation Photo\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (width - text_width) // 2
        y = (height - text_height) // 2

        draw.text((x, y), text, fill=(255, 255, 255), font=font)

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)

        logger.info("Simulation photo generated")
        return img_byte_arr.getvalue()

    def cleanup(self):
        if self.camera_enabled:
            self.camera.stop()
            logger.info("Camera stopped")