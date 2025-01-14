from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(
    filename='output.log',
    format="[%(asctime)s] [%(levelname)-5.5s] [%(filename)s::%(lineno)d %(funcName)s]: %(message)s",
    level=logging.DEBUG
)

import argparse
import asyncio
import logging
import yaml
import os
import types
import grpc
from jaison_grpc.common import Metadata, STTComponentRequest, STTComponentResponse, T2TComponentRequest, T2TComponentResponse, TTSGComponentRequest, TTSGComponentResponse, TTSCComponentRequest, TTSCComponentResponse
from jaison_grpc.server import add_MetadataInformerServicer_to_server, add_STTComponentStreamerServicer_to_server, add_T2TComponentStreamerServicer_to_server, add_TTSGComponentStreamerServicer_to_server, add_TTSCComponentStreamerServicer_to_server
from jaison_grpc.server import MetadataInformerServicer, STTComponentStreamerServicer, T2TComponentStreamerServicer, TTSGComponentStreamerServicer, TTSCComponentStreamerServicer

from custom import start_stt, start_t2t, start_ttsg, start_ttsc

metadata = None

def results_streamer(results):
    if type(results) is not types.GeneratorType:
        yield results
    else:
        for result in results:
            yield result

class STTComponentStreamer(STTComponentStreamerServicer):
    def metadata(self, request, context: grpc.aio.ServicerContext) -> Metadata:
        global metadata
        return Metadata(
            id=metadata['id'],
            name=metadata['name'],
            type=metadata['type'],
            is_windows_compatible=metadata['is_windows_compatible'],
            is_unix_compatible=metadata['is_unix_compatible'],
            windows_run_script=metadata['windows_run_script'],
            unix_run_script=metadata['unix_run_script']
        )

class STTComponentStreamer(STTComponentStreamerServicer):
    async def invoke(self, request: STTComponentRequest, context: grpc.aio.ServicerContext) -> STTComponentResponse:
        results = start_stt(request.audio)
        for result in results_streamer(results):
            yield request.run_id, result

class T2TComponentStreamer(T2TComponentStreamerServicer):
    async def invoke(self, request: T2TComponentRequest, context: grpc.aio.ServicerContext) -> T2TComponentResponse:
        results = start_t2t(request.system_input, request.user_input)
        for result in results_streamer(results):
            yield request.run_id, result

class TTSGComponentStreamer(TTSGComponentStreamerServicer):
    async def invoke(self, request: TTSGComponentRequest, context: grpc.aio.ServicerContext) -> TTSGComponentResponse:
        results = start_ttsg(request.content)
        for result in results_streamer(results):
            yield request.run_id, result

class TTSCComponentStreamer(TTSCComponentStreamerServicer):
    async def invoke(self, request: TTSCComponentRequest, context: grpc.aio.ServicerContext) -> TTSCComponentResponse:
        results = start_ttsc(request.audio)
        for result in results_streamer(results):
            yield request.run_id, result

async def serve(port) -> None:
    global metadata
    server = grpc.aio.server()

    with open(os.path.join(os.getcwd(), 'metadata.yaml')) as f:
        metadata = yaml.safe_load(f)
    
    add_STTComponentStreamerServicer_to_server(STTComponentStreamer(), server)
    match metadata['type']:
        case 'stt':
            add_STTComponentStreamerServicer_to_server(STTComponentStreamer(), server)
        case 't2t':
            add_T2TComponentStreamerServicer_to_server(T2TComponentStreamer(), server)
        case 'ttsg':
            add_TTSGComponentStreamerServicer_to_server(TTSGComponentStreamer(), server)
        case 'ttsc':
            add_TTSCComponentStreamerServicer_to_server(TTSCComponentStreamer(), server)
        case _:
            raise Exception("Unknown component type in metadata.")

    listen_addr = f"0.0.0.0:{port}"
    server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", listen_addr)
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument('--port')
    args = args.parse_args()
    asyncio.run(serve(args.port))
