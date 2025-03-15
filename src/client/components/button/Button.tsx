import { ReactNode } from "react";
import styles from "./Button.module.css"

export interface ButtonProps {
    children: ReactNode;
    onClick: () => void;
    className?: string;
    variant?: "primary" | "secondary" | "danger" | "subtle";
    icon?: ReactNode;
}

export const Button = ({ children, onClick, className, variant = "primary", icon }: ButtonProps) => {
    return (
        <button className={`${styles.button} ${className} ${styles[variant]}`} onClick={onClick}>
            {children}
            {icon && <span className={styles.icon}>{icon}</span>}
        </button>
    )
}