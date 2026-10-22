import Link from 'next/link'
import './globals.css'

export const metadata = {
  title: '03 · Data Fetching',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh">
      <body>
        <header className="site-header">
          <h1>03 · Data Fetching</h1>
          <nav>
            <Link href="/">/</Link>{' · '}
            <Link href="/basic">/basic (Server fetch)</Link>{' · '}
            <Link href="/parallel">/parallel (Promise.all)</Link>{' · '}
            <Link href="/revalidate">/revalidate (ISR)</Link>{' · '}
            <Link href="/no-store">/no-store (每次都重取)</Link>
          </nav>
        </header>
        <main className="container">{children}</main>
      </body>
    </html>
  )
}
