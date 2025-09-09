import os
import grpc
import pyaudio
import numpy as np
import time
from dotenv import load_dotenv
import openai
from tinkoff.cloud.stt.v1 import stt_pb2_grpc, stt_pb2
from tinkoff.auth import authorization_metadata

# -----------------------------
# Настройка
# -----------------------------
load_dotenv()
endpoint = os.environ.get("VOICEKIT_ENDPOINT")
api_key = os.environ["VOICEKIT_API_KEY"]
secret_key = os.environ["VOICEKIT_SECRET_KEY"]
openai_api_key = os.environ.get("OPENAI_API_KEY")

SAMPLE_RATE = 16000
CHUNK = 800
CHANNELS = 2  # микрофон + системный звук

SYSTEM_PROMPT = (
    "Ты получаешь краткую выжимку из разговора. На её основе сформулируй полезные и релевантные подсказки: "
    "что собеседнику стоит уточнить, на что обратить внимание, какие следующие шаги предпринять. "
    "Подсказки должны быть короткими, простыми и прикладными."
)

# -----------------------------
# Клиент OpenAI (новый SDK)
# -----------------------------
client = openai.OpenAI(api_key=openai_api_key)


def send_to_assistant(text):
    """Отправляем текст в GPT-4.1-mini с системным промптом"""
    if not text.strip():
        return None
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ]
        response = client.chat.completions.create(
            model="gpt-4.1-mini", messages=messages, temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Ошибка OpenAI:", e)
        return None


# -----------------------------
# Поиск Loopback устройства
# -----------------------------
def find_loopback_device(keyword="PythonSTT"):
    pa = pyaudio.PyAudio()
    for i in range(pa.get_device_count()):
        dev = pa.get_device_info_by_index(i)
        if keyword.lower() in dev["name"].lower() and dev["maxInputChannels"] > 0:
            print(f"✅ Найдено устройство: {dev['name']} (index={i})")
            return i
    raise RuntimeError(f"❌ Устройство '{keyword}' не найдено!")


DEVICE_INDEX = find_loopback_device("PythonSTT")


# -----------------------------
# STT
# -----------------------------
def build_first_request(sample_rate_hertz):
    req = stt_pb2.StreamingRecognizeRequest()
    req.streaming_config.config.encoding = stt_pb2.AudioEncoding.LINEAR16
    req.streaming_config.config.sample_rate_hertz = sample_rate_hertz
    req.streaming_config.config.num_channels = 1
    return req


def generate_requests_loopback():
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        input_device_index=DEVICE_INDEX,
        frames_per_buffer=CHUNK,
    )
    yield build_first_request(SAMPLE_RATE)
    try:
        while True:
            time.sleep(0.01)
            try:
                data = np.frombuffer(
                    stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16
                )
            except IOError:
                continue

            mic_data = data[::2]
            sys_data = data[1::2]

            # VU-метр
            mic_level = np.abs(mic_data).mean()
            sys_level = np.abs(sys_data).mean()
            bar_mic = "#" * int(mic_level / 500)
            bar_sys = "-" * int(sys_level / 500)
            print(f"\rMic: {bar_mic:<20} | Sys: {bar_sys:<20}", end="")

            mixed = (
                (mic_data.astype(np.int32) + sys_data.astype(np.int32)) // 2
            ).astype(np.int16)
            req = stt_pb2.StreamingRecognizeRequest()
            req.audio_content = mixed.tobytes()
            yield req

    except KeyboardInterrupt:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        print("\nЗавершение работы...")


# -----------------------------
# Отправка текста каждые 10 секунд
# -----------------------------
def process_responses_every_10_seconds(responses, interval=10):
    buffer_text = ""
    last_time = time.time()
    try:
        for response in responses:
            for result in response.results:
                for alt in result.recognition_result.alternatives:
                    buffer_text += alt.transcript + " "

            if time.time() - last_time >= interval:
                if buffer_text.strip():
                    print(
                        f"\n\nТекст за последние {interval} секунд:\n{buffer_text.strip()}"
                    )
                    ai_reply = send_to_assistant(buffer_text)
                    if ai_reply:
                        print(f"\nОтвет ассистента:\n{ai_reply}\n")
                buffer_text = ""
                last_time = time.time()

    except grpc._channel._MultiThreadedRendezvous as e:
        print("\ngRPC поток завершен:", e)


# -----------------------------
# Основная
# -----------------------------
if __name__ == "__main__":
    stub = stt_pb2_grpc.SpeechToTextStub(
        grpc.secure_channel(endpoint, grpc.ssl_channel_credentials())
    )
    metadata = authorization_metadata(api_key, secret_key, "tinkoff.cloud.stt")
    responses = stub.StreamingRecognize(generate_requests_loopback(), metadata=metadata)
    process_responses_every_10_seconds(responses, interval=10)
