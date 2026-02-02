import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

interface Metrics {
    num_batches: number;
    num_documents: number;
}

const DashboardPage = () => {
    const { user } = useAuth();
    const [metrics, setMetrics] = useState<Metrics | null>(null);
    const [credits, setCredits] = useState<number>(0);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const token = localStorage.getItem('token');
                if (!token) return;

                const headers = { 'Authorization': `Bearer ${token}` };

                // Fetch Metrics
                const metricsRes = await fetch('/api/v1/users/me/dashboard', { headers });
                if (metricsRes.ok) {
                    const data = await metricsRes.json();
                    setMetrics(data.data);
                }

                // Fetch Credits
                const creditsRes = await fetch('/api/v1/users/me/credits', { headers });
                if (creditsRes.ok) {
                    const data = await creditsRes.json();
                    setCredits(data.data.credits);
                }

            } catch (e: any) {
                setError(e.message);
            }
        };

        fetchData();
    }, []);

    const avg = metrics ? (metrics.num_documents / metrics.num_batches || 0).toFixed(1) : 0;

    // Top Up Message
    const adminNumber = "6285226462973"; // Should be from config, but hardcoded for now or fetched via API
    const topUpMessage = `Halo admin, saya mau top up plagiarism scan (Paket 150rb untuk 3 kali scan). Email saya: ${user?.email}`;
    const whatsappLink = `https://wa.me/${adminNumber}?text=${encodeURIComponent(topUpMessage)}`;

    return (
        <div className="container fade-in" style={{ padding: '60px 0' }}>
            <div style={{ marginBottom: '60px' }}>
                <h1 style={{ fontSize: '48px', fontWeight: 800, marginBottom: '12px', letterSpacing: '-0.02em' }}>
                    Welcome Back
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '18px' }}>
                    Here's an overview of your analysis activity.
                </p>
                <div style={{ marginTop: '20px', display: 'flex', gap: '20px', alignItems: 'center' }}>
                    <div className="glass" style={{ padding: '10px 20px', display: 'inline-flex', alignItems: 'center', gap: '10px', borderRadius: '50px', borderColor: 'var(--primary)' }}>
                        <span style={{ fontSize: '20px' }}>💳</span>
                        <span style={{ fontSize: '16px', fontWeight: 600 }}>Credits: {credits}</span>
                    </div>
                    {credits === 0 && (
                        <div style={{ color: 'var(--error)', fontWeight: 500 }}>
                            ⚠️ Insufficient credits for new scans
                        </div>
                    )}
                </div>
            </div>

            {error && (
                <div className="glass" style={{ padding: '20px', background: 'rgba(239, 68, 68, 0.05)', borderColor: 'rgba(239, 68, 68, 0.2)', borderRadius: '16px', marginBottom: '40px' }}>
                    <p style={{ color: 'var(--error)', fontWeight: 500 }}>⚠️ Error: {error}</p>
                </div>
            )}

            <div style={{ display: 'flex', gap: '16px', marginBottom: '40px' }}>
                <a
                    href={whatsappLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-primary"
                    style={{ padding: '12px 24px', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none', background: '#25D366' }}
                >
                    <span>💬</span> Top Up Credits (WhatsApp)
                </a>
                <button
                    onClick={() => {
                        alert("Please go to a specific batch to export results.");
                    }}
                    className="btn-secondary"
                    style={{ padding: '12px 24px', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}
                >
                    <span>📄</span> Export PDF Report
                </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '32px', marginBottom: '60px' }}>
                {[
                    { label: 'Total Batches', value: metrics?.num_batches || 0, icon: '📦', color: 'var(--primary)' },
                    { label: 'Documents Analyzed', value: metrics?.num_documents || 0, icon: '📄', color: 'var(--secondary)' },
                    { label: 'Avg. per Batch', value: avg, icon: '📊', color: 'var(--accent)' }
                ].map((stat, i) => (
                    <div key={i} className="glass card-hover" style={{ padding: '32px', position: 'relative', overflow: 'hidden' }}>
                        <div style={{
                            position: 'absolute',
                            top: '-10px',
                            right: '-10px',
                            fontSize: '80px',
                            opacity: 0.05,
                            transform: 'rotate(15deg)'
                        }}>
                            {stat.icon}
                        </div>
                        <h3 style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 600 }}>
                            {stat.label}
                        </h3>
                        <p style={{ fontSize: '48px', fontWeight: 800, color: 'white' }}>{stat.value}</p>
                    </div>
                ))}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '32px' }}>
                <Link to="/upload" className="glass card-hover" style={{ textDecoration: 'none', color: credits > 0 ? 'inherit' : 'grey', pointerEvents: credits > 0 ? 'auto' : 'none', padding: '40px', display: 'flex', alignItems: 'center', gap: '24px', opacity: credits > 0 ? 1 : 0.6 }}>
                    <div style={{ fontSize: '40px', background: 'rgba(99, 102, 241, 0.1)', width: '80px', height: '80px', borderRadius: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
                        📤
                    </div>
                    <div>
                        <h3 style={{ fontSize: '22px', fontWeight: 700, marginBottom: '8px' }}>Upload Documents</h3>
                        <p style={{ fontSize: '15px', color: 'var(--text-secondary)' }}>Check for plagiarism & AI content</p>
                        {credits === 0 && <span style={{ fontSize: '12px', color: 'var(--error)' }}>Credits required</span>}
                    </div>
                </Link>

                <Link to="/ai-check" className="glass card-hover" style={{ textDecoration: 'none', color: 'inherit', padding: '40px', display: 'flex', alignItems: 'center', gap: '24px' }}>
                    <div style={{ fontSize: '40px', background: 'rgba(236, 72, 153, 0.1)', width: '80px', height: '80px', borderRadius: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid rgba(236, 72, 153, 0.2)' }}>
                        🤖
                    </div>
                    <div>
                        <h3 style={{ fontSize: '22px', fontWeight: 700, marginBottom: '8px' }}>AI Detection</h3>
                        <p style={{ fontSize: '15px', color: 'var(--text-secondary)' }}>Analyze text for AI authorship</p>
                        <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Free unlimited use</span>
                    </div>
                </Link>
            </div>
        </div>
    );
};

export default DashboardPage;
