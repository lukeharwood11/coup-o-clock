import { useEffect, useState } from 'react';
import { MdInfo } from 'react-icons/md';
import styles from './Card.module.css';
import { Popup } from '../popup';
import logo from '../../assets/logo.png';
import { motion } from 'framer-motion';
import contessa from '../../assets/contessa.webp';
import captain from '../../assets/captain.webp';
import duke from '../../assets/duke.webp';
import ambassador from '../../assets/ambassador.webp';
import assassin from '../../assets/assassin.webp';
import cardData from '../../constants/cards.json';

export type FlipSpeed = 'fast' | 'slow';

export interface CardProps {
    id: string;
    width?: number;
    className?: string;
    hidden?: boolean;
    flipSpeed?: FlipSpeed;
    variant: 'contessa' | 'captain' | 'duke' | 'ambassador' | 'assassin' | 'unknown';
}

export interface CardData {
    name: string;
    description: string;
    image: string;
}

const getCardImage = (variant: CardProps['variant']): CardData => {
    switch (variant) {
        case 'contessa':
            return {
                name: cardData.contessa.name,
                description: cardData.contessa.description,
                image: contessa,
            };
        case 'captain':
            return {
                name: cardData.captain.name,
                description: cardData.captain.description,
                image: captain,
            };
        case 'duke':
            return {
                name: cardData.duke.name,
                description: cardData.duke.description,
                image: duke,
            };
        case 'ambassador':
            return {
                name: cardData.ambassador.name,
                description: cardData.ambassador.description,
                image: ambassador,
            };
        case 'assassin':
            return {
                name: cardData.assassin.name,
                description: cardData.assassin.description,
                image: assassin,
            };
        default:
            return {
                name: '',
                description: '',
                image: logo,
            };
    }
};

export const Card = ({
    width,
    className,
    hidden,
    flipSpeed = 'fast',
    variant = 'unknown',
}: CardProps) => {
    const [isPopupOpen, setIsPopupOpen] = useState(false);
    const [cardData, setCardData] = useState<CardData>(getCardImage(variant));

    useEffect(() => {
        setCardData(getCardImage(variant));
    }, [variant]);

    const cardStyle = {
        width: width || 200,
    };

    const handleInfoClick = (e: React.MouseEvent) => {
        e.stopPropagation();
        setIsPopupOpen(true);
    };

    const closePopup = () => {
        setIsPopupOpen(false);
    };

    // Animation settings based on flip speed
    const getAnimationSettings = () => {
        if (flipSpeed === 'fast') {
            return {
                duration: 0.1,
                type: 'tween' as const,
                ease: 'easeInOut',
            };
        } else {
            return {
                duration: 0.5,
                type: 'spring' as const,
                stiffness: 200,
                damping: 20,
            };
        }
    };

    const animationSettings = getAnimationSettings();

    return (
        <>
            <div className={`${styles.cardContainer} ${className || ''}`} style={cardStyle}>
                <motion.div
                    className={styles.card}
                    initial={false}
                    animate={{
                        rotateY: hidden ? 180 : 0,
                    }}
                    transition={animationSettings}
                >
                    {/* Front of card */}
                    <div className={styles.cardFace}>
                        <div className={styles.cardImageContainer}>
                            <img
                                src={cardData.image}
                                alt={cardData.name}
                                className={styles.cardImage}
                            />
                        </div>
                        {cardStyle.width > 100 && (
                            <div className={styles.cardFooter}>
                                <h1 className={styles.cardTitle}>{cardData.name}</h1>
                                <button
                                    className={styles.infoButton}
                                    onClick={handleInfoClick}
                                    aria-label="More information"
                                >
                                    <MdInfo />
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Back of card */}
                    <div className={styles.cardFace + ' ' + styles.cardBack}>
                        <img src={logo} alt="Card back" className={styles.cardBackImage} />
                    </div>
                </motion.div>
            </div>

            <Popup
                isOpen={isPopupOpen}
                onClose={closePopup}
                title={cardData.name}
                shadowColor="rgba(0, 0, 0, 0.4)"
                width="350px"
                height="auto"
            >
                <div className={styles.popupContent}>
                    <img src={cardData.image} alt={cardData.name} className={styles.popupImage} />
                    <p>{cardData.description}</p>
                </div>
            </Popup>
        </>
    );
};
