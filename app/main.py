# import views.landing as ui

# if __name__ == "__main__":
#     ui.run()

from app import api
import uvicorn

if __name__ == "__main__":
    #use for local
    uvicorn.run(api, host="0.0.0.0", port=8000, reload=True)

    #use for docker
    #uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)