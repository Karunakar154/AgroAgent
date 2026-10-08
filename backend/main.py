import os
import uuid

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_farmer
)

from backend.database.memory_db import (
    create_farmer,
    get_farmer,
    get_farmer_by_email,
    create_farm,
    get_farm,
    get_farmer_farms,
    get_farmer_conversations,
    initialize_database
)

from backend.agent.graph import agro_agent

from backend.agent.memory import (
    save_conversation,
    get_conversation
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="AgroAgent API",
    description="Autonomous AI Agriculture Assistant",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATABASE
# ============================================================

initialize_database()


# ============================================================
# REQUEST MODELS
# ============================================================

class FarmerCreate(BaseModel):
    name: str
    phone: str | None = None
    email: str | None = None


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    phone: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class FarmCreate(BaseModel):
    farmer_id: int
    farm_name: str
    latitude: float
    longitude: float


class ChatRequest(BaseModel):
    session_id: str
    farmer_id: int
    farm_id: int | None = None
    query: str
    latitude: float | None = None
    longitude: float | None = None


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "AgroAgent API is running"
    }


# ============================================================
# REGISTER
# ============================================================

@app.post("/register")
def register(request: RegisterRequest):

    existing_farmer = get_farmer_by_email(
        request.email
    )

    if existing_farmer:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    password_hash = hash_password(
        request.password
    )

    farmer_id = create_farmer(
        name=request.name,
        phone=request.phone,
        email=request.email,
        password_hash=password_hash
    )

    return {
        "message": "Farmer registered successfully",
        "farmer_id": farmer_id
    }


# ============================================================
# LOGIN
# ============================================================

@app.post("/login")
def login(request: LoginRequest):

    farmer = get_farmer_by_email(
        request.email
    )

    if not farmer:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_hash = farmer.get(
        "password_hash"
    )

    if not password_hash:
        raise HTTPException(
            status_code=401,
            detail="Account does not have a password"
        )

    password_valid = verify_password(
        request.password,
        password_hash
    )

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        farmer["farmer_id"]
    )

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "farmer_id": farmer["farmer_id"],
        "name": farmer["name"],
        "email": farmer["email"]
    }


# ============================================================
# CREATE FARMER
# ============================================================

@app.post("/farmers")
def create_farmer_endpoint(
    farmer: FarmerCreate
):

    farmer_id = create_farmer(
        name=farmer.name,
        phone=farmer.phone,
        email=farmer.email
    )

    return {
        "message": "Farmer created successfully",
        "farmer_id": farmer_id
    }


# ============================================================
# GET FARMER
# ============================================================

@app.get("/farmers/{farmer_id}")
def get_farmer_endpoint(
    farmer_id: int,
    current_farmer_id: int = Depends(get_current_farmer)
):

    if farmer_id != current_farmer_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot access another farmer's data"
        )

    farmer = get_farmer(
        farmer_id
    )

    if not farmer:
        raise HTTPException(
            status_code=404,
            detail="Farmer not found"
        )

    return farmer


# ============================================================
# CREATE FARM
# ============================================================

@app.post("/farms")
def create_farm_endpoint(
    farm: FarmCreate,
    current_farmer_id: int = Depends(get_current_farmer)
):

    if farm.farmer_id != current_farmer_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot create a farm for another farmer"
        )

    farm_id = create_farm(
        farmer_id=farm.farmer_id,
        farm_name=farm.farm_name,
        latitude=farm.latitude,
        longitude=farm.longitude
    )

    return {
        "message": "Farm created successfully",
        "farm_id": farm_id
    }


# ============================================================
# GET FARM
# ============================================================

@app.get("/farms/{farm_id}")
def get_farm_endpoint(
    farm_id: int,
    current_farmer_id: int = Depends(get_current_farmer)
):

    farm = get_farm(
        farm_id
    )

    if not farm:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    if farm["farmer_id"] != current_farmer_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot access another farmer's farm"
        )

    return farm


# ============================================================
# GET ALL FARMS OF FARMER
# ============================================================

@app.get("/farmers/{farmer_id}/farms")
def get_farmer_farms_endpoint(
    farmer_id: int,
    current_farmer_id: int = Depends(get_current_farmer)
):

    if farmer_id != current_farmer_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot access another farmer's farms"
        )

    return get_farmer_farms(
        farmer_id
    )


# ============================================================
# GET FARMER CONVERSATIONS
# ============================================================

@app.get("/farmers/{farmer_id}/conversations")
def get_farmer_conversations_endpoint(
    farmer_id: int,
    current_farmer_id: int = Depends(get_current_farmer)
):

    if farmer_id != current_farmer_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot access another farmer's conversations"
        )

    return get_farmer_conversations(
        farmer_id
    )


# ============================================================
# CHAT
# ============================================================

