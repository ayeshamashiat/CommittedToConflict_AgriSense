from fastapi import FastAPI

app = FastAPI(title="AgriSense API")


@app.get("/")
def read_root():
    return {"status": "ok"}
