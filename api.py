from fastapi import FastAPI
import uvicorn

from config import API_HOST_URL, API_HOST_PORT
from steam_api import get_app_details

class API:
    def __init__(self):
        self.app = FastAPI()

    def run(self):
        self.register_endpoints()

        uvicorn.run(self.app, host=API_HOST_URL, port=API_HOST_PORT, reload=False)

    def register_endpoints(self):
        @self.app.get("/")
        def read_root():
            return {"message": "Hello World"}

        # a test getting app details from the Steam API
        # TODO: Remove this endpoint, when database is implemented
        @self.app.get("/app/{app_id}")
        def read_app(app_id: int):
            app_details = get_app_details(app_id)
            if app_details:
                if not isinstance(app_details, dict):
                    app_details = app_details.to_dict()

                return app_details
            else:
                return {"message": "App not found"}

if __name__ == "__main__":
    api = API()
    api.run()