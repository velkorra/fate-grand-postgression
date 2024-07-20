from sqlalchemy import and_, func
from sqlalchemy.future import select
from sqlalchemy.orm import Session, aliased, selectinload, load_only, joinedload, subqueryload
from sqlalchemy.exc import IntegrityError, DataError, InternalError
from sqlalchemy.ext.asyncio import AsyncSession
from psycopg2.errors import (
    CheckViolation,
    UniqueViolation,
    RaiseException,
    ForeignKeyViolation,
)
from .models import *
from .schemas import *


class ServantService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, id: int) -> Servant:
        query = (
            select(Servant)
            .options(selectinload(Servant.localizations))
            .where(Servant.id == id)
        )
        servant = await self.db.execute(query)
        return servant.scalars().first()

    async def get_all(self) -> List[Servant]:
        query = select(Servant)
        servants = (await self.db.execute(query)).scalars().all()
        return servants

    # async def get_servant_list(self, lang) -> List[ServantAndName]:
    #     query = (
    #         select(Servant)
    #         .options(
    #             load_only(
    #                 Servant.id,
    #                 Servant.class_name,
    #                 Servant.name,
    #                 Servant.ascension_level,
    #                 Servant.level,
    #                 Servant.state,
    #                 Servant.alignment,
    #                 Servant.gender,
    #             ),
    #             selectinload(Servant.localizations).load_only(
    #                 ServantLocalization.language, ServantLocalization.name
    #             ),
    #         )
    #         .where(Servant.localizations.any(language=lang))
    #     )
    #     servants = (await self.db.execute(query)).scalars().all()
    #     response = []
    #     for servant in servants:
    #         s = ServantAndName.model_validate(servant)
    #         for localization in servant.localizations:
    #             if localization.language == lang:
    #                 s.true_name = localization.name
    #         response.append(s)
    #     return response

    async def get_servant_list(self) -> List[ServantWithLocalization]:
        query = select(Servant).options(subqueryload(Servant.localizations)).order_by(Servant.id)
        servants = (await self.db.execute(query)).scalars().all()
        return list(map(ServantWithLocalization.model_validate, servants))
            


    async def get_details(self, id: int):
        servant = await self.get(id)
        localizations: List[ServantLocalization] = await self.get_localizaion(
            servant.id
        )
        return {localization.language: localization for localization in localizations}

    async def get_name(self, servant_id, language):
        localization = await self.get_localizaion(servant_id, language)
        if type(localization) is ServantLocalization:
            return localization.name
        return "none"

    def get_aliases():
        pass

    def get_full_servant(self, id: int):
        servant = self.get(id)
        localizations = self.get_details(id)

    async def add_localization(
        self,
        language: str,
        servant_id: str,
        name: str = None,
        description: str = None,
        history: str = None,
        prototype_person: str = None,
        illustrator: str = None,
        voice_actor: str = None,
        temper: str = None,
        intro: str = None,
    ):
        details = ServantLocalization(
            language=language,
            name=name,
            description=description,
            history=history,
            prototype_person=prototype_person,
            illustrator=illustrator,
            voice_actor=voice_actor,
            temper=temper,
            intro=intro,
        )
        s = await self.get(servant_id)
        s.localizations.append(details)
        await self.db.commit()

    async def update_localization(
        self,
        language: str,
        servant_id: str,
        name: str = None,
        description: str = None,
        history: str = None,
        prototype_person: str = None,
        illustrator: str = None,
        voice_actor: str = None,
        temper: str = None,
        intro: str = None,
    ):
        query = select(ServantLocalization).where(
            (ServantLocalization.servant_id == servant_id) &
            (ServantLocalization.language == language)
        )
        details = (await self.db.execute(query)).scalars().first()
        dd = True
        if not details:
            dd = details
            details = ServantLocalization()
        if language:
            details.language = language
        if name:
            details.name = name
        if description:
            details.description = description
        if history:
            details.history = history
        if prototype_person:
            details.prototype_person = prototype_person
        if illustrator:
            details.illustrator = illustrator
        if voice_actor:
            details.voice_actor = voice_actor
        if temper:
            details.temper = temper
        if intro:
            details.intro = intro
        if not dd:
            details.servant_id = servant_id
            self.db.add(details)
        await self.db.commit()

    async def get_localizaion(self, servant_id: int, language: str):
        servant = await self.get(servant_id)
        for localization in servant.localizations:
            if localization.language == language:
                return localization
        if servant.localizations:
            return servant.localizations[0]
        return {"this servant has no info"}

    async def get_all_np(self):
        query = select(NoblePhantasm)
        np_list = (await self.db.execute(query)).scalars().all()
        return np_list

    def update_np(self, np: NoblePhantasmUpdate):
        updated_np: NoblePhantasm = self.db.query(NoblePhantasm).get(np.servant_id)
        updated_np.activation_type = np.activation_type
        updated_np.description = np.description
        updated_np.name = np.name
        updated_np.rank = np.rank
        self.db.commit()

    def create_np(self, np: NoblePhantasmUpdate):
        new_np = NoblePhantasm(
            servant_id=np.servant_id,
            activation_type=np.activation_type,
            description=np.description,
            name=np.name,
            rank=np.rank,
        )
        self.db.add(new_np)
        self.db.commit()

    def update_skill(self, skill: SkillSchema):
        updated_skill: Skill = self.db.query(Skill).get(skill.id)
        updated_skill.name = skill.name
        updated_skill.description = skill.description
        updated_skill.rank = skill.rank
        updated_skill.skill_type = skill.skill_type
        self.db.commit()

    def create_skill(self, skill: SkillSchema):
        new_skill = Skill(
            name=skill.name,
            description=skill.description,
            rank=skill.rank,
            skill_type=skill.skill_type,
        )
        self.db.add(new_skill)
        self.db.commit()

    def create(self, servant: ServantCreate) -> Servant:
        servant = Servant(
            name=servant.name,
            class_name=servant.class_name,
            alignment=servant.alignment,
            gender=servant.gender,
        )
        try:
            self.db.add(servant)
            self.db.commit()
            self.db.refresh(servant)
            return servant
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(str(e))
        except DataError as e:
            self.db.rollback()
            raise ValueError("Invalid data: " + str(e.orig)) from e

    def update(self, id: int, s: ServantUpdate):
        servant = self.get(id)
        if s.name:
            servant.name = s.name
        if s.class_name:
            servant.class_name = s.class_name
        if s.ascension_level:
            servant.ascension_level = s.ascension_level
        if s.level:
            servant.level = s.level
        if s.alignment:
            servant.alignment = s.alignment
        if s.gender:
            servant.gender = s.gender
        try:
            self.db.commit()
            self.db.refresh(servant)
            return servant
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(str(e))
        except Exception as e:
            self.db.rollback()
            raise ValueError(str(e))

    def delete(self, id: int):
        servant = self.get(id)
        if servant:
            self.db.delete(servant)
            self.db.commit()
        else:
            raise ValueError("Servant does not exist")


    def get_localizaions(self):
        return (
            self.db.query(
                Servant.name,
                ServantLocalization.language,
                ServantLocalization.name,
                ServantLocalization.description,
            )
            .join(ServantLocalization)
            .filter(ServantLocalization.language.in_(["ru", "en"]))
            .all()
        )


    def get_skills(self, id: int):
        servant = self.get(id)
        return servant.skills

    def get_skill(self, id: int) -> Skill:
        return self.db.query(Skill).get(id)

    def get_all_skills(self):
        return self.db.query(Skill).all()

    def delete_skill(self, id):
        skill = self.db.query(Skill).get(id)
        self.db.delete(skill)
        self.db.commit()

    def add_skill_picture(self, id, path):
        skill: Skill = self.db.query(Skill).get(id)
        skill.icon = path
        self.db.commit()

    def get_skill_icon(self, id):
        skill: Skill = self.db.query(Skill).get(id)
        return skill.icon

    def add_picture(self, servant_id: int, grade: int, path: str):
        new_picture = ServantPicture(grade=1, picture=path)
        servant = self.get(servant_id)
        servant.pictures.append(new_picture)
        try:
            self.db.commit()
            return new_picture
        except Exception as e:
            raise e

    async def get_picture(self, servant_id: int, grade: int):
        sp = ServantPicture
        query = select(sp).where(sp.servant_id == servant_id, sp.grade == 1)
        result = await self.db.execute(query)
        picture = result.scalars().first()
        if picture:
            return picture.picture
        else:
            raise ValueError("no picture")

    def get_level_analys(self):
        return (
            self.db.query(
                Servant.class_name,
                func.max(Servant.level).label("max_level"),
                func.min(Servant.level).label("min_level"),
                func.avg(Servant.level).label("avg_level"),
            )
            .group_by(Servant.class_name)
            .all()
        )

    def get_summoned_servants(self):
        return (
            self.db.query(
                Servant.name.label("servant_name"),
                ServantLocalization.name.label("localization_name"),
                Master.nickname.label("master_nickname"),
            )
            .join(Contract, Servant.id == Contract.servant_id)
            .join(Master, Contract.master_id == Master.id)
            .join(ServantLocalization, Servant.id == ServantLocalization.servant_id)
            .filter(ServantLocalization.language == "ru")
            .all()
        )

    def get_female_servants(self):
        return (
            self.db.query(
                Servant.name.label("servant_name"),
                ServantLocalization.language.label("language"),
                ServantLocalization.description.label("description"),
            )
            .join(ServantLocalization)
            .filter(
                Servant.gender == "female",
                ServantLocalization.language.in_(["ru", "en"]),
            )
            .all()
        )

    def get_top_servants(self):
        stmt = (
            self.db.query(
                Contract.master_id,
                Servant.id.label("servant_id"),
                Servant.level,
                func.row_number()
                .over(partition_by=Contract.master_id, order_by=Servant.level.desc())
                .label("rank"),
            )
            .join(Servant, Servant.id == Contract.servant_id)
            .subquery()
        )

        query = (
            self.db.query(
                Master.nickname.label("master_nickname"),
                ServantLocalization.name.label("servant_name"),
                stmt.c.level.label("servant_level"),
            )
            .join(Master, stmt.c.master_id == Master.id)
            .join(
                ServantLocalization,
                and_(
                    stmt.c.servant_id == ServantLocalization.servant_id,
                    ServantLocalization.language == "en",
                ),
            )
            .filter(stmt.c.rank <= 3)
            .order_by(Master.nickname, stmt.c.rank)
            .all()
        )
        response = [
            TopServantResponse(
                master_nickname=row.master_nickname,
                servant_name=row.servant_name,
                servant_level=row.servant_level,
            )
            for row in query
        ]

        return response


