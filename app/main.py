import os
from pathlib import Path
from fastapi import FastAPI, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
import uvicorn
from .crud import *
from .database import SessionLocal, Base, get_db
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import *
from fastapi.middleware.cors import CORSMiddleware
from .utils import SKILL_DIR, save_file_to_disk, MEDIA_DIR
app = FastAPI()

origins = [
    "https://d0jzr844-3000.euw.devtunnels.ms",
    "https://velkorra.github.io",
    "http://localhost:3000",
    "http://localhost:8080",
    "https://1pqzvstl-3000.euw.devtunnels.ms/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.get('/sql')
# async def root():
#     a = engine.connect()
#     with open('queries/join.sql', encoding='utf-8') as f:
#         return str(a.execute(text(f.read())).fetchall())

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/summoned_servants", response_model=List[ServantMasterResponse])
async def root(db : Session = Depends(get_db)):
    service = ServantService(db)
    query = service.get_summoned_servants()
    response = [
            ServantMasterResponse(
                servant_name=row.servant_name,
                localization_name=row.localization_name,
                master_nickname=row.master_nickname
            )
            for row in query
        ]
        
    return response

@app.get("/top_servants", response_model=List[TopServantResponse])
def root(db : Session = Depends(get_db)):
    service = ServantService(db)
    return service.get_top_servants()

@app.get("/female_servants_descriptions", response_model=List[ServantDescriptionResponse])
def get_female_servants_descriptions(db : Session = Depends(get_db)):
    service = ServantService(db)
    query = service.get_female_servants()
    response = [
            ServantDescriptionResponse(
                servant_name=row.servant_name,
                language=row.language,
                description=row.description
            )
            for row in query
        ]
        
    return response
@app.get('/level_analys', response_model=list[ClassLevelStats])
async def root(db : Session = Depends(get_db)):
    service = ServantService(db)
    results = service.get_level_analys()
    

        # Преобразование результатов в список словарей
    class_stats = [
        ClassLevelStats(
            class_name=row.class_name,
            max_level=row.max_level,
            min_level=row.min_level,
            avg_level=float(row.avg_level)  # Преобразование в float для корректной сериализации
        )
        for row in results
    ]
        
    return class_stats
    quit()
    


# Servants API -----------------------------------------------------
@app.get('/servants', response_model=List[ServantResponse])
async def get_all_servants(db: AsyncSession = Depends(get_db)):
    service = ServantService(db)
    servants = await service.get_all()
    return list(map(ServantResponse.model_validate, servants))

@app.get('/servants_list')
async def get_servant_list(db: AsyncSession = Depends(get_db)):
    service = ServantService(db)
    servants = await service.get_servant_list()
    return servants

@app.get('/servants')
async def get_all_servants(db: AsyncSession = Depends(get_db)):
    service = ServantService(db)
    servants = await service.get_all()
    return servants


@app.get('/servants/{servant_id}')
async def get_servant(servant_id: int, db: Session = Depends(get_db)):
    service = ServantService(db)
    servant = await service.get(servant_id)
    return servant


@app.post('/servants')
async def create_servant(servant: ServantCreate, db: Session = Depends(get_db)):
    service = ServantService(db)
    try:
        servant = service.create(servant)
        return {"message": f"Created {servant}", "id": servant.id}
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.put('/servants/{servant_id}')
async def update_servant(servant_id: int, name: str = Form(...), alignment: str = Form(...), class_name: str = Form(...), gender: str = Form(...), db: Session = Depends(get_db)):
    service = ServantService(db)
    try:
        servant = service.update(servant_id, ServantUpdate(name=name, alignment=alignment, class_name=class_name, gender=gender))
        return {"message": f'Updated {servant}'}
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.delete("/servants/{servant_id}")
async def delete_servant(servant_id: int, db: Session = Depends(get_db)):
    s = ServantService(db)
    try:
        s.delete(servant_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@app.get("/name/{servant_id}/{language}")
async def get_servant_name(servant_id: int, language: str, db: Session = Depends(get_db)):
    service = ServantService(db)
    name = await service.get_name(servant_id, language)
    if name:
        return {"name": name}
    return "None"


# Masters API -----------------------------------------------------

@app.get('/masters')
async def root(db : Session = Depends(get_db)):
    service = MasterService(db)
    return await service.get_all()

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
async def root(master_id: int, nickname : str = Form(...), level : int = Form(...), display_name : str = Form(...), db : Session = Depends(get_db)):
    service = MasterService(db)
    try:
        m = service.update(master_id, MasterUpdate(nickname=nickname, display_name=display_name, level=level))
        return f"updated {m}"
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.get('/masters/{master_id}/active_count')
async def root(master_id: int, db : Session = Depends(get_db)):
    service = MasterService(db)
    return {"count" : await service.get_active_contracts_count(master_id)}



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

@app.get('/all_localization', response_model=list[ServantLocalizationResponse])
def root(db : Session = Depends(get_db)):
    service = ServantService(db)
    query = service.get_localizaions()
    servant_dict = {}
    response = [
            ServantLocalizationResponse(
                servant_name=row[0],
                localization_language=row[1],
                localization_name=row[2],
                localization_description=row[3]
            )
            for row in query
        ]
    
    return response


@app.delete('/contracts')
async def root(servant_id : int, master_id: int, db : Session = Depends(get_db)):
    service = ContractService(db)
    service.delete(servant_id, master_id)
    
@app.get("/np/all")
async def root(db : Session = Depends(get_db)):
    service = ServantService(db)
    return await service.get_all_np()

@app.put("/np")
async def updateNP(noble_phantasm : NoblePhantasmUpdate, db : Session = Depends(get_db)):
    service = ServantService(db)
    service.update_np(np=noble_phantasm)

@app.post("/np")
async def updateNP(noble_phantasm : NoblePhantasmUpdate, db : Session = Depends(get_db)):
    service = ServantService(db)
    service.create_np(np=noble_phantasm)



@app.get('/localization/{servant_id}')
async def root(servant_id : int, language : str, db : Session = Depends(get_db)):
    service = ServantService(db)
    # if index == None:
    #     return [master for master in service.get_details(servant_id)]
    result = await service.get_localizaion(servant_id, language)
    return result

@app.get('/localization')
async def root(servant_id : int = None, db : Session = Depends(get_db)):
    service = ServantService(db)
    # if index == None:
    #     return [master for master in service.get_details(servant_id)]
    return service.join(servant_id)

@app.get('/skill/{servant_id}')
async def root(servant_id : int = None, db : Session = Depends(get_db)):
    service = ServantService(db)
    return service.get_skills(servant_id)
@app.delete('/skills/{id}')
async def root(id : int = None, db : Session = Depends(get_db)):
    service = ServantService(db)
    return service.delete_skill(id)
@app.get('/skills')
async def root(db : Session = Depends(get_db)):
    service = ServantService(db)

    return service.get_all_skills()

@app.post('/skills')
async def root(skill : SkillSchema, db : Session = Depends(get_db)):
    service = ServantService(db)

    return service.create_skill(skill)

@app.put('/skills')
async def root(skill : SkillSchema, db : Session = Depends(get_db)):
    service = ServantService(db)

    return service.update_skill(skill)

@app.get("/skill_picture/{id}")
async def get_image(id : int, db: Session = Depends(get_db)):
    service = ServantService(db)
    try:
        image_path = service.get_skill_icon(id)
        return FileResponse(image_path, media_type=get_mime_type(image_path))
    
    except ValueError as e:

        raise HTTPException(404, str(e))

@app.post("/add_skill_picture/{id}")
async def root(id : int, file : UploadFile = File(...), db : Session = Depends(get_db)):
    service = ServantService(db)

    picture_path = SKILL_DIR / f'skill_{id}_icon{Path(file.filename).suffix}'
    saved_path = save_file_to_disk(file, picture_path)
    service.add_skill_picture(id, saved_path)
    message = {"message" : "success"}
    return message
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
@app.post("/add_image/{servant_id}")
async def add_image(servant_id : int, file : UploadFile = File(...), db: Session = Depends(get_db)):
    service = ServantService(db)
    servant = service.get(servant_id)
    
    picture_path = MEDIA_DIR / str(servant.id) / f'asc{"1"}{Path(file.filename).suffix}'
    saved_path = save_file_to_disk(file, picture_path)
    picture : ServantPicture = service.add_picture(servant.id, 1, saved_path)
    message = {"id": picture.servant_id, "grade": picture.grade, "image": picture.picture}
    return message
@app.get("/get_image")
async def get_image(servant_id : int, grade: int, db: Session = Depends(get_db)):
    service = ServantService(db)
    try:
        image_path = await service.get_picture(servant_id, grade)
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
@app.put("/localization")
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
    service.update_localization(language = language,
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
    
