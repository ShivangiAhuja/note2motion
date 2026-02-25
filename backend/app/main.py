from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Note2Motion API is running"}