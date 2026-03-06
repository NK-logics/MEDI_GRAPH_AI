from fastapi import APIRouter
from app.db.neo4j_driver import get_session

router = APIRouter()

@router.get("/db-test")
def test_db():

    session = get_session()

    result = session.run("RETURN 'Connected to Neo4j Cloud' AS message")

    return {"status": result.single()["message"]}