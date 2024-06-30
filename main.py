import os
from pathlib import Path
from fastapi import FastAPI, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
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
        
        return {"message": f"Created {servant}", "id": servant.id}
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

@app.get("/name/{servant_id}/{language}")
async def root(servant_id : int, language : str, db : Session = Depends(get_db)):
    service = ServantService(db)
    name = service.get_name(servant_id, language)
    if name:
        return {"name": name}
    return "None"


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
async def root(nickname : str = Form(...), display_name : str = Form(...), db : Session = Depends(get_db)):
    service = MasterService(db)
    try:
        m = service.create(MasterCreate(nickname=nickname, display_name=display_name))
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

@app.get('/masters/{master_id}/active_count')
async def root(master_id: int, db : Session = Depends(get_db)):
    service = MasterService(db)
    return {"count" : service.get_active_contracts_count(master_id)}



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
async def root(servant_id : int, language : str, db : Session = Depends(get_db)):
    service = ServantService(db)
    # if index == None:
    #     return [master for master in service.get_details(servant_id)]
    return service.get_localizaion(servant_id, language)

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

# @app.post('/localization')
# async def root(servant_id : int = None, db : Session = Depends(get_db)):
#     service = ServantService(db)
#     service.add_localization()


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
        raise HTTPException(status_code=500, detail=str(e))

# @app.post("/servants_new")
# async def add_servant(servant : ServantWithPicture, db: Session = Depends(get_db)):
@app.post("/servants_new")
async def add_servant(name: str = Form(...),
                      class_name: str = Form(...),
                      gender: str = Form(...),
                      alignment: str = Form(...),
                      file: UploadFile = File(...),
                      db: Session = Depends(get_db)):
    service = ServantService(db)
    message : str
    try:
        new_servant = service.create(ServantCreate(name=name, class_name=class_name, gender=gender, alignment=alignment))
        picture_path = MEDIA_DIR / str(new_servant.id) / f'asc{"1"}{Path(file.filename).suffix}'
    
        try:
            saved_path = save_file_to_disk(file, picture_path)
            picture : ServantPicture = service.add_picture(new_servant.id, 1, saved_path)
            message = {"id": picture.servant_id, "grade": picture.grade, "image": picture.picture}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        return {"message": f"Created {new_servant}", "message2": message, "id": new_servant.id}
    except ValueError as e:
        raise HTTPException(400, str(e))
    
@app.get("/get_image/")
async def get_image(servant_id : int, grade: int, db: Session = Depends(get_db)):
    service = ServantService(db)
    try:
        image_path = service.get_picture(servant_id, grade)
        return FileResponse(image_path, media_type=get_mime_type(image_path))
    
    except ValueError as e:

        raise HTTPException(404, str(e))

@app.post("/localization")
async def root(
            servant_id : int,
            language : str,
            name: str = Form(...),
            description: str = Form(...),
            history: str = Form(...),
            prototype_person: str = Form(...),
            illustrator: str = Form(...),
            voice_actor: str = Form(...),
            temper: str = Form(...),
            intro: str = Form(...),
            db: Session = Depends(get_db)):

    service = ServantService(db)
    service.add_localization(language = language,
                            servant_id=servant_id,
                            name = name,
                            description = description,
                            history = history,
                            prototype_person = prototype_person,
                            illustrator = illustrator,
                            voice_actor = voice_actor,
                            temper = temper,
                            intro = intro)



def get_mime_type(file_path: str) -> str:
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == '.jpg' or ext == '.jpeg':
        return 'image/jpeg'
    elif ext == '.png':
        return 'image/png'
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")