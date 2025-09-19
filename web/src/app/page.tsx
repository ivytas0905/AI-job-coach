import Link from 'next/link'
export default function Home() {
  return (
    <main className="p-10 max-w-4xl mx-auto">
      <h1 className="text-4xl font-extrabold text-center">
        Your Career Journey, Guided by an AI That Cares
      </h1>
      <div className="mt-6 space-x-3 text-center">
        <Link 
          href="/sign-in" 
          className="inline-block px-6 py-3 rounded-xl bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors"
        >
          Sign In
        </Link>
        <Link
          href="/dashboard" 
          className="inline-block px-6 py-3 rounded-xl border border-gray-300 text-gray-700 font-medium hover:bg-gray-50 transition-colors"
        >
          Go to Dashboard
        </Link>
      </div>
    </main>
  )
}