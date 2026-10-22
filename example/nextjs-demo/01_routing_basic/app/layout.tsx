import Link from 'next/link'
import './globals.css'

export const metadata = {
  title: '01 · Routing Basic Demo',
  description: 'Next.js App Router 文件式路由 demo',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh">
      <body>
        <header className="site-header">
          <h1>01 · Routing Basic</h1>
          <nav>
            <Link href="/">/</Link>{' · '}
            <Link href="/about">/about</Link>{' · '}
            <Link href="/blog">/blog</Link>{' · '}
            <Link href="/blog/hello-world">/blog/hello-world</Link>{' · '}
            <Link href="/docs">/docs</Link>{' · '}
            <Link href="/docs/intro">/docs/intro</Link>{' · '}
            <Link href="/docs/intro/setup">/docs/intro/setup</Link>
          </nav>
        </header>
        <main className="container">{children}</main>
      </body>
    </html>
  )
}
