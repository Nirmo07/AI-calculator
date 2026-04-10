# from contextlib import asynccontextmanager
# from fastapi import FastAPI, APIRouter, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# import uvicorn
# from pydantic import BaseModel
# import google.generativeai as genai
# import ast
# import json
# from PIL import Image
# import base64
# from io import BytesIO
# from dotenv import load_dotenv
# import os
# import logging

# # Load environment variables
# load_dotenv()

# # Constants
# SERVER_URL = 'localhost'
# PORT = '8900'
# ENV = 'dev'
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# # Configure Gemini API
# genai.configure(api_key=GEMINI_API_KEY)

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Pydantic model for image data
# class ImageData(BaseModel):
#     image: str
#     dict_of_vars: dict

# # FastAPI app setup
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     yield

# app = FastAPI(lifespan=lifespan)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Root endpoint
# @app.get('/')
# async def root():
#     return {"message": "Server is running"}

# # Function to analyze image
# def analyze_image(img: Image, dict_of_vars: dict):
#     model = genai.GenerativeModel(model_name="gemini-1.5-flash")
#     dict_of_vars_str = json.dumps(dict_of_vars, ensure_ascii=False)
#     prompt = (
#         f"You have been given an image with some mathematical expressions, equations, or graphical problems, and you need to solve them. "
#         f"Note: Use the PEMDAS rule for solving mathematical expressions. PEMDAS stands for the Priority Order: Parentheses, Exponents, Multiplication and Division (from left to right), Addition and Subtraction (from left to right). Parentheses have the highest priority, followed by Exponents, then Multiplication and Division, and lastly Addition and Subtraction. "
#         f"For example: "
#         f"Q. 2 + 3 * 4 "
#         f"(3 * 4) => 12, 2 + 12 = 14. "
#         f"Q. 2 + 3 + 5 * 4 - 8 / 2 "
#         f"5 * 4 => 20, 8 / 2 => 4, 2 + 3 => 5, 5 + 20 => 25, 25 - 4 => 21. "
#         f"YOU CAN HAVE FIVE TYPES OF EQUATIONS/EXPRESSIONS IN THIS IMAGE, AND ONLY ONE CASE SHALL APPLY EVERY TIME: "
#         f"Following are the cases: "
#         f"1. Simple mathematical expressions like 2 + 2, 3 * 4, 5 / 6, 7 - 8, etc.: In this case, solve and return the answer in the format of a LIST OF ONE DICT [{{'expr': given expression, 'result': calculated answer}}]. "
#         f"2. Set of Equations like x^2 + 2x + 1 = 0, 3y + 4x = 0, 5x^2 + 6y + 7 = 12, etc.: In this case, solve for the given variable, and the format should be a COMMA SEPARATED LIST OF DICTS, with dict 1 as {{'expr': 'x', 'result': 2, 'assign': True}} and dict 2 as {{'expr': 'y', 'result': 5, 'assign': True}}. This example assumes x was calculated as 2, and y as 5. Include as many dicts as there are variables. "
#         f"3. Assigning values to variables like x = 4, y = 5, z = 6, etc.: In this case, assign values to variables and return another key in the dict called {{'assign': True}}, keeping the variable as 'expr' and the value as 'result' in the original dictionary. RETURN AS A LIST OF DICTS. "
#         f"4. Analyzing Graphical Math problems, which are word problems represented in drawing form, such as cars colliding, trigonometric problems, problems on the Pythagorean theorem, adding runs from a cricket wagon wheel, etc. These will have a drawing representing some scenario and accompanying information with the image. PAY CLOSE ATTENTION TO DIFFERENT COLORS FOR THESE PROBLEMS. You need to return the answer in the format of a LIST OF ONE DICT [{{'expr': given expression, 'result': calculated answer}}]. "
#         f"5. Detecting Abstract Concepts that a drawing might show, such as love, hate, jealousy, patriotism, or a historic reference to war, invention, discovery, quote, etc. USE THE SAME FORMAT AS OTHERS TO RETURN THE ANSWER, where 'expr' will be the explanation of the drawing, and 'result' will be the abstract concept. "
#         f"Analyze the equation or expression in this image and return the answer according to the given rules: "
#         f"Make sure to use extra backslashes for escape characters like \\f -> \\\\f, \\n -> \\\\n, etc. "
#         f"Here is a dictionary of user-assigned variables. If the given expression has any of these variables, use its actual value from this dictionary accordingly: {dict_of_vars_str}. "
#         f"DO NOT USE BACKTICKS OR MARKDOWN FORMATTING. "
#         f"PROPERLY QUOTE THE KEYS AND VALUES IN THE DICTIONARY FOR EASIER PARSING WITH Python's ast.literal_eval."
#     )
#     try:
#         response = model.generate_content([prompt, img])
#         logger.info(f"Gemini API response: {response.text}")
#         answers = []
#         try:
#             answers = ast.literal_eval(response.text)
#         except (ValueError, SyntaxError) as e:
#             logger.error(f"Error in parsing response from Gemini API: {e}")
#         logger.info(f"Returned answer: {answers}")
#         for answer in answers:
#             if 'assign' in answer:
#                 answer['assign'] = True
#             else:
#                 answer['assign'] = False
#         return answers
#     except Exception as e:
#         logger.error(f"Error in Gemini API call: {e}")
#         return []