@app.post("/chat")
def chat(
    request: ChatRequest,
    current_farmer_id: int = Depends(get_current_farmer)
):

    # --------------------------------------------------------
    # SECURITY CHECK
    # --------------------------------------------------------

    if request.farmer_id != current_farmer_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot access another farmer's data"
        )

    # --------------------------------------------------------
    # DEFAULT VALUES
    # --------------------------------------------------------

    image_path = ""

    latitude = request.latitude
    longitude = request.longitude

    selected_farm_id = request.farm_id

    # --------------------------------------------------------
    # IF FARM ID IS PROVIDED
    # --------------------------------------------------------

    if selected_farm_id is not None:

        farm = get_farm(
            selected_farm_id
        )

        if not farm:
            raise HTTPException(
                status_code=404,
                detail="Farm not found"
            )

        if farm["farmer_id"] != current_farmer_id:
            raise HTTPException(
                status_code=403,
                detail="You cannot access another farmer's farm"
            )

        latitude = farm["latitude"]
        longitude = farm["longitude"]

    # --------------------------------------------------------
    # IF FARM ID IS NOT PROVIDED
    # AUTOMATICALLY SELECT FIRST FARM
    # --------------------------------------------------------

    else:

        farms = get_farmer_farms(
            current_farmer_id
        )

        if farms:

            farm = farms[0]

            selected_farm_id = farm["farm_id"]

            latitude = farm["latitude"]
            longitude = farm["longitude"]

    # --------------------------------------------------------
    # PRINT FARM INFORMATION
    # --------------------------------------------------------

    print("\n==============================")
    print("SELECTED FARM")
    print("==============================")

    print(
        "Farmer ID:",
        current_farmer_id
    )

    print(
        "Farm ID:",
        selected_farm_id
    )

    print(
        "Latitude:",
        latitude
    )

    print(
        "Longitude:",
        longitude
    )

    print("==============================\n")

    # --------------------------------------------------------
    # GET PREVIOUS MEMORY
    # --------------------------------------------------------

    memory = get_conversation(
        request.session_id
    )

    if memory:

        farmer_context = memory.get(
            "farmer_context",
            {}
        )

    else:

        farmer_context = {}

    # --------------------------------------------------------
    # INITIAL AGENT STATE
    # --------------------------------------------------------

    initial_state = {

        "user_query": request.query,

        "image_path": image_path,

        "latitude": latitude,

        "longitude": longitude,

        "farmer_context": farmer_context,

        "plan": {},

        "tool_results": {},

        "verification": {},

        "final_answer": "",

        "retry_count": 0
    }

    # --------------------------------------------------------
    # RUN AGENT
    # --------------------------------------------------------

    result = agro_agent.invoke(
        initial_state
    )

    # --------------------------------------------------------
    # SAVE CONVERSATION
    # --------------------------------------------------------

    save_conversation(
        session_id=request.session_id,
        user_query=request.query,
        latitude=latitude,
        longitude=longitude,
        tool_results=result.get(
            "tool_results",
            {}
        ),
        farmer_id=current_farmer_id,
        farm_id=selected_farm_id
    )

    # --------------------------------------------------------
    # RETURN RESPONSE
    # --------------------------------------------------------

    return {

        "session_id":
        request.session_id,

        "farmer_id":
        current_farmer_id,

        "farm_id":
        selected_farm_id,

        "answer":
        result.get(
            "final_answer",
            ""
        ),

        "verification":
        result.get(
            "verification",
            {}
        ),

        "tool_results":
        result.get(
            "tool_results",
            {}
        )
    }


# ============================================================
# DISEASE DETECTION
# ============================================================

@app.post("/disease")
async def disease_detection(
    image: UploadFile = File(...),
    farmer_id: int = Form(...),
    current_farmer_id: int = Depends(get_current_farmer)
):

    # --------------------------------------------------------
    # SECURITY
    # --------------------------------------------------------

    if farmer_id != current_farmer_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot access another farmer's data"
        )

    # --------------------------------------------------------
    # CREATE UPLOAD DIRECTORY
    # --------------------------------------------------------

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    # --------------------------------------------------------
    # GET EXTENSION
    # --------------------------------------------------------

    file_extension = os.path.splitext(
        image.filename
    )[1]

    # --------------------------------------------------------
    # UNIQUE FILE NAME
    # --------------------------------------------------------

    filename = (
        f"{uuid.uuid4()}"
        f"{file_extension}"
    )

    image_path = os.path.join(
        "uploads",
        filename
    )

    # --------------------------------------------------------
    # SAVE IMAGE
    # --------------------------------------------------------

    contents = await image.read()

    with open(
        image_path,
        "wb"
    ) as file:

        file.write(contents)

    # --------------------------------------------------------
    # DISEASE MODEL
    # --------------------------------------------------------

    from backend.tools.disease_tool import (
        disease_detection_tool
    )

    result = disease_detection_tool(
        image_path
    )

    return result


# ============================================================
# GET CONVERSATION HISTORY
# ============================================================

@app.get("/history/{session_id}")
def history(
    session_id: str,
    current_farmer_id: int = Depends(get_current_farmer)
):

    conversation = get_conversation(
        session_id
    )

    if not conversation:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    stored_farmer_id = conversation.get(
        "farmer_id"
    )

    if stored_farmer_id is not None:

        if stored_farmer_id != current_farmer_id:

            raise HTTPException(
                status_code=403,
                detail="You cannot access another farmer's conversation"
            )

    return conversation