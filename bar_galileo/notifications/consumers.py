# notificaciones/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificacionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        print(f"[DEBUG][Consumer] Usuario conectado: {self.user} (auth={self.user.is_authenticated})")
        if self.user.is_authenticated:
            self.group_name = f"user_{self.user.id}"
            print(f"[DEBUG][Consumer] Uniendo al grupo: {self.group_name}")
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            print("[DEBUG][Consumer] Usuario no autenticado, cerrando WebSocket")
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            print(f"[DEBUG][Consumer] Saliendo del grupo: {self.group_name}")
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def enviar_mensaje(self, event):
        print(f"[DEBUG][Consumer] Enviando mensaje al usuario: {event['message']}")
        await self.send(text_data=json.dumps({
            "message": event["message"]
        }))

