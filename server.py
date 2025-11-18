from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession
import pydantic
from yt_api import YoutubeAPI, YtComments
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
import logging
import sys 

logging.basicConfig(stream=sys.stderr)
logger = logging.getLogger(__name__)

@dataclass
class AppContext:
    yt_client: YoutubeAPI

@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    try:
        yt_client = YoutubeAPI()
        yield AppContext(yt_client=yt_client)
    except Exception as e:
        logger.error(f'Oopsie: {e}')

mcp = FastMCP(name="youtube-mcp", lifespan=server_lifespan, port=8000)

@mcp.tool()
def get_top_comments(context: Context[ServerSession, AppContext], video_id: str, max_results=20) -> list[YtComments]:
    """Fetch the top n comments for a video"""
    yt_client = context.request_context.lifespan_context.yt_client
    return yt_client.get_top_comments(video_id=video_id, max_results=max_results)

if __name__=='__main__':
    mcp.run(transport='streamable-http')