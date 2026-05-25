import io
import os
import urllib.request
import numpy as np
import cv2
import mediapipe as mp

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

router = APIRouter(prefix="/api/ia", tags=["ia"])

# ─── Mapeo: procedimiento → partes del cuerpo que debe mostrar la foto ────────
PROCEDIMIENTO_PARTES = {
    "Liposucción":          ["Tronco / Abdomen", "Piernas"],
    "Aumento mamario":      ["Tronco / Abdomen"],
    "Cirugía de párpados":  ["Rostro"],
    "Aumento de glúteos":   ["Piernas", "Espalda"],
    "Abdominoplastia":      ["Tronco / Abdomen"],
}

# ─── Modelo MediaPipe ─────────────────────────────────────────────────────────
MODELO_PATH = "pose_landmarker_heavy.task"
MODELO_URL  = (
    "https://storage.googleapis.com/mediapipe-models/"
    "pose_landmarker/pose_landmarker_heavy/float16/latest/"
    "pose_landmarker_heavy.task"
)

_detector = None

def get_detector():
    global _detector
    if _detector is None:
        if not os.path.exists(MODELO_PATH):
            print("Descargando modelo MediaPipe...")
            urllib.request.urlretrieve(MODELO_URL, MODELO_PATH)
            print("Modelo descargado.")
        base_options = python.BaseOptions(model_asset_path=MODELO_PATH)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            num_poses=1,
        )
        _detector = vision.PoseLandmarker.create_from_options(options)
        print("Detector IA listo.")
    return _detector


# ─── Función de detección ─────────────────────────────────────────────────────
def detectar_partes(imagen_bytes: bytes) -> dict:
    nparr = np.frombuffer(imagen_bytes, np.uint8)
    imagen_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if imagen_bgr is None:
        return {"partes_detectadas": [], "confianza": {}}

    imagen_rgb = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=imagen_rgb
    )

    resultados = get_detector().detect(mp_image)

    if not resultados.pose_landmarks:
        return {"partes_detectadas": [], "confianza": {}}

    landmarks = resultados.pose_landmarks[0]

    def visible(i):
        return landmarks[i].visibility > 0.75

    UMBRAL_PUNTOS  = 0.60
    UMBRAL_BRAZOS  = 0.30

    puntos_cara_frontal   = [1, 2, 3, 4, 5, 6]
    puntos_cabeza_general = [0, 7, 8, 9, 10]
    puntos_hombros_caderas = [11, 12, 23, 24]

    cara_frontal_visible = any(visible(i) for i in puntos_cara_frontal)
    cabeza_visible       = any(visible(i) for i in puntos_cabeza_general)
    hombros_visibles     = sum(1 for i in puntos_hombros_caderas if visible(i))
    es_espalda           = hombros_visibles >= 2 and not cara_frontal_visible

    grupos = {
        "Brazos":           [11, 12, 13, 14, 15, 16],
        "Tronco / Abdomen": [11, 12, 23, 24],
        "Piernas":          [23, 24, 25, 26, 27, 28, 29, 30, 31, 32],
    }

    partes_detectadas = []
    confianza = {}

    for parte, indices in grupos.items():
        if parte == "Brazos":
            pv = [landmarks[i].visibility for i in indices
                  if landmarks[i].visibility > 0.50]
            umbral = UMBRAL_BRAZOS
        else:
            pv = [landmarks[i].visibility for i in indices if visible(i)]
            umbral = UMBRAL_PUNTOS

        if len(pv) / len(indices) >= umbral:
            partes_detectadas.append(parte)
            confianza[parte] = round(sum(pv) / len(pv) * 100, 1)

    if cara_frontal_visible:
        todos_rostro = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        vr = [landmarks[i].visibility for i in todos_rostro if visible(i)]
        partes_detectadas.append("Rostro")
        confianza["Rostro"] = round(sum(vr) / len(vr) * 100, 1)
    elif cabeza_visible:
        vc = [landmarks[i].visibility for i in puntos_cabeza_general if visible(i)]
        partes_detectadas.append("Cabeza (vista trasera)")
        confianza["Cabeza (vista trasera)"] = round(sum(vc) / len(vc) * 100, 1)

    if es_espalda:
        ve = [landmarks[i].visibility for i in puntos_hombros_caderas if visible(i)]
        partes_detectadas.append("Espalda")
        confianza["Espalda"] = round(sum(ve) / len(ve) * 100, 1)
        if "Tronco / Abdomen" in partes_detectadas:
            partes_detectadas.remove("Tronco / Abdomen")
            confianza.pop("Tronco / Abdomen", None)

    return {"partes_detectadas": partes_detectadas, "confianza": confianza}


# ─── Endpoint ─────────────────────────────────────────────────────────────────
@router.post(
    "/verificar-imagen",
    summary="Verifica que la imagen corresponde al procedimiento seleccionado",
)
async def verificar_imagen(
    imagen: UploadFile = File(...),
    procedimiento: str = "",
):
    if not imagen.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen.")

    imagen_bytes = await imagen.read()

    resultado = detectar_partes(imagen_bytes)
    partes    = resultado["partes_detectadas"]
    confianza = resultado["confianza"]

    partes_requeridas = PROCEDIMIENTO_PARTES.get(procedimiento, [])

    if not partes:
        return JSONResponse({
            "partes_detectadas": [],
            "confianza": {},
            "aprobada": False,
            "mensaje": (
                "No detectamos ninguna parte del cuerpo en la imagen. "
                "Por favor suba una foto clara con buena iluminación."
            ),
        })

    if not partes_requeridas:
        return JSONResponse({
            "partes_detectadas": partes,
            "confianza": confianza,
            "aprobada": True,
            "mensaje": f"Partes detectadas: {', '.join(partes)}.",
        })

    partes_encontradas = [p for p in partes_requeridas if p in partes]

    if partes_encontradas:
        return JSONResponse({
            "partes_detectadas": partes,
            "confianza": confianza,
            "aprobada": True,
            "mensaje": (
                f"Imagen válida. Se detectó: {', '.join(partes_encontradas)}."
            ),
        })
    else:
        return JSONResponse({
            "partes_detectadas": partes,
            "confianza": confianza,
            "aprobada": False,
            "mensaje": (
                f"La imagen no corresponde al procedimiento '{procedimiento}'. "
                f"Por favor suba una foto de: {', '.join(partes_requeridas)}."
            ),
        })