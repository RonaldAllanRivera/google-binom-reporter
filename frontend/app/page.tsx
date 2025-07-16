// e:\fullstack\google-binom-reporter\frontend\app\page.tsx
import Link from 'next/link';
import Documentation from '../components/documentation';
import { ThemeToggle } from '../components/theme-toggle';

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center">
          <div className="mr-4 hidden md:flex">
            <a className="mr-6 flex items-center space-x-2" href="/">
              <span className="hidden font-bold sm:inline-block">
                Google Binom Reporter
              </span>
            </a>
          </div>
          <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
            <nav className="flex items-center">
              <Link
                href="/auth/google"
                className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
              >
                Go to Login Page
              </Link>
              <div className="ml-4">
                <ThemeToggle />
              </div>
            </nav>
          </div>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8">
        <Documentation />
      </main>
    </div>
  );
}