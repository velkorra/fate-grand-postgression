import os
from pathlib import Path
from fastapi import FastAPI, Depends, File, Form, HTTPException, UploadFile
import uvicorn
from .crud import *
from .database import engine, SessionLocal, Base
from sqlalchemy import text
from .schemas import *
from fastapi.middleware.cors import CORSMiddleware
from .utils import save_file_to_disk, MEDIA_DIR
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

# Servants API -----------------------------------------------------
@app.get('/servants')
async def root(db : Session = Depends(get_db)):
    service = ServantService(db)
    return service.get_all()


@app.get('/servants/{servant_id}')
async def root(servant_id : int, db : Session = Depends(get_db)):
    service = ServantService(db)
    return service.get(servant_id)

        
@app.post('/servants')
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

@app.delete("/servants/{servant_id}")
async def root(servant_id : int, db : Session = Depends(get_db)):
    s = ServantService(db)
    try:
        s.delete(servant_id)
    except ValueError as e:
        raise HTTPException(404, str(e))

# Masters API -----------------------------------------------------

@app.get('/masters')
async def root(db : Session = Depends(get_db)):
    service = MasterService(db)
    return service.get_all()

@app.get('/masters/{master_id}')
async def root(master_id : int, db : Session = Depends(get_db)):
    service = MasterService(db)
    return service.get(master_id)

@app.post('/masters')
async def root(master : MasterCreate, db : Session = Depends(get_db)):
    service = MasterService(db)
    try:
        m = service.create(master)
        return {"message": f"Created {m}"}
    except ValueError as e:
        raise HTTPException(400, str(e))
    
@app.put('/masters/{master_id}')
async def root(master_id: int, master : MasterUpdate, db : Session = Depends(get_db)):
    service = MasterService(db)
    try:
        m = service.update(master_id, master)
        return f"updated {m}"
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.delete('/masters/{master_id}')
async def root(master_id : int, db : Session = Depends(get_db)):
    service = MasterService(db)
    try:
        service.delete(master_id)
        return f"deleted {master_id} master"
    except ValueError as e:
        raise HTTPException(404, str(e))
    
# Contracts API -----------------------------------------------------

@app.get('/contracts/all')
async def root(db : Session = Depends(get_db)):
    service = ContractService(db)
    return service.get_all()

@app.get('/contracts')
async def root(servant_id : int, master_id: int, db : Session = Depends(get_db)):
    service = ContractService(db)
    service.get(servant_id, master_id)

@app.post('/contracts')
async def root(contract : ContractCreate, db : Session = Depends(get_db)):
    service = ContractService(db)
    try:
        new_contract = service.create(contract)
        return {f"created contract between servant {contract.servant_id} and master {contract.master_id}": new_contract}
    except ValueError as e:
        raise HTTPException(400, str(e))
        

# @app.delete('/contracts/')
# async def root(servant_id : int, master_id: int, db : Session = Depends(get_db)):
#     service = ContractService(db)
#     service.delete(servant_id, master_id)
    


    

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

@app.post("/servants/{servant_id}/pictures/")
async def add_servant_picture(servant_id: int, grade: int = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    service = ServantService(db)
    servant = service.get(servant_id)
    if not servant:
        raise HTTPException(status_code=404, detail="Servant not found")

    picture_path = MEDIA_DIR / str(servant_id) / f'asc{grade}{Path(file.filename).suffix}'
    
    
    try:
        saved_path = save_file_to_disk(file, picture_path)
        picture : ServantPicture = service.add_picture(servant_id, grade, saved_path)
        return {"id": picture.servant_id, "grade": picture.grade, "image": picture.picture}
    except Exception as e:
        raise e
        raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     # Путь к директории app
#     app_dir = os.path.join(current_dir, "app")

#     # Меняем текущую рабочую директорию на app
#     os.chdir(app_dir)

#     uvicorn.run("main:app", host="0.0.0.0", port=8000)