import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
    title: 'Advocacy Orchestration Dashboard',
    description: 'Multi-agent AI system for grassroots lobbying campaigns',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body className="antialiased">{children}</body>
        </html>
    );
}
