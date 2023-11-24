from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def default():
    return {"success":True, "message":"Default Page"}

@app.get("/home")
def home():
    return {"success":True, "message":"Home Page"}
