import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaTimes } from 'react-icons/fa';
import { MdMessage } from 'react-icons/md';
import { Button } from '../button/Button';
import { MessageBubble } from './MessageBubble';
import styles from './MessageBar.module.css';

export interface Message {
    id: string;
    text: string;
    sender: 'user' | 'system' | 'system-notification';
    timestamp: Date;
}

export interface MessageBarProps {
    isOpen: boolean;
    onToggle: () => void;
    messages?: Message[];
    onSendMessage?: (message: string) => void;
}

export const MessageBar = ({
    isOpen,
    onToggle,
    messages = [],
    onSendMessage = () => {},
}: MessageBarProps) => {
    const [newMessage, setNewMessage] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const [isContentVisible, setIsContentVisible] = useState(isOpen);

    const handleSendMessage = (e: React.FormEvent) => {
        e.preventDefault();
        if (newMessage.trim()) {
            onSendMessage(newMessage);
            setNewMessage('');
        }
    };

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Control content visibility based on isOpen state
    useEffect(() => {
        if (isOpen) {
            setIsContentVisible(true);
        } else {
            // Delay hiding content until animation completes
            const timer = setTimeout(() => {
                setIsContentVisible(false);
            }, 300); // Match this with the stagger duration
            return () => clearTimeout(timer);
        }
    }, [isOpen]);

    // Animation variants
    const containerVariants = {
        open: {
            width: "min(400px, 100%)",
            padding: 20,
            opacity: 1,
            transition: {
                duration: 0.3,
                ease: 'easeInOut',
                when: "beforeChildren",
                staggerChildren: 0.05
            }
        },
        closed: {
            width: 0,
            padding: 0,
            opacity: 0,
            transition: {
                duration: 0.3,
                ease: 'easeInOut',
                when: "afterChildren",
                staggerChildren: 0.05,
                staggerDirection: -1
            }
        }
    };

    const itemVariants = {
        open: {
            opacity: 1,
            y: 0,
            transition: { duration: 0.2 }
        },
        closed: {
            opacity: 0,
            y: 10,
            transition: { duration: 0.2 }
        }
    };

    return (
        <>
            <motion.div
                className={styles.messageBar}
                variants={containerVariants}
                initial="closed"
                animate={isOpen ? "open" : "closed"}
            >
                {isContentVisible && (
                    <>
                        <motion.div className={styles.messageBarHeader} variants={itemVariants}>
                            <h2>Messages</h2>
                        </motion.div>
                        <motion.div className={styles.messagesContainer} variants={itemVariants}>
                            <AnimatePresence>
                                {messages.map((message) => (
                                    <MessageBubble key={message.id} message={message} />
                                ))}
                            </AnimatePresence>
                            <div ref={messagesEndRef} />
                        </motion.div>
                        <motion.form 
                            className={styles.messageInputContainer} 
                            onSubmit={handleSendMessage}
                            variants={itemVariants}
                        >
                            <input
                                type="text"
                                value={newMessage}
                                onChange={(e) => setNewMessage(e.target.value)}
                                placeholder="Type a message..."
                                className={styles.messageInput}
                            />
                            <Button 
                                variant="primary" 
                                className={styles.sendButton} 
                                onClick={() => {
                                    handleSendMessage(new Event('submit') as unknown as React.FormEvent);
                                }}
                            >
                                Send
                            </Button>
                        </motion.form>
                    </>
                )}
            </motion.div>
            <motion.div
                className={styles.sidebarToggle}
            >
                <motion.div
                    className={styles.toggleButtonContainer}
                    animate={{
                        rotate: isOpen ? 90 : 0,
                    }}
                    transition={{ duration: 0.3, ease: 'easeInOut' }}
                >
                    <Button
                        onClick={onToggle}
                        variant="subtle"
                        className={styles.toggleButton}
                    >
                        {isOpen ? <FaTimes /> : <MdMessage />}
                    </Button>
                </motion.div>
            </motion.div>
        </>
    );
}; 