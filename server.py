import asyncio
import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import SecretStr

from langchain_writer import ChatWriter
from langchain_writer.tools import GraphTool

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the current directory
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_file = BASE_DIR / "docs" / "data" / "onboarding-neuro-chat.html"
    try:
        content = html_file.read_text(encoding="utf-8")
        return HTMLResponse(content=content, media_type="text/html")
    except FileNotFoundError:
        logger.error(f"HTML file not found at {html_file}")
        raise HTTPException(
            status_code=404, detail=f"HTML file not found at {html_file}"
        )
    except Exception as e:
        logger.error(f"Error reading HTML file: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error reading HTML file: {str(e)}"
        )


@app.get("/onboarding", response_class=HTMLResponse)
async def read_onboarding():
    return await read_root()


# Initialize Writer API
writer_api_key = os.getenv("WRITER_API_KEY")
if not writer_api_key:
    raise ValueError("WRITER_API_KEY not found in environment variables")

# Initialize ChatWriter with the correct API key
chat_writer = ChatWriter(
    model="palmyra-x-004", temperature=0.7, api_key=SecretStr(writer_api_key)
)

# Initialize GraphTool with the graph ID
graph_ids = os.getenv("GRAPH_IDS")
if not graph_ids:
    raise ValueError("GRAPH_IDS not found in environment variables")

graph_tool = GraphTool(graph_ids=[graph_ids])
llm_with_tools = chat_writer.bind_tools([graph_tool])


async def process_message(message_type: str, content: str, context: list) -> dict:
    try:
        # Prepare system message based on message type
        system_message = (
            "You are a helpful AI assistant for Neuronline, a neuro-fitness platform. "
        )

        if message_type == "welcome":
            system_message += "Provide a warm welcome and introduction to the platform."
        elif message_type == "cognitive_test":
            system_message += "Guide the user through cognitive assessment and provide relevant feedback."
        elif message_type == "physical_test":
            system_message += (
                "Help assess the user's physical condition and fitness goals."
            )
        elif message_type == "plan_generation":
            system_message += "Create a personalized training plan based on the user's profile and test results."
        elif message_type == "plan_customization":
            system_message += "Help customize and refine the training plan according to user preferences."

        # Update context with system message
        context[0] = ("system", system_message)

        # Add the new message to the context
        context.append(("human", content))

        # Get response from Writer API
        response = llm_with_tools.invoke(context)

        # Extract the text content from the response
        response_text = (
            str(response.content) if hasattr(response, "content") else str(response)
        )

        # Add the response to the context
        context.append(("assistant", response_text))

        return {
            "type": "message",
            "content": response_text,
            "message_type": message_type,
        }
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return {"type": "error", "content": f"Извините, произошла ошибка: {str(e)}"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection opened")

    # Initialize conversation context
    context = [
        (
            "system",
            "You are a helpful AI assistant for Neuronline, a neuro-fitness platform.",
        )
    ]

    try:
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()
                logger.info(f"Received message: {data}")

                # Process message based on type
                if "type" not in data:
                    await websocket.send_json(
                        {"type": "error", "content": "Message type not specified"}
                    )
                    continue

                if data["type"] == "welcome":
                    # Special handling for welcome message
                    try:
                        welcome_msg = (
                            "Добро пожаловать в Neuronline! "
                            "Я помогу вам создать персонализированный план тренировок."
                        )
                        await websocket.send_json(
                            {
                                "type": "message",
                                "content": welcome_msg,
                                "message_type": "welcome",
                            }
                        )

                        # Send follow-up message after a short delay
                        await asyncio.sleep(1)
                        follow_up_msg = "Давайте начнем с оценки ваших текущих возможностей и целей."
                        await websocket.send_json(
                            {
                                "type": "message",
                                "content": follow_up_msg,
                                "message_type": "welcome",
                            }
                        )
                    except Exception as e:
                        logger.error(f"Error sending welcome messages: {str(e)}")
                        await websocket.close(code=1001)
                        break

                elif data["type"] in [
                    "message",
                    "cognitive_test",
                    "physical_test",
                    "plan_generation",
                    "plan_customization",
                ]:
                    # Process message with Writer API
                    try:
                        response = await process_message(
                            data["type"], data.get("content", ""), context
                        )
                        await websocket.send_json(response)
                    except Exception as e:
                        logger.error(
                            f"Error processing message with Writer API: {str(e)}"
                        )
                        await websocket.send_json(
                            {
                                "type": "error",
                                "content": f"Ошибка обработки сообщения: {str(e)}",
                            }
                        )

                elif data["type"] == "heartbeat":
                    await websocket.send_json({"type": "heartbeat_ack"})

                else:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "content": f"Неизвестный тип сообщения: {data['type']}",
                        }
                    )

            except json.JSONDecodeError:
                logger.error("Invalid JSON received")
                await websocket.send_json(
                    {"type": "error", "content": "Неверный формат сообщения"}
                )
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected by client")
                break
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                await websocket.send_json(
                    {"type": "error", "content": f"Ошибка: {str(e)}"}
                )
                break

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        try:
            await websocket.close()
        except Exception:
            logger.error("Error closing WebSocket connection")
        logger.info("WebSocket connection closed")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=3000)
