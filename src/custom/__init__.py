## YOU CAN IGNORE THIS TOP SECTION ###########################

from jaison_grpc.common import STTComponentRequest, T2TComponentRequest, TTSGComponentRequest, TTSCComponentRequest
from typing import Tuple
async def request_unpacker(request_iterator):
    async for request_o in request_iterator:
        if isinstance(request_o, STTComponentRequest):
            yield request_o.audio, request_o.sample_rate, request_o.sample_width, request_o.channels
        elif isinstance(request_o, T2TComponentRequest):
            yield request_o.system_input, request_o.user_input
        elif isinstance(request_o, TTSGComponentRequest):
            yield request_o.content
        elif isinstance(request_o, TTSCComponentRequest):
            yield request_o.audio, request_o.sample_rate, request_o.sample_width, request_o.channels
        else:
            raise Exception(f"Unknown request type: {type(request_o)}")              
            
## IMPLEMENTATIONS START BELOW ###############################
'''
Supported component type entrypoints

- Implement the specific entrypoint (start_stt, start_t2t, etc) associated with your component type
    - Example implementation shows expected return/yield results
    - Keep the line "async for audio_chunk, sample_rate, sample_width, channels in request_unpacker(request_iterator):"
        as this is for extracting stream of input chunks
    - You can leave the others as is

- You may yield or return your result

WARNING: Can't send results that are too large. When in doubt, yield with chunks of your response in order.
'''

# For speech-to-text models
async def start_stt(request_iterator) -> str:
    async for audio_chunk, sample_rate, sample_width, channels in request_unpacker(request_iterator):
        audio_chunk: bytes
        sample_rate: int
        sample_width: int
        channels: int

        response = "Hello world from STT!"
        yield response

# For text generation models
async def start_t2t(request_iterator) -> str:
    async for system_input_chunk, user_input_chunk in request_unpacker(request_iterator):
        system_input_chunk: str
        user_input_chunk: str

        response = "Hello world from T2T!"
        yield response

# For text-to-speech generation
async def start_ttsg(request_iterator) -> Tuple[bytes, int, int, int]:
    async for content_chunk in request_unpacker(request_iterator):
        content_chunk: str

        audio_chunk, sample_rate, sample_width, channels = b"\x00\x00", 48000, 2, 1
        yield audio_chunk, sample_rate, sample_width, channels

# For voice changers
async def start_ttsc(request_iterator) -> Tuple[bytes, int, int, int]:
    async for audio_chunk, sample_rate, sample_width, channels in request_unpacker(request_iterator):
        audio_chunk: bytes
        sample_rate: int
        sample_width: int
        channels: int

        yield audio_chunk, sample_rate, sample_width, channels