class MasterService:
    def __init__(self, db: Session):
        self.db = db

    def get(self, id) -> Master | None:
        return self.db.query(Master).get(id)

    def get_all(self):
        return self.db.query(Master).all()

    def create(self, master: MasterCreate):
        new_master = Master(
            nickname=master.nickname,
            display_name=(
                master.display_name if master.display_name else master.nickname
            ),
        )
        self.db.add(new_master)
        try:
            self.db.commit()
            self.db.refresh(new_master)
            return new_master
        except IntegrityError as e:
            self.db.rollback()
            if isinstance(e.orig, UniqueViolation):
                raise ValueError("Master with this nickname already exists")

        except Exception as e:
            self.db.rollback()
            raise Exception(str(e))

    def update(self, id: int, master: MasterUpdate):
        m = self.get(id)
        if not m:
            raise ValueError("master does not exist")
        if master.nickname:
            m.nickname = master.nickname
        if master.level:
            m.level = master.level
        if master.display_name:
            m.display_name = master.display_name
        try:
            self.db.commit()
            self.db.refresh(m)
            return m
        except IntegrityError as e:
            self.db.rollback()
            if isinstance(e.orig, UniqueViolation):
                raise ValueError("Master with this nickname already exists")
            if isinstance(e.orig, CheckViolation):
                raise ValueError("Level must be positive")

    def delete(self, id: int):
        m = self.get(id)
        if not m:
            raise ValueError("master does not exist")
        self.db.delete(m)
        self.db.commit()

    def get_active_contracts_count(self, master_id):
        c = (
            self.db.query(Contract)
            .filter(Contract.master_id == master_id and Contract.status == "active")
            .all()
        )
        return len(c)


