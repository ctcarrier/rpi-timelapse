
import sys

from wrappers import GPhoto
from wrappers import Identify
from wrappers import NetworkInfo

try:
    self.camera.set_shutter_speed(sys.argv[1])
    self.camera.set_iso(iso=str(sys.argv[2]))
except Exception, e:
    logging.info("Error setting configs")
try:
    filename = self.camera.capture_image_and_download(shot=self.shot, image_directory=TMP_DIRECTORY)
except Exception, e:
    logging.error("Error on capture." + str(e))
    print "Error on capture." + str(e)
    print "Retrying..."
    # Occasionally, capture can fail but retries will be successful.
    continue

print(dataToSendBack)
sys.stdout.flush()
