import json
from channels.generic.websocket import AsyncWebsocketConsumer

class StockConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'stock_updates'
        # Unirse al grupo de actualizaciones de stock
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Salir del grupo
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Recibir mensaje desde el grupo y enviarlo al WebSocket
    async def stock_update(self, event):
        message = event['message']
        # Enviar mensaje al cliente WebSocket
        await self.send(text_data=json.dumps(message))
