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
from typing import Generator, AsyncGenerator
import grpc
import socket
from jaison_grpc.common import Metadata, STTComponentRequest, STTComponentResponse, T2TComponentRequest, T2TComponentResponse, TTSGComponentRequest, TTSGComponentResponse, TTSCComponentRequest, TTSCComponentResponse
from jaison_grpc.server import add_MetadataInformerServicer_to_server, add_STTComponentStreamerServicer_to_server, add_T2TComponentStreamerServicer_to_server, add_TTSGComponentStreamerServicer_to_server, add_TTSCComponentStreamerServicer_to_server
from jaison_grpc.server import MetadataInformerServicer, STTComponentStreamerServicer, T2TComponentStreamerServicer, TTSGComponentStreamerServicer, TTSCComponentStreamerServicer

from custom import start_stt, start_t2t, start_ttsg, start_ttsc

metadata = None

async def results_streamer(results):
    if not isinstance(results, (Generator,AsyncGenerator)):
        yield results
    elif isinstance(results,Generator):
        for result in results:
            yield result
    else:
        async for result in results:
            yield result

class MetadataInformer(MetadataInformerServicer):
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
    async def invoke(self, request_iterator: AsyncGenerator, context: grpc.aio.ServicerContext) -> AsyncGenerator:
        details_chunk = await anext(request_iterator)
        run_id = details_chunk.run_id
        logging.debug(f"Got request for run_id {run_id}")
        
        results = start_stt(request_iterator)
        async for result in results_streamer(results):
            yield STTComponentResponse(run_id=run_id, content_chunk=result)

class T2TComponentStreamer(T2TComponentStreamerServicer):
    async def invoke(self, request_iterator: AsyncGenerator, context: grpc.aio.ServicerContext) -> AsyncGenerator:
        details_chunk = await anext(request_iterator)
        run_id = details_chunk.run_id
        logging.debug(f"Got request for run_id {run_id}")
        
        results = start_t2t(request_iterator)
        async for result in results_streamer(results):
            yield T2TComponentResponse(run_id=run_id, content_chunk=result)

class TTSGComponentStreamer(TTSGComponentStreamerServicer):
    async def invoke(self, request_iterator: AsyncGenerator, context: grpc.aio.ServicerContext) -> AsyncGenerator:
        details_chunk = await anext(request_iterator)
        run_id = details_chunk.run_id
        logging.debug(f"Got request for run_id {run_id}")
        
        results = start_ttsg(request_iterator)
        async for result, sample_rate, sample_width, channels in results_streamer(results):
            yield TTSGComponentResponse(
                run_id=run_id, 
                audio_chunk=result, 
                sample_rate=sample_rate, 
                sample_width=sample_width, 
                channels=channels
            )

class TTSCComponentStreamer(TTSCComponentStreamerServicer):
    async def invoke(self, request_iterator: AsyncGenerator, context: grpc.aio.ServicerContext) -> AsyncGenerator:
        details_chunk = await anext(request_iterator)
        run_id = details_chunk.run_id
        logging.debug(f"Got request for run_id {run_id}")

        results = start_ttsc(request_iterator)
        async for result, sample_rate, sample_width, channels in results_streamer(results):
            yield TTSCComponentResponse(
                run_id=run_id, 
                audio_chunk=result,
                sample_rate=sample_rate, 
                sample_width=sample_width, 
                channels=channels
            )

async def serve(port) -> None:
    global metadata
    server = grpc.aio.server()

    with open(os.path.join(os.getcwd(), 'metadata.yaml')) as f:
        metadata = yaml.safe_load(f)
    
    add_MetadataInformerServicer_to_server(MetadataInformer(), server)
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

def get_open_port():
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument('--port',type=int,default=-1)
    args = args.parse_args()
    port = args.port if args.port != -1 else get_open_port()
    asyncio.run(serve(port))