class ContractService:
    def __init__(self, db: Session):
        self.db = db

    def get(self, servant_id, master_id):
        return self.db.query(Contract).filter(
            Contract.servant_id == servant_id and Contract.master_id == master_id
        )

    def get_all(self):
        return self.db.query(Contract).all()

    def delete(self, servant_id, master_id):
        contract = (
            self.db.query(Contract)
            .filter(Contract.servant_id == servant_id, Contract.master_id == master_id)
            .first()
        )
        self.db.delete(contract)
        self.db.commit()

    def create(self, contract_create: ContractCreate):
        contract = Contract(
            servant_id=contract_create.servant_id, master_id=contract_create.master_id
        )
        self.db.add(contract)
        try:
            self.db.commit()
            self.db.refresh(contract)
            return contract
        except IntegrityError as e:
            self.db.rollback()
            if isinstance(e.orig, UniqueViolation):
                raise ValueError("Contract already exist")
            if isinstance(e.orig, ForeignKeyViolation):
                if "contract_master_id_fkey" in str(e):
                    raise ValueError("Master does not exist")
                else:
                    raise ValueError("Servant does not exist")
        except InternalError as e:
            self.db.rollback()
            if isinstance(e.orig, RaiseException):
                raise ValueError("Servant already has an active contract")
