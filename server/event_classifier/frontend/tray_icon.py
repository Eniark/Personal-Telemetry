import pystray
from PIL import Image
from shared.configs import PROJECT_ROOT
from ..configs import MEDIA_FOLDER

def create_icon():
    icon_path = MEDIA_FOLDER / 'catppuccin.png'
    image = Image.open(icon_path)
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