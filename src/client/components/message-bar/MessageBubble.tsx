import { motion } from 'framer-motion';
import { Message } from './MessageBar';
import styles from './MessageBar.module.css';

export interface MessageBubbleProps {
    message: Message;
}

export const MessageBubble = ({ message }: MessageBubbleProps) => {
    // Check if the message is a system notification
    if (message.sender === 'system-notification') {
        return (
            <motion.div
                className={styles.systemNotification}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
            >
                <p>{message.text}</p>
            </motion.div>
        );
    }

    // Regular message bubble for user or system messages
    return (
        <motion.div
            className={`${styles.message} ${
                message.sender === 'user' ? styles.userMessage : styles.systemMessage
            }`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
        >
            <div className={styles.messageContent}>
                <p>{message.text}</p>
                <span className={styles.timestamp}>
                    {message.timestamp.toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                    })}
                </span>
            </div>
        </motion.div>
    );
}; 