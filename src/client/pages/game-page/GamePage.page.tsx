import styles from './GamePage.module.css';
import './GamePageOverride.css';
import { useState } from 'react';
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
    const websocket = useWebSocket("1234", "Player 1", true);
    const [gameState, setGameState] = useState<GameState>(GameState.WaitingForPlayers);
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

    const toggleSidebar = () => {
        setIsSidebarOpen(!isSidebarOpen);
    };

    const handleSendMessage = (message: string) => {
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
