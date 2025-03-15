export class WebSocketService {
    private socket: WebSocket | null = null;
    private messageHandlers: Map<string, (data: any) => void> = new Map();

    connect(roomCode: string, playerName: string, isCreate: boolean): Promise<void> {
        return new Promise((resolve, reject) => {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/room/${roomCode}?player_name=${encodeURIComponent(playerName)}&create=${isCreate}`;

            this.socket = new WebSocket(wsUrl);

            this.socket.onopen = () => {
                console.log('Connected to room');
                resolve();
            };

            this.socket.onmessage = event => {
                try {
                    const message = JSON.parse(event.data);
                    this.handleMessage(message);
                } catch (error) {
                    console.error('Error parsing message:', error);
                }
            };

            this.socket.onclose = event => {
                console.log('Disconnected from room', event.code, event.reason);
                if (event.code === 4000) {
                    reject(new Error('Room already exists. Please try a different code.'));
                } else if (event.code !== 1000) {
                    reject(new Error(`Connection closed: ${event.reason || 'Unknown reason'}`));
                }
            };

            this.socket.onerror = error => {
                console.error('WebSocket error:', error);
                reject(new Error('Error connecting to room'));
            };
        });
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }

    sendMessage(type: string, data: any) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(
                JSON.stringify({
                    type,
                    ...data,
                })
            );
        } else {
            console.error('WebSocket is not connected');
        }
    }

    onMessageType(type: string, handler: (data: any) => void) {
        this.messageHandlers.set(type, handler);
        return () => {
            this.messageHandlers.delete(type);
        };
    }

    private handleMessage(message: any) {
        console.log('Received message:', message);

        const handler = this.messageHandlers.get(message.type);
        if (handler) {
            handler(message);
        }
    }
}

export const websocketService = new WebSocketService();
