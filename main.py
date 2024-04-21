from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from ops import convert_to_tik_tok

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/upload")
async def upload_video_clips(
    effect: Optional[str] = Form(None),
    clips: List[UploadFile] = File(...),
    audio: Optional[UploadFile] = File(None),
):
    video_url = await convert_to_tik_tok(clips, audio, effect)
    return {"upload": video_url}
