from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import ALLOWED_ORIGINS
from routes.auth import router as auth_router
from routes.users import router as users_router
from routes.swipe import router as swipe_router
from routes.matches import router as matches_router

app = FastAPI(title="Lobby API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(swipe_router, prefix="/api")
app.include_router(matches_router, prefix="/api")

@app.get("/api/health")
async def health():
    return {"status": "ok", "app": "Lobby"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
