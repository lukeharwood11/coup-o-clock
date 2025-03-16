import styles from './GamePage.module.css';
import './GamePageOverride.css';
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Button } from '../../components/button/Button';
import { MdPerson } from 'react-icons/md';
import { Card } from '../../components/card/Card';
import { MessageBar, Message } from '../../components/message-bar';
import { useWebSocket } from '../../hooks/useWebSocket';

enum GameState {
    WaitingForPlayers = 'WaitingForPlayers',
    InProgress = 'InProgress',
    GameOver = 'GameOver',
}

export const GamePage = () => {
    const { sendMessage, onMessageType } = useWebSocket("1234", "Player 1", true);
    const [gameState] = useState<GameState>(GameState.WaitingForPlayers);
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [handShowing, setHandShowing] = useState(false);
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            text: 'Welcome to Coup O\' Clock!',
            sender: 'system',
            timestamp: new Date(),
        },
        {
            id: '2',
            text: 'Player 1 has joined the game.',
            sender: 'system-notification',
            timestamp: new Date(),
        },
        {
            id: '3',
            text: 'Waiting for other players to join...',
            sender: 'system',
            timestamp: new Date(),
        },
    ]);

    // Example of using the websocket
    useEffect(() => {
        // Listen for game state updates
        const unsubscribe = onMessageType('gameStateUpdate', (data) => {
            // We'll implement this later
            console.log('Game state updated:', data);
        });
        
        return unsubscribe;
    }, [onMessageType]);

    const toggleSidebar = () => {
        setIsSidebarOpen(!isSidebarOpen);
    };

    const handleSendMessage = (messageText: string) => {
        if (messageText.trim()) {
            // Add message to local state
            const newMessage: Message = {
                id: Date.now().toString(),
                text: messageText,
                sender: 'user',
                timestamp: new Date(),
            };
            
            setMessages(prev => [...prev, newMessage]);
            
            // Send message through websocket
            sendMessage('chatMessage', { text: messageText });
        }
    };

    return (
        <div className={styles.gamePage}>
            <div className={styles.gameHeader}>
                <h1 className={styles.gameTitle}>Coup O' Clock</h1>
                <div className={styles.gameHeaderRight}>
                    <Button icon={<MdPerson />} variant="subtle" onClick={() => {}}>
                        Profile
                    </Button>
                </div>
            </div>
            <div className={styles.gameContainer}>
                <MessageBar 
                    isOpen={isSidebarOpen}
                    onToggle={toggleSidebar}
                    messages={messages}
                    onSendMessage={handleSendMessage}
                />
                <div className={styles.mainGameContainer}>
                    <div className={styles.gameContent}>
                        {/* Main game content goes here */}
                        <div className={styles.gameStatus}>
                            {gameState === GameState.WaitingForPlayers && (
                                <p>Waiting for players to join...</p>
                            )}
                        </div>
                        <motion.div
                            onClick={() => setHandShowing(!handShowing)}
                            className={styles.hand}
                        >
                            <Card id="1" width={150} hidden={!handShowing} variant="contessa" />
                            <Card id="2" width={150} hidden={!handShowing} variant="captain" />
                        </motion.div>
                    </div>
                    <div className={styles.gameFooter}>
                        {/* action buttons go here */}
                    </div>
                </div>
            </div>
        </div>
    );
};
