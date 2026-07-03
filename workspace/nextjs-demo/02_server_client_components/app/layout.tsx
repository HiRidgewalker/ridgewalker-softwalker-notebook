import Link from 'next/link'
import './globals.css'

export const metadata = {
  title: '02 · Server/Client Components',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh">
      <body>
        <header className="site-header">
          <h1>02 · Server / Client Components</h1>
          <nav>
            <Link href="/">/</Link>{' · '}
            <Link href="/counter">/counter (混合)</Link>{' · '}
            <Link href="/wrapper">/wrapper (children 模式)</Link>{' · '}
            <Link href="/show-time">/show-time (错误示范)</Link>
          </nav>
        </header>
        <main className="container">{children}</main>
      </body>
    </html>
  )
}
