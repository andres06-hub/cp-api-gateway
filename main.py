from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import io
import os
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICE2_URL = os.getenv("SERVICE2_URL", "http://0.0.0.0:8001")
ENDPOINT = SERVICE2_URL + "/tint-image/"

@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    try:
        async with httpx.AsyncClient() as client:
            form_data = {"file": (file.filename, await file.read(), file.content_type)}
            response = await client.post(ENDPOINT, files=form_data)

            if response.status_code == 200:
                return StreamingResponse(io.BytesIO(response.content), media_type="image/png")
            else:
                print(f"Error: Service responded with code {response.status_code}")
                print(f"Detail: {response.text}")
                return {"error": f"Service failed with code {response.status_code}"}

    except Exception as e:
        print(f"Error communicating with the service: {e}")
        return {"error": "The request could not be processed. Please try again later."}
    
@app.get("/")
async def root():
    return {"message": "Welcome to the cp API Gateway!"}

if __name__ == "__main__":
    print("Starting cp-api-gateway")
    port = int(os.getenv("PORT", 8000))
    print(f"Service 1 running on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)