import Link from 'next/link'
import './globals.css'

export const metadata = {
  title: '04 · Server Actions',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh">
      <body>
        <header className="site-header">
          <h1>04 · Server Actions</h1>
          <nav>
            <Link href="/">/</Link>{' · '}
            <Link href="/simple-form">/simple-form (原生 form)</Link>{' · '}
            <Link href="/client-form">/client-form (useActionState)</Link>{' · '}
            <Link href="/toggle">/toggle (按钮触发)</Link>
          </nav>
        </header>
        <main className="container">{children}</main>
      </body>
    </html>
  )
}
