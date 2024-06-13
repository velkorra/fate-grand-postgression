from fastapi import FastAPI, Depends, HTTPException
from .crud import *
from .database import engine, SessionLocal, Base
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get('/servants')
async def root(index : int = None, db : Session = Depends(get_db)):
    if index == None:
        return [servant for servant in get_servants(db)]
    return [get_servants(db)[index]]

@app.post('/create_servant')
async def root(name: str, class_name : str, db : Session = Depends(get_db)):
    try:
        servant = create_servant(db, name, class_name)
        return {"message": f"Created {servant}"}
    except ValueError as e:
        raise HTTPException(400, str(e))