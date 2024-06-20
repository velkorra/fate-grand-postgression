from fastapi import FastAPI, Depends, HTTPException
from .crud import *
from .database import engine, SessionLocal, Base
from .schemas import *
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
    service = ServantService(db)
    if index == None:
        return [servant for servant in service.get_all()]
    return service.get(index)

@app.post('/create_servant')
async def root(name: str, class_name : str, db : Session = Depends(get_db)):
    service = ServantService(db)
    try:
        servant = service.create(name, class_name)
        return {"message": f"Created {servant}"}
    except ValueError as e:
        raise HTTPException(400, str(e))
    
@app.put('/servant_update/{servant_id}')
async def root(servant_id : int, s : ServantUpdate, db : Session = Depends(get_db)):
    service = ServantService(db)
    try:
        servant = service.update(servant_id, s.name, s.class_name, s.ascension_level, s.level)
        return {"message": f'Updated {servant}'}
    except ValueError as e:
        raise HTTPException(400, str(e))
    
@app.get('/contracts')
async def root(index : int = None, db : Session = Depends(get_db)):
    service = ContractService(db)
    if index == None:
        return [contract for contract in service.get_all()]
    return service.get(index)

@app.get('/masters')
async def root(index : int = None, db : Session = Depends(get_db)):
    service = MasterService(db)
    if index == None:
        return [master for master in service.get_all()]
    return service.get(index)

@app.get('/localization/{servant_id}')
async def root(servant_id : int, db : Session = Depends(get_db)):
    service = ServantService(db)
    # if index == None:
    #     return [master for master in service.get_details(servant_id)]
    return service.get_details(servant_id)