# # Router setup
# router = APIRouter()

# @router.post('')
# async def run(data: ImageData):
#     try:
#         # Decode the base64 image
#         image_data = base64.b64decode(data.image.split(",")[1])  # Assumes data:image/png;base64,<data>
#         image_bytes = BytesIO(image_data)
#         image = Image.open(image_bytes)

#         # Check if the image is blank
#         if not image.getbbox():
#             logger.warning("The image is blank")
#             return {"message": "The image is blank", "data": [], "status": "error"}

#         # Analyze the image
#         responses = analyze_image(image, dict_of_vars=data.dict_of_vars)

#         # Prepare the response data
#         processed_data = []
#         if responses:
#             for response in responses:
#                 processed_data.append(response)
#             logger.info(f"Response in route: {processed_data}")
#         else:
#             logger.warning("No valid responses from Gemini API")

#         return {"message": "Image processed", "data": processed_data, "status": "success"}
#     except Exception as e:
#         logger.error(f"Error in /calculate route: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")

# app.include_router(router, prefix="/calculate", tags=["calculate"])

# if __name__ == "__main__":
#     uvicorn.run("main:app", host=SERVER_URL, port=int(PORT), reload=(ENV == "dev"))

from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import google.generativeai as genai
from PIL import Image
import base64
from io import BytesIO
from dotenv import load_dotenv
import os
import logging
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import ast
import json

# Load environment variables
load_dotenv()

# Constants
SERVER_URL = 'localhost'
PORT = '8900'
ENV = 'dev'
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
model = genai.GenerativeModel("gemini-1.5-flash")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Hand Detector
detector = HandDetector(staticMode=False, maxHands=1, detectionCon=0.7, minTrackCon=0.5)

# FastAPI app setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get('/')
async def root():
    return {"message": "Server is running"}

# Pydantic model for image data
class ImageData(BaseModel):
    image: str
    dict_of_vars: dict

# Function to analyze image
def analyze_image(img: Image, dict_of_vars: dict):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    dict_of_vars_str = json.dumps(dict_of_vars, ensure_ascii=False)
    prompt = (
        f"You have been given an image with some mathematical expressions, equations, or graphical problems, and you need to solve them. "
        f"Note: Use the PEMDAS rule for solving mathematical expressions. PEMDAS stands for the Priority Order: Parentheses, Exponents, Multiplication and Division (from left to right), Addition and Subtraction (from left to right). Parentheses have the highest priority, followed by Exponents, then Multiplication and Division, and lastly Addition and Subtraction. "
        f"For example: "
        f"Q. 2 + 3 * 4 "
        f"(3 * 4) => 12, 2 + 12 = 14. "
        f"Q. 2 + 3 + 5 * 4 - 8 / 2 "
        f"5 * 4 => 20, 8 / 2 => 4, 2 + 3 => 5, 5 + 20 => 25, 25 - 4 => 21. "
        f"YOU CAN HAVE FIVE TYPES OF EQUATIONS/EXPRESSIONS IN THIS IMAGE, AND ONLY ONE CASE SHALL APPLY EVERY TIME: "
        f"Following are the cases: "
        f"1. Simple mathematical expressions like 2 + 2, 3 * 4, 5 / 6, 7 - 8, etc.: In this case, solve and return the answer in the format of a LIST OF ONE DICT [{{'expr': given expression, 'result': calculated answer}}]. "
        f"2. Set of Equations like x^2 + 2x + 1 = 0, 3y + 4x = 0, 5x^2 + 6y + 7 = 12, etc.: In this case, solve for the given variable, and the format should be a COMMA SEPARATED LIST OF DICTS, with dict 1 as {{'expr': 'x', 'result': 2, 'assign': True}} and dict 2 as {{'expr': 'y', 'result': 5, 'assign': True}}. This example assumes x was calculated as 2, and y as 5. Include as many dicts as there are variables. "
        f"3. Assigning values to variables like x = 4, y = 5, z = 6, etc.: In this case, assign values to variables and return another key in the dict called {{'assign': True}}, keeping the variable as 'expr' and the value as 'result' in the original dictionary. RETURN AS A LIST OF DICTS. "
        f"4. Analyzing Graphical Math problems, which are word problems represented in drawing form, such as cars colliding, trigonometric problems, problems on the Pythagorean theorem, adding runs from a cricket wagon wheel, etc. These will have a drawing representing some scenario and accompanying information with the image. PAY CLOSE ATTENTION TO DIFFERENT COLORS FOR THESE PROBLEMS. You need to return the answer in the format of a LIST OF ONE DICT [{{'expr': given expression, 'result': calculated answer}}]. "
        f"5. Detecting Abstract Concepts that a drawing might show, such as love, hate, jealousy, patriotism, or a historic reference to war, invention, discovery, quote, etc. USE THE SAME FORMAT AS OTHERS TO RETURN THE ANSWER, where 'expr' will be the explanation of the drawing, and 'result' will be the abstract concept. "
        f"Analyze the equation or expression in this image and return the answer according to the given rules: "
        f"Make sure to use extra backslashes for escape characters like \\f -> \\\\f, \\n -> \\\\n, etc. "
        f"Here is a dictionary of user-assigned variables. If the given expression has any of these variables, use its actual value from this dictionary accordingly: {dict_of_vars_str}. "
        f"DO NOT USE BACKTICKS OR MARKDOWN FORMATTING. "
        f"PROPERLY QUOTE THE KEYS AND VALUES IN THE DICTIONARY FOR EASIER PARSING WITH Python's ast.literal_eval."
    )
    try:
        response = model.generate_content([prompt, img])
        logger.info(f"Gemini API response: {response.text}")
        answers = []
        try:
            answers = ast.literal_eval(response.text)
        except (ValueError, SyntaxError) as e:
            logger.error(f"Error in parsing response from Gemini API: {e}")
        logger.info(f"Returned answer: {answers}")
        for answer in answers:
            if 'assign' in answer:
                answer['assign'] = True
            else:
                answer['assign'] = False
        return answers
    except Exception as e:
        logger.error(f"Error in Gemini API call: {e}")
        return []

