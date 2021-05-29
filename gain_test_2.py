from time import sleep

from filmscanner import FilmScanner


scanner = FilmScanner()

scanner.camera.shutter_speed = int(1e6/4000)
scanner.camera.iso = 40
sleep(2)
scanner.camera.capture("gain_test_2_iso.jpg", bayer=True)

scanner.camera.shutter_speed = int(1e6/4000)
scanner.camera.exposure_mode = "off"
scanner.camera.analog_gain = 1
scanner.camera.analog_gain = 1
sleep(2)
scanner.camera.capture("gain_test_2_gain.jpg", bayer=True)
