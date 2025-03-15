import { useEffect, useCallback } from 'react';
import { websocketService } from '../services/websocket.service';

export function useWebSocket(
  roomCode: string,
  playerName: string,
  isCreate: boolean,
  onConnect?: () => void,
  onError?: (error: Error) => void
) {
  useEffect(() => {
    websocketService.connect(roomCode, playerName, isCreate)
      .then(() => {
        if (onConnect) onConnect();
      })
      .catch((error) => {
        if (onError) onError(error);
      });

    return () => {
      websocketService.disconnect();
    };
  }, [roomCode, playerName, isCreate, onConnect, onError]);

  const sendMessage = useCallback((type: string, data: any) => {
    websocketService.sendMessage(type, data);
  }, []);

  const onMessageType = useCallback((type: string, handler: (data: any) => void) => {
    return websocketService.onMessageType(type, handler);
  }, []);

  return { sendMessage, onMessageType };
} 