import styles from '../app/auth.module.css';

interface AuthTabsProps {
    userType: 'athlete' | 'trainer';
    setUserType: (type: 'athlete' | 'trainer') => void;
}

export default function AuthTabs({ userType, setUserType }: AuthTabsProps) {
    return (
        <div className={styles.tabs}>
            <button
                className={`${styles.tab} ${userType === 'athlete' ? styles.activeTab : ''}`}
                onClick={() => setUserType('athlete')}
            >
                ATHLETE
            </button>
            <button
                className={`${styles.tab} ${userType === 'trainer' ? styles.activeTab : ''}`}
                onClick={() => setUserType('trainer')}
            >
                TRAINER
            </button>
        </div>
    );
}
