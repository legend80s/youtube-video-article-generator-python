from typing import Annotated

from fastapi import HTTPException, Query, APIRouter, status
from sqlmodel import Field, SQLModel, select

from app.core.database import SessionDep


router = APIRouter(prefix="/heroes", tags=["heroes"])


# 1 create table mode
class HeroBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)


# 2 create table mode In SQLModel, any model class that has table=True is a table model.
class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    secret_name: str


# 3 create a HeroPublic model, this is the one that will be returned to the clients of the API.
class HeroPublic(HeroBase):
    id: int


# 请求模型（API 输入）
class HeroCreate(SQLModel):
    name: str
    secret_name: str
    age: int | None = None

    def toSQlModel(self) -> Hero:
        return Hero(name=self.name, age=self.age, secret_name=self.secret_name)


@router.post("", response_model=HeroPublic, status_code=status.HTTP_201_CREATED)
async def create_hero(heroCreate: HeroCreate, session: SessionDep) -> HeroPublic:
    print(f"{heroCreate=}")
    hero = heroCreate.toSQlModel()
    print(f"{hero=}")
    session.add(hero)
    await session.commit()
    await session.refresh(hero)

    return HeroPublic(id=hero.id, name=hero.name, age=hero.age)


@router.get("", response_model=list[HeroPublic])
async def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[HeroPublic]:
    result = await session.execute(select(Hero).offset(offset).limit(limit))

    heroes = result.scalars().all()

    return [HeroPublic.model_validate(hero) for hero in heroes]


@router.get("/{hero_id}", response_model=HeroPublic)
async def read_hero(hero_id: int, session: SessionDep) -> HeroPublic:
    hero = await session.get(Hero, hero_id)

    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    return HeroPublic.model_validate(hero)


@router.delete("/{hero_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hero(hero_id: int, session: SessionDep):
    hero: Hero | None = await session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    await session.delete(hero)
    await session.commit()
    return None
