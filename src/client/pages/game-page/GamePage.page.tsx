import styles from "./GamePage.module.css"
import "./GamePageOverride.css"
import { useState } from "react"
import { motion } from "framer-motion"
import { Button } from "../../components/button/Button"
import { FaBars, FaTimes } from "react-icons/fa"
import { MdMessage, MdPerson } from "react-icons/md"
import { Card } from "../../components/card/Card"
import contessa from "../../assets/contessa.webp"
import captain from "../../assets/captain.webp"

enum GameState {
    WaitingForPlayers = "WaitingForPlayers",
    InProgress = "InProgress",
    GameOver = "GameOver"
}


export const GamePage = () => {
    const [gameState, setGameState] = useState<GameState>(GameState.WaitingForPlayers);
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [handShowing, setHandShowing] = useState(false);

    const toggleSidebar = () => {
        setIsSidebarOpen(!isSidebarOpen);
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
                <motion.div 
                    className={styles.gameSidebar}
                    initial={{ width: 250 }}
                    animate={{ 
                        width: isSidebarOpen ? 250 : 0,
                        padding: isSidebarOpen ? 20 : 0,
                        opacity: isSidebarOpen ? 1 : 0
                    }}
                    transition={{ duration: 0.3, ease: "easeInOut" }}
                >
                    {/* Sidebar content */}
                </motion.div>
                <motion.div 
                    className={styles.sidebarToggle}
                    animate={{ 
                        left: isSidebarOpen ? 260 : 10 
                    }}
                    transition={{ duration: 0.3, ease: "easeInOut" }}
                >

                    <motion.div
                        className={styles.toggleButtonContainer}
                        animate={{
                            rotate: isSidebarOpen ? 90 : 0
                        }}
                        transition={{ duration: 0.3, ease: "easeInOut" }}
                    >
                        <Button 
                            onClick={toggleSidebar} 
                            variant="subtle"
                            className={styles.toggleButton}
                        >
                            {isSidebarOpen ? <FaTimes /> : <FaBars />}
                        </Button>
                    </motion.div>
                </motion.div>
                <div className={styles.mainGameContainer}>
                    <div className={styles.gameContent}>
                        {/* Main game content goes here */}
                        <motion.div 
                            onClick={() => setHandShowing(!handShowing)}
                            className={styles.hand} >
                            <Card id="1" width={150} hidden={!handShowing} variant="contessa" />
                            <Card id="2" width={150} hidden={!handShowing} variant="captain" />
                        </motion.div>
                    </div>
                    <div className={styles.gameFooter}>
                        {/* action buttons go here */}
                        <Button icon={<MdMessage />} variant="subtle" onClick={() => {}}>
                            Chat
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    )
}