import React, { ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './Popup.module.css';
import { MdClose } from 'react-icons/md';
import { Button } from '../button/Button';

interface PopupProps {
  isOpen: boolean;
  onClose: () => void;
  children: ReactNode;
  height: string;
  shadowColor?: string;
  width?: string;
  title?: string;
}

const Popup: React.FC<PopupProps> = ({
  isOpen,
  onClose,
  children,
  title,
  shadowColor = 'rgba(0, 0, 0, 0.3)',
  width = '400px',
  height = 'auto',
}) => {
  // Stop propagation to prevent closing when clicking inside the popup
  const handleContentClick = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className={styles.overlay}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            className={styles.popup}
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            onClick={handleContentClick}
            style={{
              width,
              height,
              boxShadow: `0 10px 25px ${shadowColor}`,
            }}
          >
            <div className={styles.popupHeader}>
              <h2 className={styles.title}>{title}</h2>
              <Button onClick={onClose} variant="secondary">
                <MdClose />
              </Button>
            </div>
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default Popup;
