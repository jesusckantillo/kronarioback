from fastapi import FastAPI
from routes.majors import majors

app = FastAPI()
app.include_router(majors)

@app.get(path="/")
def home():
    return {"Kronario API: Working"}