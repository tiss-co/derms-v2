from backend import configs
from backend.modules.cbiot import CBIOT

# CBIOT client
cbiot = CBIOT(username=configs.CBIOT_USERNAME, password=configs.CBIOT_PASSWORD)
