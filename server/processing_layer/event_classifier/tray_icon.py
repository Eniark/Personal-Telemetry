import pystray
from PIL import Image
from shared.configs import PROJECT_ROOT

def create_icon():
    image = Image.open(PROJECT_ROOT / 'server' / 'processing_layer' / 'event_classifier' / 'media' / 'catppuccin.png')
    return image


icon = pystray.Icon(
    "personalTelemetry",
    create_icon(),
    "Personal Telemetry",
    menu=pystray.Menu(
        pystray.MenuItem("Status", lambda: print("Running")),
        pystray.MenuItem("Exit", lambda icon, _: icon.stop()),
        pystray.MenuItem("Notify",
                lambda icon, _: icon.notify('WIP'))
    ),
)

icon.run()