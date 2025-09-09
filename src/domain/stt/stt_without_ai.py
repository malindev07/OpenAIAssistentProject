import os
import grpc
import pyaudio
import numpy as np
import time
from dotenv import load_dotenv
from tinkoff.cloud.stt.v1 import stt_pb2_grpc, stt_pb2
from tinkoff.auth import authorization_metadata

# -----------------------------
# Настройка
# -----------------------------
load_dotenv()
endpoint = os.environ.get("VOICEKIT_ENDPOINT")
api_key = os.environ["VOICEKIT_API_KEY"]
secret_key = os.environ["VOICEKIT_SECRET_KEY"]

SAMPLE_RATE = 16000
CHUNK = 800
CHANNELS = 2  # микрофон + голос собеседника


pa = pyaudio.PyAudio()
for i in range(pa.get_device_count()):
    dev = pa.get_device_info_by_index(i)
    print(i, dev["name"], dev["maxInputChannels"])


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
    req.streaming_config.config.num_channels = 1  # STT принимает моно
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

    # первый пакет конфигурации
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

            # Разделяем каналы
            mic_data = data[::2]  # канал 0 = микрофон
            sys_data = data[1::2]  # канал 1 = голос собеседника

            # VU-метр
            mic_level = np.abs(mic_data).mean()
            sys_level = np.abs(sys_data).mean()
            bar_mic = "#" * int(mic_level / 500)
            bar_sys = "-" * int(sys_level / 500)
            print(f"\rMic: {bar_mic:<20} | Sys: {bar_sys:<20}", end="")

            # Микшируем в один моно-поток для STT
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


def print_responses(responses):
    try:
        for response in responses:
            for result in response.results:
                for alt in result.recognition_result.alternatives:
                    print("\nРаспознано:", alt.transcript)
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
    print_responses(responses)
