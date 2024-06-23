from fastapi import FastAPI, Depends, File, HTTPException, UploadFile
from .crud import *
from .database import engine, SessionLocal, Base
from sqlalchemy import text
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


@app.get('/sql')
async def root():
    a = engine.connect()
    with open('queries/join.sql', encoding='utf-8') as f:
        return str(a.execute(text(f.read())).fetchall())

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get('/servants')
async def root(db : Session = Depends(get_db)):
    service = ServantService(db)
    return service.get_all()


@app.get('/servants/{servant_id}')
async def root(servant_id : int, db : Session = Depends(get_db)):
    service = ServantService(db)
    return service.get(servant_id)

@app.delete("/servants/{servant_id}")
async def root(servant_id : int, db : Session = Depends(get_db)):
    s = ServantService(db)
    try:
        s.delete(servant_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
        
@app.post('/servants/new')
async def root(servant : ServantCreate, db : Session = Depends(get_db)):
    service = ServantService(db)
    try:
        servant = service.create(servant)
        return {"message": f"Created {servant}"}
    except ValueError as e:
        raise HTTPException(400, str(e))
    
@app.put('/servants/{servant_id}')
async def root(servant_id : int, s : ServantUpdate, db : Session = Depends(get_db)):
    service = ServantService(db)
    try:
        servant = service.update(servant_id, s)
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

@app.get('/localization')
async def root(servant_id : int = None, db : Session = Depends(get_db)):
    service = ServantService(db)
    # if index == None:
    #     return [master for master in service.get_details(servant_id)]
    return service.join(servant_id)

@app.get('/skill/{servant_id}')
async def root(servant_id : int = None, db : Session = Depends(get_db)):
    service = ServantService(db)
    # if index == None:
    #     return [master for master in service.get_details(servant_id)]
    return service.get_skills(servant_id)

@app.post('/localization')
async def root(servant_id : int = None, db : Session = Depends(get_db)):
    service = ServantService(db)
    service.add_localization()


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):

    with open(file.filename, "wb") as buffer:
        # Считываем и записываем содержимое файла на диск
        buffer.write(await file.read())
    return {"filename": file.filename, "message": "File uploaded successfully"}
