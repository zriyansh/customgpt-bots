from aiohttp import web
import asyncio
from datetime import datetime
import structlog

logger = structlog.get_logger()


class HealthCheckServer:
    def __init__(self, port: int = 8080):
        self.port = port
        self.start_time = datetime.now()
        self.app = web.Application()
        self.stats = {
            'messages_processed': 0,
            'errors': 0,
            'active_sessions': 0
        }
        
        # Setup routes
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/metrics', self.metrics)
    
    async def health_check(self, request):
        """Basic health check endpoint"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return web.json_response({
            'status': 'healthy',
            'uptime_seconds': uptime,
            'timestamp': datetime.now().isoformat()
        })
    
    async def metrics(self, request):
        """Metrics endpoint for monitoring"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return web.json_response({
            'uptime_seconds': uptime,
            'messages_processed': self.stats['messages_processed'],
            'errors': self.stats['errors'],
            'active_sessions': self.stats['active_sessions'],
            'timestamp': datetime.now().isoformat()
        })
    
    def increment_messages(self):
        self.stats['messages_processed'] += 1
    
    def increment_errors(self):
        self.stats['errors'] += 1
    
    def update_sessions(self, count: int):
        self.stats['active_sessions'] = count
    
    async def start(self):
        """Start the health check server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        logger.info("health_check_server_started", port=self.port)