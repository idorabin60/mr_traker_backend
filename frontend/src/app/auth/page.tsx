"use client";

import { useState } from 'react';
import styles from '../auth.module.css';
import AuthTabs from '../../components/AuthTabs';

export default function AuthPage() {
    const [userType, setUserType] = useState<'athlete' | 'trainer'>('athlete');
    const [isLogin, setIsLogin] = useState(true);

    // State for form fields
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [organization, setOrganization] = useState('');
    const [trainerPasskey, setTrainerPasskey] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const formData = {
            userType,
            username,
            password,
            ...(userType === 'athlete' ? { trainerPasskey } : { organization }),
            ...(!isLogin ? { email } : {})
        };

        console.log(`Submitting ${isLogin ? 'Login' : 'Signup'} for ${userType}:`, formData);
        alert("Form Submitted (Console Log Only)");
    };

    return (
        <div className={styles.container}>
            <div className={styles.authCard}>
                <div className={styles.header}>
                    <h1 className={styles.title}>MR. TRAKER</h1>
                    <p className={styles.subtitle}>
                        {isLogin ? `Welcome back, ${userType === 'athlete' ? 'Athlete' : 'Trainer'}.` : `Create your ${userType} account.`}
                    </p>
                </div>

                <AuthTabs userType={userType} setUserType={setUserType} />

                <form onSubmit={handleSubmit}>
                    <div className={styles.formGroup}>
                        <label className={styles.label}>USERNAME</label>
                        <input
                            className={styles.input}
                            placeholder="Enter your username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>

                    {!isLogin && (
                        <div className={styles.formGroup}>
                            <label className={styles.label}>EMAIL</label>
                            <input
                                className={styles.input}
                                type="email"
                                placeholder="name@example.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>
                    )}

                    <div className={styles.formGroup}>
                        <label className={styles.label}>PASSWORD</label>
                        <input
                            className={styles.input}
                            type="password"
                            placeholder="******"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    {!isLogin && userType === 'trainer' && (
                        <div className={styles.formGroup}>
                            <label className={styles.label}>ORGANIZATION</label>
                            <input
                                className={styles.input}
                                placeholder="Team or Gym Name"
                                value={organization}
                                onChange={(e) => setOrganization(e.target.value)}
                            />
                        </div>
                    )}

                    {!isLogin && userType === 'athlete' && (
                        <div className={styles.formGroup}>
                            <label className={styles.label}>TRAINER PASSKEY</label>
                            <input
                                className={styles.input}
                                placeholder="Ask your trainer for their code"
                                value={trainerPasskey}
                                onChange={(e) => setTrainerPasskey(e.target.value)}
                                required
                            />
                        </div>
                    )}

                    <button type="submit" className={styles.submitButton}>
                        {isLogin ? "SIGN IN" : "CREATE ACCOUNT"}
                    </button>

                    <div className={styles.toggleContainer}>
                        {isLogin ? "Don't have an account?" : "Already have an account?"}
                        <span className={styles.toggleLink} onClick={() => setIsLogin(!isLogin)}>
                            {isLogin ? "Sign Up" : "Sign In"}
                        </span>
                    </div>
                </form>
            </div>
        </div>
    );
}
