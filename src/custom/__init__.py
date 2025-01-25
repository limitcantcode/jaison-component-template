'''
Supported component type entrypoints

- Implement the specific entrypoint associated with your component type
- You can leave the others unimplemented

To support streaming, your implementation should be a generator: https://wiki.python.org/moin/Generators
You may also simply return the final result
'''

from jaison_grpc.common import STTComponentRequest, T2TComponentRequest, TTSGComponentRequest, TTSCComponentRequest
async def request_unpacker(request_iterator):
    async for request_o in request_iterator:
        match request_o:
            case STTComponentRequest():
                yield request_o.audio, request_o.sample_rate, request_o.sample_width, request_o.channels
            case T2TComponentRequest():
                yield request_o.system_input, request_o.user_input
            case TTSGComponentRequest():
                yield request_o.content
            case TTSCComponentRequest():
                yield request_o.audio, request_o.sample_rate, request_o.sample_width, request_o.channels
            case _:
                raise Exception(f"Unknown request type: {type(request_o)}")

# For speech-to-text models
async def start_stt(request_iterator):
    async for audio_chunk, sample_rate, sample_width, channels in request_unpacker(request_iterator): # receiving chunks of info through a stream
        raise NotImplementedError

# For text generation models
async def start_t2t(request_iterator):
    async for system_input_chunk, user_input_chunk in request_unpacker(request_iterator): # receiving chunks of info through a stream
        raise NotImplementedError

# For text-to-speech generation
async def start_ttsg(request_iterator):
    async for content_chunk in request_unpacker(request_iterator): # receiving chunks of info through a stream
        raise NotImplementedError

# For voice changers
async def start_ttsc(request_iterator):
    async for audio_chunk, sample_rate, sample_width, channels in request_unpacker(request_iterator): # receiving chunks of info through a stream
        raise NotImplementedError