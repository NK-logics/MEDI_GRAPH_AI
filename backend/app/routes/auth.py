import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from neo4j.exceptions import ServiceUnavailable
from pydantic import BaseModel, EmailStr, Field

from app.core.auth_utils import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.neo4j_driver import get_session

router = APIRouter()
security = HTTPBearer()


class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str
    password: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


@router.post("/signup")
def signup(data: SignupRequest):
    clean_name = data.name.strip()
    if not clean_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Name cannot be empty",
        )

    user_id = str(uuid.uuid4())
    password_hash = hash_password(data.password)

    exists_query = """
    MATCH (u:User {email:$email})
    RETURN u
    LIMIT 1
    """

    create_query = """
    CREATE (u:User {
      id:$id,
      name:$name,
      email:$email,
      password_hash:$password_hash
    })
    """

    try:
        with get_session() as session:
            existing_user = session.run(exists_query, email=str(data.email)).single()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered",
                )

            session.run(
                create_query,
                id=user_id,
                name=clean_name,
                email=str(data.email),
                password_hash=password_hash,
            )
    except ServiceUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Neo4j is unavailable: {exc}",
        )

    return {"message": "User created"}


@router.post("/login")
def login(data: LoginRequest):
    query = """
    MATCH (u:User {email:$email})
    RETURN u
    """

    try:
        with get_session() as session:
            result = session.run(query, email=data.email).single()

            if not result:
                return {"error": "User not found"}

            user = result["u"]

            if not verify_password(data.password, user["password_hash"]):
                return {"error": "Wrong password"}

            token = create_access_token({"user_id": user["id"]})

            return {
                "access_token": token,
                "user_id": user["id"],
            }
    except ServiceUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Neo4j is unavailable: {exc}",
        )

@router.get("/me")
def get_me(user_id: str = Depends(get_current_user)):

    query = """
    MATCH (u:User {id:$user_id})
    RETURN u.name AS name
    """

    with get_session() as session:
        result = session.run(query, user_id=user_id).single()

        if not result:
            raise HTTPException(status_code=404, detail="User not found")

    return {
        "name": result["name"]
    }


@router.get("/graph")
def get_graph(user_id: str = Depends(get_current_user)):
    query = """
    MATCH (u:User {id:$user_id})-[r]->(n)
    RETURN u,r,n
    """

    nodes_by_id = {}
    edges_by_id = {}

    def node_id(node):
        return node.get("id") or node.element_id

    def node_label(node):
        if "name" in node and node.get("name"):
            return node.get("name")
        if "id" in node and node.get("id"):
            return str(node.get("id"))
        values = [v for v in node.values() if v is not None]
        if values:
            return str(values[0])
        labels = list(node.labels)
        return labels[0] if labels else "Node"

    try:
        with get_session() as session:
            result = session.run(query, user_id=user_id)

            for record in result:
                u = record["u"]
                r = record["r"]
                n = record["n"]

                u_id = node_id(u)
                n_id = node_id(n)

                nodes_by_id[u_id] = {"id": u_id, "label": node_label(u)}
                nodes_by_id[n_id] = {"id": n_id, "label": node_label(n)}

                rel_key = r.element_id
                edges_by_id[rel_key] = {
                    "from": u_id,
                    "to": n_id,
                    "label": r.type,
                }
    except ServiceUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Neo4j is unavailable: {exc}",
        )

    return {"nodes": list(nodes_by_id.values()), "edges": list(edges_by_id.values())}
