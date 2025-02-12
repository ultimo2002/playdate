from fastapi.staticfiles import StaticFiles

import api
import config
import uvicorn
from fastapi import FastAPI


#run de api
def run():
    api.register_endpoints(app)

    print("Run API")

    uvicorn.run(app, host=config.API_HOST_URL, port=config.API_HOST_PORT, reload=False)


def main():
    global app
    # maak app FastAPI instance
    app = FastAPI()
    # ?? CSS ofzo?
    app.mount("/static", StaticFiles(directory="static"), name="static")
    run()


main()