# Router setup
router = APIRouter()

@router.post('')
async def run(data: ImageData):
    try:
        # Decode the base64 image
        image_data = base64.b64decode(data.image.split(",")[1])  # Assumes data:image/png;base64,<data>
        image_bytes = BytesIO(image_data)
        image = Image.open(image_bytes)

        # Check if the image is blank
        if not image.getbbox():
            logger.warning("The image is blank")
            return {"message": "The image is blank", "data": [], "status": "error"}

        # Analyze the image
        responses = analyze_image(image, dict_of_vars=data.dict_of_vars)

        # Prepare the response data
        processed_data = []
        if responses:
            for response in responses:
                processed_data.append(response)
            logger.info(f"Response in route: {processed_data}")
        else:
            logger.warning("No valid responses from Gemini API")

        return {"message": "Image processed", "data": processed_data, "status": "success"}
    except Exception as e:
        logger.error(f"Error in /calculate route: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

app.include_router(router, prefix="/calculate", tags=["calculate"])

# WebSocket endpoint for hand tracking and drawing
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    canvas = np.zeros((720, 1280, 3), dtype=np.uint8)
    prev_pos = None
    sent_to_ai = False

    while True:
        success, img = cap.read()
        if not success:
            continue

        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, draw=True, flipType=True)

        if hands:
            hand1 = hands[0]
            fingers = detector.fingersUp(hand1)
            lmlist = hand1["lmList"]

            if fingers == [0, 1, 1, 0, 0]:  # Stop drawing
                prev_pos = None

            if fingers == [0, 1, 0, 0, 0]:  # Draw with index finger
                current_pos = tuple(map(int, lmlist[8][:2]))
                if prev_pos:
                    cv2.line(canvas, prev_pos, current_pos, (255, 0, 255), 10)
                prev_pos = current_pos

            if fingers == [0, 0, 0, 0, 1]:  # Erase canvas
                canvas = np.zeros((720, 1280, 3), dtype=np.uint8)

            if fingers == [0, 1, 1, 1, 0] and not sent_to_ai:  # Send to AI
                sent_to_ai = True
                pil_image = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
                response = model.generate_content(["Solve this Math Problem", pil_image])
                await websocket.send_text(response.text)

        image_combined = cv2.addWeighted(img, 0.7, canvas, 0.3, 0)
        _, buffer = cv2.imencode('.jpg', image_combined)
        await websocket.send_bytes(buffer.tobytes())

    cap.release()

if __name__ == "__main__":
    uvicorn.run("main:app", host=SERVER_URL, port=int(PORT), reload=(ENV == "dev"))