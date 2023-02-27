from backend import configs
from backend.modules.coreAPI import CoreAPI

# CORE-API client
core_api = CoreAPI(
    username=configs.CORE_API_USERNAME, password=configs.CORE_API_PASSWORD
)
